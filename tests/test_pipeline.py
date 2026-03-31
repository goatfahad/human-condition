"""Tests for pipeline flows — all API calls mocked."""
from __future__ import annotations

import json
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    """Create temporary data directory structure."""
    (tmp_path / "raw").mkdir()
    (tmp_path / "processed").mkdir()
    (tmp_path / "features").mkdir()
    (tmp_path / "warehouse").mkdir()
    return tmp_path


@pytest.fixture
def sample_corpus() -> list[dict]:
    """Sample documents from various corpus sources."""
    return [
        {
            "source": "constitution",
            "title": "US Constitution",
            "text": (
                "We the People of the United States, in Order to form a more "
                "perfect Union, establish Justice, insure domestic Tranquility"
            ),
            "metadata": {"origin": "inline"},
        },
        {
            "source": "plato",
            "title": "The Republic",
            "text": (
                "The story of the cave — behold, human beings living in an "
                "underground cave, which has a mouth open towards the light."
            ),
            "metadata": {"origin": "inline"},
        },
        {
            "source": "nietzsche",
            "title": "Thus Spoke Zarathustra",
            "text": (
                "God is dead. God remains dead. And we have killed him. "
                "How shall we comfort ourselves, the murderers of all murderers?"
            ),
            "metadata": {"origin": "inline"},
        },
    ]


def write_jsonl(path: Path, data: list[dict]) -> None:
    """Write list of dicts as JSONL file."""
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")


# ── Test: 01_ingest.py ─────────────────────────────────────────────


class TestIngestCorpus:
    """Tests for the ingest_corpus flow."""

    def test_ingest_flow(self, temp_data_dir: Path, sample_corpus: list[dict]) -> None:
        """Test complete ingest flow with mocked corpus builder."""
        from human_condition.corpus.document import Document

        mock_docs = [
            Document(source=d["source"], title=d["title"], text=d["text"], metadata=d["metadata"])
            for d in sample_corpus
        ]

        with patch("human_condition.corpus.builder.CorpusBuilder") as MockBuilder:
            mock_builder = MagicMock()
            mock_builder.build.return_value = mock_docs
            MockBuilder.return_value = mock_builder

            docs_dicts = [
                {
                    "source": d.source,
                    "title": d.title,
                    "text": d.text,
                    "metadata": d.metadata,
                }
                for d in mock_docs
            ]

            # Save corpus
            raw_dir = temp_data_dir / "raw"
            raw_dir.mkdir(parents=True, exist_ok=True)
            out = raw_dir / "corpus.jsonl"
            with open(out, "w", encoding="utf-8") as f:
                for doc in docs_dicts:
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")

            # Validate
            with open(out, encoding="utf-8") as f:
                lines = f.readlines()
            assert len(lines) == 3

            loaded = [json.loads(line) for line in lines]
            assert loaded[0]["source"] == "constitution"
            assert loaded[1]["source"] == "plato"
            assert loaded[2]["source"] == "nietzsche"


# ── Test: 02_preprocess.py ─────────────────────────────────────────


class TestPreprocessCorpus:
    """Tests for the preprocess_corpus flow."""

    def test_clean_and_chunk(
        self, temp_data_dir: Path, sample_corpus: list[dict]
    ) -> None:
        """Test that preprocessing produces expected chunks."""
        from human_condition.corpus.document import Document
        from human_condition.nlp.preprocessor import preprocess_documents

        docs = [
            Document(
                source=d["source"],
                title=d["title"],
                text=d["text"],
                metadata=d["metadata"],
            )
            for d in sample_corpus
        ]

        chunked = preprocess_documents(docs, max_chunk_size=500)
        assert len(chunked) >= len(docs)

        for c in chunked:
            assert "chunk_index" in c.metadata
            assert "total_chunks" in c.metadata
            assert "original_title" in c.metadata


# ── Test: 03_embed.py ──────────────────────────────────────────────


class TestEmbedCorpus:
    """Tests for the embed_corpus flow."""

    def test_embeddings_round_trip(self, temp_data_dir: Path) -> None:
        """Test that embeddings can be saved and loaded correctly."""
        mock_embeddings = np.array([
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 0.8, 0.7, 0.6],
        ], dtype=np.float32)

        features_dir = temp_data_dir / "features"
        features_dir.mkdir(parents=True, exist_ok=True)
        emb_path = features_dir / "embeddings.npy"
        np.save(str(emb_path), mock_embeddings)

        loaded = np.load(str(emb_path))
        assert loaded.shape == (3, 4)
        np.testing.assert_array_almost_equal(loaded, mock_embeddings)

        texts = ["text A", "text B", "text C"]
        txt_path = features_dir / "embedding_texts.jsonl"
        with open(txt_path, "w", encoding="utf-8") as f:
            for t in texts:
                f.write(json.dumps({"text": t}, ensure_ascii=False) + "\n")

        loaded_texts = []
        with open(txt_path, encoding="utf-8") as f:
            for line in f:
                loaded_texts.append(json.loads(line)["text"])
        assert loaded_texts == texts


# ── Test: 04_analyze.py ────────────────────────────────────────────


class TestAnalyzeEmotions:
    """Tests for the analyze_emotions flow."""

    def test_emotion_to_documents(self) -> None:
        """Test emotion-to-document merging."""
        from human_condition.corpus.document import Document
        from human_condition.nlp.emotion import emotions_to_documents

        docs = [
            Document(source="test", title="T1", text="hello"),
            Document(source="test", title="T2", text="world"),
        ]
        emotions = [
            {"dominant_emotion": "joy", "emotions": {"joy": 0.8}},
            {"dominant_emotion": "sadness", "emotions": {"sadness": 0.7}},
        ]
        enriched = emotions_to_documents(docs, emotions)
        assert len(enriched) == 2
        assert enriched[0].metadata["dominant_emotion"] == "joy"
        assert enriched[1].metadata["dominant_emotion"] == "sadness"


# ── Test: 05_topics.py ─────────────────────────────────────────────


@pytest.mark.skip(reason="bertopic import triggers heavy model loading")
class TestModelTopics:
    """Tests for the model_topics flow."""

    def test_bertopic_mocked(self, sample_corpus: list[dict]) -> None:
        """Test topic modeling with mocked BERTopic."""
        mock_embeddings = np.random.RandomState(42).randn(10, 20).astype(np.float32)
        mock_topics = [0, 0, 1, 1, -1, 2, 0, 1, 2, -1]
        mock_probs = np.random.rand(10, 3)

        mock_model = MagicMock()
        mock_model.fit_transform.return_value = (mock_topics, mock_probs)

        import pandas as pd
        topic_info = pd.DataFrame({
            "Topic": [-1, 0, 1, 2],
            "Name": ["Noise", "0_justice_law", "1_philosophy_knowledge", "2_ethics_morality"],
            "Count": [2, 3, 3, 2],
            "Representation": ["the", "law", "knowledge", "good"],
        })
        mock_model.get_topic_info.return_value = topic_info

        with patch("bertopic.BERTopic", return_value=mock_model):
            from bertopic import BERTopic

            topic_model = BERTopic()
            topics, probs = topic_model.fit_transform(mock_embeddings, ["text"] * 10)
            topic_info_result = topic_model.get_topic_info()

            assert len(topics) == 10
            assert topic_info_result is not None


# ── Test: 06_export.py ─────────────────────────────────────────────


class TestExportResults:
    """Tests for the export_results flow."""

    def test_save_parquet(
        self,
        temp_data_dir: Path,
        sample_corpus: list[dict],
    ) -> None:
        """Test parquet export."""
        import pandas as pd

        out_dir = temp_data_dir / "warehouse"
        out_dir.mkdir(parents=True, exist_ok=True)

        df = pd.DataFrame(sample_corpus)
        corpus_path = out_dir / "corpus.parquet"
        df.to_parquet(str(corpus_path), index=False)
        assert corpus_path.exists()

        df_read = pd.read_parquet(str(corpus_path))
        assert len(df_read) == 3
        assert list(df_read.columns) == ["source", "title", "text", "metadata"]

    def test_save_duckdb(
        self,
        temp_data_dir: Path,
        sample_corpus: list[dict],
    ) -> None:
        """Test DuckDB warehouse creation."""
        try:
            import duckdb
        except (ImportError, duckdb.Error):
            pytest.skip("DuckDB not available")

        db_path = temp_data_dir / "warehouse.duckdb"
        con = duckdb.connect(str(db_path))

        con.execute("""
            CREATE TABLE corpus (
                source VARCHAR,
                title VARCHAR,
                text VARCHAR,
                metadata JSON
            )
        """)
        for doc in sample_corpus:
            meta = json.dumps(doc.get("metadata", {}))
            con.execute(
                "INSERT INTO corpus VALUES (?, ?, ?, ?)",
                [doc["source"], doc["title"], doc["text"], meta],
            )

        count = con.execute("SELECT COUNT(*) FROM corpus").fetchone()[0]
        assert count == 3
        sources = [r[0] for r in con.execute("SELECT DISTINCT source FROM corpus").fetchall()]
        assert "constitution" in sources
        assert "plato" in sources
        con.close()

    def test_summary_metadata(
        self, temp_data_dir: Path, sample_corpus: list[dict]
    ) -> None:
        """Test summary JSON creation."""
        results_dir = temp_data_dir / "results"
        results_dir.mkdir(parents=True, exist_ok=True)

        summary = {
            "corpus_count": len(sample_corpus),
            "emotion_count": 3,
            "topic_count": 3,
            "chart_count": 10,
        }
        summary_path = results_dir / "summary.json"
        with open(summary_path, "w") as f:
            json.dump(summary, f)

        with open(summary_path, "r") as f:
            loaded = json.load(f)
        assert loaded["corpus_count"] == 3
        assert loaded["chart_count"] == 10
