#!/usr/bin/env python3
"""
scan_goals.py — read /agents/executive/goals/ and surface freshness / pace.

Each goal is a markdown file with simple YAML-ish frontmatter. Schema (see
goal-tracker/SKILL.md for the authoritative spec):

  ---
  name: Hit $50k MRR
  target_value: 50000
  current_value: 38000
  unit: usd
  target_date: 2026-06-30
  status: active            # active | paused | closed  (lifecycle only)
  final_grade: null         # hit | slipped | missed | pivoted — set only when closed
  stated_in_qbr: Q2-2026
  linked_kpi: mrr           # optional — kpi_config.json field; null if unlinked
  last_update: 2026-05-04
  cadence_days: 14          # expected refresh interval
  ---

Only `status: active` goals are processed — `paused` and `closed` are skipped.
This script is forgiving — missing fields are treated as unknown, not errors.

Returns each active goal with computed status:
  pace        "on" | "slipping" | "off" | "unknown"
  freshness   "fresh" | "stale" | "very_stale"
  flag        the one thing the morning brief should ask about — one of:
              "milestone_soon_no_progress" | "off_pace_no_touch" | "stale_30d"
              | "near_complete" (>=85% with time left — nudge to close on hit)
              | "data_drift" (current >= target but still active — should be closed)
              | null
  days_to_target | null
  days_since_update | null
  linked_kpi, stated_in_qbr — passed through for downstream skills

Env vars:
  GOALS_ROOT     Default: agents/executive/goals
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any


def goals_root() -> Path:
    return Path(os.environ.get("GOALS_ROOT", "agents/executive/goals"))


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict[str, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fm: dict[str, str] = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip()] = v.strip()
    return fm


def days_between(d1: date, d2: date) -> int:
    return (d2 - d1).days


def to_float(v: str | None) -> float | None:
    if v is None:
        return None
    try:
        return float(v.replace(",", "").replace("$", "").strip())
    except (ValueError, AttributeError):
        return None


def to_date(v: str | None) -> date | None:
    if not v:
        return None
    try:
        return date.fromisoformat(v.strip())
    except ValueError:
        return None


def classify_goal(fm: dict) -> dict[str, Any]:
    today = date.today()
    name = fm.get("name", "(unnamed)")
    status = fm.get("status", "active").lower()
    target = to_float(fm.get("target_value"))
    current = to_float(fm.get("current_value"))
    target_date = to_date(fm.get("target_date"))
    last_update = to_date(fm.get("last_update"))
    cadence = int(fm.get("cadence_days", "14")) if fm.get("cadence_days", "").isdigit() else 14

    days_to_target = days_between(today, target_date) if target_date else None
    days_since_update = days_between(last_update, today) if last_update else None

    # Pace
    pace = "unknown"
    if target and current and target_date and last_update:
        elapsed_total = days_between(last_update, target_date) + max(days_since_update or 0, 0)
        # Simple: where should we be by now (linear)?
        if target_date and target > 0:
            # We assume the goal started when first measured; rough but useful.
            # If you want precision, add a start_date field.
            pct_complete = current / target if target else 0
            time_window = max((target_date - today).days + max(days_since_update or 0, 1), 1)
            # Just classify by percent vs days remaining
            if pct_complete >= 1:
                pace = "on"
            elif (days_to_target or 0) <= 0:
                pace = "off"
            elif pct_complete >= 0.85:
                pace = "on"
            elif pct_complete >= 0.5:
                pace = "slipping"
            else:
                pace = "off"

    # Freshness
    if days_since_update is None:
        freshness = "unknown"
    elif days_since_update <= cadence:
        freshness = "fresh"
    elif days_since_update <= cadence * 2:
        freshness = "stale"
    else:
        freshness = "very_stale"

    # Percent complete — used for near_complete / data_drift flags
    pct_complete = (current / target) if (target and current is not None and target > 0) else None

    # Flag (the one thing morning-brief should ask about). Priority order:
    # data_drift first (a correctness issue), then the surfacing flags.
    flag = None
    if status == "active":
        if pct_complete is not None and pct_complete >= 1.0:
            # Goal is mathematically hit but still marked active — should be closed.
            flag = "data_drift"
        elif (
            pct_complete is not None and pct_complete >= 0.85
            and days_to_target is not None and days_to_target > 0
        ):
            # About to hit — nudge [FOUNDER NAME] to close it cleanly on `hit`.
            flag = "near_complete"
        elif days_to_target is not None and 0 < days_to_target <= 14 and (days_since_update or 0) > 7:
            flag = "milestone_soon_no_progress"
        elif pace == "off" and (days_since_update or 0) > cadence:
            flag = "off_pace_no_touch"
        elif (days_since_update or 0) > 30:
            flag = "stale_30d"

    return {
        "name": name,
        "status": status,
        "current": current,
        "target": target,
        "pct_complete": round(pct_complete, 3) if pct_complete is not None else None,
        "target_date": target_date.isoformat() if target_date else None,
        "last_update": last_update.isoformat() if last_update else None,
        "days_to_target": days_to_target,
        "days_since_update": days_since_update,
        "pace": pace,
        "freshness": freshness,
        "flag": flag,
        "linked_kpi": fm.get("linked_kpi") or None,
        "stated_in_qbr": fm.get("stated_in_qbr") or None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only-flagged", action="store_true",
                        help="Return only goals with a flag set (what brief surfaces)")
    args = parser.parse_args()

    root = goals_root()
    if not root.exists():
        json.dump({"goals": [], "meta": {"goals_root_missing": str(root)}}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    goals = []
    for path in sorted(root.glob("*.md")):
        try:
            fm = parse_frontmatter(path.read_text())
        except Exception as e:
            goals.append({"name": path.stem, "_error": str(e)})
            continue
        if not fm:
            continue
        classified = classify_goal(fm)
        classified["path"] = str(path)
        if classified["status"] != "active":
            continue
        if args.only_flagged and not classified["flag"]:
            continue
        goals.append(classified)

    json.dump({"goals": goals, "count": len(goals)}, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
