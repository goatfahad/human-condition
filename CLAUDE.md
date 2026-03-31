# The Human Condition v2.0 — Project Conventions

## Overview
A data science project analyzing 5,000 years of human writing through NLP (BERTopic, sentence-transformers, emotion analysis) with a TurboQuant KV cache compression demo. Full Airflow pipeline → dbt → DuckDB warehouse → Streamlit dashboard.

## Key Directories
- `src/human_condition/` — core library (corpus, nlp, viz, warehouse)
- `airflow/` — standalone Airflow DAGs (6 DAGs, no containers)
- `dbt/` — dbt transformations on DuckDB
- `tests/` — pytest tests
- `data/` — generated pipeline artifacts (not committed)

## Code Conventions
- **Python 3.13** — use `match/case`, type hints everywhere, `from __future__ import annotations`
- **No stubs, no TODOs, no `pass`** in production code
- **Type hints** on every function signature
- **Docstrings** on every class and public function
- **Frozen dataclasses** where data is immutable
- **Type narrowing** — handle `dict` and `Document` with `isinstance` or `hasattr`
- **Type safety** — use `np.ndarray`, `list[dict]` etc.
- **Imports** — standard library → third-party → local, grouped and sorted

## Architecture Rules
- `@task` functions in Airflow DAGs do all heavy imports (not at module level)
- DAGs are `@once` schedule, `catchup=False`
- DuckDB warehouse is the single source of truth for processed data
- Corpus sources (quran, bible, gutenberg) gracefully fall back on API failure
- Embedder auto-detects device: cuda > mps > cpu

## Testing
- **TDD first** — write test before implementation
- Tests use `pytest`, no network calls (APIs are tested at module level only)
- Tests for charts use `pytest` fixtures, verify `go.Figure` returned
- TurboQuant tests use small synthetic arrays (not full model outputs)

## Dependencies (pyproject.toml)
- numpy, requests, nltk, sentence-transformers, bertopic, transformers, torch
- duckdb, plotly, streamlit, apache-airflow
- pytest, ruff, mypy (dev)

## Skills to Use
- `authoring-dags` for any Airflow DAG work
- `systematic-debugging` before retrying
- `verification-before-completion` before marking tasks done
- `test-driven-development` for all new code
- `finishing-a-development-branch` when ready to commit
