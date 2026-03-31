"""Text preprocessing: cleaning, chunking, and document preparation."""
from __future__ import annotations

import re

from human_condition.corpus.document import Document


def clean_text(text: str) -> str:
    """Normalize text for downstream NLP.

    - Lowercase
    - Collapse whitespace runs
    - Strip leading/trailing whitespace
    - Keep sentence-ending punctuation (. ! ?)
    - Replace unicode whitespace variants with ASCII space
    - Remove control characters except newlines
    """
    if not text:
        return ""
    # Replace unicode whitespace variants
    text = re.sub(r"[\u00a0\u2000-\u200b\u202f\u205f\u3000\ufeff]", " ", text)
    # Remove control characters (keep \n)
    text = re.sub(r"[^\S\n]", " ", text)
    text = re.sub(r"\n+", "\n", text)
    text = text.lower().strip()
    # Collapse multiple spaces within lines
    text = re.sub(r"[^\S\n]+", " ", text)
    return text


def _sentence_boundary(text: str, pos: int, max_len: int) -> int:
    """Find the nearest sentence boundary at or before pos."""
    end = min(pos + max_len, len(text))
    # Look for sentence-ending punctuation followed by space or newline
    for i in range(end, max(pos, end - max_len), -1):
        if i > 0 and i < len(text) and text[i - 1] in ".!?" and (
            i >= len(text) or text[i] in (" ", "\n", "\r")
        ):
            return i
    # Fallback: look for any whitespace break
    for i in range(end, max(pos, end - max_len // 2), -1):
        if i > 0 and text[i - 1] in (" ", "\n", "\t"):
            return i
    return end


def chunk_text(
    text: str, max_chunk_size: int = 200, stride: int = 50
) -> list[str]:
    """Split text into overlapping chunks.

    Strategy:
    1. If text fits in one chunk, return as-is
    2. Split on sentence boundaries, word boundaries, or character boundary
    3. stride controls overlap between consecutive chunks
    """
    if not text:
        return []

    text = text.strip()
    if not text:
        return []
    if len(text) <= max_chunk_size:
        return [text]

    chunks: list[str] = []
    start = 0

    while start < len(text):
        end = min(start + max_chunk_size, len(text))
        if end >= len(text):
            chunks.append(text[start:].strip())
            break

        # Find best split point within [start, end]
        best = _find_sentence_end(text, start, end, max_chunk_size)
        if best <= start + 10:
            best = _find_word_end(text, start, end)
        if best <= start:
            best = end

        chunk = text[start:best].strip()
        if chunk:
            chunks.append(chunk)

        # Advance with overlap, ensuring forward progress
        next_start = best - stride
        if next_start <= start:
            next_start = start + 1
        start = next_start

    # Deduplicate adjacent identical chunks
    deduped: list[str] = []
    for c in chunks:
        if not deduped or c != deduped[-1]:
            deduped.append(c)

    return deduped


def _find_sentence_end(text: str, start: int, end: int, max_len: int) -> int:
    """Find the closest sentence boundary at or before `end`."""
    search_start = max(end - max_len // 2, start)
    for i in range(end, search_start, -1):
        if i < len(text) - 1 and text[i - 1] in ".!?" and text[i] == " ":
            return i
    return 0


def _find_word_end(text: str, start: int, end: int) -> int:
    """Find the closest word boundary at or before `end`."""
    for i in range(end, start, -1):
        if i < len(text) and text[i] == " ":
            return i
    return 0


def preprocess_documents(
    docs: list[Document], max_chunk_size: int = 200
) -> list[Document]:
    """Clean and chunk a list of Documents.

    Each original document may produce multiple chunked Documents with
    `chunk_N` suffixes on the title.
    """
    result: list[Document] = []
    for doc in docs:
        cleaned = clean_text(doc.text)
        chunks = chunk_text(cleaned, max_chunk_size=max_chunk_size)
        for i, chunk in enumerate(chunks):
            result.append(
                Document(
                    source=doc.source,
                    title=f"{doc.title} (chunk {i + 1})",
                    text=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "original_title": doc.title,
                    },
                )
            )
    return result
