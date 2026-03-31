"""Flow: embed_corpus
Purpose: Generate sentence embeddings for all text chunks
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from prefect import flow, task

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@task(name="read_processed_chunks")
def _read_processed_chunks() -> list[dict]:
    inp = DATA_DIR / "processed" / "chunks.jsonl"
    if not inp.exists():
        raise FileNotFoundError(
            f"Chunks not found at {inp}. Run preprocess_corpus first."
        )
    chunks = []
    with open(inp, encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    print(f"Loaded {len(chunks)} text chunks")
    return chunks


@task(name="generate_sentence_embeddings")
def _generate_embeddings(chunks: list[dict]) -> dict:
    from human_condition.corpus.document import Document
    from human_condition.nlp.embedder import Embedder

    docs = [
        Document(
            source=c["source"],
            title=c["title"],
            text=c["text"],
            metadata=c.get("metadata", {}),
        )
        for c in chunks
    ]
    embedder = Embedder()
    embeddings, texts = embedder.embed_documents(docs)
    print(f"Generated embeddings: {embeddings.shape}")
    return {
        "embeddings": embeddings.tolist(),
        "texts": texts,
        "dim": int(embeddings.shape[1]),
    }


@task(name="save_embeddings")
def _save_embeddings(data: dict) -> str:
    embeddings = np.array(data["embeddings"], dtype=np.float32)
    texts = data["texts"]

    emb_path = DATA_DIR / "features" / "embeddings.npy"
    emb_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(str(emb_path), embeddings)

    txt_path = DATA_DIR / "features" / "embedding_texts.jsonl"
    with open(txt_path, "w", encoding="utf-8") as f:
        for t in texts:
            f.write(json.dumps({"text": t}, ensure_ascii=False) + "\n")

    print(f"Saved embeddings: {embeddings.shape} -> {emb_path}")
    return str(emb_path)


@flow(name="embed_corpus")
def embed_corpus() -> str:
    """Generate and save sentence embeddings for all corpus chunks."""
    chunks = _read_processed_chunks()
    emb_data = _generate_embeddings(chunks)
    path = _save_embeddings(emb_data)
    return path


if __name__ == "__main__":
    embed_corpus()
