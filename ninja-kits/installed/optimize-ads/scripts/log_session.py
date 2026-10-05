#!/usr/bin/env python3
"""Write structured session logs for the optimize-ads skill.

Two modes:

  1. Create a new session log:
       python3 log_session.py \
           --snapshot /tmp/optimize-ads-snapshot.json \
           --recommendations-file /tmp/optimize-ads-recs.json \
           [--considered-file /tmp/optimize-ads-considered.json] \
           [--what-we-learned "preamble text"]

  2. Mark user decisions on an existing session:
       python3 log_session.py \
           --session 2026-05-21-1430 \
           --mark-decisions \
           --decisions-file /tmp/decisions.json
       # decisions-file is a list of {rec_id, decision, note?}
       # decision is one of: accepted, rejected, deferred

The recommendations-file is a JSON list. Each item:
    {
      "framework": "Kill the Drainers",
      "target_type": "adset",
      "target_id": "1234567890",
      "target_name": "Broad LAL 1% — Hero Tee",
      "action": "Pause",
      "evidence": "...",
      "confidence": "high",
      "expected_impact": "...",
      "success_metric": "...",
      "risk_if_wrong": "...",
      "snapshot_at_recommendation": { ... }
    }
The script assigns rec_id values rec-1..rec-N.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
LOGS_DIR = SKILL_DIR / "logs"
SESSIONS_DIR = LOGS_DIR / "sessions"
INDEX_PATH = LOGS_DIR / "index.md"


def session_id_now() -> str:
    return datetime.now().strftime("%Y-%m-%d-%H%M")


def derive_summary(snapshot: dict) -> dict[str, Any]:
    account_rows = snapshot.get("levels", {}).get("account", [])
    if not account_rows:
        return {}
    a = account_rows[0]
    return {
        "spend": round(a.get("spend", 0), 2),
        "impressions": a.get("impressions", 0),
        "purchases": a.get("purchases", 0),
        "purchase_value": round(a.get("purchase_value", 0), 2),
        "roas": round(a.get("roas", 0), 3),
        "cpa": round(a["cpa"], 2) if a.get("cpa") is not None else None,
        "link_ctr": round(a.get("link_ctr", 0), 4),
        "frequency": round(a.get("frequency", 0), 2),
    }


def write_index_line(session: dict) -> None:
    summary = session.get("snapshot_summary", {})
    decisions = session.get("user_decisions", [])
    counts = {"accepted": 0, "rejected": 0, "deferred": 0}
    for d in decisions:
        counts[d.get("decision", "deferred")] = counts.get(d.get("decision", "deferred"), 0) + 1
    n_recs = len(session.get("recommendations", []))
    decided = sum(counts.values())
    parts = [
        f"- {session['session_id']}",
        f"{n_recs} recs",
    ]
    if decided:
        parts.append(
            f"({counts['accepted']} accepted, {counts['rejected']} rejected, {counts['deferred']} deferred)"
        )
    else:
        parts.append("(no decisions yet)")
    if summary:
        spend = summary.get("spend", 0)
        roas = summary.get("roas")
        cpa = summary.get("cpa")
        kpi = f"ROAS {roas:.2f}" if roas else (f"CPA ${cpa:.2f}" if cpa else "")
        parts.append(f"spend ${spend:,.0f}{(', ' + kpi) if kpi else ''}")
    line = " — ".join(parts) + "\n"

    if not INDEX_PATH.exists():
        # Header lives on one line; entries follow newest-first.
        INDEX_PATH.write_text("# Session Index — newest first (maintained by log_session.py)\n\n")
    existing = INDEX_PATH.read_text()
    sid = session["session_id"]

    # Try to replace an existing entry for this session in place.
    out_lines = existing.splitlines(keepends=True)
    replaced = False
    for i, raw in enumerate(out_lines):
        if raw.startswith(f"- {sid}"):
            out_lines[i] = line
            replaced = True
            break
    if replaced:
        INDEX_PATH.write_text("".join(out_lines))
        return

    # Otherwise, insert this entry as the first bullet (right below the header block).
    # Find the index of the first existing `- ` line; insert just before it.
    insert_at: int | None = None
    for i, raw in enumerate(out_lines):
        if raw.lstrip().startswith("- "):
            insert_at = i
            break
    if insert_at is None:
        # No bullets yet — append. Ensure exactly one blank line before the first bullet.
        text = "".join(out_lines).rstrip() + "\n\n" + line
        INDEX_PATH.write_text(text)
    else:
        out_lines.insert(insert_at, line)
        INDEX_PATH.write_text("".join(out_lines))


def create_session(args: argparse.Namespace) -> int:
    snapshot = json.loads(Path(args.snapshot).read_text())
    recs_in = json.loads(Path(args.recommendations_file).read_text())
    if not isinstance(recs_in, list):
        print("ERROR: recommendations file must be a JSON list", file=sys.stderr)
        return 2

    considered: list[dict] = []
    if args.considered_file:
        considered = json.loads(Path(args.considered_file).read_text())

    session_id = args.session_id or session_id_now()
    recs_out: list[dict] = []
    for i, r in enumerate(recs_in, start=1):
        rec = dict(r)
        rec.setdefault("id", f"rec-{i}")
        recs_out.append(rec)

    session = {
        "session_id": session_id,
        "started_at": datetime.now().astimezone().isoformat(),
        "lookback_window": snapshot.get("lookback_window", {}),
        "ad_account_id": snapshot.get("ad_account_id"),
        "snapshot_summary": derive_summary(snapshot),
        "what_we_learned": args.what_we_learned or "",
        "recommendations": recs_out,
        "considered_and_skipped": considered,
        "user_decisions": [],
        "outcomes": [],
    }

    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = SESSIONS_DIR / f"{session_id}.json"
    out_path.write_text(json.dumps(session, indent=2) + "\n")
    write_index_line(session)

    print(json.dumps({"session_id": session_id, "log_path": str(out_path), "n_recommendations": len(recs_out)}))
    return 0


def mark_decisions(args: argparse.Namespace) -> int:
    session_path = SESSIONS_DIR / f"{args.session}.json"
    if not session_path.exists():
        print(f"ERROR: no session log at {session_path}", file=sys.stderr)
        return 2

    if args.decisions_file:
        decisions_in = json.loads(Path(args.decisions_file).read_text())
    else:
        decisions_in = json.loads(sys.stdin.read())
    if not isinstance(decisions_in, list):
        print("ERROR: decisions must be a JSON list", file=sys.stderr)
        return 2

    session = json.loads(session_path.read_text())
    rec_ids = {r["id"] for r in session.get("recommendations", [])}
    valid_decisions = {"accepted", "rejected", "deferred"}

    cleaned: list[dict] = []
    now = datetime.now().astimezone().isoformat()
    for d in decisions_in:
        rid = d.get("rec_id")
        dec = d.get("decision")
        if rid not in rec_ids:
            print(f"WARN: unknown rec_id {rid!r}, skipping", file=sys.stderr)
            continue
        if dec not in valid_decisions:
            print(f"WARN: invalid decision {dec!r} for {rid}, skipping", file=sys.stderr)
            continue
        cleaned.append(
            {"rec_id": rid, "decision": dec, "decided_at": now, "note": d.get("note", "")}
        )

    # Merge: keep prior decisions for recs not in this update
    prior = {d["rec_id"]: d for d in session.get("user_decisions", [])}
    for d in cleaned:
        prior[d["rec_id"]] = d
    session["user_decisions"] = list(prior.values())

    session_path.write_text(json.dumps(session, indent=2) + "\n")
    write_index_line(session)
    print(json.dumps({"session_id": args.session, "marked": len(cleaned)}))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", help="Existing session_id to update.")
    parser.add_argument("--session-id", help="Override the auto-generated session_id when creating.")
    parser.add_argument("--snapshot", help="Snapshot JSON path (for creating a new session).")
    parser.add_argument("--recommendations-file", help="Recommendations JSON list (for creating a new session).")
    parser.add_argument("--considered-file", help="Optional 'considered and skipped' JSON list.")
    parser.add_argument("--what-we-learned", help="Optional preamble text summarizing past-session outcomes.")
    parser.add_argument("--mark-decisions", action="store_true", help="Update user_decisions on an existing session.")
    parser.add_argument("--decisions-file", help="JSON list of decisions; otherwise read from stdin.")
    args = parser.parse_args()

    if args.mark_decisions:
        if not args.session:
            print("ERROR: --mark-decisions requires --session", file=sys.stderr)
            return 2
        return mark_decisions(args)

    if not args.snapshot or not args.recommendations_file:
        print("ERROR: creating a session requires --snapshot and --recommendations-file", file=sys.stderr)
        return 2
    return create_session(args)


if __name__ == "__main__":
    sys.exit(main())
