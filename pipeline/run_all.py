"""The Human Condition v2.0 — Full Pipeline Runner

Chains all 6 Prefect flows in sequence with error handling.
Run this single file to execute the complete pipeline:

    python pipeline/run_all.py

Flows in order:
    01 ingest_corpus   → Download and cache raw corpora
    02 preprocess      → Clean, chunk, normalize texts
    03 embed           → Generate sentence embeddings
    04 analyze         → Emotion classification
    05 model_topics    → BERTopic clustering
    06 export          → DuckDB + parquet + HTML charts
"""
from __future__ import annotations

import sys
import time
import importlib.util
from pathlib import Path

PIPELINE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = PIPELINE_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

FLOWS = [
    ("01_ingest", "ingest_corpus", "Download and cache raw corpora"),
    ("02_preprocess", "preprocess_corpus", "Clean, chunk, normalize texts"),
    ("03_embed", "embed_corpus", "Generate sentence embeddings"),
    ("04_analyze", "analyze_emotions", "Emotion classification"),
    ("05_topics", "model_topics", "BERTopic clustering"),
    ("06_export", "export_results", "DuckDB + parquet + HTML charts"),
]


def _load_flow_module(module_name: str):
    """Dynamically load a pipeline module (handles digit-starting names)."""
    flow_path = PIPELINE_DIR / f"{module_name}.py"
    spec = importlib.util.spec_from_file_location(f"pipeline_mod_{module_name}", flow_path)
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f"Cannot find {flow_path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"pipeline_mod_{module_name}"] = mod
    spec.loader.exec_module(mod)
    return mod


def run_flow(module_name: str, flow_name: str, description: str) -> bool:
    """Import and run a single Prefect flow with error handling."""
    print(f"\n{'=' * 70}")
    print(f"  STEP: {module_name} — {description}")
    print(f"{'=' * 70}")

    try:
        module = _load_flow_module(module_name)
        flow_fn = getattr(module, flow_name)
        result = flow_fn()
        print(f"  OK: {module_name} completed with result: {result}")
        return True
    except FileNotFoundError as e:
        print(f"  FAIL: {module_name} — missing prerequisite file: {e}")
        return False
    except ImportError as e:
        print(f"  FAIL: {module_name} — import error: {e}")
        return False
    except Exception as e:
        print(f"  FAIL: {module_name} — {type(e).__name__}: {e}")
        return False


def main() -> int:
    """Run all pipeline flows in sequence. Returns 0 on success, 1 on failure."""
    start = time.monotonic()
    print("The Human Condition v2.0 — Full Pipeline")
    print(f"Running {len(FLOWS)} flows...")

    completed = 0
    failed = 0

    for module_name, flow_name, description in FLOWS:
        ok = run_flow(module_name, flow_name, description)
        if ok:
            completed += 1
        else:
            failed += 1
            print(f"\n  Pipeline halted at {module_name}.")
            print(f"  Completed: {completed}/{len(FLOWS)}")
            return 1

    elapsed = time.monotonic() - start
    print(f"\n{'=' * 70}")
    print(f"  ALL {len(FLOWS)} FLOWS COMPLETED in {elapsed:.1f}s")
    print(f"{'=' * 70}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
