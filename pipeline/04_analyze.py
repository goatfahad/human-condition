"""Flow: analyze_emotions
Purpose: Emotion classification on text chunks
"""
from __future__ import annotations

import json
from pathlib import Path

from prefect import flow, task

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@task(name="read_processed_chunks_for_analysis")
def _read_chunks() -> list[dict]:
    inp = DATA_DIR / "processed" / "chunks.jsonl"
    if not inp.exists():
        raise FileNotFoundError(
            f"Chunks not found at {inp}. Run preprocess_corpus first."
        )
    chunks = []
    with open(inp, encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line))
    print(f"Loaded {len(chunks)} chunks for emotion analysis")
    return chunks


@task(name="classify_text_emotions")
def _classify_emotions(chunks: list[dict], limit: int = 100) -> list[dict]:
    from human_condition.corpus.document import Document
    from human_condition.nlp.emotion import EmotionClassifier

    # Limit to manageable batch for demo
    sample = chunks[:limit]
    docs = [
        Document(
            source=c["source"],
            title=c["title"],
            text=c["text"],
            metadata=c.get("metadata", {}),
        )
        for c in sample
    ]
    texts = [d.text for d in docs]
    classifier = EmotionClassifier()
    emotions = classifier.classify_emotions(texts)
    print(f"Classified emotions for {len(emotions)} texts")
    return emotions


@task(name="attach_emotion_metadata")
def _attach_emotions(chunks: list[dict], emotions: list[dict]) -> list[dict]:
    enriched = []
    for chunk, emotion in zip(chunks, emotions, strict=False):
        new_chunk = {**chunk}
        new_chunk["metadata"] = {
            **chunk.get("metadata", {}),
            "dominant_emotion": emotion.get("dominant_emotion", "neutral"),
            "emotion_scores": emotion.get("emotions", {}),
        }
        enriched.append(new_chunk)
    print(f"Attached emotions to {len(enriched)} documents")
    return enriched


@task(name="save_analyzed_documents")
def _save_analyzed(docs: list[dict]) -> str:
    out = DATA_DIR / "features" / "emotions.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        for doc in docs:
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
    print(f"Saved {len(docs)} emotion-analyzed documents")
    return str(out)


@flow(name="analyze_emotions")
def analyze_emotions() -> int:
    """Run emotion classification and save results."""
    chunks = _read_chunks()
    emotions = _classify_emotions(chunks)
    enriched = _attach_emotions(chunks, emotions)
    _save_analyzed(enriched)
    return len(enriched)


if __name__ == "__main__":
    analyze_emotions()
