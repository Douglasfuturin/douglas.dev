#!/usr/bin/env python3
"""
aggregate_snapshots.py — read today's daily snapshots from every brain and
return a single merged JSON blob the morning-brief skill can consume directly.

The 5am prefetch routine populates `/shared-context/daily-snapshots/YYYY-MM-DD/`
with files like cash.json, revenue.json, ads.json, etc. This script:
  1. Picks today's snapshot directory (or --date YYYY-MM-DD)
  2. Reads every *.json file in it
  3. Returns {brain_name: contents, "meta": {...}}
  4. Computes which expected snapshots are MISSING (so the brief can call it out)

Also supports --compare-to YESTERDAY|N_DAYS_AGO to surface deltas inline.

Env vars:
  SHARED_CONTEXT_ROOT      Default: "shared-context"
  EXPECTED_SNAPSHOTS       Comma-separated list of expected snapshot file names
                           Default: cash.json,revenue.json,ads.json,creative.json,
                                    pipeline.json,call-outcomes.json,inbox.json,
                                    churn-signals.json,team-activity.json,
                                    creative-queue.json

Usage:
  python aggregate_snapshots.py                       # today's snapshots
  python aggregate_snapshots.py --date 2026-05-14
  python aggregate_snapshots.py --compare-to yesterday
  python aggregate_snapshots.py --compare-to 7        # compare to 7 days ago
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

DEFAULT_EXPECTED = [
    "cash.json", "revenue.json",
    "ads.json", "creative.json", "creative-queue.json",
    "pipeline.json", "call-outcomes.json",
    "inbox.json", "churn-signals.json",
    "team-activity.json",
]


def snapshot_root() -> Path:
    return Path(os.environ.get("SHARED_CONTEXT_ROOT", "shared-context")) / "daily-snapshots"


def expected_files() -> list[str]:
    raw = os.environ.get("EXPECTED_SNAPSHOTS", "")
    if raw.strip():
        return [f.strip() for f in raw.split(",") if f.strip()]
    return DEFAULT_EXPECTED


def load_snapshot_dir(d: date) -> tuple[dict[str, Any], list[str]]:
    """Return (data, missing_files) for the given date."""
    dir_path = snapshot_root() / d.isoformat()
    data: dict[str, Any] = {}
    found: set[str] = set()

    if dir_path.exists():
        for f in sorted(dir_path.glob("*.json")):
            try:
                data[f.stem] = json.loads(f.read_text())
                found.add(f.name)
            except json.JSONDecodeError as e:
                data[f.stem] = {"_error": f"malformed JSON: {e}"}
                found.add(f.name)

    missing = [f for f in expected_files() if f not in found]
    return data, missing


def resolve_compare_target(spec: str, today: date) -> date:
    if spec.lower() == "yesterday":
        return today - timedelta(days=1)
    try:
        return today - timedelta(days=int(spec))
    except ValueError:
        # Maybe it's already a date string
        return date.fromisoformat(spec)


def compute_deltas(today_data: dict, prior_data: dict) -> dict:
    """For matching brain files, surface simple numeric deltas at the top level.

    Only handles scalar numeric fields. Nested structures are skipped — the
    skill itself synthesizes those.
    """
    deltas: dict[str, dict] = {}
    for brain, today_blob in today_data.items():
        if not isinstance(today_blob, dict):
            continue
        prior_blob = prior_data.get(brain)
        if not isinstance(prior_blob, dict):
            continue
        brain_deltas = {}
        for k, v in today_blob.items():
            if not isinstance(v, (int, float)):
                continue
            pv = prior_blob.get(k)
            if not isinstance(pv, (int, float)):
                continue
            change = v - pv
            pct = (change / pv * 100) if pv != 0 else None
            brain_deltas[k] = {
                "today": v, "prior": pv, "change": change, "pct_change": round(pct, 2) if pct is not None else None
            }
        if brain_deltas:
            deltas[brain] = brain_deltas
    return deltas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--date", default=date.today().isoformat(),
                        help="Date to read (default: today, ISO format)")
    parser.add_argument("--compare-to", dest="compare_to", default=None,
                        help="'yesterday' | N (days ago) | YYYY-MM-DD")
    args = parser.parse_args()

    target = date.fromisoformat(args.date)
    data, missing = load_snapshot_dir(target)

    output: dict[str, Any] = {
        "date": target.isoformat(),
        "brains": data,
        "meta": {
            "missing_snapshots": missing,
            "complete": not missing,
        },
    }

    if args.compare_to:
        prior_date = resolve_compare_target(args.compare_to, target)
        prior_data, prior_missing = load_snapshot_dir(prior_date)
        output["compare_to"] = {
            "date": prior_date.isoformat(),
            "missing_snapshots": prior_missing,
        }
        output["deltas"] = compute_deltas(data, prior_data)

    json.dump(output, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
