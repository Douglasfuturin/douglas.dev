#!/usr/bin/env python3
"""
scan_tripwires.py — find decision tripwires firing in the next N days.

Reads /agents/executive/log/decisions/*.md (the output of /decision-research)
and surfaces ones whose tripwire check date falls in [today, today + window].

Each decision memo is expected to have either:

  - Frontmatter with a tripwire_date field:

    ---
    decision: Should we keep running ads on channel X?
    tripwire_date: 2026-05-20
    tripwire_metric: weekly_pipeline_from_channel
    tripwire_threshold: 25000
    tripwire_action: kill if below
    status: committed   # committed | reviewed | killed | held
    ---

  - Or a "## Tripwires & kill criteria" section in the body (parsed best-effort
    for dates in YYYY-MM-DD or "by <month> <day>" format).

Frontmatter is preferred — it makes scanning fast and exact.

Env vars:
  DECISIONS_ROOT       Default: agents/executive/log/decisions
  TRIPWIRE_WINDOW_DAYS Default: 7

Usage:
  python scan_tripwires.py
  python scan_tripwires.py --window 14
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any


def decisions_root() -> Path:
    return Path(os.environ.get("DECISIONS_ROOT", "agents/executive/log/decisions"))


FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
DATE_IN_BODY = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")


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


def extract_body_tripwire_date(text: str) -> date | None:
    """Look in the Tripwires section for the first YYYY-MM-DD."""
    lower = text.lower()
    if "tripwire" not in lower and "kill criteria" not in lower:
        return None
    # Find the section heading and take a window after it
    idx = lower.find("tripwire")
    if idx < 0:
        idx = lower.find("kill criteria")
    section = text[idx : idx + 1500]
    m = DATE_IN_BODY.search(section)
    if not m:
        return None
    try:
        return date.fromisoformat(m.group(1))
    except ValueError:
        return None


def to_date(v: str | None) -> date | None:
    if not v:
        return None
    try:
        return date.fromisoformat(v.strip())
    except ValueError:
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--window", type=int,
                        default=int(os.environ.get("TRIPWIRE_WINDOW_DAYS", "7")),
                        help="Days ahead to scan for firing tripwires")
    args = parser.parse_args()

    root = decisions_root()
    if not root.exists():
        json.dump({"tripwires": [], "meta": {"decisions_root_missing": str(root)}},
                  sys.stdout, indent=2)
        sys.stdout.write("\n")
        return

    today = date.today()
    end = today + timedelta(days=args.window)
    firing: list[dict[str, Any]] = []

    for path in sorted(root.glob("*.md")):
        text = path.read_text()
        fm = parse_frontmatter(text)
        status = (fm.get("status") or "committed").lower()
        if status in ("killed", "held"):
            continue  # already resolved
        tripwire_date = to_date(fm.get("tripwire_date")) or extract_body_tripwire_date(text)
        if not tripwire_date:
            continue
        if tripwire_date < today or tripwire_date > end:
            continue
        firing.append({
            "decision": fm.get("decision") or path.stem,
            "path": str(path),
            "tripwire_date": tripwire_date.isoformat(),
            "tripwire_metric": fm.get("tripwire_metric"),
            "tripwire_threshold": fm.get("tripwire_threshold"),
            "tripwire_action": fm.get("tripwire_action"),
            "status": status,
            "days_until_check": (tripwire_date - today).days,
        })

    firing.sort(key=lambda t: t["days_until_check"])
    json.dump({"tripwires": firing, "count": len(firing), "window_days": args.window},
              sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
