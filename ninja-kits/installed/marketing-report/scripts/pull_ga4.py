#!/usr/bin/env python3
"""
pull_ga4.py — Pull GA4 web analytics for a given window and write data/ga4.json.

Requires:
  GA4_SERVICE_ACCOUNT_PATH  — path to GCP service account JSON
  GA4_PROPERTY_ID           — numeric GA4 property ID
  pip install google-analytics-data

Usage:
  python3 pull_ga4.py --start 2026-05-13 --end 2026-05-19 --out data/ga4.json

If credentials are missing, exits writing a {"status": "missing", "reason": "..."} JSON
so the downstream composer / renderer can degrade gracefully.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path


def _write_missing(out: Path, reason: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"status": "missing", "source": "ga4", "reason": reason}, indent=2))
    print(f"ga4: missing — {reason}", file=sys.stderr)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="YYYY-MM-DD inclusive")
    ap.add_argument("--end", required=True, help="YYYY-MM-DD inclusive")
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    sa = os.environ.get("GA4_SERVICE_ACCOUNT_PATH")
    prop = os.environ.get("GA4_PROPERTY_ID")
    if not sa or not prop:
        _write_missing(args.out, "GA4_SERVICE_ACCOUNT_PATH or GA4_PROPERTY_ID not set")
        return 0
    if not Path(sa).exists():
        _write_missing(args.out, f"service account file not found: {sa}")
        return 0

    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import DateRange, Dimension, Metric, RunReportRequest
        from google.oauth2 import service_account
    except ImportError:
        _write_missing(args.out, "google-analytics-data not installed (pip install google-analytics-data)")
        return 0

    creds = service_account.Credentials.from_service_account_file(sa)
    client = BetaAnalyticsDataClient(credentials=creds)

    start = datetime.strptime(args.start, "%Y-%m-%d").date()
    end = datetime.strptime(args.end, "%Y-%m-%d").date()
    window_days = (end - start).days + 1
    prior_start = start - timedelta(days=window_days)
    prior_end = start - timedelta(days=1)

    def run_report(metrics, dimensions, date_range):
        req = RunReportRequest(
            property=f"properties/{prop}",
            date_ranges=[DateRange(start_date=date_range[0].isoformat(), end_date=date_range[1].isoformat())],
            dimensions=[Dimension(name=d) for d in dimensions],
            metrics=[Metric(name=m) for m in metrics],
        )
        return client.run_report(req)

    # 1) totals current window
    cur = run_report(
        metrics=["sessions", "totalUsers", "screenPageViews", "engagedSessions", "conversions", "engagementRate"],
        dimensions=[],
        date_range=(start, end),
    )
    cur_row = cur.rows[0].metric_values if cur.rows else []

    def _f(idx, cast=float, default=0):
        try:
            return cast(cur_row[idx].value)
        except (IndexError, ValueError):
            return default

    totals = {
        "sessions": _f(0, int),
        "users": _f(1, int),
        "pageviews": _f(2, int),
        "engaged_sessions": _f(3, int),
        "conversions": _f(4, int),
        "engagement_rate": _f(5, float),
    }

    # 2) by source/medium
    by_src = run_report(
        metrics=["sessions", "conversions"],
        dimensions=["sessionSourceMedium"],
        date_range=(start, end),
    )
    by_source = []
    for row in by_src.rows:
        by_source.append({
            "source": row.dimension_values[0].value,
            "sessions": int(row.metric_values[0].value or 0),
            "conversions": int(row.metric_values[1].value or 0),
        })
    by_source.sort(key=lambda x: -x["sessions"])
    by_source = by_source[:12]

    # 3) daily
    daily_resp = run_report(
        metrics=["sessions", "conversions"],
        dimensions=["date"],
        date_range=(start, end),
    )
    daily = []
    for row in daily_resp.rows:
        d = row.dimension_values[0].value  # YYYYMMDD
        iso = f"{d[:4]}-{d[4:6]}-{d[6:]}"
        daily.append({
            "date": iso,
            "sessions": int(row.metric_values[0].value or 0),
            "conversions": int(row.metric_values[1].value or 0),
        })
    daily.sort(key=lambda x: x["date"])

    # 4) top pages
    pages_resp = run_report(
        metrics=["sessions", "engagementRate"],
        dimensions=["pagePath"],
        date_range=(start, end),
    )
    top_pages = []
    for row in pages_resp.rows:
        top_pages.append({
            "path": row.dimension_values[0].value,
            "sessions": int(row.metric_values[0].value or 0),
            "engagement_rate": float(row.metric_values[1].value or 0),
        })
    top_pages.sort(key=lambda x: -x["sessions"])
    top_pages = top_pages[:10]

    # 5) prior-window totals
    prior = run_report(
        metrics=["sessions", "totalUsers", "conversions"],
        dimensions=[],
        date_range=(prior_start, prior_end),
    )
    p_row = prior.rows[0].metric_values if prior.rows else []
    prior_window = {
        "sessions": int(p_row[0].value) if len(p_row) > 0 else 0,
        "users": int(p_row[1].value) if len(p_row) > 1 else 0,
        "conversions": int(p_row[2].value) if len(p_row) > 2 else 0,
    }

    out = {
        "status": "ok",
        "source": "ga4",
        "window": {"start": args.start, "end": args.end},
        "totals": totals,
        "by_source": by_source,
        "daily": daily,
        "top_pages": top_pages,
        "prior_window": prior_window,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2))
    print(f"ga4: wrote {args.out} (sessions={totals['sessions']:,})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
