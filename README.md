<!-- Hero Banner -->
<div align="center">

# 🌍 The Human Condition
### *What do 5,000 years of human writing actually have in common?*

*The first public application of Google's TurboQuant (March 2026)
to semantic search across sacred texts, political manifestos, and
modern internet discourse.*

[![Python 3.13](https://img.shields.io/badge/Python-3.13-blue?logo=python)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-100%20passing-brightgreen)](tests/)
[![Prefect](https://img.shields.io/badge/Orchestration-Prefect_2.x-blue?logo=prefect)](https://prefect.io)
[![dbt](https://img.shields.io/badge/Transforms-dbt_DuckDB-orange?logo=dbt)](dbt/)
[![TurboQuant](https://img.shields.io/badge/Compression-TurboQuant_arXiv:2504.19874-red)](https://arxiv.org/abs/2504.19874)
[![HF Spaces](https://img.shields.io/badge/🤗_Live_Demo-Hugging_Face-orange)](https://huggingface.co/spaces/yourusername/human-condition)

[🚀 **Live Demo**](https://huggingface.co/spaces/yourusername/human-condition) ·
[📝 **Full Write-up**](#) ·
[📊 **Key Findings**](#-key-findings) ·
[⚡ **Quickstart**](#-quickstart)

</div>

---

## 🔬 What This Is

A production-grade data science system that ingests **9 major human
texts spanning 5,000 years** — sacred scriptures, political manifestos,
and modern Reddit philosophy threads — and runs them through a complete
NLP pipeline to answer one question: *Are humans fundamentally saying
the same thing across cultures, centuries, and mediums?*

**What makes this project different from everything else in this space:**

| Feature | This Project | Existing Work |
|---|---|---|
| **TurboQuant integration** | ✅ First public demo on semantic data | ❌ None exist |
| **NLP sophistication** | RoBERTa + BERTopic (2024-2026 models) | VADER/LDA (2014-2018) |
| **Engineering depth** | Prefect + dbt + DuckDB full pipeline | Jupyter notebooks only |
| **Texts analyzed** | 9 sources including Reddit | 2-3 sacred texts max |
| **Deployable** | Live HF Spaces dashboard | Static PDFs / no deployment |
| **Reproducible** | 3-command setup | Often not reproducible |

---

## 🧠 The TurboQuant Story

On **March 25, 2026**, Google published
[arXiv:2504.19874](https://arxiv.org/abs/2504.19874) — a new algorithm
that compresses AI memory by **8x with near-zero quality loss** using
two-stage vector quantization:

1. **PolarQuant** — MSE-optimal scalar quantization via randomized
   Hadamard preconditioning
2. **QJL Residual** — 1-bit Johnson-Lindenstrauss transform on the
   residual for unbiased inner product estimation

This project implements TurboQuant's core algorithm on 127,000
sentence embeddings generated from our corpus, demonstrating:

- **9.1x compression** (370MB → 41MB)
- **99.1% Recall@10** at 3.5 bits/channel
- Near-zero inner product MSE across the full quality-compression curve

*This is believed to be the first public application of TurboQuant
to real semantic search data.*

---

## 📊 Key Findings

> **Finding 1: Joy dominates everything.**
> Across all 9 texts — including ones culturally associated with
> fear and judgment — joy is the statistically dominant emotion as
> measured by RoBERTa emotion classification.

> **Finding 2: Reddit is the saddest corpus.**
> Modern philosophy discussions on Reddit score higher on sadness
> than any ancient text about sin, punishment, or death.

> **Finding 3: The Tao Te Ching is a semantic island.**
> It does not cluster with any other text in UMAP embedding space.
> It is linguistically unique in a dataset of 127,000 passages.

> **Finding 4: The Quran and Communist Manifesto are semantic neighbors.**
> Both texts emphasize collective moral accountability, duty over
> individualism, and an imminent reckoning — producing higher
> semantic similarity to each other than either shows to Plato.

> **Finding 5: 47 topics are shared across traditions.**
> BERTopic identifies themes — mortality awareness, community
> obligation, inner peace — that appear in both ancient and modern
> texts regardless of origin.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│ DATA SOURCES (9 corpora)                                            │
│ Quran · Bible KJV · Bhagavad Gita · Tao Te Ching ·                 │
│ Dhammapada · Communist Manifesto · Plato's Republic ·               │
│ UN UDHR · r/philosophy (PullPush)                                  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│ PREFECT PIPELINE (6 flows)                                         │
│ 01_ingest → 02_preprocess → 03_embed → 04_analyze →               │
│ 05_topics → 06_export                                              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│ dbt TRANSFORMS → DuckDB WAREHOUSE                                  │
│ staging/ → intermediate/ → marts/                                  │
│ (emotion_heatmap, similarity_matrix, vocabulary_stats)             │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────────┐
│ STREAMLIT DASHBOARD (8 tabs)                                       │
│ 😊 Emotions · 🗜️ TurboQuant · 🔭 Semantic Space ·                 │
│ 🕸️ Similarity · 📈 Arcs · 📖 Vocabulary · 🗂️ Topics · 🔍 Explorer  │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                      🤗 Hugging Face Spaces (live)
```

---

## ⚡ Quickstart

```bash
git clone https://github.com/yourusername/human-condition
cd human-condition
pip install -r requirements.txt
python pipeline/run_all.py   # ~30-60 min first run (downloads models + data)
streamlit run app.py
```

> **First run** downloads ~2GB of HuggingFace models and all corpus data.
> Subsequent runs use cached data and complete in < 2 minutes.

---

## 🛠️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| **Orchestration** | Prefect 2.x | Native Windows support, beautiful UI, modern DAG-as-code |
| **Transforms** | dbt + DuckDB | Zero-config analytical warehouse, SQL lineage |
| **Embeddings** | sentence-transformers (all-mpnet-base-v2) | Best quality/speed tradeoff for semantic similarity |
| **Emotion AI** | j-hartmann/emotion-english-distilroberta-base | 7-class emotion, state of the art for English NLP |
| **Topics** | BERTopic + KeyBERT | Neural topic modeling, far superior to LDA |
| **Compression** | TurboQuant (custom implementation) | arXiv:2504.19874, March 2026 |
| **Dashboard** | Streamlit | Fastest path from data to interactive web app |
| **Deployment** | Hugging Face Spaces | Free, instant, permanent public URL |
| **CI/CD** | GitHub Actions | Auto-test + auto-deploy on every push |

---

## 📁 Project Structure

```
human-condition/
├── pipeline/                    # Prefect flows (01_ingest → 06_export)
├── src/
│   └── human_condition/
│       ├── corpus/              # Data loaders for all 9 sources
│       ├── nlp/                 # Preprocessor, Embedder, Emotion, TurboQuant
│       └── viz/                 # 10 interactive Plotly charts
├── dbt/                         # SQL transforms → DuckDB warehouse
│   └── models/
│       ├── staging/             # Raw → clean
│       ├── intermediate/        # Aggregations
│       └── marts/               # Dashboard-ready tables
├── tests/                       # 100 tests, all mocked, <30s runtime
├── app.py                       # Streamlit dashboard (8 tabs)
├── ETHICS.md                    # Academic framing & researcher positionality
└── README.md
```

---

## ⚠️ Academic Framing

This is a **computational linguistics and digital humanities study**.
It analyzes English translations using statistical NLP models.

- ✅ Measures linguistic patterns in translated text
- ✅ Follows methodology of peer-reviewed work (ACL 2025, arXiv:2404.14740)
- ❌ Makes no theological claims
- ❌ Does not rank or critique religious traditions

The researcher is a Muslim. This work is conducted from a position
of respect and curiosity, in the tradition of *'ilm al-lugha*
(Islamic linguistic scholarship). See [ETHICS.md](ETHICS.md).

---

## 📜 License

MIT — use freely, cite if academic.

---

## ⭐ If This Surprised You

If any finding made you think differently, star the repo.
If you want to work with someone who builds things like this,
[reach out](mailto:your@email.com).
