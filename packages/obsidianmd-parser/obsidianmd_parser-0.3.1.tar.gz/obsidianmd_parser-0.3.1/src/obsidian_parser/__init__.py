"""Obsidian Parser - A Python library for parsing Obsidian Markdown files."""

__version__ = "0.3.0"
__author__ = "paddyd"
__email__ = "patduf1@gmail.com"

from obsidian_parser.note import Embed, Note, Section, Tag, WikiLink
from obsidian_parser.vault import Vault

__all__ = [
    "Vault",
    "Note",
    "WikiLink",
    "Tag",
    "Embed",
    "Section",
]
