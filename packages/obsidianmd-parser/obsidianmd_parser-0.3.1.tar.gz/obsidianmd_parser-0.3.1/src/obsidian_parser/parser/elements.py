"""Element-specific parsing functions."""

import re
from typing import Any

import frontmatter
import yaml

from obsidian_parser.note import Callout, Embed, Section, Tag, Task, WikiLink, Frontmatter

EMBED_TYPES = {
    "png": "image",
    "jpg": "image",
    "jpeg": "image",
    "gif": "image",
    "svg": "image",
    "webp": "image",
    "pdf": "pdf",
    "mp4": "video",
    "webm": "video",
    "ogv": "video",
    "mp3": "audio",
    "wav": "audio",
    "ogg": "audio",
    "m4a": "audio",
}


def debug_frontmatter_issues(vault_path: str, sample_size: int = 10):
    """Debug frontmatter parsing issues in a vault.

    Args:
        vault_path: Path to the vault
        sample_size: Number of problematic notes to examine
    """
    from pathlib import Path

    import yaml

    vault = Path(vault_path)
    issues = []

    for md_file in vault.rglob("*.md"):
        content = md_file.read_text(encoding="utf-8")

        if content.startswith("---"):
            # Try to find the frontmatter section
            match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                fm_text = match.group(1)
                try:
                    yaml.safe_load(fm_text)
                except yaml.YAMLError as e:
                    issues.append(
                        {
                            "file": md_file,
                            "error": str(e),
                            "frontmatter": fm_text[:200] + "..." if len(fm_text) > 200 else fm_text,
                        }
                    )

    print(f"Found {len(issues)} notes with frontmatter issues:")
    for issue in issues[:sample_size]:
        print(f"\n{issue['file'].name}:")
        print(f"Error: {issue['error']}")
        print(f"Frontmatter preview:\n{issue['frontmatter']}")
        print("-" * 40)

    return issues


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Parse YAML frontmatter from content.

    Args:
        content: The full note content

    Returns:
        Tuple of (frontmatter dict, content without frontmatter)
    """
    handler = frontmatter.default_handlers.YAMLHandler()

    # Try to parse
    try:
        post = frontmatter.loads(content, handler=handler)
        metadata = post.metadata
        content_without_fm = post.content

        # Ensure metadata is a dict
        if not isinstance(metadata, dict):
            metadata = {}

        return Frontmatter(metadata), content_without_fm

    except (yaml.scanner.ScannerError, TypeError) as e:
        # TypeError can occur when there's a naming conflict with 'content'
        # Common YAML errors - try to extract frontmatter manually
        if content.startswith("---"):
            match = re.search(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                yaml_content = match.group(1)
                content_without_fm = content[match.end() :]

                # Try to parse the YAML directly
                try:
                    metadata = yaml.safe_load(yaml_content)
                    if isinstance(metadata, dict):
                        return Frontmatter(metadata), content_without_fm
                except yaml.YAMLError:
                    pass

                # If parsing fails, return empty metadata but still remove frontmatter
                print(f"Warning - YAML parsing error (content removed): {str(e)[:100]}...")
                return {}, content_without_fm

        # No valid frontmatter found
        return Frontmatter(), content

    except Exception as e:
        # Log but don't crash
        print(f"Warning - error parsing frontmatter: {str(e)[:100]}...")
        return Frontmatter(), content


def parse_wikilinks(content: str) -> list[WikiLink]:
    """Parse all wikilinks from content.

    Args:
        content: The note content

    Returns:
        list of WikiLink objects
    """
    wikilinks: list[WikiLink] = []

    # First, remove code blocks to avoid parsing links inside them
    # Remove fenced code blocks (```...```)
    code_block_pattern = r"```[\s\S]*?```"
    content_no_fenced = re.sub(code_block_pattern, "", content)

    # Remove inline code (`...`)
    inline_code_pattern = r"`[^`]+`"
    content_no_code = re.sub(inline_code_pattern, "", content_no_fenced)

    # Pattern: [[target#heading^block-id|alias]]
    pattern = r"(?<!!)\[\[([^\[\]|#\^]+?)(?:#([^\[\]|^]+?))?(?:\^([^\[\]|]+?))?(?:\|([^\[\]]+?))?\]\]"

    for match in re.finditer(pattern, content_no_code):
        target = match.group(1).strip()
        heading = match.group(2).strip() if match.group(2) else None
        block_id = match.group(3).strip() if match.group(3) else None
        alias = match.group(4).strip() if match.group(4) else None

        wikilinks.append(WikiLink(target=target, heading=heading, block_id=block_id, alias=alias))

    return wikilinks


def parse_tags(content: str) -> list[Tag]:
    """Parse all tags from content.

    Args:
        content: The note content

    Returns:
        list of Tag objects
    """
    tags: list[Tag] = []
    seen: set[str] = set()

    # Updated pattern to allow tags after various punctuation marks
    # Negative lookbehind to ensure # is not preceded by alphanumeric or another #
    pattern = r"(?<![#\w])#([\w\-/]+)(?=\s|[.,;:!?)\]}\'\"]|$)"

    # Exclude tags in code blocks
    # Simple approach: remove code blocks before parsing
    code_block_pattern = r"```[\s\S]*?```|`[^`]+`"
    content_no_code = re.sub(code_block_pattern, "", content)

    # Remove URLs to prevent anchor fragments from being detected as tags
    # Pattern covers:
    # - URLs in angle brackets: <http://...>
    # - URLs in markdown links: [text](http://...)
    # - Plain URLs: http://... or https://...
    url_patterns = [
        r'<[^>]+>',              # Angle bracket URLs
        r'\[[^\]]*\]\([^)]+\)',  # Markdown links
        r'https?://[^\s]+',      # Plain URLs
    ]

    content_clean = content_no_code
    for url_pattern in url_patterns:
        content_clean = re.sub(url_pattern, "", content_clean)

    for match in re.finditer(pattern, content_clean, re.MULTILINE | re.UNICODE):
        tag_name = match.group(1)
        if tag_name not in seen:
            seen.add(tag_name)
            tags.append(Tag(name=tag_name))

    return tags


def parse_embeds(content: str) -> list[Embed]:
    """Parse all embeds from content.

    Args:
        content: The note content

    Returns:
        list of Embed objects
    """
    embeds: list[Embed] = []

    # Pattern: ![[target#heading^block-id]]
    pattern = r"!\[\[([^\[\]|#\^]+?)(?:#([^\[\]|^]+?))?(?:\^([^\[\]|]+?))?\]\]"

    for match in re.finditer(pattern, content):
        target = match.group(1).strip()
        heading = match.group(2).strip() if match.group(2) else None
        block_id = match.group(3).strip() if match.group(3) else None

        # Determine embed type based on file extension
        embed_type = "note"
        if "." in target:
            ext = target.split(".")[-1].lower()
            embed_type = EMBED_TYPES.get(ext, "note")

        embeds.append(Embed(target=target, type=embed_type, heading=heading, block_id=block_id))

    return embeds


def parse_sections(content: str) -> list[Section]:
    """Parse sections (headings and their content).

    Args:
        content: The note content

    Returns:
        list of Section objects in document order
    """
    sections: list[Section] = []
    lines = content.split("\n")

    # Find all headings
    heading_pattern = r"^(#{1,6})\s+(.+)$"
    heading_lines: list[tuple[int, int, str]] = []

    for i, line in enumerate(lines):
        match = re.match(heading_pattern, line)
        if match:
            level = len(match.group(1))
            heading_text = match.group(2).strip()
            heading_lines.append((i, level, heading_text))

    # Build sections with content
    for idx, (line_num, level, heading) in enumerate(heading_lines):
        # Determine content range
        start_line = line_num + 1
        end_line = heading_lines[idx + 1][0] if idx + 1 < len(heading_lines) else len(lines)

        # Extract content
        content_lines = lines[start_line:end_line]
        content = "\n".join(content_lines).strip()

        section = Section(heading=heading, level=level, content=content, line_number=line_num)
        sections.append(section)

    # Build hierarchy with parent references
    for i, section in enumerate(sections):
        # Find parent section (previous section with lower level)
        for j in range(i - 1, -1, -1):
            if sections[j].level < section.level:
                sections[j].subsections.append(section)
                section.parent = sections[j]  # Set parent reference
                break

    # Return all sections (flat list) - users can filter for top-level if needed
    return sections

def get_top_level_sections(sections: list[Section]) -> list[Section]:
    """Get only top-level sections (those without parents).
    
    Args:
        sections: All sections from parse_sections
        
    Returns:
        List of top-level Section objects
    """
    return [s for s in sections if s.parent is None]

def parse_callouts(content: str) -> list[Callout]:
    """Parse Obsidian callouts.

    Args:
        content: The note content

    Returns:
        List of Callout objects
    """
    callouts: list[Callout] = []

    # Pattern for callout start: > [!TYPE] or > [!TYPE]+ or > [!TYPE]-
    callout_pattern = r"^>\s*\[!([A-Z]+)\]([-+])?\s*(.*)$"

    lines = content.split("\n")

    # First, identify which lines are in code blocks
    in_code_block = False
    code_block_lines = set()

    for i, line in enumerate(lines):
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            code_block_lines.add(i)
        elif in_code_block:
            code_block_lines.add(i)

    # Now parse callouts, skipping those in code blocks
    i = 0
    while i < len(lines):
        # Skip if this line is in a code block
        if i in code_block_lines:
            i += 1
            continue

        if match := re.match(callout_pattern, lines[i], re.IGNORECASE):
            callout_type = match.group(1).upper()
            fold_indicator = match.group(2)
            title = match.group(3) if match.group(3) else ""

            is_foldable = fold_indicator in ("+", "-")
            is_folded = fold_indicator == "-"

            # Collect callout content
            content_lines: list[str] = []
            start_line = i
            i += 1

            # Continue collecting lines that start with '>' and aren't in code blocks
            while i < len(lines) and lines[i].startswith(">") and i not in code_block_lines:
                # Remove '>' prefix and optional space
                content_line = lines[i][1:].lstrip()
                content_lines.append(content_line)
                i += 1

            callouts.append(
                Callout(
                    type=callout_type,
                    title=title,
                    content="\n".join(content_lines),
                    line_number=start_line,
                    is_foldable=is_foldable,
                    is_folded=is_folded,
                )
            )
        else:
            i += 1

    return callouts


def parse_tasks(content: str) -> list[Task]:
    """Parse task list items."""
    # Mask code blocks to prevent parsing
    masked_content = mask_code_blocks(content)

    tasks: list[Task] = []
    task_pattern = r"^([\s\t]*)-\s*\[(.)\]\s*(.*)$"

    for i, line in enumerate(masked_content.split("\n")):
        if match := re.match(task_pattern, line):
            # Get the original line to extract the actual text
            original_line = content.split("\n")[i]
            if match_original := re.match(task_pattern, original_line):
                indent = match_original.group(1)
                status = match_original.group(2)
                text = match_original.group(3).strip()

                indent_level = len(indent.replace("\t", "    "))

                tasks.append(
                    Task(
                        text=text,
                        status=status,  # type: ignore
                        line_number=i,
                        indent_level=indent_level,
                    )
                )

    return tasks


def mask_code_blocks(content: str, mask_char: str = "\x00") -> str:
    """Replace code block content with mask characters.

    This preserves line numbers while preventing parsing of code content.

    Args:
        content: The note content
        mask_char: Character to use for masking (should not appear in patterns)

    Returns:
        Content with code blocks masked
    """
    lines = content.split("\n")
    result = []
    in_code_block = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            result.append(mask_char * len(line))
        elif in_code_block:
            result.append(mask_char * len(line))
        else:
            result.append(line)

    return "\n".join(result)
