#!/usr/bin/env python3
"""Local diagnostic driver for the four-phase tech-insight agent workflow.

This does not depend on GitHub Actions or a Copilot LLM. Phases 2, 3, and 4
pass empty LLM drafts to trigger deterministic *_or_fallback logic and verify
that the Python toolchain can run locally.

Run from the repository root:
    python Lab-01-Tech-Insights/run_local_pipeline.py
"""

from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path

# Repository root. This script lives under Lab-01-Tech-Insights/.
REPO_ROOT = Path(__file__).resolve().parents[1]
LAB_DIR = REPO_ROOT / "Lab-01-Tech-Insights"
SCRIPTS_DIR = LAB_DIR / "mcp-scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from tech_insight_tools import (  # noqa: E402
    tech_cluster_or_fallback,
    tech_fetch_all_to_disk,
    tech_insight_or_fallback,
    tech_load_articles_from_disk,
    tech_read_source_list,
    tech_render_report_or_fallback,
)

# Workflow defaults, kept in sync with .github/workflows/tech-insight.md.
SOURCE_LIST_PATH = "Lab-01-Tech-Insights/input/api/rss_list.json"
SIGNALS_DIR = "Lab-01-Tech-Insights/output/signals"
OUTPUT_DIR = "Lab-01-Tech-Insights/output"
TIME_WINDOW_HOURS = 24
TOP_K = 12
MAX_ITEMS_PER_SOURCE = 25
TIMEOUT_SECONDS = 15
MAX_CHARS = 200000


def _hr(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70, flush=True)


def _write(rel_path: str, text: str) -> str:
    p = REPO_ROOT / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return str(p.relative_to(REPO_ROOT))


def main() -> int:
    import os

    os.chdir(REPO_ROOT)
    print(f"[cwd] {Path.cwd()}")

    diag: dict[str, object] = {}

    # ---------------- Phase 1: fetch and load raw signals ----------------
    _hr("Phase 1: fetch and load raw signals")

    src = tech_read_source_list(source_list_path=SOURCE_LIST_PATH)
    print(f"[read_source_list] source count: {src.get('count')}")
    diag["source_count"] = src.get("count")

    t0 = time.time()
    fetch = tech_fetch_all_to_disk(
        source_list_path=SOURCE_LIST_PATH,
        signals_dir=SIGNALS_DIR,
        timeout_seconds=TIMEOUT_SECONDS,
        max_chars=MAX_CHARS,
        max_items_per_source=MAX_ITEMS_PER_SOURCE,
    )
    print(
        f"[fetch_all_to_disk] fetched {fetch.get('fetched')} sources, "
        f"{fetch.get('ok')} succeeded, elapsed {time.time() - t0:.1f}s"
    )
    diag["fetch_total"] = fetch.get("fetched")
    diag["fetch_ok"] = fetch.get("ok")

    raw_signals = tech_load_articles_from_disk(
        signals_dir=SIGNALS_DIR,
        source_list_path=SOURCE_LIST_PATH,
        max_items_per_source=MAX_ITEMS_PER_SOURCE,
        time_window_hours=TIME_WINDOW_HOURS,
    )
    items = raw_signals.get("items") or []
    print(f"[load_articles_from_disk] items in {TIME_WINDOW_HOURS}h window: {len(items)}")
    diag["raw_items"] = len(items)

    raw_signals_json = json.dumps(raw_signals, ensure_ascii=False, default=str)
    p1 = _write("Lab-01-Tech-Insights/output/raw_signals.json", raw_signals_json + "\n")
    print(f"[written] {p1}")

    # ---------------- Phase 2: clustering via fallback path ----------------
    _hr("Phase 2: cluster trends and updates (local no-LLM fallback)")
    clusters = tech_cluster_or_fallback(
        raw_signals_json=raw_signals_json,
        clusters_json="",  # Local no-LLM mode triggers fallback.
        top_k=TOP_K,
    )
    hotspots = clusters.get("hotspots") or []
    print(f"[cluster_or_fallback] mode={clusters.get('mode')} hotspots: {len(hotspots)}")
    diag["cluster_mode"] = clusters.get("mode")
    diag["hotspots"] = len(hotspots)

    clusters_json = json.dumps(clusters, ensure_ascii=False, default=str)
    p2 = _write("Lab-01-Tech-Insights/output/clusters/hotspots.json", clusters_json + "\n")
    print(f"[written] {p2}")

    # ---------------- Phase 3: insights via fallback path ----------------
    _hr("Phase 3: generate hotspot insights (local no-LLM fallback)")
    insights = tech_insight_or_fallback(
        clusters_json=clusters_json,
        insights_json="",  # Local no-LLM mode triggers fallback.
    )
    insights_list = insights.get("insights") or []
    print(f"[insight_or_fallback] mode={insights.get('mode')} insights: {len(insights_list)}")
    diag["insight_mode"] = insights.get("mode")
    diag["insights"] = len(insights_list)

    insights_json = json.dumps(insights, ensure_ascii=False, default=str)
    p3 = _write("Lab-01-Tech-Insights/output/insights/insights.json", insights_json + "\n")
    print(f"[written] {p3}")

    # ---------------- Phase 4: report via fallback path ----------------
    _hr("Phase 4: generate Markdown report (local no-LLM fallback)")
    report_md = tech_render_report_or_fallback(
        clusters_json=clusters_json,
        insights_json=insights_json,
        draft_markdown="",  # Local no-LLM mode triggers fallback.
    )
    print(f"[render_report_or_fallback] report length: {len(report_md)} chars")
    diag["report_chars"] = len(report_md)

    p4a = _write("Lab-01-Tech-Insights/output/report.md", report_md)
    p4b = _write("Lab-01-Tech-Insights/frontend/report.md", report_md)
    print(f"[written] {p4a}")
    print(f"[written] {p4b}")

    # ---------------- Diagnostic summary ----------------
    _hr("Diagnostic summary")
    print(json.dumps(diag, ensure_ascii=False, indent=2))

    ok = (
        diag.get("source_count")
        and (diag.get("hotspots") or 0) >= 0
        and (diag.get("report_chars") or 0) > 0
    )
    print(f"\n[result] pipeline execution: {'success' if ok else 'issues found'}")
    return 0 if ok else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        print("\n[FATAL] pipeline execution failed:", flush=True)
        traceback.print_exc()
        raise SystemExit(2)
