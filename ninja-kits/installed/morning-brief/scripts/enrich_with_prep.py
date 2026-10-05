#!/usr/bin/env python3
"""
enrich_with_prep.py — adds prep_status to each event in the calendar JSON.

Reads the JSON output of fetch_calendar.py from stdin, cross-references each
event against `/agents/executive/log/meetings/` (and `/decisions/` for board
decks etc.), and adds a `prep_status` field. Writes enriched JSON to stdout.

Usage:
  python fetch_calendar.py --lookahead 21 | python enrich_with_prep.py

prep_status values:
  "ready"          — prep file exists, updated within 7 days of event
  "stale"          — prep file exists but >7 days old; event is <14 days away
  "in_progress"    — prep file exists but is empty / very short
  "missing"        — no prep file found and event is high-stakes
  "not_needed"     — event is recurring, low-stakes, or internal routine
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Override via env var if log lives elsewhere (e.g. inside a workspace dir).
LOG_ROOT = Path(os.environ.get(
    "EXECUTIVE_LOG_ROOT",
    "agents/executive/log"
))
MEETINGS_DIR = LOG_ROOT / "meetings"
DECISIONS_DIR = LOG_ROOT / "decisions"

# A prep file shorter than this is considered "in progress", not "ready".
MIN_READY_BYTES = 400


def find_prep_file(event: dict) -> Path | None:
    """Search meetings/ and decisions/ for a file that matches this event."""
    if not MEETINGS_DIR.exists() and not DECISIONS_DIR.exists():
        return None

    keywords = [k.lower() for k in event.get("prep_keywords", [])]
    # Also try attendee names
    for a in event.get("attendees", []):
        name = (a.get("name") or "").lower()
        if name:
            keywords.extend(name.split())

    if not keywords:
        return None

    candidates: list[Path] = []
    for directory in (MEETINGS_DIR, DECISIONS_DIR):
        if not directory.exists():
            continue
        for path in directory.glob("*.md"):
            name_lower = path.name.lower()
            if any(k in name_lower for k in keywords):
                candidates.append(path)

    if not candidates:
        return None
    # Return the most recently modified candidate
    return max(candidates, key=lambda p: p.stat().st_mtime)


def days_until(iso_dt: str) -> int:
    try:
        dt = datetime.fromisoformat(iso_dt.replace("Z", "+00:00"))
    except ValueError:
        # Date-only events (all-day)
        dt = datetime.fromisoformat(iso_dt + "T00:00:00+00:00")
    return (dt - datetime.now(timezone.utc)).days


def days_since_modified(path: Path) -> int:
    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    return (datetime.now(timezone.utc) - mtime).days


def classify_prep(event: dict) -> dict:
    days_to_event = days_until(event["start"])

    # Low-stakes routine — no prep file needed
    if not event.get("is_high_stakes") and event.get("is_recurring"):
        return {"status": "not_needed", "file": None, "age_days": None}
    if not event.get("is_high_stakes") and not event.get("is_external"):
        return {"status": "not_needed", "file": None, "age_days": None}

    prep_file = find_prep_file(event)
    if not prep_file:
        return {"status": "missing", "file": None, "age_days": None}

    size = prep_file.stat().st_size
    age = days_since_modified(prep_file)

    if size < MIN_READY_BYTES:
        return {"status": "in_progress", "file": str(prep_file), "age_days": age}
    if age > 7 and days_to_event <= 14:
        return {"status": "stale", "file": str(prep_file), "age_days": age}
    return {"status": "ready", "file": str(prep_file), "age_days": age}


def main() -> None:
    try:
        events = json.load(sys.stdin)
    except json.JSONDecodeError as e:
        sys.stderr.write(f"Invalid JSON input: {e}\n")
        sys.exit(1)

    enriched: list[dict] = []
    for event in events:
        prep = classify_prep(event)
        event["prep_status"] = prep["status"]
        event["prep_file"] = prep["file"]
        event["prep_age_days"] = prep["age_days"]
        event["days_until"] = days_until(event["start"])
        enriched.append(event)

    json.dump(enriched, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
