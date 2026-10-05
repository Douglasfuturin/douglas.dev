#!/usr/bin/env python3
"""Pull Meta Ads performance data for the configured account.

Fetches insights at account, campaign, adset, and ad level, plus
campaign/adset/ad metadata (status, objective, budget), and writes a single
normalized snapshot JSON ready for the skill to analyze.

Usage:
    python3 .claude/skills/optimize-ads/scripts/pull_performance.py \
        --since 2026-05-14 \
        --until 2026-05-21 \
        --output /tmp/optimize-ads-snapshot.json

    # If --since omitted, defaults to the last session's end (from logs/index.md)
    # or 7 days ago if no prior session exists.

The snapshot shape is documented in references/meta_api_guide.md.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any


SKILL_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = SKILL_DIR.parent.parent.parent
ENV_PATH = PROJECT_ROOT / ".env"
CONFIG_PATH = SKILL_DIR / "config" / "config.json"
LOGS_DIR = SKILL_DIR / "logs"
SESSIONS_DIR = LOGS_DIR / "sessions"

# Fields we ask Meta for, by level.
INSIGHT_FIELDS_BASE = [
    "spend",
    "impressions",
    "reach",
    "frequency",
    "clicks",
    "inline_link_clicks",
    "ctr",
    "inline_link_click_ctr",
    "cpc",
    "cpm",
    "actions",
    "action_values",
    "cost_per_action_type",
    "purchase_roas",
]

LEVEL_EXTRA_FIELDS = {
    "account": [],
    "campaign": ["campaign_id", "campaign_name", "objective"],
    "adset": ["adset_id", "adset_name", "campaign_id"],
    "ad": ["ad_id", "ad_name", "adset_id", "campaign_id"],
}

# Action types we surface as named metrics in the snapshot.
TRACKED_ACTION_TYPES = [
    "purchase",
    "omni_purchase",
    "offsite_conversion.fb_pixel_purchase",
    "lead",
    "complete_registration",
    "add_to_cart",
    "initiate_checkout",
    "link_click",
]


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    if ENV_PATH.exists():
        for raw in ENV_PATH.read_text().splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip()
    # env vars override .env
    for k in ("META_ACCESS_TOKEN", "META_AD_ACCOUNT_ID", "META_API_VERSION"):
        if k in os.environ:
            out[k] = os.environ[k]
    return out


def load_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def last_session_until() -> str | None:
    """Return the `until` date of the most recent session, or None."""
    if not SESSIONS_DIR.exists():
        return None
    candidates = sorted(SESSIONS_DIR.glob("*.json"))
    if not candidates:
        return None
    try:
        data = json.loads(candidates[-1].read_text())
        return data.get("lookback_window", {}).get("until")
    except Exception:
        return None


def http_get_json(url: str, *, max_retries: int = 4) -> dict:
    """GET with exponential backoff on 4xx/5xx that looks like rate-limit/server."""
    delay = 2.0
    last_err: Exception | None = None
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "optimize-ads/1.0"})
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8")
            except Exception:
                pass
            # rate limit codes from Meta: 4, 17, 32, 80004, 613
            transient = e.code in (429, 500, 502, 503, 504) or any(
                f'"code":{c}' in body for c in (4, 17, 32, 613, 80004)
            )
            if transient and attempt < max_retries - 1:
                print(f"[pull] transient HTTP {e.code}, sleeping {delay:.1f}s...", file=sys.stderr)
                time.sleep(delay)
                delay *= 2
                last_err = e
                continue
            # surface a useful error
            try:
                err = json.loads(body).get("error", {})
                raise RuntimeError(
                    f"Meta API error {e.code}: {err.get('message')} (code {err.get('code')}, type {err.get('type')})"
                ) from e
            except (json.JSONDecodeError, AttributeError):
                raise RuntimeError(f"Meta API error {e.code}: {body[:300]}") from e
        except urllib.error.URLError as e:
            if attempt < max_retries - 1:
                time.sleep(delay)
                delay *= 2
                last_err = e
                continue
            raise
    if last_err:
        raise last_err  # pragma: no cover — defensive
    raise RuntimeError("unreachable")


def paginate(url: str) -> list[dict]:
    """Walk Meta's cursor-paginated list endpoints."""
    out: list[dict] = []
    next_url: str | None = url
    while next_url:
        payload = http_get_json(next_url)
        out.extend(payload.get("data", []))
        next_url = payload.get("paging", {}).get("next")
    return out


def fetch_insights(
    base: str,
    account_id: str,
    token: str,
    level: str,
    since: str,
    until: str,
) -> list[dict]:
    fields = INSIGHT_FIELDS_BASE + LEVEL_EXTRA_FIELDS[level]
    params = {
        "level": level,
        "time_range": json.dumps({"since": since, "until": until}),
        "fields": ",".join(fields),
        "limit": "500",
        "access_token": token,
    }
    url = f"{base}/{account_id}/insights?{urllib.parse.urlencode(params)}"
    return paginate(url)


def fetch_entities(base: str, account_id: str, token: str, edge: str, fields: list[str]) -> list[dict]:
    params = {
        "fields": ",".join(fields),
        "limit": "500",
        "access_token": token,
    }
    url = f"{base}/{account_id}/{edge}?{urllib.parse.urlencode(params)}"
    return paginate(url)


def actions_to_dict(actions: list[dict] | None) -> dict[str, float]:
    if not actions:
        return {}
    out: dict[str, float] = {}
    for a in actions:
        t = a.get("action_type")
        v = a.get("value")
        if t is None or v is None:
            continue
        try:
            out[t] = float(v)
        except (TypeError, ValueError):
            continue
    return out


def normalize_row(row: dict, purchase_action_type: str) -> dict:
    """Add derived metrics so the skill doesn't have to do string parsing."""
    actions = actions_to_dict(row.get("actions"))
    action_values = actions_to_dict(row.get("action_values"))
    cpa_map = actions_to_dict(row.get("cost_per_action_type"))

    spend = float(row.get("spend", 0) or 0)
    impressions = int(float(row.get("impressions", 0) or 0))
    clicks = int(float(row.get("clicks", 0) or 0))
    link_clicks = int(float(row.get("inline_link_clicks", 0) or 0))

    purchases = actions.get(purchase_action_type, 0.0)
    if not purchases:
        # fall back through common aliases
        for alt in ("omni_purchase", "purchase", "offsite_conversion.fb_pixel_purchase"):
            if actions.get(alt):
                purchases = actions[alt]
                break
    purchase_value = action_values.get(purchase_action_type, 0.0)
    if not purchase_value:
        for alt in ("omni_purchase", "purchase", "offsite_conversion.fb_pixel_purchase"):
            if action_values.get(alt):
                purchase_value = action_values[alt]
                break

    derived: dict[str, Any] = {
        "spend": spend,
        "impressions": impressions,
        "reach": int(float(row.get("reach", 0) or 0)),
        "frequency": float(row.get("frequency", 0) or 0),
        "clicks": clicks,
        "link_clicks": link_clicks,
        "ctr": float(row.get("ctr", 0) or 0) / 100.0 if row.get("ctr") else 0.0,
        "link_ctr": float(row.get("inline_link_click_ctr", 0) or 0) / 100.0
        if row.get("inline_link_click_ctr")
        else 0.0,
        "cpc": float(row.get("cpc", 0) or 0),
        "cpm": float(row.get("cpm", 0) or 0),
        "purchases": purchases,
        "purchase_value": purchase_value,
        "roas": (purchase_value / spend) if spend > 0 and purchase_value else 0.0,
        "cpa": (spend / purchases) if purchases > 0 else None,
    }
    for at in TRACKED_ACTION_TYPES:
        if at in actions:
            derived[f"actions.{at}"] = actions[at]
        if at in cpa_map:
            derived[f"cpa.{at}"] = cpa_map[at]

    # Carry through metadata fields
    for k in ("campaign_id", "campaign_name", "adset_id", "adset_name", "ad_id", "ad_name", "objective"):
        if k in row:
            derived[k] = row[k]

    return derived


def main() -> int:
    parser = argparse.ArgumentParser(description="Pull Meta Ads insights snapshot.")
    parser.add_argument("--since", help="ISO date, e.g. 2026-05-14. Default: last session end or 7d ago.")
    parser.add_argument("--until", help="ISO date, e.g. 2026-05-21. Default: today.")
    parser.add_argument("--output", required=True, help="Path to write snapshot JSON.")
    parser.add_argument(
        "--levels",
        default="account,campaign,adset,ad",
        help="Comma-separated levels to pull. Default: all. Drop 'ad' to reduce API cost.",
    )
    args = parser.parse_args()

    env = load_env()
    token = env.get("META_ACCESS_TOKEN")
    account_id = env.get("META_AD_ACCOUNT_ID")
    api_version = env.get("META_API_VERSION", "v21.0")
    if not token or not account_id:
        print("ERROR: META_ACCESS_TOKEN / META_AD_ACCOUNT_ID not set. Run setup.py first.", file=sys.stderr)
        return 2

    cfg = load_config()
    purchase_action_type = cfg.get("purchase_action_type", "omni_purchase")

    today = date.today()
    until = args.until or today.isoformat()
    if args.since:
        since = args.since
    else:
        last_until = last_session_until()
        if last_until:
            since = last_until
        else:
            since = (today - timedelta(days=cfg.get("default_lookback_days", 7))).isoformat()

    # Light validation: ISO yyyy-mm-dd
    for label, v in (("since", since), ("until", until)):
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v):
            print(f"ERROR: --{label} must be YYYY-MM-DD, got {v!r}", file=sys.stderr)
            return 2

    base = f"https://graph.facebook.com/{api_version}"
    levels = [lvl.strip() for lvl in args.levels.split(",") if lvl.strip()]

    print(f"[pull] window {since} → {until}, levels={levels}", file=sys.stderr)

    snapshot: dict[str, Any] = {
        "pulled_at": datetime.now().astimezone().isoformat(),
        "ad_account_id": account_id,
        "api_version": api_version,
        "lookback_window": {"since": since, "until": until},
        "config_at_pull": cfg,
        "levels": {},
        "entities": {},
    }

    for level in levels:
        rows = fetch_insights(base, account_id, token, level, since, until)
        snapshot["levels"][level] = [normalize_row(r, purchase_action_type) for r in rows]
        print(f"[pull] insights.{level}: {len(rows)} rows", file=sys.stderr)

    # Entity metadata — status, budgets, etc. — pull regardless of insight levels chosen
    snapshot["entities"]["campaigns"] = fetch_entities(
        base,
        account_id,
        token,
        "campaigns",
        ["id", "name", "objective", "status", "effective_status", "daily_budget", "lifetime_budget", "start_time", "stop_time"],
    )
    snapshot["entities"]["adsets"] = fetch_entities(
        base,
        account_id,
        token,
        "adsets",
        ["id", "name", "campaign_id", "status", "effective_status", "daily_budget", "optimization_goal"],
    )
    if "ad" in levels:
        snapshot["entities"]["ads"] = fetch_entities(
            base,
            account_id,
            token,
            "ads",
            ["id", "name", "adset_id", "campaign_id", "status", "effective_status"],
        )

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(snapshot, indent=2))
    print(f"[pull] wrote {out_path}", file=sys.stderr)

    # Friendly stdout summary for the agent to chain off of
    account_rows = snapshot["levels"].get("account", [])
    if account_rows:
        a = account_rows[0]
        print(
            json.dumps(
                {
                    "since": since,
                    "until": until,
                    "spend": a["spend"],
                    "purchases": a["purchases"],
                    "purchase_value": a["purchase_value"],
                    "roas": a["roas"],
                    "cpa": a["cpa"],
                    "link_ctr": a["link_ctr"],
                    "campaigns": len(snapshot["levels"].get("campaign", [])),
                    "adsets": len(snapshot["levels"].get("adset", [])),
                    "ads": len(snapshot["levels"].get("ad", [])),
                    "snapshot_path": str(out_path),
                }
            )
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
