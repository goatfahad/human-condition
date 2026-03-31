"""Document dataclass — the atomic unit of corpus text."""
from __future__ import annotations

import re
from dataclasses import dataclass, field


def document_id(doc: "Document") -> str:
    """Deterministic identifier from source + slugified title."""
    slug = doc.title.lower()
    slug = re.sub(r"[^a-z0-9\s_-]", "", slug)
    slug = re.sub(r"[\s]+", "_", slug)
    while "__" in slug:
        slug = slug.replace("__", "_")
    slug = slug.strip("_")
    return f"{doc.source}_{slug}"


@dataclass(frozen=True)
class Document:
    """A single text unit from a corpus source.

    Attributes:
        source: Origin identifier (e.g. 'gutenberg', 'quran', 'reddit').
        title: Human-readable name of this text.
        text: The actual text content (stripped).
        metadata: Arbitrary key-value data (year, author, language, URL, etc.).
    """

    source: str
    title: str
    text: str
    metadata: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source:
            raise ValueError("source must not be empty")
        if not self.title.strip():
            raise ValueError("title must not be empty")
        object.__setattr__(self, "title", self.title.strip())
        object.__setattr__(self, "text", self.text.strip())

    @property
    def id(self) -> str:
        return document_id(self)

    def __len__(self) -> int:
        return len(self.text)

    @property
    def word_count(self) -> int:
        return len(self.text.split())
