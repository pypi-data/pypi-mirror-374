# src/obsidian_parser/models/dataview.py
"""Data models for Dataview queries and elements."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TYPE_CHECKING
import pandas as pd
import re


if TYPE_CHECKING:
    from obsidian_parser.vault import Vault
    from obsidian_parser.note import Note

class DataviewQueryType(str, Enum):
    """Types of Dataview queries."""

    TABLE = "TABLE"
    LIST = "LIST"
    TASK = "TASK"
    CALENDAR = "CALENDAR"

    @classmethod
    def from_string(cls, value: str) -> "DataviewQueryType":
        """Create from string, case-insensitive."""
        return cls(value.upper())


class DataviewFieldType(str, Enum):
    """Types of fields in Dataview."""

    FILE = "file"
    LINK = "link"
    DATE = "date"
    NUMBER = "number"
    TEXT = "text"
    LIST = "list"
    OBJECT = "object"


@dataclass
class DataviewField:
    """Represents a field in a Dataview query."""

    name: str
    alias: str | None = None
    expression: str | None = None

    @property
    def display_name(self) -> str:
        """Get the display name (alias or name)."""
        return self.alias if self.alias else self.name

    def __str__(self) -> str:
        if self.alias:
            return f"{self.expression or self.name} AS {self.alias}"
        return self.expression or self.name


@dataclass
class DataviewSort:
    """Represents a sort clause in Dataview."""

    field: str
    ascending: bool = True

    def __str__(self) -> str:
        direction = "ASC" if self.ascending else "DESC"
        return f"{self.field} {direction}"


@dataclass
class DataviewQuery:
    """Represents a parsed Dataview query block."""

    source: str
    query_type: DataviewQueryType
    line_number: int

    # Query components
    fields: list[DataviewField] = field(default_factory=list)
    from_clause: str | None = None
    where_clause: str | None = None
    sort_clauses: list[DataviewSort] = field(default_factory=list)
    group_by: str | None = None
    limit: int | None = None
    flatten: str | None = None

    # For TABLE queries
    without_id: bool = False

    @property
    def is_valid(self) -> bool:
        """Check if the query has minimum required components."""
        # Most queries need at least a query type
        # FROM is optional (defaults to all pages)
        return self.query_type is not None

    def get_query_string(self) -> str:
        """Reconstruct the query string from components."""
        lines = [self.query_type.value]

        # Add fields for TABLE
        if self.query_type == DataviewQueryType.TABLE and self.fields:
            if self.without_id:
                field_str = "WITHOUT ID"
                if self.fields:
                    field_str += f" {', '.join(str(f) for f in self.fields)}"
                lines[0] += f" {field_str}"
            else:
                lines[0] += f" {', '.join(str(f) for f in self.fields)}"

        # Add clauses
        if self.from_clause:
            lines.append(f"FROM {self.from_clause}")
        if self.where_clause:
            lines.append(f"WHERE {self.where_clause}")
        if self.sort_clauses:
            sort_str = ", ".join(str(s) for s in self.sort_clauses)
            lines.append(f"SORT {sort_str}")
        if self.group_by:
            lines.append(f"GROUP BY {self.group_by}")
        if self.flatten:
            lines.append(f"FLATTEN {self.flatten}")
        if self.limit is not None:
            lines.append(f"LIMIT {self.limit}")

        return "\n".join(lines)
        
    def evaluate(self, vault: "Vault", source_note: "Note | None" = None) -> str:
        """Evaluate this query and return the result as markdown.

        Args:
            vault: The vault to query against
            source_note: The note containing this query (for context)

        Returns:
            Markdown representation of the query results
        """
        from obsidian_parser.dataview.evaluator import DataviewEvaluator
        
        # Create evaluator and run query
        evaluator = DataviewEvaluator(vault)
        df = evaluator.evaluate(self, source_note)
        
        # Convert DataFrame to markdown based on query type
        if df.empty:
            return "*No results found*"
        
        if self.query_type == DataviewQueryType.TABLE:
            return self._dataframe_to_markdown_table(df)
        elif self.query_type == DataviewQueryType.LIST:
            return self._dataframe_to_markdown_list(df)
        elif self.query_type == DataviewQueryType.TASK:
            return self._dataframe_to_markdown_tasks(df)
        else:
            return f"<!-- Query type {self.query_type.value} not yet implemented -->"

    def _dataframe_to_markdown_table(self, df) -> str:
        """Convert DataFrame to markdown table."""
        # Get column names
        columns = df.columns.tolist()
        
        # Build header
        lines = []
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join("---" for _ in columns) + " |")
        
        # Build rows
        for _, row in df.iterrows():
            cells = []
            for col in columns:
                value = row[col]
                # Format value appropriately
                if pd.isna(value):
                    cells.append("")
                elif isinstance(value, (list, tuple)):
                    cells.append(", ".join(str(v) for v in value))
                else:
                    cells.append(str(value))
            lines.append("| " + " | ".join(cells) + " |")
        
        return "\n".join(lines)

    def _dataframe_to_markdown_list(self, df) -> str:
        """Convert DataFrame to markdown list."""
        lines = []
        for _, row in df.iterrows():
            # For LIST queries, we typically just show the file link
            file_link = row.get("File", "")
            lines.append(f"- {file_link}")
        return "\n".join(lines)

    def _dataframe_to_markdown_tasks(self, df) -> str:
        """Convert DataFrame to markdown task list."""
        lines = []
        for _, row in df.iterrows():
            # Extract task information
            status = row.get("status", " ")
            text = row.get("text", "")
            file_link = row.get("File", "")
            
            lines.append(f"- [{status}] {text} ({file_link})")
        
        return "\n".join(lines)

@dataclass
class DataviewInlineQuery:
    """Represents an inline Dataview query."""

    source: str
    expression: str
    line_number: int
    start_pos: int
    end_pos: int

    @property
    def is_complex(self) -> bool:
        """Check if this is a complex expression (not just a field reference)."""
        # Simple field references don't contain operators or function calls
        operators = ["+", "-", "*", "/", "=", ">", "<", "(", ")", "[", "]"]
        return any(op in self.expression for op in operators)
    
    def evaluate(self, vault: "Vault", source_note: "Note | None" = None) -> str:
        """Evaluate this inline query and return the result.

        Args:
            vault: The vault for context
            source_note: The note containing this query

        Returns:
            String representation of the evaluated result
        """
        from obsidian_parser.dataview.evaluator import DataviewEvaluator
        
        if not source_note:
            return "<!-- Error: No source note for inline query -->"
        
        # Create evaluator
        evaluator = DataviewEvaluator(vault)
        
        # Use the evaluator's expression evaluation
        # We need to evaluate this in the context of the source note
        try:
            result = evaluator._evaluate_expression(self.expression, source_note, source_note)
            
            # Format the result appropriately
            if result is None:
                return ""
            elif isinstance(result, bool):
                return str(result).lower()
            elif isinstance(result, (list, tuple)):
                return ", ".join(str(item) for item in result)
            elif isinstance(result, float):
                # Format floats nicely
                if result.is_integer():
                    return str(int(result))
                return f"{result:.2f}"
            else:
                return str(result)
        except Exception as e:
            return f"<!-- Error evaluating inline query: {e} -->"


@dataclass
class DataviewInlineField:
    """Represents an inline field (key:: value syntax)."""

    key: str
    value: str
    line_number: int
    raw_value: str  # Original value with any formatting

    @property
    def is_list(self) -> bool:
        """Check if the value appears to be a list."""
        return "," in self.value or self.value.startswith("[")

    def get_list_values(self) -> list[str]:
        """Parse list values if this is a list field."""
        if self.value.startswith("[") and self.value.endswith("]"):
            # [value1, value2] format
            inner = self.value[1:-1]
        else:
            inner = self.value

        # Split by comma and clean up
        values = [v.strip() for v in inner.split(",")]
        return [v for v in values if v]  # Remove empty values

    def get_typed_value(self) -> Any:
        """Get the value with appropriate type conversion.

        Returns:
            The value converted to appropriate Python type
        """
        # Handle lists
        if self.is_list:
            list_values = self.get_list_values()
            # Try to convert each list item
            typed_list = []
            for item in list_values:
                typed_list.append(self._convert_single_value(item))
            return typed_list
        
        # Handle single values
        return self._convert_single_value(self.value)

    def _convert_single_value(self, value: str) -> Any:
        """Convert a single string value to appropriate type."""
        value = value.strip()
        
        # Handle quoted strings
        if (value.startswith('"') and value.endswith('"')) or \
           (value.startswith("'") and value.endswith("'")):
            return value[1:-1]
        
        # Handle booleans
        if value.lower() in ("true", "false"):
            return value.lower() == "true"
        
        # Handle null/none
        if value.lower() in ("null", "none", ""):
            return None
        
        # Handle numbers
        try:
            if "." in value:
                return float(value)
            return int(value)
        except ValueError:
            pass
        
        # Handle dates (basic ISO format)
        date_patterns = [
            (r"^\d{4}-\d{2}-\d{2}$", "%Y-%m-%d"),
            (r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$", "%Y-%m-%d %H:%M"),
            (r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$", "%Y-%m-%d %H:%M:%S"),
        ]
        
        for pattern, date_format in date_patterns:
            if re.match(pattern, value):
                try:
                    return datetime.strptime(value, date_format)
                except ValueError:
                    pass
        
        # Handle wikilinks
        if value.startswith("[[") and value.endswith("]]"):
            # Return the link target
            link_content = value[2:-2]
            if "|" in link_content:
                return link_content.split("|")[0]
            return link_content
        
        # Default to string
        return value

    def to_dataview_string(self) -> str:
        """Convert the field back to Dataview inline field syntax."""
        return f"{self.key}:: {self.raw_value}"