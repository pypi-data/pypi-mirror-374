from pathlib import Path


class NoteNotFoundError(Exception):
    """Raised when a note cannot be found."""

    pass


class AmbiguousNoteError(Exception):
    """Raised when multiple notes match a query."""

    def __init__(self, query: str, matches: list[Path]):
        self.query = query
        self.matches = matches
        super().__init__(f"Multiple notes found for '{query}': {[m.stem for m in matches]}")
