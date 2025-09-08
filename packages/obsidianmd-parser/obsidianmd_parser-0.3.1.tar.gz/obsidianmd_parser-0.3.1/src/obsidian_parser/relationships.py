"""Note relationship analysis and metadata functionality."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

import pandas as pd

from obsidian_parser.note import Note

if TYPE_CHECKING:
    from obsidian_parser.vault import Vault


@dataclass
class NoteRelationship:
    """Represents a relationship between two notes."""

    source: "Note"
    target: "Note"
    relationship_type: str  # 'link', 'tag', 'folder', 'metadata'
    context: str | None = None  # e.g., the text around a link
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class NoteMetadata:
    """Enhanced metadata for a note including computed properties."""

    note: "Note"

    # Basic file metadata
    path: Path
    size: int
    created: datetime
    modified: datetime

    # Content metadata
    word_count: int
    line_count: int

    # Tag metadata
    tags: list[str]

    # Structural metadata
    heading_count: int
    max_heading_depth: int
    has_frontmatter: bool
    has_dataview: bool

    # Link metadata
    outgoing_links: list[str]
    incoming_links: list[str] = field(default_factory=list)
    broken_links: list[str] = field(default_factory=list)

    # Relationships
    relationships: list[NoteRelationship] = field(default_factory=list)

    @property
    def link_count(self) -> int:
        """Total number of outgoing links."""
        return len(self.outgoing_links)

    @property
    def backlink_count(self) -> int:
        """Total number of incoming links."""
        return len(self.incoming_links)

    @property
    def connectivity_score(self) -> float:
        """Score representing how connected this note is (0-1)."""
        total_links = self.link_count + self.backlink_count
        if total_links == 0:
            return 0.0
        # Normalize by a reasonable max (e.g., 20 total links = 1.0)
        return min(total_links / 20.0, 1.0)


class RelationshipAnalyzer:
    """Analyzes relationships between notes in a vault."""

    def __init__(self, vault: "Vault"):
        """Initialize analyzer with a vault.

        Args:
            vault: The vault to analyze
        """
        self.vault = vault
        self._metadata_cache: dict[str, NoteMetadata] = {}
        self._relationship_graph: dict[str, list[NoteRelationship]] = defaultdict(list)
        self._analyzed = False

    def analyze(self, progress_callback: Callable[[int, int, str], None] | None = None) -> None:
        """Analyze all notes in the vault.

        Args:
            progress_callback: Optional callback for progress updates
        """
        total_notes = len(self.vault.notes)

        # First pass: Build metadata for each note
        for i, note in enumerate(self.vault.notes):
            if progress_callback:
                progress_callback(i, total_notes, f"Analyzing {note.name}")

            self._build_note_metadata(note)

        # Second pass: Build incoming links
        for note_meta in self._metadata_cache.values():
            for link_target in note_meta.outgoing_links:
                if link_target in self._metadata_cache:
                    self._metadata_cache[link_target].incoming_links.append(note_meta.note.name)

        self._analyzed = True

    def _build_note_metadata(self, note: Note) -> NoteMetadata:
        """Build metadata for a single note.

        Args:
            note: The note to analyze

        Returns:
            NoteMetadata object
        """
        if note.name in self._metadata_cache:
            return self._metadata_cache[note.name]

        # Get file stats
        stats = note.path.stat()

        # Count words and lines
        content = note.content
        word_count = len(content.split())
        line_count = content.count("\n") + 1

        # Get outgoing links
        outgoing_links = list({link.target for link in note.wikilinks})

        # Check for broken links
        broken_links = []
        for link in outgoing_links:
            if not self.vault.get_note(link):
                broken_links.append(link)

        # Get tags
        tags = [tag.name for tag in note.tags]

        # Analyze structure
        heading_count = len(note.sections)
        max_heading_depth = max((s.level for s in note.sections), default=0)

        metadata = NoteMetadata(
            note=note,
            path=note.path,
            size=stats.st_size,
            created=datetime.fromtimestamp(stats.st_ctime),
            modified=datetime.fromtimestamp(stats.st_mtime),
            word_count=word_count,
            line_count=line_count,
            outgoing_links=outgoing_links,
            broken_links=broken_links,
            tags=tags,
            heading_count=heading_count,
            max_heading_depth=max_heading_depth,
            has_frontmatter=bool(note.frontmatter),
            has_dataview=note.has_dataview,
        )

        self._metadata_cache[note.name] = metadata
        return metadata

    def get_metadata(self, note: Note | str) -> NoteMetadata | None:
        """Get metadata for a specific note.

        Args:
            note: Note object or note name

        Returns:
            NoteMetadata if found
        """
        if not self._analyzed:
            self.analyze()

        if isinstance(note, Note):
            note_name = note.name
        else:
            note_name = note

        return self._metadata_cache.get(note_name)

    def find_orphaned_notes(self) -> list[Note]:
        """Find notes with no incoming or outgoing links.

        Returns:
            List of orphaned notes
        """
        if not self._analyzed:
            self.analyze()

        orphaned = []
        for metadata in self._metadata_cache.values():
            if not metadata.incoming_links and not metadata.outgoing_links:
                orphaned.append(metadata.note)

        return orphaned

    def find_hub_notes(self, min_connections: int = 10) -> list[tuple[Note, int]]:
        """Find highly connected hub notes.

        Args:
            min_connections: Minimum total connections to be considered a hub

        Returns:
            List of (note, connection_count) tuples sorted by connections
        """
        if not self._analyzed:
            self.analyze()

        hubs = []
        for metadata in self._metadata_cache.values():
            total_connections = len(metadata.incoming_links) + len(metadata.outgoing_links)
            if total_connections >= min_connections:
                hubs.append((metadata.note, total_connections))

        return sorted(hubs, key=lambda x: x[1], reverse=True)

    def find_related_notes(self, note: Note | str, max_distance: int = 2) -> list[tuple[Note, int]]:
        """Find notes related to a given note.

        Args:
            note: Note object or note name
            max_distance: Maximum link distance to consider

        Returns:
            List of (note, distance) tuples
        """
        if not self._analyzed:
            self.analyze()

        if isinstance(note, Note):
            start_name = note.name
        else:
            start_name = note

        if start_name not in self._metadata_cache:
            return []

        # BFS to find related notes
        visited = {start_name: 0}
        queue = [(start_name, 0)]
        related = []

        while queue:
            current_name, distance = queue.pop(0)

            if distance >= max_distance:
                continue

            current_meta = self._metadata_cache.get(current_name)
            if not current_meta:
                continue

            # Check outgoing links
            for link_target in current_meta.outgoing_links:
                if link_target not in visited:
                    visited[link_target] = distance + 1
                    queue.append((link_target, distance + 1))
                    if link_target in self._metadata_cache:
                        related.append((self._metadata_cache[link_target].note, distance + 1))

            # Check incoming links
            for link_source in current_meta.incoming_links:
                if link_source not in visited:
                    visited[link_source] = distance + 1
                    queue.append((link_source, distance + 1))
                    if link_source in self._metadata_cache:
                        related.append((self._metadata_cache[link_source].note, distance + 1))

        # Sort by distance, then by name
        return sorted(related, key=lambda x: (x[1], x[0].name))

    def find_similar_notes(self, note: Note | str, min_similarity: float = 0.3) -> list[tuple[Note, float]]:
        """Find notes similar to a given note based on tags and links.

        Args:
            note: Note object or note name
            min_similarity: Minimum similarity score (0-1)

        Returns:
            List of (note, similarity_score) tuples
        """
        if not self._analyzed:
            self.analyze()

        if isinstance(note, Note):
            source_meta = self.get_metadata(note.name)
        else:
            source_meta = self.get_metadata(note)

        if not source_meta:
            return []

        similar = []
        source_tags = set(source_meta.tags)
        source_links = set(source_meta.outgoing_links + source_meta.incoming_links)

        for other_meta in self._metadata_cache.values():
            if other_meta.note.name == source_meta.note.name:
                continue

            # Calculate similarity based on shared tags and links
            other_tags = set(other_meta.tags)
            other_links = set(other_meta.outgoing_links + other_meta.incoming_links)

            # Jaccard similarity for tags
            tag_similarity = 0.0
            if source_tags or other_tags:
                tag_similarity = len(source_tags & other_tags) / len(source_tags | other_tags)

            # Jaccard similarity for links
            link_similarity = 0.0
            if source_links or other_links:
                link_similarity = len(source_links & other_links) / len(source_links | other_links)

            # Combined similarity (weighted average)
            similarity = 0.6 * tag_similarity + 0.4 * link_similarity

            if similarity >= min_similarity:
                similar.append((other_meta.note, similarity))

        return sorted(similar, key=lambda x: x[1], reverse=True)

    def build_statistics_report(self) -> dict[str, Any]:
        """Build comprehensive statistics about the vault.

        Returns:
            Dictionary with vault statistics
        """
        if not self._analyzed:
            self.analyze()

        total_notes = len(self._metadata_cache)
        if total_notes == 0:
            return {"total_notes": 0, "error": "No notes analyzed"}

        # Calculate various statistics
        stats = {
            "total_notes": total_notes,
            "total_words": sum(m.word_count for m in self._metadata_cache.values()),
            "total_links": sum(m.link_count for m in self._metadata_cache.values()),
            "total_backlinks": sum(m.backlink_count for m in self._metadata_cache.values()),
            "total_tags": sum(len(m.tags) for m in self._metadata_cache.values()),
            "unique_tags": len(set(tag for m in self._metadata_cache.values() for tag in m.tags)),
            "orphaned_notes": len(self.find_orphaned_notes()),
            "notes_with_broken_links": sum(1 for m in self._metadata_cache.values() if m.broken_links),
            "total_broken_links": sum(len(m.broken_links) for m in self._metadata_cache.values()),
            "notes_with_frontmatter": sum(1 for m in self._metadata_cache.values() if m.has_frontmatter),
            "notes_with_dataview": sum(1 for m in self._metadata_cache.values() if m.has_dataview),
            "average_word_count": (
                sum(m.word_count for m in self._metadata_cache.values()) / total_notes if total_notes > 0 else 0
            ),
            "average_links_per_note": (
                sum(m.link_count for m in self._metadata_cache.values()) / total_notes if total_notes > 0 else 0
            ),
        }

        # Find most connected notes
        hubs = self.find_hub_notes(min_connections=5)
        stats["top_hubs"] = [(n.name, count) for n, count in hubs[:10]]

        # Find largest notes
        largest = sorted(self._metadata_cache.values(), key=lambda m: m.word_count, reverse=True)[:10]
        stats["largest_notes"] = [(m.note.name, m.word_count) for m in largest]

        # Most used tags
        tag_counts = defaultdict(int)
        for m in self._metadata_cache.values():
            for tag in m.tags:
                if tag:  # Only count non-empty tags
                    tag_counts[tag] += 1
        if tag_counts:
            stats["top_tags"] = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:20]
        else:
            stats["top_tags"] = []

        return stats

    def export_to_dataframe(self) -> pd.DataFrame:
        """Export metadata to a pandas DataFrame for analysis.

        Returns:
            DataFrame with note metadata
        """
        if not self._analyzed:
            self.analyze()

        data = []
        for metadata in self._metadata_cache.values():
            data.append(
                {
                    "name": metadata.note.name,
                    "path": str(metadata.path.relative_to(self.vault.path)),
                    "size": metadata.size,
                    "created": metadata.created,
                    "modified": metadata.modified,
                    "word_count": metadata.word_count,
                    "line_count": metadata.line_count,
                    "outgoing_links": metadata.link_count,
                    "incoming_links": metadata.backlink_count,
                    "broken_links": len(metadata.broken_links),
                    "tags": ", ".join(metadata.tags),
                    "tag_count": len(metadata.tags),
                    "heading_count": metadata.heading_count,
                    "max_heading_depth": metadata.max_heading_depth,
                    "has_frontmatter": metadata.has_frontmatter,
                    "has_dataview": metadata.has_dataview,
                    "connectivity_score": metadata.connectivity_score,
                }
            )

        return pd.DataFrame(data)
