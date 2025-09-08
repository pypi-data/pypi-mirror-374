"""Vault class for representing an Obsidian vault."""

from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterator, Literal, Optional

import pandas as pd

from obsidian_parser.errors import AmbiguousNoteError, NoteNotFoundError
from obsidian_parser.models.dataview import DataviewQuery
from obsidian_parser.note import Note
from obsidian_parser.relationships import RelationshipAnalyzer
from obsidian_parser.renderer import ContentRenderer


class Vault:
    """Represents an Obsidian vault."""

    __slots__ = (
        "path",
        "lazy_load",
        "_cache",
        "_note_paths",
        "_index",
        "_name_to_paths",
        "_renderer",
    )

    def __init__(self, path: str | Path, lazy_load: bool = True) -> None:
        """Initialize a Vault.

        Args:
            path: Path to the vault directory
            lazy_load: If True, notes are parsed only when accessed
        """
        self.path = Path(path).resolve()
        if not self.path.exists():
            raise ValueError(f"Vault path does not exist: {self.path}")
        if not self.path.is_dir():
            raise ValueError(f"Vault path is not a directory: {self.path}")

        self.lazy_load = lazy_load
        self._cache: dict[Path, Note] = {}
        self._note_paths: list[Path] | None = None
        self._index: pd.DataFrame | None = None
        self._name_to_paths: dict[str, list[Path]] | None = None
        self._renderer: ContentRenderer | None = None

        if not self.lazy_load:
            for path in self._get_note_paths():
                self._cache[path] = Note(path)

    @property
    def renderer(self) -> ContentRenderer:
        """Get the vault's content renderer."""
        if self._renderer is None:
            self._renderer = ContentRenderer(vault=self)
        return self._renderer

    def render_content(self, content: str, source_note: "Note | None" = None) -> str:
        """Render content using the vault's renderer.

        Args:
            content: Raw content to render
            source_note: Optional source note for context

        Returns:
            Rendered content
        """
        return self.renderer.render(content, source_note)

    def _get_note_paths(self) -> list[Path]:
        """Get all markdown file paths in the vault."""
        if self._note_paths is None:
            self._note_paths = list(self.path.rglob("*.md"))
        return self._note_paths

    def _build_name_index(self) -> dict[str, list[Path]]:
        """Build an index of note names to paths."""
        if self._name_to_paths is None:
            self._name_to_paths = {}
            for path in self._get_note_paths():
                name = path.stem.lower()
                if name not in self._name_to_paths:
                    self._name_to_paths[name] = []
                self._name_to_paths[name].append(path)
        return self._name_to_paths

    @property
    def notes(self) -> list[Note]:
        """Get all notes in the vault.

        Returns:
            list of Note objects
        """
        if self.lazy_load:
            return [self._get_note_by_path(p) for p in self._get_note_paths()]
        else:
            # Load all notes into cache if not lazy loading
            for path in self._get_note_paths():
                if path not in self._cache:
                    self._cache[path] = Note(path)
            return list(self._cache.values())

    def _get_note_by_path(self, path: Path) -> Note:
        """Get a note by its absolute path, using cache."""
        if path not in self._cache:
            self._cache[path] = Note(path)  # No vault reference needed!
        return self._cache[path]

    def get_note(self, query: str, strategy: Literal["exact", "smart", "interactive"] = "smart") -> Note | None:
        """Get a specific note by path.

        Args:
            query: Note name (e.g., "Barovia") or path (e.g., "Lore/Locations/Barovia.md")
            strategy: Resolution strategy:
                - 'exact': Only return if exactly one match
                - 'smart': Try to intelligently pick the best match
                - 'interactive': Prompt user to choose if ambiguous

        Returns:
            Note object if found, None if not found

        Raises:
            AmbiguousNoteError: If multiple matches and strategy is 'exact'
            NoteNotFoundError: If no matches found and strategy is 'exact'
        """
        # Convert Path to string for consistent handling
        if isinstance(query, Path):
            query = str(query)

        # First, try as a path
        if "/" in query or query.endswith(".md"):
            return self._get_note_by_path_query(query)

        # Otherwise, treat as a name
        return self._get_note_by_name(query, strategy)

    def _get_note_by_path_query(self, path_query: str) -> Note | None:
        """Get a note by path query."""
        path = Path(path_query)

        # Convert to absolute path if relative
        if not path.is_absolute():
            path = self.path / path

        # Ensure .md extension
        if path.suffix != ".md":
            path = path.with_suffix(".md")

        # Check if path exists and is within vault
        if not path.exists() or not str(path).startswith(str(self.path)):
            return None

        return self._get_note_by_path(path)

    def _get_note_by_name(self, name: str, strategy: Literal["exact", "smart", "interactive"] = "smart") -> Note | None:
        """Get a note by name with different resolution strategies."""
        name_index = self._build_name_index()
        name_lower = name.lower()

        # Exact match
        if name_lower in name_index:
            matches = name_index[name_lower]
            if len(matches) == 1:
                return self._get_note_by_path(matches[0])

            # Multiple exact matches - use strategy
            if strategy == "exact":
                raise AmbiguousNoteError(name, matches)
            elif strategy == "smart":
                return self._smart_resolve(name, matches)
            else:  # interactive
                return self._interactive_resolve(name, matches)

        # No exact match - try fuzzy matching
        similar = self._find_similar_notes(name)

        if not similar:
            if strategy == "exact":
                raise NoteNotFoundError(f"No note found matching '{name}'")
            return None

        if len(similar) == 1:
            return self._get_note_by_path(similar[0])

        # Multiple similar matches
        if strategy == "exact":
            raise AmbiguousNoteError(name, similar)
        elif strategy == "smart":
            return self._smart_resolve(name, similar)
        else:  # interactive
            return self._interactive_resolve(name, similar)

    def _find_similar_notes(self, name: str, threshold: float = 0.8) -> list[Path]:
        """Find notes with similar names using fuzzy matching."""
        name_lower = name.lower()
        similar: list[tuple[float, Path]] = []

        for path in self._get_note_paths():
            note_name = path.stem.lower()

            # Skip if name is too short and would match too many things
            if len(name_lower) <= 2 and name_lower not in note_name.lower():
                continue

            # Check for exact match first
            if note_name == name_lower:
                similar.append((1.0, path))
                continue

            # Check if query is a word in the note name (not just substring)
            import re

            if re.search(rf"\b{re.escape(name_lower)}\b", note_name):
                # Higher score for word boundary matches
                similarity = 0.95
                similar.append((similarity, path))
            elif name_lower in note_name:
                # Lower score for substring matches
                # Penalize based on how much extra content there is
                extra_chars = len(note_name) - len(name_lower)
                similarity = max(0.7 - (extra_chars * 0.05), 0.3)
                similar.append((similarity, path))
            else:
                # Use sequence matching for fuzzy search
                similarity = SequenceMatcher(None, name_lower, note_name).ratio()
                if similarity >= threshold:
                    similar.append((similarity, path))

        # Sort by similarity (highest first)
        similar.sort(key=lambda x: x[0], reverse=True)

        # Filter out low-quality matches if we have good ones
        if similar and similar[0][0] >= 0.95:
            # We have very good matches, filter out poor ones
            similar = [(score, path) for score, path in similar if score >= 0.8]

        return [path for _, path in similar]

    def _smart_resolve(self, query: str, matches: list[Path]) -> Note | None:
        """Intelligently resolve ambiguous matches."""
        query_lower = query.lower()

        # Strategy 1: Prefer exact name match (not substring)
        exact_matches = [p for p in matches if p.stem.lower() == query_lower]
        if len(exact_matches) == 1:
            return self._get_note_by_path(exact_matches[0])
        elif len(exact_matches) > 1:
            # Multiple exact matches - this shouldn't happen often
            # Prefer the one in the root or with shorter path
            exact_matches.sort(key=lambda p: (len(p.parts), str(p)))
            return self._get_note_by_path(exact_matches[0])

        # Strategy 2: Filter out obvious false positives
        # Remove matches where query is just a substring in a longer word
        filtered_matches = []
        for path in matches:
            name_lower = path.stem.lower()
            # Check if query appears as a word boundary
            import re

            if re.search(rf"\b{re.escape(query_lower)}\b", name_lower):
                filtered_matches.append(path)

        if len(filtered_matches) == 1:
            return self._get_note_by_path(filtered_matches[0])
        elif len(filtered_matches) > 1:
            matches = filtered_matches

        # Strategy 3: Prefer shorter names (likely more specific)
        matches_by_length = sorted(matches, key=lambda p: len(p.stem))
        if matches_by_length and len(matches_by_length[0].stem) < len(matches_by_length[1].stem) * 0.8:
            return self._get_note_by_path(matches_by_length[0])

        # Strategy 4: Prefer notes in common folders
        priority_folders = ["Lore", "Characters", "Locations", "Gods"]
        for folder in priority_folders:
            folder_matches = [p for p in matches if folder in str(p)]
            if len(folder_matches) == 1:
                return self._get_note_by_path(folder_matches[0])

        # Strategy 5: If still ambiguous, return None instead of guessing
        if len(matches) > 5:  # Too many matches suggests a common substring
            return None

        # Last resort: return the first match but warn
        print(f"Warning: Multiple notes match '{query}'. Returning '{matches[0].stem}'.")
        print(f"Other matches: {[m.stem for m in matches[1:]]}")
        return self._get_note_by_path(matches[0])

    def _interactive_resolve(self, query: str, matches: list[Path]) -> Note | None:
        """Interactively resolve ambiguous matches."""
        print(f"\nMultiple notes found matching '{query}':")
        for i, path in enumerate(matches, 1):
            rel_path = path.relative_to(self.path)
            print(f"  {i}. {path.stem} ({rel_path.parent})")

        while True:
            choice = input("\nEnter number to select (or 'q' to quit): ")
            if choice.lower() == "q":
                return None

            try:
                idx = int(choice) - 1
                if 0 <= idx < len(matches):
                    return self._get_note_by_path(matches[idx])
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number or 'q'.")

    def find_notes(self, title_contains: str, case_sensitive: bool = False) -> list[Note]:
        """Find notes by title/name.

        Args:
            title_contains: Substring to search for in note titles
            case_sensitive: Whether to perform case-sensitive search

        Returns:
            List of matching Note objects
        """
        results: list[Note] = []
        search_term = title_contains if case_sensitive else title_contains.lower()

        for note_path in self._get_note_paths():
            note_name = note_path.stem
            compare_name = note_name if case_sensitive else note_name.lower()

            if search_term in compare_name:
                results.append(self._get_note_by_path(note_path))

        return results

    def search_notes(self, query: str, limit: int = 10, threshold: float = 0.6) -> list[tuple[Note, float]]:
        """Search for notes using fuzzy matching.

        Args:
            query: Search query
            limit: Maximum number of results
            threshold: Minimum similarity score (0-1)

        Returns:
            List of (Note, similarity_score) tuples, sorted by relevance
        """
        results: list[tuple[Note, float]] = []
        query_lower = query.lower()

        for path in self._get_note_paths():
            note_name = path.stem.lower()

            # Calculate similarity
            if query_lower in note_name:
                # Boost score for substring matches
                base_score = SequenceMatcher(None, query_lower, note_name).ratio()
                similarity = min(base_score + 0.2, 1.0)
            else:
                similarity = SequenceMatcher(None, query_lower, note_name).ratio()

            if similarity >= threshold:
                note = self._get_note_by_path(path)
                results.append((note, similarity))

        # Sort by similarity score
        results.sort(key=lambda x: x[1], reverse=True)

        return results[:limit]

    def get_notes_with_tag(self, tag: str) -> list[Note]:
        """Get all notes containing a specific tag.

        Args:
            tag: Tag to search for (without # prefix)

        Returns:
            List of Note objects containing the tag
        """
        tag = tag.lstrip("#")  # Remove # if provided
        results = []

        for note in self.notes:
            # Check parsed tags from content
            if any(t.name == tag for t in note.tags):
                results.append(note)
                continue

            # Also check frontmatter tags
            fm_tags = note.frontmatter.get("tags", [])
            if isinstance(fm_tags, list) and tag in fm_tags:
                results.append(note)
            elif isinstance(fm_tags, str) and tag == fm_tags:
                results.append(note)

        return results

    def get_notes_linking_to(self, target: str) -> list[Note]:
        """Get all notes that link to a specific note.

        Args:
            target: Name of the target note (can be just name or path)

        Returns:
            List of Note objects that contain links to the target
        """
        results = []

        # Normalize the target - remove .md extension if present
        target = target.replace(".md", "")
        target_lower = target.lower()

        for note in self.notes:
            for link in note.wikilinks:
                link_target_lower = link.target.lower()

                # Check exact match (case-insensitive)
                if link_target_lower == target_lower:
                    results.append(note)
                    break

                # Check if target matches the last part of the path (just the name)
                if "/" in link.target:
                    link_name = link.target.split("/")[-1].lower()
                    if link_name == target_lower:
                        results.append(note)
                        break

                # Check if our target is a name and the link uses a path ending with it
                if "/" not in target and link_target_lower.endswith("/" + target_lower):
                    results.append(note)
                    break

        return results

    def build_index(self) -> pd.DataFrame:
        """Build a pandas DataFrame index of all notes.

        Returns:
            DataFrame with note metadata
        """
        if self._index is not None:
            return self._index

        data = []
        for note in self.notes:
            data.append(
                {
                    "path": str(note.path.relative_to(self.path)),
                    "name": note.name,
                    "tags": [tag.name for tag in note.tags],
                    "num_wikilinks": len(note.wikilinks),
                    "num_embeds": len(note.embeds),
                    "has_frontmatter": bool(note.frontmatter),
                }
            )

        self._index = pd.DataFrame(data)
        return self._index

    def clear_cache(self) -> None:
        """Clear the note cache."""
        self._cache.clear()
        self._index = None
        self._name_to_paths = None

    def __repr__(self) -> str:
        """String representation of the Vault."""
        return f"Vault(path='{self.path}', notes={len(self._get_note_paths())})"

    def __len__(self) -> int:
        """Get the number of notes in the vault."""
        return len(self._get_note_paths())

    def __iter__(self) -> Iterator[Note]:
        """Iterate over all notes in the vault."""
        return iter(self.notes)

    def get_notes_with_dataview(self, skip_errors: bool = True) -> list[Note]:
        """Get all notes that contain Dataview queries or fields.

        Args:
            skip_errors: If True, skip notes that cause parsing errors

        Returns:
            List of notes with Dataview content
        """
        results = []
        errors = []

        for note_path in self._get_note_paths():
            try:
                note = self._get_note_by_path(note_path)  # Use the internal method directly
                if note.has_dataview:  # Remove the "note and" check - we know note exists
                    results.append(note)
            except Exception as e:
                error_msg = f"Error parsing {note_path}: {str(e)[:100]}"
                if skip_errors:
                    print(f"Warning - {error_msg}")
                    errors.append((note_path, e))
                else:
                    raise

        if errors and skip_errors:
            print(f"\nSkipped {len(errors)} notes due to parsing errors")

        return results

    def get_notes_with_field(self, field_key: str) -> list[Note]:
        """Get all notes that have a specific Dataview field.

        Args:
            field_key: The field key to search for

        Returns:
            List of notes containing the field
        """
        results = []
        for note in self.notes:
            if note.get_dataview_field(field_key) is not None:
                results.append(note)
        return results

    def get_field_values(self, field_key: str) -> dict[str, Any]:
        """Get all values for a specific field across the vault.

        Args:
            field_key: The field key to collect

        Returns:
            Dictionary mapping note names to field values
        """
        values = {}
        for note in self.notes:
            field = note.get_dataview_field(field_key)
            if field:
                values[note.name] = field.value
        return values

    def build_dataview_index(self) -> pd.DataFrame:
        """Build an index of all Dataview fields across the vault.

        Returns:
            DataFrame with columns: note_name, field_key, field_value
        """
        data = []
        for note in self.notes:
            for field in note.dataview_fields:
                data.append(
                    {
                        "note_name": note.name,
                        "note_path": str(note.path.relative_to(self.path)),
                        "field_key": field.key,
                        "field_value": field.value,
                        "is_list": field.is_list,
                    }
                )

        return pd.DataFrame(data)

    def get_all_dataview_queries(self) -> list[tuple[Note, DataviewQuery]]:
        """Get all Dataview queries in the vault.

        Returns:
            List of (note, query) tuples
        """
        queries = []
        for note in self.notes:
            for query in note.dataview_queries:
                queries.append((note, query))
        return queries

    def analyze_dataview_usage(self) -> dict[str, Any]:
        """Analyze Dataview usage across the vault.

        Returns:
            Dictionary with usage statistics
        """
        stats = {
            "total_queries": 0,
            "total_inline_queries": 0,
            "total_fields": 0,
            "query_types": {},
            "common_fields": {},
            "notes_with_dataview": 0,
        }

        field_counter = {}

        for note in self.notes:
            if note.has_dataview:
                stats["notes_with_dataview"] += 1

            # Count queries
            stats["total_queries"] += len(note.dataview_queries)
            stats["total_inline_queries"] += len(note.dataview_inline_queries)
            stats["total_fields"] += len(note.dataview_fields)

            # Count query types
            for query in note.dataview_queries:
                query_type = query.query_type.value
                stats["query_types"][query_type] = stats["query_types"].get(query_type, 0) + 1

            # Count field usage
            for field in note.dataview_fields:
                field_counter[field.key] = field_counter.get(field.key, 0) + 1

        # Get top 10 most common fields
        stats["common_fields"] = dict(sorted(field_counter.items(), key=lambda x: x[1], reverse=True)[:10])

        return stats

    def analyze_relationships(self, progress_callback: Optional[Callable] = None) -> RelationshipAnalyzer:
        """Analyze relationships between notes in the vault.

        Args:
            progress_callback: Optional callback for progress updates

        Returns:
            RelationshipAnalyzer instance
        """

        analyzer = RelationshipAnalyzer(self)
        analyzer.analyze(progress_callback)
        return analyzer

    def get_backlinks(self, note: Note | str) -> list[Note]:
        """Get all notes that link to a specific note.

        Args:
            note: Note object or note name

        Returns:
            List of notes that link to the target note
        """
        if isinstance(note, Note):
            target_name = note.name
        else:
            target_name = note

        return self.get_notes_linking_to(target_name)

    def find_broken_links(self) -> dict[str, list[str]]:
        """Find all broken links in the vault.

        Returns:
            Dictionary mapping note names to their broken links
        """
        broken_links = {}

        for note in self.notes:
            broken = []
            for link in note.wikilinks:
                if not self.get_note(link.target):
                    broken.append(link.target)

            if broken:
                # Use relative path from vault root for consistency with test expectations
                relative_path = note.path.relative_to(self.path)
                broken_links[str(relative_path)] = broken

        return broken_links

    def get_note_graph(self) -> tuple[list[str], list[tuple[str, str]]]:
        """Get the note graph as nodes and edges.

        Returns:
            Tuple of (nodes, edges) where nodes are note names and edges are (source, target) tuples
        """
        nodes = [note.name for note in self.notes]
        edges = []

        for note in self.notes:
            for link in note.wikilinks:
                if self.get_note(link.target):  # Only include valid links
                    edges.append((note.name, link.target))

        return nodes, edges

    def get_note_strict(self, name: str) -> Note | None:
        """Get a note by exact name match only.

        Args:
            name: Exact note name (case-insensitive)

        Returns:
            Note if found with exact match, None otherwise
        """
        for path in self._get_note_paths():
            if path.stem == name:  # Exact case-sensitive match
                return self._get_note_by_path(path)

        return None
