"""Flow: ingest_corpus
Purpose: Download and cache all text corpora to data/raw/
"""
from __future__ import annotations

import json
from pathlib import Path

from prefect import flow, task

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@task(name="load_all_corpus")
def _load_all_corpus() -> list[dict]:
    from human_condition.corpus.builder import CorpusBuilder

    builder = CorpusBuilder()
    docs = builder.build()
    return [
        {
            "source": d.source,
            "title": d.title,
            "text": d.text,
            "metadata": d.metadata,
        }
        for d in docs
    ]


@task(name="save_corpus_jsonl")
def _save_corpus(docs: list[dict]) -> str:
    out = DATA_DIR / "raw" / "corpus.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"Saved {len(docs)} documents to {out}")
    return str(out)


@task(name="validate_corpus")
def _validate_corpus(path: str) -> int:
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()
    count = len(lines)
    if count < 1:
        raise ValueError(f"Corpus has no records ({path})")
    print(f"Corpus validated: {count} documents")
    return count


@flow(name="ingest_corpus")
def ingest_corpus() -> int:
    """Download and cache all source text corpora."""
    docs = _load_all_corpus()
    path = _save_corpus(docs)
    count = _validate_corpus(path)
    return count


if __name__ == "__main__":
    ingest_corpus()
