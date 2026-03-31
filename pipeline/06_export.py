"""Flow: export_results
Purpose: Export pipeline artifacts to DuckDB warehouse + parquet + HTML charts
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from prefect import flow, task

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@task(name="load_all_artifacts")
def _load_artifacts() -> dict:
    """Load embeddings, topics, emotions, and corpus for export."""
    from human_condition.corpus.builder import CorpusBuilder
    from human_condition.viz.charts import (
        compression_curve,
        emotion_heatmap,
        emotion_timeline_chart,
        radar_chart,
        similarity_matrix,
        source_distribution,
        summary_stats,
        topic_barchart,
        topic_scatter,
        word_cloud_data,
    )
    from human_condition.viz.theme import BG_PRIMARY, BG_CARD, TEXT_PRIMARY, ACCENT_GOLD

    result: dict = {
        "corpus": [],
        "emotions": [],
        "topics": [],
        "embeddings": None,
        "charts": {},
    }

    # Load corpus
    corp_path = DATA_DIR / "raw" / "corpus.jsonl"
    if corp_path.exists():
        with open(corp_path, encoding="utf-8") as f:
            for line in f:
                result["corpus"].append(json.loads(line))

    # Load emotions
    emo_path = DATA_DIR / "features" / "emotions.jsonl"
    if emo_path.exists():
        with open(emo_path, encoding="utf-8") as f:
            for line in f:
                result["emotions"].append(json.loads(line))

    # Load topics
    topic_path = DATA_DIR / "features" / "topic_info.jsonl"
    if topic_path.exists():
        with open(topic_path, encoding="utf-8") as f:
            for line in f:
                result["topics"].append(json.loads(line))

    # Load embeddings
    emb_path = DATA_DIR / "features" / "embeddings.npy"
    if emb_path.exists():
        result["embeddings"] = np.load(str(emb_path))

    # Generate emotion data for charts
    if result["emotions"]:
        fig = emotion_heatmap(result["emotions"])
        result["charts"]["emotion_heatmap.html"] = fig

        fig = emotion_timeline_chart(result["emotions"])
        result["charts"]["emotion_timeline.html"] = fig

        # Radar chart: emotion profiles by source
        source_profiles: dict[str, dict[str, float]] = {}
        for e in result["emotions"]:
            src = e.get("source", "other")
            if src not in source_profiles:
                source_profiles[src] = {}
            scores = e.get("emotion_scores", {})
            for k, v in scores.items():
                source_profiles[src][k] = source_profiles[src].get(k, []) + [v]
        avg_profiles = {}
        for src, vals in source_profiles.items():
            avg_profiles[src] = {k: float(np.mean(v)) for k, v in vals.items()}
        fig = radar_chart(avg_profiles)
        result["charts"]["emotion_radar.html"] = fig

    # Generate topic charts
    if result["topics"]:
        fig = topic_barchart(result["topics"])
        result["charts"]["topic_barchart.html"] = fig

        if result["embeddings"] is not None:
            from sklearn.decomposition import PCA

            emb_2d = PCA(n_components=2).fit_transform(result["embeddings"][:500])
            topic_labels = list(range(min(len(result["topics"]), 500)))
            fig = topic_scatter(emb_2d, topic_labels)
            result["charts"]["topic_scatter.html"] = fig

    # Source distribution
    if result["corpus"]:
        fig = source_distribution(result["corpus"])
        result["charts"]["source_distribution.html"] = fig

    # Similarity matrix
    if result["corpus"] and result["embeddings"] is not None:
        sources = sorted({d.get("source", "unknown") for d in result["corpus"]})
        source_embs = {}
        for d, emb in zip(result["corpus"], result["embeddings"]):
            src = d.get("source", "unknown")
            source_embs.setdefault(src, []).append(emb)
        source_means = {s: np.mean(embs, axis=0) for s, embs in source_embs.items()}
        source_list = sorted(source_means.keys())
        n = len(source_list)
        sim = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                sim[i, j] = float(
                    np.dot(
                        source_means[source_list[i]],
                        source_means[source_list[j]],
                    )
                )
        fig = similarity_matrix(sim, source_list)
        result["charts"]["similarity_matrix.html"] = fig

    # Compression curve
    if result["embeddings"] is not None and len(result["embeddings"]) > 10:
        from human_condition.nlp.turboquant_demo import TurboQuantDemo

        tq = TurboQuantDemo()
        levels = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 8.0, 32.0]
        results = tq.benchmark_compression_levels(
            result["embeddings"][:500], levels
        )
        benchmark_data = [
            {
                "compressed_bits_per_channel": r.compressed_bits_per_channel,
                "recall_at_10": r.recall_at_10,
                "inner_product_mse": r.inner_product_mse,
                "compression_ratio": r.compression_ratio,
            }
            for r in results
        ]
        fig = compression_curve(benchmark_data)
        result["charts"]["compression_curve.html"] = fig

    # Summary stats
    if result["emotions"]:
        stats = []
        for e in result["emotions"]:
            stats.append(
                {
                    "source": e.get("source", "unknown"),
                    "word_count": len(e.get("text", "").split()),
                    "dominant_emotion_score": next(
                        iter(e.get("emotion_scores", {}).values()), 0
                    ),
                    "topic": "unknown",
                    "text": e.get("text", ""),
                }
            )
        fig = summary_stats(stats)
        result["charts"]["summary_stats.html"] = fig

    # Word cloud
    if result["corpus"]:
        word_counts: dict[str, int] = {}
        for d in result["corpus"]:
            for w in d.get("text", "").lower().split():
                word_counts[w] = word_counts.get(w, 0) + 1
        vocab = [
            {"word": w, "count": c}
            for w, c in sorted(word_counts.items(), key=lambda x: -x[1])[:50]
        ]
        fig = word_cloud_data(vocab)
        result["charts"]["word_cloud.html"] = fig

    return result


@task(name="save_to_parquet")
def _save_parquet(artifacts: dict) -> None:
    """Save corpus and emotions to parquet files."""
    import pandas as pd

    out_dir = DATA_DIR / "warehouse"
    out_dir.mkdir(parents=True, exist_ok=True)

    if artifacts["corpus"]:
        df = pd.DataFrame(artifacts["corpus"])
        df.to_parquet(str(out_dir / "corpus.parquet"), index=False)

    if artifacts["emotions"]:
        docs = []
        for e in artifacts["emotions"]:
            flat = {
                "source": e.get("source", "unknown"),
                "title": e.get("title", ""),
                "text": e.get("text", ""),
                "dominant_emotion": e.get("dominant_emotion", "neutral"),
            }
            for k, v in e.get("emotion_scores", {}).items():
                flat[f"emotion_{k}"] = v
            docs.append(flat)
        df = pd.DataFrame(docs)
        df.to_parquet(str(out_dir / "emotions.parquet"), index=False)

    if artifacts["topics"]:
        df = pd.DataFrame(artifacts["topics"])
        df.to_parquet(str(out_dir / "topics.parquet"), index=False)

    print("Saved parquet files to data/warehouse/")


@task(name="save_to_duckdb")
def _save_duckdb(artifacts: dict) -> str:
    """Save all artifacts to DuckDB warehouse."""
    import duckdb
    import pandas as pd

    db_path = DATA_DIR / "warehouse.duckdb"
    con = duckdb.connect(str(db_path))

    con.execute("CREATE OR REPLACE TABLE corpus (source STRING, title STRING, text STRING, metadata JSON)")
    for doc in artifacts["corpus"]:
        meta = json.dumps(doc.get("metadata", {}), ensure_ascii=False)
        con.execute(
            "INSERT INTO corpus VALUES (?, ?, ?, ?)",
            [doc.get("source", ""), doc.get("title", ""), doc.get("text", ""), meta],
        )

    con.execute("CREATE OR REPLACE TABLE emotions (source STRING, title STRING, text STRING, dominant_emotion STRING)")
    for e in artifacts["emotions"]:
        scores = json.dumps(e.get("emotion_scores", {}))
        con.execute(
            "INSERT INTO emotions VALUES (?, ?, ?, ?)",
            [e.get("source", ""), e.get("title", ""), e.get("text", ""), e.get("dominant_emotion", "neutral")],
        )

    if artifacts["topics"]:
        topic_cols = list(artifacts["topics"][0].keys())
        create_cols = ", ".join(f"{c} STRING" for c in topic_cols)
        placeholders = ", ".join("?" for _ in topic_cols)
        con.execute(f"CREATE OR REPLACE TABLE topics ({create_cols})")
        for row in artifacts["topics"]:
            vals = [str(row.get(c, "")) for c in topic_cols]
            con.execute(f"INSERT INTO topics VALUES ({placeholders})", vals)

    con.close()
    print(f"Saved warehouse to {db_path}")
    return str(db_path)


@task(name="save_charts_as_html")
def _save_charts(artifacts: dict) -> int:
    """Save all generated charts as standalone HTML files."""
    out_dir = DATA_DIR / "charts"
    out_dir.mkdir(parents=True, exist_ok=True)

    count = 0
    for filename, fig in artifacts["charts"].items():
        path = out_dir / filename
        fig.write_html(str(path))
        count += 1
        print(f"Saved chart: {path}")

    # Save summary metadata
    summary = {
        "corpus_count": len(artifacts["corpus"]),
        "emotion_count": len(artifacts["emotions"]),
        "topic_count": len(artifacts["topics"]),
        "chart_count": count,
    }
    summary_path = DATA_DIR / "results" / "summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Saved {count} charts to {out_dir}")
    return count


@flow(name="export_results")
def export_results() -> dict:
    """Export all pipeline results to DuckDB, parquet, and HTML charts."""
    artifacts = _load_artifacts()
    _save_parquet(artifacts)
    db_path = _save_duckdb(artifacts)
    chart_count = _save_charts(artifacts)
    return db_path, chart_count


if __name__ == "__main__":
    export_results()
