#!/usr/bin/env python3
"""Check how a past session's recommendations actually performed.

For each ACCEPTED recommendation in a session, pull the target's current
performance from Meta and compare it to the snapshot taken at the time of
the recommendation. Classify each as:

    worked        — the metric moved in the predicted direction by a
                    meaningful amount (and spend since is enough to trust it)
    didn't_work   — moved the wrong way, or didn't move with enough spend
    inconclusive  — not enough spend / time since the change

Writes the classifications back into the session log under `outcomes`.

Usage:
    python3 measure_outcomes.py --session 2026-05-14-0930
    python3 measure_outcomes.py --session 2026-05-14-0930 --dry-run

Notes:
- This is best-effort. Causality on ad accounts is messy; we report what
  the numbers did, with a confidence note. The skill should treat this as
  signal, not proof.
- For "pause" recommendations, we measure account-level CPA/ROAS impact
  since the rec was made (since the target is no longer running).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
SESSIONS_DIR = SKILL_DIR / "logs" / "sessions"


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if ENV_PATH.exists():
        for raw in ENV_PATH.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    for k in ("META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID", "META_API_VERSION"):
        if k in os.environ:
            out[k] = os.environ[k]
    return out


def http_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "optimize-ads-outcomes/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8")
        except Exception:
            pass
        raise RuntimeError(f"HTTP {e.code}: {body[:200]}") from e


def fetch_target_insights(
    base: str, target_type: str, target_id: str, token: str, since: str, until: str
) -> dict | None:
    """Pull insights for a single entity over a window. Returns first row or None."""
    edge_for_level = {"campaign": "campaign", "adset": "adset", "ad": "ad"}
    level = edge_for_level.get(target_type)
    if not level:
        # account-level recs use the account itself
        level = "account"
    params = {
        "level": level,
        "time_range": json.dumps({"since": since, "until": until}),
        "fields": "spend,impressions,clicks,inline_link_click_ctr,frequency,actions,action_values,purchase_roas",
        "access_token": token,
    }
    url = f"{base}/{target_id}/insights?{urllib.parse.urlencode(params)}"
    try:
        payload = http_get_json(url)
    except RuntimeError as e:
        return {"_error": str(e)}
    data = payload.get("data") or []
    return data[0] if data else None


def actions_total(actions: list[dict] | None, key: str) -> float:
    if not actions:
        return 0.0
    for a in actions:
        if a.get("action_type") == key:
            try:
                return float(a.get("value", 0))
            except (TypeError, ValueError):
                return 0.0
    return 0.0


def compute_metric(row: dict, metric: str, purchase_key: str = "omni_purchase") -> float | None:
    if row is None or row.get("_error"):
        return None
    spend = float(row.get("spend", 0) or 0)
    if metric == "spend":
        return spend
    if metric == "frequency":
        return float(row.get("frequency", 0) or 0)
    if metric == "link_ctr":
        v = row.get("inline_link_click_ctr")
        return float(v) / 100.0 if v else 0.0
    if metric == "purchases":
        return actions_total(row.get("actions"), purchase_key)
    if metric == "purchase_value":
        return actions_total(row.get("action_values"), purchase_key)
    if metric == "roas":
        pv = actions_total(row.get("action_values"), purchase_key)
        return (pv / spend) if spend > 0 else 0.0
    if metric == "cpa":
        pur = actions_total(row.get("actions"), purchase_key)
        return (spend / pur) if pur > 0 else None
    return None


def classify(framework: str, rec_metric_before: float | None, current: float | None, spend_since: float) -> tuple[str, str]:
    """Heuristic classifier: returns (status, note)."""
    if current is None or rec_metric_before is None:
        return "inconclusive", "Missing metric values."
    # "Kill the Drainers" — target was paused. Measure spend_since as a sanity check.
    # We don't really know if killing it helped without account-level counterfactuals;
    # report directionally.
    if "drain" in framework.lower():
        if spend_since < 1:
            return "worked", "Drainer is paused; no further spend on it."
        return "didn't_work", "Spend continued — was it actually paused?"
    if "scale" in framework.lower():
        # Expect ROAS to hold within ±15% of prior and spend to be up.
        rel = (current - rec_metric_before) / rec_metric_before if rec_metric_before else 0
        if rel >= -0.15:
            return "worked", f"Metric held ({rel*100:+.1f}%) at higher spend."
        if rel < -0.30:
            return "didn't_work", f"Metric dropped significantly ({rel*100:+.1f}%)."
        return "inconclusive", f"Metric softened ({rel*100:+.1f}%) — watch."
    if "fatigue" in framework.lower() or "refresh" in framework.lower():
        # Expect link_ctr to recover.
        rel = (current - rec_metric_before) / max(rec_metric_before, 1e-9)
        if rel >= 0.20:
            return "worked", f"link_ctr recovered ({rel*100:+.1f}%)."
        if rel <= -0.10:
            return "didn't_work", f"link_ctr continued to decline ({rel*100:+.1f}%)."
        return "inconclusive", f"link_ctr roughly flat ({rel*100:+.1f}%)."
    if "saturation" in framework.lower():
        # Expect frequency to drop and/or ROAS to improve.
        rel = (current - rec_metric_before) / max(rec_metric_before, 1e-9)
        if rel <= -0.15:
            return "worked", f"Frequency dropped ({rel*100:+.1f}%)."
        if rel >= 0.05:
            return "didn't_work", f"Frequency continued to rise ({rel*100:+.1f}%)."
        return "inconclusive", "Frequency roughly flat."
    if "consolidat" in framework.lower():
        # Expect cpa to improve.
        rel = (current - rec_metric_before) / max(rec_metric_before, 1e-9)
        if rel <= -0.10:
            return "worked", f"CPA improved {rel*100:+.1f}%."
        if rel >= 0.10:
            return "didn't_work", f"CPA worsened {rel*100:+.1f}%."
        return "inconclusive", "CPA roughly flat."
    # Default: report direction without a verdict.
    rel = (current - rec_metric_before) / max(rec_metric_before, 1e-9)
    return "inconclusive", f"Metric changed {rel*100:+.1f}% — framework-specific verdict not defined."


# Which metric matters for each framework's outcome
FRAMEWORK_METRIC = {
    "kill the drainers": ("spend", "lower is better"),
    "scale the winners": ("roas", "hold or rise"),
    "creative fatigue refresh": ("link_ctr", "recover"),
    "audience saturation": ("frequency", "drop"),
    "cpm spike investigation": ("link_ctr", "diagnostic"),
    "consolidation": ("cpa", "improve"),
    "creative winner cross-pollination": ("roas", "hold or rise"),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--session", required=True, help="Session ID to measure outcomes for.")
    parser.add_argument("--dry-run", action="store_true", help="Print results without writing back.")
    parser.add_argument(
        "--min-spend-since",
        type=float,
        default=50.0,
        help="Below this much spend since the rec, mark inconclusive.",
    )
    parser.add_argument(
        "--until",
        default=date.today().isoformat(),
        help="ISO date to measure up to. Default: today.",
    )
    args = parser.parse_args()

    session_path = SESSIONS_DIR / f"{args.session}.json"
    if not session_path.exists():
        print(f"ERROR: no session log at {session_path}", file=sys.stderr)
        return 2

    env = load_env()
    token = env.get("META_ACCESS_TOKEN")
    if not token:
        print("ERROR: META_ACCESS_TOKEN not set", file=sys.stderr)
        return 2
    api_version = env.get("META_API_VERSION", "v21.0")
    base = f"https://graph.facebook.com/{api_version}"

    session = json.loads(session_path.read_text())

    # Find the date the recommendation became actionable: use lookback_window.until
    rec_until = session.get("lookback_window", {}).get("until")
    if not rec_until or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", rec_until):
        print(f"ERROR: session has invalid lookback_window.until: {rec_until!r}", file=sys.stderr)
        return 2
    since = (date.fromisoformat(rec_until) + timedelta(days=1)).isoformat()
    until = args.until

    decisions_by_rec = {d["rec_id"]: d for d in session.get("user_decisions", [])}
    outcomes: list[dict] = []

    for rec in session.get("recommendations", []):
        decision = decisions_by_rec.get(rec["id"], {}).get("decision")
        if decision != "accepted":
            outcomes.append(
                {
                    "rec_id": rec["id"],
                    "framework": rec.get("framework"),
                    "status": "not_evaluated",
                    "reason": f"decision={decision or 'none'}",
                }
            )
            continue

        framework_key = (rec.get("framework") or "").lower()
        metric_key, _ = FRAMEWORK_METRIC.get(framework_key, ("roas", "hold or rise"))

        before_value = (rec.get("snapshot_at_recommendation") or {}).get(metric_key)

        row = fetch_target_insights(base, rec.get("target_type", "campaign"), rec["target_id"], token, since, until)
        current_value = compute_metric(row, metric_key) if row else None
        spend_since = compute_metric(row, "spend") if row else 0.0

        if spend_since is not None and spend_since < args.min_spend_since and "drain" not in framework_key:
            status, note = "inconclusive", f"Only ${spend_since:.0f} spend since {since} — too little to judge."
        else:
            status, note = classify(rec.get("framework", ""), before_value, current_value, spend_since or 0.0)

        outcomes.append(
            {
                "rec_id": rec["id"],
                "framework": rec.get("framework"),
                "metric": metric_key,
                "before": before_value,
                "after": current_value,
                "spend_since": spend_since,
                "measurement_window": {"since": since, "until": until},
                "status": status,
                "note": note,
            }
        )

    print(json.dumps({"session_id": args.session, "outcomes": outcomes}, indent=2))

    if not args.dry_run:
        session["outcomes"] = outcomes
        session_path.write_text(json.dumps(session, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
