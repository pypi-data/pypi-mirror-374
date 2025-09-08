"""Core parsing functionality."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from obsidian_parser.note import Note


def parse_note(note: "Note") -> None:
    """Parse a note and populate its elements.

    Args:
        note: The Note object to parse
    """
    try:
        content = note.content
        if not isinstance(content, str):
            raise ValueError(f"Expected string content, got {type(content)}")

        # Import specific parsers
        from obsidian_parser.parser.dataview import DataviewParser
        from obsidian_parser.parser.elements import (
            parse_callouts,
            parse_embeds,
            parse_frontmatter,
            parse_sections,
            parse_tags,
            parse_tasks,
            parse_wikilinks,
        )

        # Parse frontmatter first (it affects content parsing)
        frontmatter, content_without_frontmatter = parse_frontmatter(content)
        note._frontmatter = frontmatter

        # Parse other elements from the content without frontmatter
        note._wikilinks = parse_wikilinks(content_without_frontmatter)
        note._tags = parse_tags(content_without_frontmatter)
        note._embeds = parse_embeds(content_without_frontmatter)

        # Add tags from frontmatter
        if "tags" in frontmatter:
            fm_tags = frontmatter["tags"]
            if isinstance(fm_tags, str):
                fm_tags = [fm_tags]
            elif not isinstance(fm_tags, list):
                fm_tags = []

            # Convert frontmatter tags to Tag objects
            from obsidian_parser.note import Tag

            for tag_name in fm_tags:
                if isinstance(tag_name, str):
                    # Check if tag already exists (avoid duplicates)
                    if not any(t.name == tag_name for t in note._tags):
                        note._tags.append(Tag(name=tag_name))

        # Parse sections and build section map
        note._sections = parse_sections(content_without_frontmatter)
        note._sections_map = {section.heading: section for section in note._sections}

        # Store additional parsed elements
        note._callouts = parse_callouts(content_without_frontmatter)
        note._tasks = parse_tasks(content_without_frontmatter)

        # Parse Dataview elements - add try/catch here
        try:
            note._dataview_queries = DataviewParser.parse_query_blocks(content_without_frontmatter)
            note._dataview_inline_queries = DataviewParser.parse_inline_queries(content_without_frontmatter)
            note._dataview_fields = DataviewParser.parse_inline_fields(content_without_frontmatter)
        except Exception as e:
            # If Dataview parsing fails, set empty lists
            print(f"Warning - Dataview parsing failed for {note.path}: {e}")
            note._dataview_queries = []
            note._dataview_inline_queries = []
            note._dataview_fields = []

    except Exception as e:
        print(f"Error in parse_note for {note.path}: {e}")
        raise
