"""Note class for representing a single Obsidian markdown file."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Literal
import re
from datetime import date, datetime

from obsidian_parser.models.dataview import DataviewInlineField, DataviewInlineQuery, DataviewQuery


class CalloutType(str, Enum):
    """Standard Obsidian callout types."""

    NOTE = "NOTE"
    INFO = "INFO"
    TODO = "TODO"
    TIP = "TIP"
    HINT = "HINT"
    IMPORTANT = "IMPORTANT"
    SUCCESS = "SUCCESS"
    CHECK = "CHECK"
    DONE = "DONE"
    QUESTION = "QUESTION"
    HELP = "HELP"
    FAQ = "FAQ"
    WARNING = "WARNING"
    CAUTION = "CAUTION"
    ATTENTION = "ATTENTION"
    FAILURE = "FAILURE"
    FAIL = "FAIL"
    MISSING = "MISSING"
    DANGER = "DANGER"
    ERROR = "ERROR"
    BUG = "BUG"
    EXAMPLE = "EXAMPLE"
    QUOTE = "QUOTE"
    CITE = "CITE"


@dataclass(slots=True)
class Callout:
    """Represents an Obsidian callout block."""

    type: str  # Can be CalloutType or custom string
    title: str
    content: str
    line_number: int
    is_foldable: bool = False  # If it has + or - suffix
    is_folded: bool = False  # If it starts folded (-)

    @property
    def type_enum(self) -> CalloutType | None:
        """Get the callout type as enum if it's a standard type."""
        try:
            return CalloutType(self.type.upper())
        except ValueError:
            return None

    @property
    def is_standard_type(self) -> bool:
        """Check if this is a standard Obsidian callout type."""
        return self.type_enum is not None


# Obsidian supports extended task statuses
TaskStatus = Literal[
    " ", "x", "X", "/", "-", ">", "<", "?", "!", "*", '"', "l", "b", "i", "S", "I", "p", "c", "f", "k", "w", "u", "d"
]

TASK_STATUS_MEANINGS = {
    " ": "Unchecked",
    "x": "Checked",
    "X": "Checked",
    "/": "In Progress",
    "-": "Cancelled",
    ">": "Forwarded/Scheduled",
    "<": "Scheduling",
    "?": "Question",
    "!": "Important",
    "*": "Star",
    '"': "Quote",
    "l": "Location",
    "b": "Bookmark",
    "i": "Information",
    "S": "Savings",
    "I": "Idea",
    "p": "Pros",
    "c": "Cons",
    "f": "Fire",
    "k": "Key",
    "w": "Win",
    "u": "Up",
    "d": "Down",
}

class Frontmatter(dict):
    """Dictionary-like object for frontmatter with cleaning capabilities."""
    
    def clean(self, date_format: str = '%Y-%m-%d') -> dict[str, Any]:
        """Return a cleaned version of the frontmatter.
        
        Args:
            date_format: strftime format for dates (or 'DD-MM-YYYY' style)
            
        Returns:
            Dictionary with cleaned values (wikilinks removed, dates formatted)
        """
        cleaned = {}
        
        # Convert date format if using DD-MM-YYYY style
        if 'DD' in date_format or 'MM' in date_format or 'YYYY' in date_format:
            date_format = (date_format
                .replace('DD', '%d')
                .replace('MM', '%m')
                .replace('YYYY', '%Y')
                .replace('YY', '%y'))
        
        for key, value in self.items():
            cleaned[key] = self._clean_value(value, date_format)
            
        return cleaned
    
    def _clean_value(self, value: Any, date_format: str) -> Any:
        """Clean a single value."""
        if isinstance(value, str):
            # Remove wikilink formatting with more robust pattern
            value = re.sub(
                r'\[\[([^\[\]]+?)(?:\|([^\[\]]+?))?\]\]',
                lambda m: m.group(2) if m.group(2) else m.group(1),
                value
            )
        elif isinstance(value, (date, datetime)):
            # Format dates with error handling
            try:
                return value.strftime(date_format)
            except ValueError:
                return value.isoformat()
        elif isinstance(value, list):
            # Recursively clean list items
            return [self._clean_value(item, date_format) for item in value]
        elif isinstance(value, dict):
            # Recursively clean dict values
            return {k: self._clean_value(v, date_format) for k, v in value.items()}
            
        return value

@dataclass(slots=True)
class Task:
    """Represents a task item."""

    text: str
    status: TaskStatus
    line_number: int
    indent_level: int = 0  # Number of spaces/tabs before the task

    @property
    def completed(self) -> bool:
        """Check if task is completed."""
        return self.status in ("x", "X")

    @property
    def status_meaning(self) -> str:
        """Get human-readable meaning of the status."""
        return TASK_STATUS_MEANINGS.get(self.status, "Custom")

    def __str__(self) -> str:
        """String representation as it would appear in Obsidian."""
        indent = " " * self.indent_level
        return f"{indent}- [{self.status}] {self.text}"


@dataclass(slots=True)
class WikiLink:
    """Represents an Obsidian wikilink."""

    target: str
    heading: str | None = None
    block_id: str | None = None
    alias: str | None = None

    @property
    def display_text(self) -> str:
        """Get the display text for this link."""
        return self.alias if self.alias else self.target


@dataclass(slots=True)
class Tag:
    """Represents an Obsidian tag."""

    name: str

    @property
    def hierarchy(self) -> list[str]:
        """Get tag hierarchy as list. E.g., 'project/python' -> ['project', 'python']"""
        return self.name.split("/")

    @property
    def parent(self) -> str | None:
        """Get parent tag if nested."""
        parts = self.hierarchy
        return "/".join(parts[:-1]) if len(parts) > 1 else None


@dataclass(slots=True)
class Embed:
    """Represents an Obsidian embed."""

    target: str
    type: str = "note"  # note, image, pdf, etc.
    heading: str | None = None
    block_id: str | None = None


@dataclass
class LinkUsage:
    """Represents usage statistics for a wikilink."""

    target: str
    total_count: int
    aliases: list[str] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        """String representation."""
        if self.aliases:
            return f"{self.target} ({self.total_count}x, aliases: {', '.join(self.aliases)})"
        return f"{self.target} ({self.total_count}x)"


@dataclass
class Section:
    """Represents a section of content under a heading."""

    heading: str
    level: int
    content: str
    line_number: int
    subsections: list["Section"] = field(default_factory=list)
    parent: "Section | None" = field(default=None, repr=False)
    _wikilinks: list[WikiLink] | None = field(default=None, init=False, repr=False)
    _link_usage: dict[str, LinkUsage] | None = field(default=None, init=False, repr=False)

    @property
    def reading_view(self) -> str:
        """Get content as it would appear in Obsidian's reading view."""
        from obsidian_parser.renderer import ContentRenderer

        renderer = ContentRenderer()
        return renderer.render(self.content)

    def get_evaluated_view(self, vault: "Vault", source_note: "Note | None" = None) -> str:
        """Get content with Dataview queries evaluated.

        Args:
            vault: The vault for query evaluation
            source_note: The note containing this section

        Returns:
            Content with Dataview queries replaced by their results
        """
        from obsidian_parser.renderer import ContentRenderer

        renderer = ContentRenderer(vault=vault, evaluate_dataview=True)
        return renderer.render(self.content, source_note=source_note)

    @property
    def wikilinks(self) -> list[WikiLink]:
        """Get all wikilinks in this section's content."""
        if self._wikilinks is None:
            from obsidian_parser.parser.elements import parse_wikilinks

            self._wikilinks = parse_wikilinks(self.content)
        return self._wikilinks

    @property
    def all_wikilinks(self) -> list[WikiLink]:
        """Get all wikilinks including subsections."""
        links = self.wikilinks.copy()
        for subsection in self.subsections:
            links.extend(subsection.all_wikilinks)
        return links

    @property
    def link_usage(self) -> dict[str, LinkUsage]:
        """Get link usage statistics for this section only."""
        if self._link_usage is None:
            self._link_usage = self._analyze_links(self.wikilinks)
        return self._link_usage

    @property
    def all_link_usage(self) -> dict[str, LinkUsage]:
        """Get link usage statistics including subsections."""
        return self._analyze_links(self.all_wikilinks)

    def _analyze_links(self, links: list[WikiLink]) -> dict[str, LinkUsage]:
        """Analyze link usage patterns."""
        usage: dict[str, LinkUsage] = {}

        for link in links:
            if link.target not in usage:
                usage[link.target] = LinkUsage(target=link.target, total_count=0)

            usage[link.target].total_count += 1

            # Track unique aliases
            if link.alias and link.alias not in usage[link.target].aliases:
                usage[link.target].aliases.append(link.alias)

            # Track unique headings
            if link.heading and link.heading not in usage[link.target].headings:
                usage[link.target].headings.append(link.heading)

        return usage

    def get_most_linked(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get the most frequently linked notes.

        Args:
            limit: Maximum number of results

        Returns:
            List of (note_name, count) tuples sorted by frequency
        """
        usage = self.all_link_usage
        sorted_links = sorted([(u.target, u.total_count) for u in usage.values()], key=lambda x: x[1], reverse=True)
        return sorted_links[:limit]

    def get_unique_links(self) -> set[str]:
        """Get unique link targets in this section."""
        return {link.target for link in self.wikilinks}

    def get_all_unique_links(self) -> set[str]:
        """Get unique link targets including subsections."""
        return {link.target for link in self.all_wikilinks}

    def find_links_to(self, target: str) -> list[WikiLink]:
        """Find all links to a specific target.

        Args:
            target: The note name to search for

        Returns:
            List of WikiLink objects pointing to the target
        """
        return [link for link in self.all_wikilinks if link.target.lower() == target.lower()]

    def get_link_context(self, target: str, context_chars: int = 50) -> list[str]:
        """Get context around links to a specific target.

        Args:
            target: The note name to search for
            context_chars: Number of characters before/after link

        Returns:
            List of context strings
        """
        import re

        contexts = []

        # Pattern to find links with context
        pattern = rf"(.{{0,{context_chars}}})(\[\[{re.escape(target)}(?:[^\]]*?)?\]\])(.{{0,{context_chars}}})"

        for match in re.finditer(pattern, self.content, re.IGNORECASE):
            before = match.group(1).strip()
            link = match.group(2)
            after = match.group(3).strip()
            contexts.append(f"...{before} {link} {after}...")

        return contexts

    def export_links(self, link_format: Literal["list", "markdown", "csv"] = "list") -> str:
        """Export wikilinks in various formats.

        Args:
            format: Export format

        Returns:
            Formatted string of links
        """
        usage = self.all_link_usage

        if link_format == "list":
            lines = []
            for link_usage in sorted(usage.values(), key=lambda x: x.total_count, reverse=True):
                lines.append(str(link_usage))
            return "\n".join(lines)

        elif link_format == "markdown":
            lines = ["# Link Usage Report", ""]
            for link_usage in sorted(usage.values(), key=lambda x: x.total_count, reverse=True):
                lines.append(f"- [[{link_usage.target}]] - {link_usage.total_count} reference(s)")
                if link_usage.aliases:
                    lines.append(f"  - Aliases: {', '.join(link_usage.aliases)}")
                if link_usage.headings:
                    lines.append(f"  - Headings: {', '.join(link_usage.headings)}")
            return "\n".join(lines)

        elif link_format == "csv":
            lines = ["Target,Count,Aliases,Headings"]
            for link_usage in sorted(usage.values(), key=lambda x: x.total_count, reverse=True):
                aliases = "|".join(link_usage.aliases) if link_usage.aliases else ""
                headings = "|".join(link_usage.headings) if link_usage.headings else ""
                lines.append(f'"{link_usage.target}",{link_usage.total_count},"{aliases}","{headings}"')
            return "\n".join(lines)

        else:
            raise ValueError(f"Unknown format: {link_format}")

    def get_reading_view_with_renderer(self, renderer: Any) -> str:
        """Get content with a specific renderer.

        Args:
            renderer: A ContentRenderer instance

        Returns:
            Rendered content
        """
        return renderer.render(self.content)

    def get_all_content(self) -> str:
        """Get all content including subsections (raw)."""
        parts = [self.content]
        for subsection in self.subsections:
            parts.append(f"{'#' * subsection.level} {subsection.heading}")
            parts.append(subsection.get_all_content())
        return "\n\n".join(parts)

    def get_all_content_rendered(self, renderer: Any | None = None) -> str:
        """Get all content including subsections (rendered for reading view)."""
        if renderer is None:
            from obsidian_parser.renderer import ContentRenderer

            renderer = ContentRenderer()

        parts = [renderer.render(self.content)]
        for subsection in self.subsections:
            parts.append(f"{'#' * subsection.level} {subsection.heading}")
            parts.append(subsection.get_all_content_rendered(renderer))
        return "\n\n".join(parts)
    
    @property
    def parent_headings(self) -> list[tuple[int, str]]:
        """Get all parent headings in order from root to immediate parent.
        
        Returns:
            List of (level, heading) tuples
        """
        parents = []
        current = self.parent
        while current:
            parents.append((current.level, current.heading))
            current = current.parent
        return list(reversed(parents))  # Return from root to immediate parent
    
    @property
    def full_path(self) -> str:
        """Get the full heading path from root to this section.
        
        Returns:
            Path like "Parent > Child > This Section"
        """
        path_parts = [heading for _, heading in self.parent_headings]
        path_parts.append(self.heading)
        return " > ".join(path_parts)
    
    @property
    def breadcrumb(self) -> list[str]:
        """Get breadcrumb trail of headings.
        
        Returns:
            List of heading texts from root to this section
        """
        breadcrumb = [heading for _, heading in self.parent_headings]
        breadcrumb.append(self.heading)
        return breadcrumb


class Note:
    """Represents a parsed Obsidian note."""

    __slots__ = (
        "path",
        "_raw_content",
        "_parsed",
        "_frontmatter",
        "_wikilinks",
        "_tags",
        "_embeds",
        "_sections",
        "_sections_map",
        "_callouts",
        "_tasks",
        "_dataview_queries",
        "_dataview_inline_queries",
        "_dataview_fields",
    )

    def __init__(self, path: Path) -> None:
        """Initialize a Note from a file path.

        Args:
            path: Path to the markdown file
            vault: Optional vault reference for link resolution
        """
        self.path = path
        self._raw_content: str | None = None
        self._parsed = False

        # Parsed elements storage
        self._frontmatter: Frontmatter = Frontmatter()
        self._wikilinks: list[WikiLink] = []
        self._tags: list[Tag] = []
        self._embeds: list[Embed] = []
        self._sections: list[Section] = []
        self._sections_map: dict[str, Section] = {}
        self._callouts: list[Callout] = []
        self._tasks: list[Task] = []

        # Dataview elements
        self._dataview_queries: list[DataviewQuery] = []
        self._dataview_inline_queries: list[DataviewInlineQuery] = []
        self._dataview_fields: list[DataviewInlineField] = []

    @property
    def name(self) -> str:
        """Get the note name (filename without extension)."""
        return self.path.stem

    @property
    def title(self) -> str:
        """Get the note title (alias for name)."""
        return self.name

    @property
    def content(self) -> str:
        """Get the raw content of the note."""
        if self._raw_content is None:
            self._raw_content = self.path.read_text(encoding="utf-8")
        return self._raw_content

    @property
    def dataview_queries(self) -> list[DataviewQuery]:
        """Get all Dataview query blocks in the note."""
        self._ensure_parsed()
        return self._dataview_queries

    @property
    def dataview_inline_queries(self) -> list[DataviewInlineQuery]:
        """Get all inline Dataview queries in the note."""
        self._ensure_parsed()
        return self._dataview_inline_queries

    @property
    def dataview_fields(self) -> list[DataviewInlineField]:
        """Get all inline Dataview fields in the note."""
        self._ensure_parsed()
        return self._dataview_fields

    @property
    def reading_view(self) -> str:
        """Get the entire note content as reading view."""
        from obsidian_parser.renderer import ContentRenderer

        renderer = ContentRenderer()

        # Skip frontmatter in reading view
        _, content_without_frontmatter = self._split_frontmatter()
        return renderer.render(content_without_frontmatter)

    def get_reading_view_with_renderer(self, renderer: Any) -> str:
        """Get reading view with a specific renderer.

        Args:
            renderer: A ContentRenderer instance

        Returns:
            Rendered content
        """
        _, content_without_frontmatter = self._split_frontmatter()
        return renderer.render(content_without_frontmatter, source_note=self)

    def _split_frontmatter(self) -> tuple[str, str]:
        """Split content into frontmatter and main content."""
        content = self.content
        if content.startswith("---\n"):
            parts = content.split("---\n", 2)
            if len(parts) >= 3:
                return f"---\n{parts[1]}---\n", parts[2]
        return "", content

    def _ensure_parsed(self) -> None:
        """Ensure the note has been parsed."""
        if not self._parsed:
            self._parse()
            self._parsed = True

    def _parse(self) -> None:
        """Parse the note content."""
        from obsidian_parser.parser.core import parse_note

        parse_note(self)

    @property
    def frontmatter(self) -> Frontmatter:
        """Get the parsed frontmatter."""
        self._ensure_parsed()
        return self._frontmatter

    @property
    def wikilinks(self) -> list[WikiLink]:
        """Get all wikilinks in the note."""
        self._ensure_parsed()
        return self._wikilinks

    @property
    def tags(self) -> list[Tag]:
        """Get all tags in the note."""
        self._ensure_parsed()
        return self._tags

    @property
    def embeds(self) -> list[Embed]:
        """Get all embeds in the note."""
        self._ensure_parsed()
        return self._embeds

    @property
    def tasks(self) -> list[WikiLink]:
        """Get all tasks in the note."""
        self._ensure_parsed()
        return self._tasks

    @property
    def callouts(self) -> list[WikiLink]:
        """Get all callouts in the note."""
        self._ensure_parsed()
        return self._callouts

    @property
    def sections(self) -> list[Section]:
        """Get all sections (headings and their content)."""
        self._ensure_parsed()
        return self._sections

    def get_section(self, heading: str) -> Section | None:
        """Get a specific section by heading text.

        Args:
            heading: The heading text to search for

        Returns:
            The Section object if found, None otherwise
        """
        self._ensure_parsed()
        return self._sections_map.get(heading)

    def get_link_usage(self) -> dict[str, LinkUsage]:
        """Get link usage statistics for the entire note."""
        from obsidian_parser.parser.elements import parse_wikilinks

        # Get links from non-section content
        _, content_without_frontmatter = self._split_frontmatter()
        all_links = parse_wikilinks(content_without_frontmatter)

        # Create usage statistics
        usage: dict[str, LinkUsage] = {}

        for link in all_links:
            if link.target not in usage:
                usage[link.target] = LinkUsage(target=link.target, total_count=0)

            usage[link.target].total_count += 1

            if link.alias and link.alias not in usage[link.target].aliases:
                usage[link.target].aliases.append(link.alias)

            if link.heading and link.heading not in usage[link.target].headings:
                usage[link.target].headings.append(link.heading)

        return usage

    def get_most_linked(self, limit: int = 10) -> list[tuple[str, int]]:
        """Get the most frequently linked notes in this note."""
        usage = self.get_link_usage()
        sorted_links = sorted([(u.target, u.total_count) for u in usage.values()], key=lambda x: x[1], reverse=True)
        return sorted_links[:limit]

    def export_link_report(self, link_format: Literal["list", "markdown", "csv"] = "markdown") -> str:
        """Export a comprehensive link report for this note."""
        usage = self.get_link_usage()

        if link_format == "markdown":
            lines = [f"# Link Report: {self.name}", ""]
            lines.append(f"Total unique links: {len(usage)}")
            lines.append(f"Total link references: {sum(u.total_count for u in usage.values())}")
            lines.append("")
            lines.append("## Link Usage")
            lines.append("")

            for link_usage in sorted(usage.values(), key=lambda x: x.total_count, reverse=True):
                lines.append(f"- [[{link_usage.target}]] - {link_usage.total_count} reference(s)")
                if link_usage.aliases:
                    lines.append(f"  - Aliases: {', '.join(link_usage.aliases)}")
                if link_usage.headings:
                    lines.append(f"  - Headings: {', '.join(link_usage.headings)}")

            return "\n".join(lines)

        elif link_format == "list":
            lines = []
            for link_usage in sorted(usage.values(), key=lambda x: x.total_count, reverse=True):
                lines.append(str(link_usage))
            return "\n".join(lines)

        elif link_format == "csv":
            lines = ["Target,Count,Aliases,Headings"]
            for link_usage in sorted(usage.values(), key=lambda x: x.total_count, reverse=True):
                aliases = "|".join(link_usage.aliases) if link_usage.aliases else ""
                headings = "|".join(link_usage.headings) if link_usage.headings else ""
                lines.append(f'"{link_usage.target}",{link_usage.total_count},"{aliases}","{headings}"')
            return "\n".join(lines)

        else:
            raise ValueError(f"Unknown format: {link_format}")

    def __repr__(self) -> str:
        """String representation of the Note."""
        return f"Note(name='{self.name}', path='{self.path}')"

    def get_tasks_by_status(self, status: TaskStatus) -> list[Task]:
        """Get all tasks with a specific status.

        Args:
            status: The task status to filter by

        Returns:
            List of tasks with the given status
        """
        return [task for task in self.tasks if task.status == status]

    def get_incomplete_tasks(self) -> list[Task]:
        """Get all incomplete tasks."""
        return [task for task in self.tasks if not task.completed]

    def get_callouts_by_type(self, callout_type: str | CalloutType) -> list[Callout]:
        """Get all callouts of a specific type.

        Args:
            callout_type: The callout type to filter by

        Returns:
            List of callouts with the given type
        """
        if isinstance(callout_type, CalloutType):
            callout_type = callout_type.value

        return [callout for callout in self.callouts if callout.type.upper() == callout_type.upper()]

    def get_dataview_field(self, key: str) -> DataviewInlineField | None:
        """Get a specific Dataview field by key.

        Args:
            key: The field key to search for

        Returns:
            The field if found, None otherwise
        """
        self._ensure_parsed()
        for dataview_field in self._dataview_fields:
            if dataview_field.key.lower() == key.lower():
                return dataview_field
        return None

    def get_dataview_field_value(self, key: str, default: Any = None) -> Any:
        """Get the value of a Dataview field.

        Args:
            key: The field key
            default: Default value if field not found

        Returns:
            The field value or default
        """
        dataview_field = self.get_dataview_field(key)
        return dataview_field.value if dataview_field else default

    @property
    def has_dataview(self) -> bool:
        """Check if this note contains any Dataview elements."""
        self._ensure_parsed()
        return bool(self._dataview_queries or self._dataview_inline_queries or self._dataview_fields)

    def get_metadata(self) -> dict[str, Any]:
        """Get all metadata from frontmatter and Dataview fields combined.

        Returns:
            Dictionary of all metadata
        """
        self._ensure_parsed()

        # Start with frontmatter
        metadata = self.frontmatter.copy()

        # Add Dataview fields
        for field in self._dataview_fields:
            # Dataview fields override frontmatter if same key
            if field.is_list:
                metadata[field.key] = field.get_list_values()
            else:
                metadata[field.key] = field.value

        return metadata

    def get_evaluated_view(self, vault: "Vault") -> str:
        """Get the entire note content with Dataview queries evaluated.

        Args:
            vault: The vault for query evaluation

        Returns:
            Content with Dataview queries replaced by their results
        """
        from obsidian_parser.renderer import ContentRenderer

        renderer = ContentRenderer(vault=vault, evaluate_dataview=True)

        # Skip frontmatter in reading view
        _, content_without_frontmatter = self._split_frontmatter()
        return renderer.render(content_without_frontmatter, source_note=self)

    def __str__(self) -> str:
        """Human-readable string representation."""
        self._ensure_parsed()
        return (
            f"Note: {self.name}\n"
            f"  Tags: {len(self.tags)}\n"
            f"  Links: {len(self.wikilinks)}\n"
            f"  Sections: {len(self.sections)}\n"
            f"  Tasks: {len(self.tasks)} ({len(self.get_incomplete_tasks())} incomplete)\n"
            f"  Callouts: {len(self.callouts)}"
        )

    def get_backlinks(self, vault: "Vault") -> list["Note"]:
        """Get all notes that link to this note.

        Args:
            vault: The vault containing this note

        Returns:
            List of notes that link to this note
        """
        return vault.get_backlinks(self)

    def get_forward_links(self, vault: "Vault") -> list["Note"]:
        """Get all notes this note links to.

        Args:
            vault: The vault containing this note

        Returns:
            List of notes this note links to
        """
        forward_links = []
        for link in self.wikilinks:
            linked_note = vault.get_note(link.target)
            if linked_note:
                forward_links.append(linked_note)

        return forward_links

    def get_related_by_tags(self, vault: "Vault", min_shared_tags: int = 1) -> list[tuple["Note", int]]:
        """Find notes that share tags with this note.

        Args:
            vault: The vault containing this note
            min_shared_tags: Minimum number of shared tags

        Returns:
            List of (note, shared_tag_count) tuples
        """
        if not self.tags:
            return []

        my_tags = {tag.name for tag in self.tags}
        related = []

        for other_note in vault.notes:
            if other_note.name == self.name:
                continue

            other_tags = {tag.name for tag in other_note.tags}
            shared = len(my_tags & other_tags)

            if shared >= min_shared_tags:
                related.append((other_note, shared))

        return sorted(related, key=lambda x: x[1], reverse=True)

    def get_link_context(self, target: str, context_chars: int = 100) -> list[str]:
        """Get context around links to a specific target.

        Args:
            target: The target note name
            context_chars: Number of characters of context to include

        Returns:
            List of context strings
        """
        contexts = []
        content = self.content

        # Find all links to the target
        import re

        pattern = rf"\[\[{re.escape(target)}(?:[^\]]*?)?\]\]"

        for match in re.finditer(pattern, content):
            start = max(0, match.start() - context_chars)
            end = min(len(content), match.end() + context_chars)

            context = content[start:end]
            # Clean up context
            context = context.replace("\n", " ").strip()
            if start > 0:
                context = "..." + context
            if end < len(content):
                context = context + "..."

            contexts.append(context)

        return contexts
