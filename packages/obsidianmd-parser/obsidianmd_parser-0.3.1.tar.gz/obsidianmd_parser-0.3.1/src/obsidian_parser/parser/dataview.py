"""Parser for Dataview queries and elements."""

import re
from typing import Any

from obsidian_parser.models.dataview import (
    DataviewField,
    DataviewInlineField,
    DataviewInlineQuery,
    DataviewQuery,
    DataviewQueryType,
    DataviewSort,
)


class DataviewParser:
    """Parser for Dataview syntax."""

    # Regex patterns
    QUERY_BLOCK_PATTERN = r"```dataview\s*\n(.*?)\n```"
    INLINE_QUERY_PATTERN = r"`=\s*(.+?)\s*`"
    INLINE_FIELD_PATTERN = r"^\s*([^:\n]+)::\s*(.+)$"

    # Query component patterns
    QUERY_TYPE_PATTERN = r"^(TABLE|LIST|TASK|CALENDAR)(?:\s+(.+?))?$"
    FROM_PATTERN = r"^FROM\s+(.+)$"
    WHERE_PATTERN = r"^WHERE\s+(.+)$"
    SORT_PATTERN = r"^SORT\s+(.+)$"
    GROUP_BY_PATTERN = r"^GROUP\s+BY\s+(.+)$"
    LIMIT_PATTERN = r"^LIMIT\s+(\d+)$"
    FLATTEN_PATTERN = r"^FLATTEN\s+(.+)$"

    @classmethod
    def parse_query_blocks(cls, content: str) -> list[DataviewQuery]:
        """Parse all Dataview query blocks from content.

        Args:
            content: The note content

        Returns:
            List of DataviewQuery objects
        """
        queries = []

        # Find all dataview code blocks
        for match in re.finditer(cls.QUERY_BLOCK_PATTERN, content, re.DOTALL | re.MULTILINE):
            query_text = match.group(1).strip()
            line_number = content[: match.start()].count("\n")

            query = cls._parse_query(query_text, line_number)
            if query:
                queries.append(query)

        return queries

    @classmethod
    def _parse_query(cls, query_text: str, line_number: int) -> DataviewQuery | None:
        """Parse a single Dataview query.

        Args:
            query_text: The query text
            line_number: Line number in the source file

        Returns:
            DataviewQuery object or None if invalid
        """
        lines = query_text.strip().split("\n")
        if not lines:
            return None

        # Create a simple state machine to parse the query
        query_type = None
        current_clause = None
        clause_content = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check what type of line this is
            if re.match(r"^(TABLE|LIST|TASK|CALENDAR)", line, re.IGNORECASE):
                match = re.match(r"^(TABLE|LIST|TASK|CALENDAR)(?:\s+(.+))?$", line, re.IGNORECASE)
                query_type = DataviewQueryType.from_string(match.group(1))
                current_clause = "type"
                if match.group(2):  # Fields on same line as TABLE
                    clause_content["fields"] = [match.group(2)]
                else:
                    clause_content["fields"] = []
            elif re.match(r"^FROM\s+", line, re.IGNORECASE):
                current_clause = "from"
                clause_content["from"] = re.sub(r"^FROM\s+", "", line, flags=re.IGNORECASE)
            elif re.match(r"^WHERE\s+", line, re.IGNORECASE):
                current_clause = "where"
                clause_content["where"] = re.sub(r"^WHERE\s+", "", line, flags=re.IGNORECASE)
            elif re.match(r"^SORT\s+", line, re.IGNORECASE):
                current_clause = "sort"
                clause_content["sort"] = re.sub(r"^SORT\s+", "", line, flags=re.IGNORECASE)
            elif re.match(r"^GROUP\s+BY\s+", line, re.IGNORECASE):
                current_clause = "group"
                clause_content["group"] = re.sub(r"^GROUP\s+BY\s+", "", line, flags=re.IGNORECASE)
            elif re.match(r"^LIMIT\s+", line, re.IGNORECASE):
                current_clause = "limit"
                clause_content["limit"] = re.sub(r"^LIMIT\s+", "", line, flags=re.IGNORECASE)
            elif re.match(r"^FLATTEN\s+", line, re.IGNORECASE):
                current_clause = "flatten"
                clause_content["flatten"] = re.sub(r"^FLATTEN\s+", "", line, flags=re.IGNORECASE)
            else:
                # Continuation of current clause
                if current_clause == "type" and "fields" in clause_content:
                    clause_content["fields"].append(line)

        if not query_type:
            return None

        # Create query object
        query = DataviewQuery(source=query_text, query_type=query_type, line_number=line_number)

        # Set the parsed values
        if query_type == DataviewQueryType.TABLE and "fields" in clause_content:
            fields_text = " ".join(clause_content["fields"])
            if fields_text:
                query.without_id, query.fields = cls._parse_table_fields(fields_text)

        if "from" in clause_content:
            query.from_clause = clause_content["from"]
        if "where" in clause_content:
            query.where_clause = clause_content["where"]
        if "sort" in clause_content:
            query.sort_clauses = cls._parse_sort_clauses(clause_content["sort"])
        if "group" in clause_content:
            query.group_by = clause_content["group"]
        if "limit" in clause_content:
            try:
                query.limit = int(clause_content["limit"])
            except ValueError:
                pass
        if "flatten" in clause_content:
            query.flatten = clause_content["flatten"]

        return query

    @classmethod
    def _parse_table_fields(cls, fields_text: str) -> tuple[bool, list[DataviewField]]:
        """Parse TABLE fields.

        Args:
            fields_text: The fields portion of a TABLE query

        Returns:
            Tuple of (without_id, fields)
        """
        without_id = False
        fields = []

        # Check for WITHOUT ID
        if fields_text.upper().startswith("WITHOUT ID"):
            without_id = True
            fields_text = fields_text[10:].strip()

        if not fields_text:
            return without_id, fields

        # Parse fields (simple version - can be enhanced)
        # Handle: field, field AS alias, expression AS alias
        field_parts = cls._split_respecting_parens(fields_text, ",")

        for part in field_parts:
            part = part.strip()
            if not part:
                continue

            # Check for AS alias
            as_match = re.match(r"(.+?)\s+AS\s+(.+)", part, re.IGNORECASE)
            if as_match:
                expression = as_match.group(1).strip()
                alias = as_match.group(2).strip()

                if (alias.startswith('"') and alias.endswith('"')) or (alias.startswith("'") and alias.endswith("'")):
                    alias = alias[1:-1]

                fields.append(DataviewField(name=expression, expression=expression, alias=alias))
            else:
                fields.append(DataviewField(name=part, expression=part))

        return without_id, fields

    @classmethod
    def _parse_sort_clauses(cls, sort_text: str) -> list[DataviewSort]:
        """Parse SORT clauses.

        Args:
            sort_text: The sort clause text

        Returns:
            List of DataviewSort objects
        """
        sorts = []
        parts = cls._split_respecting_parens(sort_text, ",")

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check for DESC/ASC
            if part.upper().endswith(" DESC"):
                field = part[:-5].strip()
                ascending = False
            elif part.upper().endswith(" ASC"):
                field = part[:-4].strip()
                ascending = True
            else:
                field = part
                ascending = True

            sorts.append(DataviewSort(field=field, ascending=ascending))

        return sorts

    @classmethod
    def _split_respecting_parens(cls, text: str, delimiter: str) -> list[str]:
        """Split text by delimiter, respecting parentheses.

        Args:
            text: Text to split
            delimiter: Delimiter to split by

        Returns:
            List of parts
        """
        parts = []
        current = []
        paren_depth = 0

        for char in text:
            if char == "(":
                paren_depth += 1
            elif char == ")":
                paren_depth -= 1
            elif char == delimiter and paren_depth == 0:
                parts.append("".join(current))
                current = []
                continue

            current.append(char)

        if current:
            parts.append("".join(current))

        return parts

    @classmethod
    def parse_inline_queries(cls, content: str) -> list[DataviewInlineQuery]:
        """Parse inline Dataview queries.

        Args:
            content: The note content

        Returns:
            List of DataviewInlineQuery objects
        """
        queries = []

        for match in re.finditer(cls.INLINE_QUERY_PATTERN, content):
            expression = match.group(1)
            line_number = content[: match.start()].count("\n")

            queries.append(
                DataviewInlineQuery(
                    source=match.group(0),
                    expression=expression,
                    line_number=line_number,
                    start_pos=match.start(),
                    end_pos=match.end(),
                )
            )

        return queries

    @classmethod
    def parse_inline_fields(cls, content: str) -> list[DataviewInlineField]:
        """Parse inline fields (key:: value syntax).

        Args:
            content: The note content

        Returns:
            List of DataviewInlineField objects
        """
        fields = []

        if not isinstance(content, str):
            return fields

        for line_num, line in enumerate(content.split("\n")):
            # Skip if line is in a code block (simple check)
            if line.strip().startswith("```"):
                continue

            if "::" not in line:
                continue

            match = re.match(cls.INLINE_FIELD_PATTERN, line.strip())
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()

                key_cleaned = re.sub(r"^[-*+]\s+", "", key)  # Bullet points
                key_cleaned = re.sub(r"^\d+\.\s+", "", key_cleaned)  # Numbered lists
                key_cleaned = key_cleaned.strip()

                if key_cleaned and not key_cleaned.startswith("-"):
                    fields.append(
                        DataviewInlineField(
                            key=key_cleaned,
                            value=value,
                            line_number=line_num,
                            raw_value=match.group(2),  # Keep original formatting
                        )
                    )

        return fields
