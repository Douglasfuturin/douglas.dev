#!/usr/bin/env python3
"""
fetch_slack.py — Slack mentions + unanswered DMs for the morning-brief skill.

Two passes:
  --pass mentions     @[FOUNDER NAME] mentions across channels in the last 24 hrs
  --pass dms          DMs where the last message is NOT from [FOUNDER NAME]
                      (i.e. someone is waiting on them), older than --min-age-hours
  --pass all          Both, returned together

Returns JSON to stdout. Channel-browsing is NOT included — only direct signals
the founder owes a response to.

Env vars:
  SLACK_BOT_TOKEN        Bot token (xoxb-...) — needs the scopes below
  SLACK_USER_ID          [FOUNDER NAME]'s Slack user ID (U0XXXXXX)
  SLACK_LOOKBACK_HOURS   How far back to look for mentions (default 24)
  SLACK_DM_STALE_HOURS   DM is "unanswered" if no reply this many hours (default 24)

Required scopes for the bot token:
  - channels:history  (public channel mentions)
  - groups:history    (private channels [FOUNDER NAME] is in)
  - im:history        (direct messages)
  - im:read           (list DMs)
  - users:read        (resolve user IDs to names)
  - search:read       (mentions search — user token only; if bot token, omit)

For mentions across the workspace, a user token (xoxp-) with search:read is
the cleanest path. If you only have a bot token, mentions are limited to the
channels the bot has been invited to.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

API_BASE = "https://slack.com/api"


class SlackError(Exception):
    pass


def slack_get(method: str, params: dict | None = None) -> dict:
    token = os.environ.get("SLACK_BOT_TOKEN") or os.environ.get("SLACK_USER_TOKEN")
    if not token:
        sys.stderr.write("Set SLACK_BOT_TOKEN (or SLACK_USER_TOKEN for search).\n")
        sys.exit(2)
    qs = urllib.parse.urlencode(params or {})
    url = f"{API_BASE}/{method}?{qs}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        raise SlackError(f"HTTP error calling {method}: {e}")
    if not data.get("ok"):
        raise SlackError(f"Slack API error on {method}: {data.get('error')}")
    return data


def user_id() -> str:
    uid = os.environ.get("SLACK_USER_ID")
    if not uid:
        sys.stderr.write("Set SLACK_USER_ID to [FOUNDER NAME]'s Slack user ID.\n")
        sys.exit(2)
    return uid


_user_cache: dict[str, str] = {}


def resolve_user(uid: str) -> str:
    if uid in _user_cache:
        return _user_cache[uid]
    try:
        data = slack_get("users.info", {"user": uid})
        name = data["user"]["profile"].get("real_name") or data["user"].get("name", uid)
    except SlackError:
        name = uid
    _user_cache[uid] = name
    return name


def ts_to_iso(ts: str) -> str:
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).isoformat()


def hours_ago(ts: str) -> float:
    dt = datetime.fromtimestamp(float(ts), tz=timezone.utc)
    return (datetime.now(timezone.utc) - dt).total_seconds() / 3600


def fetch_mentions(lookback_hours: int) -> list[dict]:
    """Search for messages mentioning the founder. Requires search:read scope."""
    uid = user_id()
    # Slack search supports "<@U123>" queries
    query = f"<@{uid}>"
    try:
        data = slack_get("search.messages", {"query": query, "count": 50, "sort": "timestamp"})
    except SlackError as e:
        sys.stderr.write(
            f"{e}\n"
            "Note: search.messages requires a USER token with search:read. "
            "If you only have a bot token, this pass returns nothing.\n"
        )
        return []

    matches = data.get("messages", {}).get("matches", [])
    cutoff = lookback_hours
    results = []
    for m in matches:
        if hours_ago(m.get("ts", "0")) > cutoff:
            continue
        user = m.get("user", "")
        results.append({
            "type": "mention",
            "channel_id": m.get("channel", {}).get("id"),
            "channel_name": m.get("channel", {}).get("name"),
            "channel_is_private": m.get("channel", {}).get("is_private", False),
            "from_user_id": user,
            "from_user_name": resolve_user(user) if user else "unknown",
            "text": m.get("text", ""),
            "ts": m.get("ts"),
            "ts_iso": ts_to_iso(m.get("ts", "0")),
            "age_hours": round(hours_ago(m.get("ts", "0")), 1),
            "permalink": m.get("permalink"),
        })
    return results


def fetch_dms(stale_hours: int) -> list[dict]:
    """List open DMs, return those where last message is NOT from founder and is stale."""
    uid = user_id()
    try:
        listing = slack_get("conversations.list", {
            "types": "im,mpim",
            "exclude_archived": "true",
            "limit": 200,
        })
    except SlackError as e:
        sys.stderr.write(f"{e}\n")
        return []

    results = []
    for conv in listing.get("channels", []):
        cid = conv.get("id")
        try:
            history = slack_get("conversations.history", {
                "channel": cid, "limit": 5,
            })
        except SlackError:
            continue
        msgs = history.get("messages", [])
        if not msgs:
            continue
        last = msgs[0]  # API returns newest first
        last_user = last.get("user", "")
        if last_user == uid or not last_user:
            continue  # founder sent the last message, or it's a bot message
        age = hours_ago(last.get("ts", "0"))
        if age < stale_hours:
            continue  # too fresh to surface
        results.append({
            "type": "dm",
            "channel_id": cid,
            "is_group_dm": conv.get("is_mpim", False),
            "from_user_id": last_user,
            "from_user_name": resolve_user(last_user),
            "text": last.get("text", ""),
            "ts": last.get("ts"),
            "ts_iso": ts_to_iso(last.get("ts", "0")),
            "age_hours": round(age, 1),
            "thread_ts": last.get("thread_ts"),
        })

    results.sort(key=lambda r: -r["age_hours"])
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pass", dest="which",
                        choices=["mentions", "dms", "all"], required=True)
    parser.add_argument("--limit", type=int, default=10)
    args = parser.parse_args()

    lookback = int(os.environ.get("SLACK_LOOKBACK_HOURS", "24"))
    stale = int(os.environ.get("SLACK_DM_STALE_HOURS", "24"))

    if args.which == "mentions":
        result = fetch_mentions(lookback)[: args.limit]
    elif args.which == "dms":
        result = fetch_dms(stale)[: args.limit]
    else:
        result = {
            "mentions": fetch_mentions(lookback)[: args.limit],
            "dms":      fetch_dms(stale)[: args.limit],
        }
        result["counts"] = {
            "mentions": len(result["mentions"]),
            "dms":      len(result["dms"]),
        }

    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
