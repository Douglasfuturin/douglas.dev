#!/usr/bin/env python3
"""
pull_meta_ads.py — Pull Meta (Facebook + Instagram) Ads insights and write data/meta_ads.json.

Requires:
  META_ADS_ACCESS_TOKEN  — long-lived or system-user token with ads_read
  META_ADS_ACCOUNT_ID    — "act_1234567890" form
  META_ADS_API_VERSION   — optional; default v22.0

Usage:
  python3 pull_meta_ads.py --start 2026-05-13 --end 2026-05-19 --out data/meta_ads.json

If credentials are missing, exits with a {"status":"missing"} JSON.
"""

from __future__ import annotations
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    import requests
except ImportError:
    print("requests not installed (pip install requests)", file=sys.stderr)
    sys.exit(1)


def _write_missing(out: Path, reason: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"status": "missing", "source": "meta_ads", "reason": reason}, indent=2))
    print(f"meta_ads: missing — {reason}", file=sys.stderr)


def _insights(account_id: str, token: str, api_v: str, since: str, until: str,
              level: str, fields: list[str], breakdowns: list[str] | None = None,
              time_increment: int | None = None) -> list[dict]:
    url = f"https://graph.facebook.com/{api_v}/{account_id}/insights"
    params = {
        "access_token": token,
        "level": level,
        "fields": ",".join(fields),
        "time_range": json.dumps({"since": since, "until": until}),
        "limit": 500,
    }
    if breakdowns:
        params["breakdowns"] = ",".join(breakdowns)
    if time_increment:
        params["time_increment"] = str(time_increment)

    rows = []
    while True:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        body = r.json()
        rows.extend(body.get("data", []))
        nxt = body.get("paging", {}).get("next")
        if not nxt:
            break
        url, params = nxt, {}
    return rows


def _sum_metric(rows: list[dict], key: str) -> float:
    total = 0.0
    for r in rows:
        v = r.get(key)
        if v is None:
            continue
        try:
            total += float(v)
        except (TypeError, ValueError):
            pass
    return total


def _action_count(rows: list[dict], action_type: str) -> float:
    total = 0.0
    for r in rows:
        for a in r.get("actions") or []:
            if a.get("action_type") == action_type:
                try:
                    total += float(a.get("value", 0))
                except (TypeError, ValueError):
                    pass
    return total


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--conversion-event", default="offsite_conversion.fb_pixel_lead",
                    help="The action_type to count as a conversion. Default: pixel Lead event.")
    args = ap.parse_args()

    token = os.environ.get("META_ADS_ACCESS_TOKEN")
    account = os.environ.get("META_ADS_ACCOUNT_ID")
    api_v = os.environ.get("META_ADS_API_VERSION", "v22.0")
    if not token or not account:
        _write_missing(args.out, "META_ADS_ACCESS_TOKEN or META_ADS_ACCOUNT_ID not set")
        return 0
    if not account.startswith("act_"):
        account = f"act_{account}"

    base_fields = ["spend", "impressions", "clicks", "ctr", "cpc", "actions", "action_values"]
    start = args.start
    end = args.end

    try:
        # 1) account totals
        acc = _insights(account, token, api_v, start, end, level="account", fields=base_fields)

        # 2) by campaign
        camps = _insights(account, token, api_v, start, end, level="campaign",
                          fields=base_fields + ["campaign_name"])

        # 3) by creative (ad level — top 20 by spend)
        ads = _insights(account, token, api_v, start, end, level="ad",
                        fields=base_fields + ["ad_name", "ad_id"])

        # 4) daily breakdown
        daily_rows = _insights(account, token, api_v, start, end, level="account",
                               fields=base_fields, time_increment=1)

        # 5) prior window
        sdt = datetime.strptime(start, "%Y-%m-%d").date()
        edt = datetime.strptime(end, "%Y-%m-%d").date()
        days = (edt - sdt).days + 1
        prior_start = (sdt - timedelta(days=days)).isoformat()
        prior_end = (sdt - timedelta(days=1)).isoformat()
        prior = _insights(account, token, api_v, prior_start, prior_end, level="account", fields=base_fields)
    except requests.HTTPError as e:
        _write_missing(args.out, f"Meta API HTTP error: {e}")
        return 0
    except Exception as e:  # noqa: BLE001
        _write_missing(args.out, f"Meta API error: {e}")
        return 0

    def _build_totals(rows):
        spend = _sum_metric(rows, "spend")
        impressions = _sum_metric(rows, "impressions")
        clicks = _sum_metric(rows, "clicks")
        conversions = _action_count(rows, args.conversion_event)
        # revenue from purchases or leads:
        purchase_value = 0.0
        for r in rows:
            for av in r.get("action_values") or []:
                if av.get("action_type") in ("offsite_conversion.fb_pixel_purchase", "purchase"):
                    try:
                        purchase_value += float(av.get("value", 0))
                    except (TypeError, ValueError):
                        pass
        return {
            "spend": round(spend, 2),
            "impressions": int(impressions),
            "clicks": int(clicks),
            "ctr": round(clicks / impressions, 4) if impressions else 0,
            "cpc": round(spend / clicks, 3) if clicks else 0,
            "conversions": int(conversions),
            "roas": round(purchase_value / spend, 2) if spend else 0,
            "purchase_value": round(purchase_value, 2),
        }

    totals = _build_totals(acc)
    prior_totals = _build_totals(prior)

    by_campaign = []
    for r in camps:
        t = _build_totals([r])
        by_campaign.append({"name": r.get("campaign_name", "?"), **t})
    by_campaign.sort(key=lambda x: -x["spend"])

    by_creative = []
    for r in ads:
        t = _build_totals([r])
        by_creative.append({"id": r.get("ad_id", "?"), "name": r.get("ad_name", "?"), **t})
    by_creative.sort(key=lambda x: -x["spend"])
    by_creative = by_creative[:20]

    daily = []
    for r in daily_rows:
        d = r.get("date_start")
        if not d:
            continue
        t = _build_totals([r])
        daily.append({"date": d, **t})

    out = {
        "status": "ok",
        "source": "meta_ads",
        "window": {"start": start, "end": end},
        "totals": totals,
        "by_campaign": by_campaign,
        "by_creative": by_creative,
        "daily": daily,
        "prior_window": prior_totals,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, indent=2))
    print(f"meta_ads: wrote {args.out} (spend=${totals['spend']:,.2f}, roas={totals['roas']}x)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
