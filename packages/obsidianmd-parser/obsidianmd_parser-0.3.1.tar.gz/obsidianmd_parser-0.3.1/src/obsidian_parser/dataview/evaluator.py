# src/obsidian_parser/dataview/evaluator.py
"""Dataview query evaluation engine."""

import re
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from obsidian_parser.models.dataview import DataviewQuery, DataviewQueryType
from obsidian_parser.note import Note
from obsidian_parser.vault import Vault


class DataviewEvaluator:
    """Evaluates Dataview queries against a vault."""

    def __init__(self, vault: Vault):
        """Initialize evaluator with a vault.

        Args:
            vault: The vault to query against
        """
        self.vault = vault
        self._metadata_cache: dict[str, dict[str, Any]] = {}

    def evaluate(self, query: DataviewQuery, context_note: Optional[Note] = None) -> pd.DataFrame:
        """Evaluate a Dataview query.

        Args:
            query: The query to evaluate
            context_note: The note containing the query (for 'this' references)

        Returns:
            DataFrame with query results
        """
        # Get candidate notes based on FROM clause
        candidates = self._get_candidates(query.from_clause, context_note)

        # Filter based on WHERE clause
        if query.where_clause:
            candidates = self._apply_where(candidates, query.where_clause, context_note)

        # Build result data
        if query.query_type == DataviewQueryType.TABLE:
            df = self._build_table(candidates, query)
        elif query.query_type == DataviewQueryType.LIST:
            df = self._build_list(candidates)
        else:
            raise NotImplementedError(f"Query type {query.query_type} not yet supported")

        # Apply sorting
        if query.sort_clauses and not df.empty:
            for sort in reversed(query.sort_clauses):  # Apply in reverse order
                df = self._apply_sort(df, sort)

        # Apply limit
        if query.limit and len(df) > query.limit:
            df = df.head(query.limit)

        return df

    def _get_candidates(self, from_clause: str | None, context_note: Note | None) -> list[Note]:
        """Get candidate notes based on FROM clause.

        Args:
            from_clause: The FROM clause (e.g., '"Lore/Locations"', '#tag')
            context_note: The note containing the query

        Returns:
            List of candidate notes
        """
        if not from_clause:
            # No FROM clause means all notes
            return self.vault.notes

        from_clause = from_clause.strip()

        # Handle folder paths (quoted strings)
        if from_clause.startswith('"') and from_clause.endswith('"'):
            folder = from_clause[1:-1]
            return self._get_notes_in_folder(folder)

        # Handle tags
        if from_clause.startswith("#"):
            tag = from_clause[1:]
            return self.vault.get_notes_with_tag(tag)

        # Handle other patterns (simplified for now)
        return self.vault.notes

    def _get_notes_in_folder(self, folder: str) -> list[Note]:
        """Get all notes in a specific folder.

        Args:
            folder: Folder path relative to vault root

        Returns:
            List of notes in the folder
        """
        folder_path = self.vault.path / folder
        notes = []

        for note in self.vault.notes:
            # Check if note is in the specified folder
            try:
                note.path.relative_to(folder_path)
                notes.append(note)
            except ValueError:
                # Not in this folder
                continue

        return notes

    def _get_metadata(self, note: Note) -> dict[str, Any]:
        """Get all metadata for a note (cached).

        Args:
            note: The note to get metadata for

        Returns:
            Dictionary of metadata
        """
        if note.path not in self._metadata_cache:
            metadata = {
                "file": {
                    "name": note.name,
                    "link": f"[[{note.name}]]",  # Add file.link
                    "path": str(note.path.relative_to(self.vault.path)),
                    "folder": str(note.path.parent.relative_to(self.vault.path)),
                    "ext": note.path.suffix,
                    "size": note.path.stat().st_size,
                    "ctime": note.path.stat().st_ctime,
                    "mtime": note.path.stat().st_mtime,
                },
                **note.get_metadata(),  # Frontmatter + inline fields
            }
            self._metadata_cache[note.path] = metadata

        return self._metadata_cache[note.path]

    def _evaluate_function(self, func_name: str, args_str: str, note: Note, context_note: Note | None) -> bool:
        """Evaluate a Dataview function.

        Args:
            func_name: The function name (e.g., 'contains')
            args_str: The function arguments as a string
            note: The note being evaluated
            context_note: The note containing the query

        Returns:
            The function result
        """
        # Parse arguments
        args = [arg.strip() for arg in self._split_function_args(args_str)]

        if func_name == "contains":
            if len(args) != 2:
                return False

            # Evaluate both arguments
            container = self._evaluate_expression(args[0], note, context_note)
            value = self._evaluate_expression(args[1], note, context_note)

            # Handle different container types
            if container is None or value is None:
                return False

            # Normalize the search value - remove [[ ]] if present
            search_value = str(value).strip()
            search_value_plain = search_value.strip("[]")
            search_value_link = f"[[{search_value_plain}]]"

            if isinstance(container, str):
                # For strings, check if value is contained (case-insensitive)
                container_lower = container.lower()
                return (
                    search_value.lower() in container_lower
                    or search_value_plain.lower() in container_lower
                    or search_value_link.lower() in container_lower
                )

            if isinstance(container, list):
                # For lists, check each item
                for item in container:
                    if item is None:
                        continue

                    item_str = str(item).strip()
                    item_lower = item_str.lower()

                    # Check if the item matches any form of the search value
                    if (
                        item_lower == search_value.lower()
                        or item_lower == search_value_plain.lower()
                        or item_lower == search_value_link.lower()
                        or
                        # Also check if the plain value is contained within a wikilink
                        (
                            item_str.startswith("[[")
                            and item_str.endswith("]]")
                            and item_str[2:-2].lower() == search_value_plain.lower()
                        )
                    ):
                        return True

                return False

            # For other types, convert to string and check
            container_str = str(container).lower()
            return (
                search_value.lower() in container_str
                or search_value_plain.lower() in container_str
                or search_value_link.lower() in container_str
            )

        # Add more functions as needed
        print(f"Warning: Unknown function '{func_name}'")
        return False

    def _evaluate_expression(self, expr: str, note: Note, context_note: Note | None) -> Any:
        """Evaluate a Dataview expression.

        Args:
            expr: The expression to evaluate (e.g., 'file.name', 'this.region')
            note: The note being evaluated
            context_note: The note containing the query

        Returns:
            The evaluated value
        """
        expr = expr.strip()
        metadata = self._get_metadata(note)

        # Handle quoted strings
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Handle numbers
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Handle boolean
        if expr.lower() in ("true", "false"):
            return expr.lower() == "true"

        metadata = self._get_metadata(note)

        # Handle 'this' references
        if expr.startswith("this.") and context_note:
            this_metadata = self._get_metadata(context_note)
            field = expr[5:]  # Remove 'this.'
            return self._get_field_value(this_metadata, field)

        # Handle file properties
        if expr.startswith("file."):
            field = expr[5:]  # Remove 'file.'
            return metadata["file"].get(field)

        # Direct field reference
        return self._get_field_value(metadata, expr)

    def _get_field_value(self, metadata: dict[str, Any], field: str) -> Any:
        """Get a field value from metadata, handling nested fields.

        Args:
            metadata: The metadata dictionary
            field: The field name (may be nested with dots)

        Returns:
            The field value
        """
        parts = field.split(".")
        value = metadata

        for part in parts:
            if isinstance(value, dict):
                # Try exact match first
                if part in value:
                    value = value.get(part)
                else:
                    # Try case-insensitive match
                    for key in value.keys():
                        if key.lower() == part.lower():
                            value = value[key]
                            break
                    else:
                        return None
            else:
                return None

        return value

    def _apply_where(self, notes: list[Note], where_clause: str, context_note: Note | None) -> list[Note]:
        """Apply WHERE clause filtering.

        Args:
            notes: List of notes to filter
            where_clause: The WHERE clause
            context_note: The note containing the query

        Returns:
            Filtered list of notes
        """
        filtered = []

        for note in notes:
            if self._evaluate_where_condition(note, where_clause, context_note):
                filtered.append(note)

        return filtered

    def _evaluate_where_condition(self, note: Note, condition: str, context_note: Note | None) -> bool:
        """Evaluate a WHERE condition for a note.

        Args:
            note: The note to evaluate
            condition: The WHERE condition
            context_note: The note containing the query

        Returns:
            True if condition is met
        """
        condition = condition.strip()
        if condition.startswith("(") and condition.endswith(")"):
            # Check if these are matching outer parentheses
            depth = 0
            for i, char in enumerate(condition):
                if char == "(":
                    depth += 1
                elif char == ")":
                    depth -= 1
                if depth == 0 and i < len(condition) - 1:
                    # Not outer parentheses
                    break
            else:
                # These are outer parentheses, remove them
                condition = condition[1:-1].strip()

        # Handle OR with proper precedence (OR has lower precedence than AND)
        # First, split by OR at the top level (not inside parentheses)
        or_parts = self._split_by_operator(condition, " OR ")
        if len(or_parts) > 1:
            return any(self._evaluate_where_condition(note, part.strip(), context_note) for part in or_parts)

        # Handle AND at the top level
        and_parts = self._split_by_operator(condition, " AND ")
        if len(and_parts) > 1:
            return all(self._evaluate_where_condition(note, part.strip(), context_note) for part in and_parts)

        # Handle function calls like contains()
        func_match = re.match(r"(\w+)\s*\((.*)\)", condition.strip())
        if func_match:
            func_name = func_match.group(1)
            args_str = func_match.group(2)
            return self._evaluate_function(func_name, args_str, note, context_note)

        # Handle != comparison
        if " != " in condition:
            left, right = condition.split(" != ", 1)
            left_val = self._evaluate_expression(left.strip(), note, context_note)
            right_val = self._evaluate_expression(right.strip(), note, context_note)
            return left_val != right_val

        # Handle = comparison
        if " = " in condition:
            left, right = condition.split(" = ", 1)
            left_val = self._evaluate_expression(left.strip(), note, context_note)
            right_val = self._evaluate_expression(right.strip(), note, context_note)
            return left_val == right_val

        # If we can't parse the condition, return False (safer than True)
        print(f"Warning: Could not parse WHERE condition: {condition}")
        return False

    def _split_by_operator(self, text: str, operator: str) -> list[str]:
        """Split text by operator, respecting parentheses.

        Args:
            text: The text to split
            operator: The operator to split by (e.g., ' AND ', ' OR ')

        Returns:
            List of parts
        """
        parts = []
        current = []
        paren_depth = 0
        i = 0

        while i < len(text):
            if text[i] == "(":
                paren_depth += 1
                current.append(text[i])
            elif text[i] == ")":
                paren_depth -= 1
                current.append(text[i])
            elif paren_depth == 0 and text[i : i + len(operator)] == operator:
                # Found operator at top level
                parts.append("".join(current))
                current = []
                i += len(operator) - 1  # Skip the operator
            else:
                current.append(text[i])
            i += 1

        # Don't forget the last part
        if current:
            parts.append("".join(current))

        return parts if len(parts) > 1 else [text]

    def _evaluate_function(self, func_name: str, args_str: str, note: Note, context_note: Note | None) -> bool:
        """Evaluate a Dataview function.

        Args:
            func_name: The function name (e.g., 'contains')
            args_str: The function arguments as a string
            note: The note being evaluated
            context_note: The note containing the query

        Returns:
            The function result
        """
        # Parse arguments (simple comma split - doesn't handle nested functions)
        args = [arg.strip() for arg in self._split_function_args(args_str)]

        if func_name == "contains":
            if len(args) != 2:
                return False

            # Evaluate both arguments
            container = self._evaluate_expression(args[0], note, context_note)
            value = self._evaluate_expression(args[1], note, context_note)

            # Handle different container types
            if container is None:
                return False

            if isinstance(container, str) and isinstance(value, str):
                return value.lower() in container.lower()

            if isinstance(container, list):
                # Check if value is in the list (case-insensitive for strings)
                return any(
                    (isinstance(item, str) and isinstance(value, str) and item.lower() == value.lower())
                    or item == value
                    for item in container
                )

            return False

        # Add more functions as needed
        print(f"Warning: Unknown function '{func_name}'")
        return False

    def _split_function_args(self, args_str: str) -> list[str]:
        """Split function arguments respecting quotes and parentheses.

        Args:
            args_str: The arguments string

        Returns:
            List of argument strings
        """
        args = []
        current = []
        paren_depth = 0
        quote_char = None

        for char in args_str:
            if quote_char:
                # Inside quotes
                current.append(char)
                if char == quote_char and (not current or current[-2] != "\\"):
                    quote_char = None
            elif char in ('"', "'"):
                # Starting quotes
                quote_char = char
                current.append(char)
            elif char == "(":
                paren_depth += 1
                current.append(char)
            elif char == ")":
                paren_depth -= 1
                current.append(char)
            elif char == "," and paren_depth == 0:
                # Argument separator
                args.append("".join(current).strip())
                current = []
            else:
                current.append(char)

        # Don't forget the last argument
        if current:
            args.append("".join(current).strip())

        return args

    def _evaluate_expression(self, expr: str, note: Note, context_note: Note | None) -> Any:
        """Evaluate a Dataview expression.

        Args:
            expr: The expression to evaluate (e.g., 'file.name', 'this.region')
            note: The note being evaluated
            context_note: The note containing the query

        Returns:
            The evaluated value
        """
        expr = expr.strip()

        # Handle quoted strings
        if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Handle numbers
        try:
            if "." in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Handle boolean
        if expr.lower() in ("true", "false"):
            return expr.lower() == "true"

        metadata = self._get_metadata(note)

        # Handle 'this' references
        if expr.startswith("this.") and context_note:
            this_metadata = self._get_metadata(context_note)
            field = expr[5:]  # Remove 'this.'
            return self._get_field_value(this_metadata, field)

        # Handle file properties
        if expr.startswith("file."):
            field = expr[5:]  # Remove 'file.'
            return metadata["file"].get(field)

        # Direct field reference
        return self._get_field_value(metadata, expr)

    def _build_table(self, notes: list[Note], query: DataviewQuery) -> pd.DataFrame:
        """Build a table from notes based on query fields.

        Args:
            notes: List of notes to include
            query: The query with field definitions

        Returns:
            DataFrame with table data
        """
        data = []

        for note in notes:
            row = {"File": f"[[{note.name}]]"}

            # Add requested fields
            for field in query.fields:
                value = self._evaluate_expression(field.expression or field.name, note, None)
                row[field.display_name] = value if value is not None else ""

            data.append(row)

        return pd.DataFrame(data)

    def _build_list(self, notes: list[Note]) -> pd.DataFrame:
        """Build a list from notes.

        Args:
            notes: List of notes to include

        Returns:
            DataFrame with list data
        """
        data = [{"File": f"[[{note.name}]]"} for note in notes]
        return pd.DataFrame(data)

    def _apply_sort(self, df: pd.DataFrame, sort) -> pd.DataFrame:
        """Apply sorting to a DataFrame.

        Args:
            df: The DataFrame to sort
            sort: The sort specification

        Returns:
            Sorted DataFrame
        """
        # Map field names to column names
        sort_col = sort.field
        if sort.field == "file.name":
            sort_col = "File"

        if sort_col in df.columns:
            return df.sort_values(by=sort_col, ascending=sort.ascending)

        return df


class DebugDataviewEvaluator(DataviewEvaluator):
    """Debug version that prints evaluation steps."""

    def _apply_where(self, notes: list[Note], where_clause: str, context_note: Note | None) -> list[Note]:
        """Apply WHERE clause filtering with debug output."""
        print(f"\nDEBUG: Applying WHERE clause: {where_clause}")
        print(f"DEBUG: Context note: {context_note.name if context_note else 'None'}")

        filtered = []

        for note in notes:
            result = self._evaluate_where_condition(note, where_clause, context_note)
            if result:
                filtered.append(note)
                print(f"  ✓ {note.name}: INCLUDED")
            else:
                print(f"  ✗ {note.name}: EXCLUDED")

        print(f"DEBUG: Filtered from {len(notes)} to {len(filtered)} notes")
        return filtered

    def _evaluate_function(self, func_name: str, args_str: str, note: Note, context_note: Note | None) -> bool:
        """Evaluate function with debug output."""
        result = super()._evaluate_function(func_name, args_str, note, context_note)

        # Parse and evaluate arguments for debugging
        args = [arg.strip() for arg in self._split_function_args(args_str)]
        evaluated_args = [self._evaluate_expression(arg, note, context_note) for arg in args]

        print(f"    {func_name}({', '.join(str(a) for a in evaluated_args)}) = {result}")
        return result
