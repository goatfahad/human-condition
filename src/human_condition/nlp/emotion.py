"""Emotion classification using RoBERTa emotion model."""
from __future__ import annotations

from dataclasses import dataclass


def _get_torch():
    import torch
    return torch


def _get_pipeline():
    from transformers import pipeline
    return pipeline


LABEL_MAP: dict[str, str] = {
    "LABEL_0": "admiration",
    "LABEL_1": "amusement",
    "LABEL_2": "anger",
    "LABEL_3": "annoyance",
    "LABEL_4": "approval",
    "LABEL_5": "caring",
    "LABEL_6": "confusion",
    "LABEL_7": "curiosity",
    "LABEL_8": "desire",
    "LABEL_9": "disappointment",
    "LABEL_10": "disapproval",
    "LABEL_11": "disgust",
    "LABEL_12": "embarrassment",
    "LABEL_13": "excitement",
    "LABEL_14": "fear",
    "LABEL_15": "gratitude",
    "LABEL_16": "grief",
    "LABEL_17": "joy",
    "LABEL_18": "love",
    "LABEL_19": "nervousness",
    "LABEL_20": "optimism",
    "LABEL_21": "pride",
    "LABEL_22": "realization",
    "LABEL_23": "relief",
    "LABEL_24": "remorse",
    "LABEL_25": "sadness",
    "LABEL_26": "surprise",
    "LABEL_27": "neutral",
}


class EmotionClassifier:
    """Classifier using fine-tuned RoBERTa for emotion detection.

    Attributes:
        model_name: HuggingFace model identifier.
        device: Compute device ('cuda', 'mps', or 'cpu').
        top_k: Number of top emotions to return per text.
    """

    def __init__(
        self,
        model_name: str = "SamLowe/roberta-base-go_emotions",
        device: str | None = None,
        top_k: int | None = None,
    ) -> None:
        self.model_name = model_name
        self.top_k = top_k if top_k is not None else 28
        torch_mod = _get_torch()
        if device is None:
            if torch_mod.cuda.is_available():
                self.device = "cuda"
            elif hasattr(torch_mod.backends, "mps") and torch_mod.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device
        self._pipeline = None

    def _ensure_pipeline(self):
        """Lazy-load the classification pipeline."""
        if self._pipeline is None:
            pipe = _get_pipeline()
            self._pipeline = pipe(
                "text-classification",
                model=self.model_name,
                tokenizer=self.model_name,
                device=0 if self.device == "cuda" else -1,
                top_k=self.top_k,
                truncation=True,
                max_length=512,
            )
        return self._pipeline

    def classify_emotions(
        self,
        texts: list[str],
        batch_size: int = 8,
        return_flat: bool = True,
    ) -> list[dict] | list[list[dict]]:
        """Classify emotion for each text.

        Args:
            texts: List of text strings to classify.
            batch_size: Number of texts per batch.
            return_flat: If True, returns one dict per text.

        Returns:
            List of dicts with structure:
            {"text": ..., "emotions": {name: score, ...}, "dominant_emotion": "..."}
        """
        pipe = self._ensure_pipeline()
        all_results: list = []

        for text in texts:
            if not text.strip():
                all_results.append({
                    "text": "",
                    "emotions": {},
                    "dominant_emotion": "neutral",
                })
                continue

            truncated = text[:510] if len(text) > 510 else text
            raw = pipe(truncated)

            if isinstance(raw, list) and len(raw) > 0 and isinstance(raw[0], list):
                emotions_list = raw[0]
            else:
                emotions_list = raw if isinstance(raw, list) else [raw]

            emotions: dict[str, float] = {}
            for item in emotions_list:
                label = item.get("label", "")
                score = item.get("score", 0.0)
                emotion_name = LABEL_MAP.get(label, label)
                emotions[emotion_name] = round(score, 4)

            dominant = max(emotions, key=lambda k: emotions[k]) if emotions else "neutral"  # type: ignore[arg-type]
            all_results.append({
                "text": text[:100],
                "emotions": emotions,
                "dominant_emotion": dominant,
            })

        return all_results

    def classify_single(self, text: str) -> dict:  # type: ignore[return-value]
        """Classify a single text and return dict."""
        results: list[dict] = self.classify_emotions([text])  # type: ignore[assignment]
        return results[0]


def emotions_to_documents(docs: list, emotions: list[dict]) -> list:
    """Attach emotion metadata to Documents.

    Merges emotion classification results back into Document objects
    by adding emotion metadata fields.

    Args:
        docs: Original Document list.
        emotions: List of dicts from classify_emotions.

    Returns:
        New Document list with emotion metadata in metadata dict.
    """
    from human_condition.corpus.document import Document

    enriched: list = []
    for doc, emotion_data in zip(docs, emotions, strict=False):
        new_metadata = {
            **doc.metadata,
            "dominant_emotion": emotion_data.get("dominant_emotion", "neutral"),
            "emotion_scores": emotion_data.get("emotions", {}),
        }
        enriched.append(
            Document(
                source=doc.source,
                title=doc.title,
                text=doc.text,
                metadata=new_metadata,
            )
        )
    return enriched
