#!/usr/bin/env python3
"""Load the last N session logs for the skill to review.

Outputs a JSON object to stdout:

    {
      "count": 3,
      "sessions": [ <full session log>, ... ]   # newest first
    }

Usage:
    python3 load_history.py                # default: last 5
    python3 load_history.py --last 3
    python3 load_history.py --last 3 --summary   # compact: drop large fields
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parent.parent
SESSIONS_DIR = SKILL_DIR / "logs" / "sessions"


def summarize(session: dict) -> dict:
    """Drop heavy fields so the agent can scan many sessions cheaply."""
    return {
        "session_id": session.get("session_id"),
        "started_at": session.get("started_at"),
        "lookback_window": session.get("lookback_window"),
        "snapshot_summary": session.get("snapshot_summary", {}),
        "what_we_learned": session.get("what_we_learned", ""),
        "recommendations": [
            {
                "id": r.get("id"),
                "framework": r.get("framework"),
                "target_type": r.get("target_type"),
                "target_id": r.get("target_id"),
                "target_name": r.get("target_name"),
                "action": r.get("action"),
                "confidence": r.get("confidence"),
            }
            for r in session.get("recommendations", [])
        ],
        "user_decisions": session.get("user_decisions", []),
        "outcomes": session.get("outcomes", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--last", type=int, default=5, help="How many sessions to load (newest first).")
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Drop heavy fields (full evidence, snapshot_at_recommendation) for fast scanning.",
    )
    args = parser.parse_args()

    if not SESSIONS_DIR.exists():
        print(json.dumps({"count": 0, "sessions": [], "note": "no sessions logged yet"}))
        return 0

    files = sorted(SESSIONS_DIR.glob("*.json"))[-args.last:][::-1]  # newest first
    sessions: list[dict] = []
    for p in files:
        try:
            data = json.loads(p.read_text())
        except Exception as e:  # noqa: BLE001
            print(f"WARN: could not parse {p.name}: {e}", file=sys.stderr)
            continue
        sessions.append(summarize(data) if args.summary else data)

    print(json.dumps({"count": len(sessions), "sessions": sessions}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
