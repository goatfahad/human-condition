"""Flow: preprocess_corpus
Purpose: Clean, chunk, and normalize ingested texts
"""
from __future__ import annotations

import json
from pathlib import Path

from prefect import flow, task

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@task(name="read_raw_corpus")
def _read_raw_corpus() -> list[dict]:
    inp = DATA_DIR / "raw" / "corpus.jsonl"
    if not inp.exists():
        raise FileNotFoundError(
            f"Raw corpus not found at {inp}. Run ingest_corpus first."
        )
    docs = []
    with open(inp, encoding="utf-8") as f:
        for line in f:
            docs.append(json.loads(line))
    print(f"Loaded {len(docs)} raw documents")
    return docs


@task(name="clean_and_chunk")
def _clean_and_chunk(docs: list[dict]) -> list[dict]:
    from human_condition.corpus.document import Document
    from human_condition.nlp.preprocessor import preprocess_documents

    original = [
        Document(
            source=d["source"],
            title=d["title"],
            text=d["text"],
            metadata=d.get("metadata", {}),
        )
        for d in docs
    ]
    chunked = preprocess_documents(original, max_chunk_size=200)
    result = [
        {
            "source": d.source,
            "title": d.title,
            "text": d.text,
            "metadata": d.metadata,
        }
        for d in chunked
    ]
    print(f"Produced {len(result)} chunks from {len(docs)} documents")
    return result


@task(name="save_processed_chunks")
def _save_processed(docs: list[dict]) -> str:
    out = DATA_DIR / "processed" / "chunks.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"Saved {len(docs)} chunks to {out}")
    return str(out)


@flow(name="preprocess_corpus")
def preprocess_corpus() -> int:
    """Clean and chunk all ingested texts."""
    raw = _read_raw_corpus()
    chunked = _clean_and_chunk(raw)
    _save_processed(chunked)
    return len(chunked)


if __name__ == "__main__":
    preprocess_corpus()
