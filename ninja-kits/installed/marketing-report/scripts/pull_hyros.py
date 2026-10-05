#!/usr/bin/env python3
"""
pull_hyros.py — Pull Hyros cross-channel attribution and write data/hyros.json.

Hyros's public API surface varies by account tier. This script targets the v1 REST
endpoints (api.hyros.com/v1/api/v1.0/) and uses generic paginated fetches that have
been stable since 2023. If the account uses different endpoints, the URL constants
at the top can be swapped without touching the rest of the script.

Requires:
  HYROS_API_KEY        — from Hyros → Integrations → API Keys
  HYROS_WORKSPACE_ID   — optional (only some endpoints require it)

Usage:
  python3 pull_hyros.py --start 2026-05-13 --end 2026-05-19 --out data/hyros.json
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("requests not installed (pip install requests)", file=sys.stderr)
    sys.exit(1)

API_BASE = "https://api.hyros.com/v1/api/v1.0"


def _write_missing(out: Path, reason: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"status": "missing", "source": "hyros", "reason": reason}, indent=2))
    print(f"hyros: missing — {reason}", file=sys.stderr)


def _get(endpoint: str, params: dict, key: str) -> list[dict] | dict:
    headers = {"API-Key": key, "Accept": "application/json"}
    rows = []
    page = 1
    while True:
        p = dict(params, pageId=page)
        r = requests.get(f"{API_BASE}{endpoint}", params=p, headers=headers, timeout=30)
        r.raise_for_status()
        body = r.json()
        # Hyros responses commonly wrap data in { result: { data: [...], hasMore: bool } }
        result = body.get("result", body)
        data = result.get("data") if isinstance(result, dict) else result
        if data is None:
            return result
        rows.extend(data if isinstance(data, list) else [data])
        has_more = result.get("hasMore") if isinstance(result, dict) else False
        if not has_more:
            break
        page += 1
        if page > 50:  # safety
            break
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    key = os.environ.get("HYROS_API_KEY")
    if not key:
        _write_missing(args.out, "HYROS_API_KEY not set")
        return 0

    sdt = datetime.strptime(args.start, "%Y-%m-%d").date()
    edt = datetime.strptime(args.end, "%Y-%m-%d").date()
    days = (edt - sdt).days + 1
    prior_start = (sdt - timedelta(days=days)).isoformat()
    prior_end = (sdt - timedelta(days=1)).isoformat()

    try:
        # 1) Sales for the window — Hyros endpoint `/sales` returns attributed revenue per sale.
        sales = _get("/sales", {"fromDate": args.start, "toDate": args.end}, key)
        # 2) Leads for the window — endpoint `/leads`.
        leads = _get("/leads", {"fromDate": args.start, "toDate": args.end}, key)
        # 3) Sales for the prior window
        prior_sales = _get("/sales", {"fromDate": prior_start, "toDate": prior_end}, key)
        prior_leads = _get("/leads", {"fromDate": prior_start, "toDate": prior_end}, key)
    except requests.HTTPError as e:
        _write_missing(args.out, f"Hyros HTTP error: {e}")
        return 0
    except Exception as e:  # noqa: BLE001
        _write_missing(args.out, f"Hyros error: {e}")
        return 0

    def _safe_float(v, default=0.0) -> float:
        try:
            return float(v)
        except (TypeError, ValueError):
            return default

    def _aggregate(s_rows, l_rows):
        revenue = sum(_safe_float(s.get("amount", 0)) for s in s_rows)
        n_leads = len(l_rows)
        n_calls = sum(1 for l in l_rows if l.get("isBooked") or l.get("isCall") or l.get("type") == "call")
        if n_calls == 0:
            # Some accounts represent a 'call' via tags or a custom event — fall back to all booked actions.
            n_calls = sum(1 for l in l_rows if (l.get("tags") and any("call" in t.lower() for t in l.get("tags") or [])))
        by_channel_revenue = defaultdict(float)
        by_channel_leads = defaultdict(int)
        by_channel_calls = defaultdict(int)
        for s in s_rows:
            ch = (s.get("source") or s.get("channel") or "unknown").lower()
            by_channel_revenue[ch] += _safe_float(s.get("amount", 0))
        for l in l_rows:
            ch = (l.get("source") or l.get("channel") or "unknown").lower()
            by_channel_leads[ch] += 1
            if l.get("isBooked") or l.get("isCall") or l.get("type") == "call":
                by_channel_calls[ch] += 1
        by_channel = []
        for ch in sorted(set(by_channel_revenue) | set(by_channel_leads) | set(by_channel_calls)):
            by_channel.append({
                "channel": ch,
                "revenue": round(by_channel_revenue.get(ch, 0), 2),
                "leads": by_channel_leads.get(ch, 0),
                "calls": by_channel_calls.get(ch, 0),
            })
        return {
            "revenue": round(revenue, 2),
            "leads": n_leads,
            "calls_booked": n_calls,
            "by_channel": by_channel,
        }

    cur = _aggregate(sales, leads)
    prior = _aggregate(prior_sales, prior_leads)

    out = {
        "status": "ok",
        "source": "hyros",
        "window": {"start": args.start, "end": args.end},
        "totals": {
            "revenue": cur["revenue"],
            "leads": cur["leads"],
            "calls_booked": cur["calls_booked"],
        },
        "by_channel": cur["by_channel"],
        "prior_window": {
            "revenue": prior["revenue"],
            "calls_booked": prior["calls_booked"],
            "leads": prior["leads"],
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2))
    print(f"hyros: wrote {args.out} (revenue=${cur['revenue']:,.2f}, calls={cur['calls_booked']})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
