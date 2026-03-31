"""Flow: model_topics
Purpose: BERTopic modeling on corpus embeddings
"""
from __future__ import annotations

import json
import numpy as np
from pathlib import Path

from prefect import flow, task

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@task(name="load_embeddings_and_texts")
def _load_embeddings() -> dict:
    emb_path = DATA_DIR / "features" / "embeddings.npy"
    txt_path = DATA_DIR / "features" / "embedding_texts.jsonl"
    if not emb_path.exists():
        raise FileNotFoundError(
            f"Embeddings not found at {emb_path}. Run embed_corpus first."
        )
    embeddings = np.load(str(emb_path))
    texts = []
    if txt_path.exists():
        with open(txt_path, encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                texts.append(data.get("text", ""))
    print(f"Loaded embeddings: {embeddings.shape}, texts: {len(texts)}")
    return {
        "embeddings": embeddings.tolist(),
        "texts": texts,
    }


@task(name="fit_bertopic_model")
def _fit_topics(data: dict) -> dict:
    from bertopic import BERTopic

    embeddings = np.array(data["embeddings"], dtype=np.float32)
    texts = data["texts"]

    topic_model = BERTopic(
        language="english",
        calculate_probabilities=True,
        verbose=True,
        nr_topics="auto",
        min_topic_size=max(5, len(texts) // 50),
    )
    topics, probs = topic_model.fit_transform(embeddings, texts)
    topic_info = topic_model.get_topic_info()
    topic_info_dict = topic_info.to_dict(orient="records")

    print(f"Found {len(topic_info_dict)} topics")
    return {
        "topics": topics.tolist(),
        "probs": probs.tolist() if hasattr(probs, "tolist") else list(probs),
        "topic_info": topic_info_dict,
        "num_topics": len(topic_info_dict),
    }


@task(name="save_topic_results")
def _save_topics(data: dict) -> str:
    out_dir = DATA_DIR / "features"
    out_dir.mkdir(parents=True, exist_ok=True)

    info_path = out_dir / "topic_info.jsonl"
    with open(info_path, "w", encoding="utf-8") as f:
        for row in data["topic_info"]:
            f.write(json.dumps(row, ensure_ascii=False, default=str) + "\n")

    topics_path = out_dir / "topics.npy"
    np.save(str(topics_path), np.array(data["topics"]))

    print(f"Saved topic info to {info_path}")
    return str(info_path)


@flow(name="model_topics")
def model_topics() -> int:
    """Run BERTopic clustering on corpus embeddings."""
    emb_data = _load_embeddings()
    topic_data = _fit_topics(emb_data)
    _save_topics(topic_data)
    return topic_data["num_topics"]


if __name__ == "__main__":
    model_topics()
