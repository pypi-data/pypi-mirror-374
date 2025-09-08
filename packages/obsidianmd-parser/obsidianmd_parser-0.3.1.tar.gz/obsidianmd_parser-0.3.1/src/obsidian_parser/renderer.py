"""Content rendering functionality for Obsidian notes."""

import re
from typing import TYPE_CHECKING

import pandas as pd

if TYPE_CHECKING:
    from obsidian_parser.note import Note
    from obsidian_parser.vault import Vault


class ContentRenderer:
    """Renders Obsidian content to reading view format."""

    def __init__(self, vault: "Vault | None" = None, evaluate_dataview: bool = False):
        """Initialize renderer with optional vault for link resolution.

        Args:
            vault: Optional vault for resolving wikilinks to display text
            evaluate_dataview: Whether to evaluate Dataview queries
        """
        self.vault = vault
        self.evaluate_dataview = evaluate_dataview
        self._evaluator = None

    @property
    def evaluator(self):
        """Get the Dataview evaluator (lazy initialization)."""
        if self._evaluator is None and self.vault and self.evaluate_dataview:
            from obsidian_parser.dataview.evaluator import DataviewEvaluator

            self._evaluator = DataviewEvaluator(self.vault)
        return self._evaluator

    def render(self, content: str, source_note: "Note | None" = None) -> str:
        """Render content to reading view format.

        Args:
            content: Raw Obsidian markdown content
            source_note: Optional source note for context

        Returns:
            Rendered content as it would appear in reading view
        """
        # Process in order of precedence
        rendered = content

        # 1. Remove comments
        rendered = self._remove_comments(rendered)

        # 2. Process Dataview queries if enabled
        if self.evaluate_dataview and self.evaluator:
            rendered = self._render_dataview_queries(rendered, source_note)

        # 3. Process wikilinks
        rendered = self._render_wikilinks(rendered, source_note)

        # 4. Remove embeds (they would be expanded in real Obsidian)
        rendered = self._remove_embeds(rendered)

        # 5. Process tags (optional - could keep or remove)
        rendered = self._render_tags(rendered)

        # 6. Clean up extra whitespace
        rendered = self._clean_whitespace(rendered)

        return rendered

    def _remove_comments(self, content: str) -> str:
        """Remove Obsidian comments %%...%%."""
        # Handle multi-line comments
        pattern = r"%%.*?%%"
        return re.sub(pattern, "", content, flags=re.DOTALL)

    def _render_wikilinks(self, content: str, source_note: "Note | None" = None) -> str:
        """Convert wikilinks to display text."""

        def replace_link(match: re.Match[str]) -> str:
            full_match = match.group(0)
            target = match.group(1)
            heading = match.group(2)
            block_id = match.group(3)
            alias = match.group(4)

            # If there's an alias, use it
            if alias:
                return alias

            # If there's a heading/block reference, include it
            if heading:
                return f"{target} > {heading}"
            elif block_id:
                return target  # Just show target for block refs

            # Otherwise, just the target
            return target

        # Pattern: [[target#heading^block-id|alias]]
        pattern = r"\[\[([^\[\]|#\^]+?)(?:#([^\[\]|^]+?))?(?:\^([^\[\]|]+?))?(?:\|([^\[\]]+?))?\]\]"
        return re.sub(pattern, replace_link, content)

    def _remove_embeds(self, content: str) -> str:
        """Remove embed syntax (in real Obsidian these would be expanded)."""
        # Pattern: ![[...]]
        pattern = r"!\[\[([^\[\]]+?)\]\]"
        return re.sub(pattern, "", content)

    def _render_tags(self, content: str) -> str:
        """Render tags (optional - can be customized)."""
        # Option 1: Keep tags as-is
        # return content

        # Option 2: Remove tags for cleaner reading
        pattern = r"(?:^|(?<=\s))#[a-zA-Z0-9_\-/]+(?=\s|[.,;:!?]|$)"
        return re.sub(pattern, "", content)

    def _clean_whitespace(self, content: str) -> str:
        """Clean up extra whitespace."""
        # Remove multiple consecutive blank lines
        content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

        # Remove trailing whitespace
        content = "\n".join(line.rstrip() for line in content.split("\n"))

        # Remove leading/trailing whitespace
        content = content.strip()

        return content

    def _render_dataview_queries(self, content: str, source_note: "Note | None") -> str:
        """Render Dataview query blocks to tables.

        Args:
            content: Content with potential Dataview blocks
            source_note: The note containing the content

        Returns:
            Content with Dataview blocks replaced by tables
        """
        from obsidian_parser.parser.dataview import DataviewParser

        def replace_query_block(match: re.Match[str]) -> str:
            query_text = match.group(1)

            try:
                # Parse the query
                queries = DataviewParser._parse_query(query_text, 0)
                if not queries:
                    return match.group(0)  # Return original if parsing fails

                # Evaluate the query
                df = self.evaluator.evaluate(queries, source_note)

                # Convert to markdown table
                if df.empty:
                    return "*No results*"

                # Format as markdown table
                return self._dataframe_to_markdown(df)

            except Exception as e:
                # Return error message in output
                return f"*Dataview Error: {str(e)}*"

        # Replace all dataview code blocks
        pattern = r"```dataview\s*\n(.*?)\n```"
        return re.sub(pattern, replace_query_block, content, flags=re.DOTALL | re.MULTILINE)

    def _dataframe_to_markdown(self, df: pd.DataFrame) -> str:
        """Convert a DataFrame to a markdown table.

        Args:
            df: The DataFrame to convert

        Returns:
            Markdown table string
        """
        # Get column widths
        col_widths = {}
        for col in df.columns:
            max_width = len(str(col))
            for val in df[col]:
                max_width = max(max_width, len(str(val)))
            col_widths[col] = max_width

        # Build header
        header_parts = []
        separator_parts = []
        for col in df.columns:
            width = col_widths[col]
            header_parts.append(str(col).ljust(width))
            separator_parts.append("-" * width)

        lines = ["| " + " | ".join(header_parts) + " |", "|" + "|".join(f"-{sep}-" for sep in separator_parts) + "|"]

        # Build rows
        for _, row in df.iterrows():
            row_parts = []
            for col in df.columns:
                width = col_widths[col]
                val = str(row[col]) if pd.notna(row[col]) else ""
                row_parts.append(val.ljust(width))
            lines.append("| " + " | ".join(row_parts) + " |")

        return "\n".join(lines)


class ReadingView:
    """Wrapper for content that provides reading view rendering."""

    def __init__(self, content: str, renderer: ContentRenderer | None = None):
        """Initialize reading view wrapper.

        Args:
            content: Raw content
            renderer: Optional renderer instance
        """
        self._raw = content
        self._renderer = renderer or ContentRenderer()
        self._cached_render: str | None = None

    @property
    def raw(self) -> str:
        """Get raw content."""
        return self._raw

    def render(self) -> str:
        """Render content to reading view format."""
        if self._cached_render is None:
            self._cached_render = self._renderer.render(self._raw)
        return self._cached_render

    def __str__(self) -> str:
        """String representation returns rendered content."""
        return self.render()

    def __repr__(self) -> str:
        """Repr shows both raw and rendered."""
        rendered = self.render()
        preview = rendered[:100] + "..." if len(rendered) > 100 else rendered
        return f"ReadingView({preview!r})"
