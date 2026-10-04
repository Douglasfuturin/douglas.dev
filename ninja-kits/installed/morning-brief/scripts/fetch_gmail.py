#!/usr/bin/env python3
"""
fetch_gmail.py — three-pass Gmail follow-up sweep for the morning-brief skill.

Runs the three passes spec'd in SKILL.md:
  --pass overnight    Unread / starred / important in the last 18 hrs
  --pass incoming     Threads where someone is waiting on [FOUNDER NAME] (last 7 days)
  --pass outgoing     Threads where [FOUNDER NAME] sent and got crickets (last 14 days)
  --pass all          Run all three and return a single combined object

Returns JSON to stdout. Total result cap is 5 items per pass by default
(--limit N to override), matching the brief's "cap at 5 in the email block" rule.

Schema returned (when --pass all):
  {
    "overnight":  [<thread>],   # priority order — most signal first
    "incoming":   [<thread>],
    "outgoing":   [<thread>],
    "counts":     {"overnight": N, "incoming": N, "outgoing": N}
  }

A <thread> item:
  {
    "id":              str,
    "subject":         str,
    "snippet":         str,
    "from":            "<name> <email>",
    "to":              [str],
    "last_message_at": ISO8601 str,
    "age_days":        int,
    "age_hours":       int | None,   # for overnight only
    "is_unread":       bool,
    "is_starred":      bool,
    "is_vip":          bool,         # sender in VIP list
    "has_question":    bool,         # heuristic — looks for ?, "can you", etc.
    "question_phrase": str | None,   # the matched phrase
    "permalink":       str
  }

Env vars (extends the calendar script):
  GMAIL_CREDENTIALS_PATH    Path to OAuth client_secret.json (can be same as calendar)
  GMAIL_TOKEN_PATH          Path to cached token.json (separate from calendar token)
  GMAIL_VIP_SENDERS         Comma-separated email addresses [FOUNDER NAME] cares about
  GMAIL_NEWSLETTER_FILTERS  Comma-separated From: patterns to drop (e.g.
                            "noreply@,@substack.com,@beehiiv.com")
"""

from __future__ import annotations

import argparse
import base64
import email.utils
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    sys.stderr.write(
        "Missing Google API deps. Install with:\n"
        "  pip install -r scripts/requirements.txt\n"
    )
    sys.exit(2)

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

# Heuristic for "someone is asking [FOUNDER NAME] something".
# Tuned to be specific — false positives are worse than false negatives here.
QUESTION_MARKERS = [
    r"\bcan you\b", r"\bcould you\b", r"\bwould you\b",
    r"\bwhen works\b", r"\bwhen are you\b", r"\blet me know\b",
    r"\byour thoughts\b", r"\bplease (review|sign|approve|confirm)\b",
    r"\bawaiting\b", r"\bwaiting on\b", r"\bfollowing up\b",
    r"\bany update\b", r"\bcircle back\b", r"\bthoughts\?",
    r"\?$",  # ends with a question mark (looks at snippet)
]

# Things that look like newsletters/automated and should always be dropped
DEFAULT_NEWSLETTER_PATTERNS = [
    "noreply@", "no-reply@", "donotreply@", "mailer-daemon@",
    "@substack.com", "@beehiiv.com", "@convertkit.com",
    "notifications@", "alerts@", "billing@",
]


def load_credentials() -> Credentials:
    token_path = os.environ.get("GMAIL_TOKEN_PATH", "credentials/gmail_token.json")
    creds_path = os.environ.get(
        "GMAIL_CREDENTIALS_PATH",
        os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials/google_client_secret.json"),
    )

    creds = None
    if Path(token_path).exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(creds_path).exists():
                sys.stderr.write(
                    f"No OAuth client secret at {creds_path}. "
                    f"Set GMAIL_CREDENTIALS_PATH (or GOOGLE_CREDENTIALS_PATH).\n"
                )
                sys.exit(2)
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(token_path).parent.mkdir(parents=True, exist_ok=True)
        Path(token_path).write_text(creds.to_json())

    return creds


def get_vip_set() -> set[str]:
    raw = os.environ.get("GMAIL_VIP_SENDERS", "")
    return {e.strip().lower() for e in raw.split(",") if e.strip()}


def get_newsletter_patterns() -> list[str]:
    extra = os.environ.get("GMAIL_NEWSLETTER_FILTERS", "")
    extras = [p.strip().lower() for p in extra.split(",") if p.strip()]
    return DEFAULT_NEWSLETTER_PATTERNS + extras


def looks_automated(from_header: str, patterns: list[str]) -> bool:
    lower = from_header.lower()
    return any(p in lower for p in patterns)


def find_question(text: str) -> str | None:
    for pat in QUESTION_MARKERS:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(0)
    return None


def header(msg: dict, name: str) -> str:
    for h in msg.get("payload", {}).get("headers", []):
        if h["name"].lower() == name.lower():
            return h["value"]
    return ""


def parse_date(date_header: str) -> datetime | None:
    if not date_header:
        return None
    try:
        return email.utils.parsedate_to_datetime(date_header)
    except (TypeError, ValueError):
        return None


def fetch_messages(service, query: str, max_results: int = 25) -> list[dict]:
    """List messages matching query, then fetch each one with metadata format."""
    try:
        listing = service.users().messages().list(
            userId="me", q=query, maxResults=max_results
        ).execute()
    except HttpError as err:
        sys.stderr.write(f"Gmail API error (list): {err}\n")
        return []

    ids = [m["id"] for m in listing.get("messages", [])]
    messages: list[dict] = []
    for mid in ids:
        try:
            msg = service.users().messages().get(
                userId="me", id=mid,
                format="metadata",
                metadataHeaders=["From", "To", "Subject", "Date"],
            ).execute()
            messages.append(msg)
        except HttpError as err:
            sys.stderr.write(f"Gmail API error (get {mid}): {err}\n")
    return messages


def fetch_thread_last_message(service, thread_id: str) -> dict | None:
    """Get the last message in a thread (cheap — metadata only)."""
    try:
        thread = service.users().threads().get(
            userId="me", id=thread_id,
            format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"],
        ).execute()
    except HttpError as err:
        sys.stderr.write(f"Gmail API error (thread {thread_id}): {err}\n")
        return None
    msgs = thread.get("messages", [])
    return msgs[-1] if msgs else None


def get_user_email(service) -> str:
    profile = service.users().getProfile(userId="me").execute()
    return profile.get("emailAddress", "").lower()


def normalize_message(
    msg: dict, founder_email: str, vips: set[str], patterns: list[str],
    include_question_check: bool = True,
) -> dict[str, Any] | None:
    from_h = header(msg, "From")
    to_h = header(msg, "To")
    subject = header(msg, "Subject")
    date_h = header(msg, "Date")
    snippet = msg.get("snippet", "")

    if looks_automated(from_h, patterns):
        return None

    dt = parse_date(date_h)
    if not dt:
        return None
    now = datetime.now(timezone.utc)
    age = now - dt

    labels = msg.get("labelIds", [])
    is_unread = "UNREAD" in labels
    is_starred = "STARRED" in labels
    from_email = _extract_email(from_h)
    is_vip = bool(from_email and from_email in vips)

    question = find_question(snippet + " " + subject) if include_question_check else None

    return {
        "id": msg.get("id"),
        "thread_id": msg.get("threadId"),
        "subject": subject or "(no subject)",
        "snippet": snippet,
        "from": from_h,
        "to": [t.strip() for t in to_h.split(",") if t.strip()],
        "last_message_at": dt.isoformat(),
        "age_days": age.days,
        "age_hours": int(age.total_seconds() / 3600) if age.days < 2 else None,
        "is_unread": is_unread,
        "is_starred": is_starred,
        "is_vip": is_vip,
        "has_question": bool(question),
        "question_phrase": question,
        "permalink": f"https://mail.google.com/mail/u/0/#inbox/{msg.get('threadId')}",
    }


def _extract_email(header_value: str) -> str:
    m = re.search(r"<([^>]+)>", header_value)
    if m:
        return m.group(1).lower()
    if "@" in header_value:
        return header_value.strip().lower()
    return ""


def pass_overnight(service, founder_email: str, vips: set[str],
                   patterns: list[str], limit: int) -> list[dict]:
    """Pass A: unread / starred / VIP in last 18 hours."""
    query = "(is:unread OR is:starred OR is:important) newer_than:1d"
    msgs = fetch_messages(service, query, max_results=50)
    normalized = []
    for msg in msgs:
        n = normalize_message(msg, founder_email, vips, patterns, include_question_check=False)
        if n and n["age_hours"] is not None and n["age_hours"] <= 18:
            normalized.append(n)
    # VIP / starred / question-bearing first, then by recency
    normalized.sort(key=lambda m: (
        not m["is_vip"], not m["is_starred"], not m["is_unread"], m["age_hours"]
    ))
    return normalized[:limit]


def pass_incoming(service, founder_email: str, vips: set[str],
                  patterns: list[str], limit: int) -> list[dict]:
    """Pass B: threads where someone is waiting on [FOUNDER NAME]."""
    # newer_than:7d, not from founder, in inbox
    query = f"-from:me in:inbox newer_than:7d"
    msgs = fetch_messages(service, query, max_results=50)

    # Group by thread, find threads where the most recent message is not from founder
    by_thread: dict[str, dict] = {}
    for msg in msgs:
        tid = msg.get("threadId")
        if tid not in by_thread:
            by_thread[tid] = msg

    candidates = []
    for tid in by_thread:
        last = fetch_thread_last_message(service, tid)
        if not last:
            continue
        from_email = _extract_email(header(last, "From"))
        if not from_email or from_email == founder_email:
            continue  # founder already replied
        n = normalize_message(last, founder_email, vips, patterns, include_question_check=True)
        if not n:
            continue
        # Only surface if there's a question / ask / it's VIP / it's starred
        if n["has_question"] or n["is_vip"] or n["is_starred"]:
            candidates.append(n)

    # Oldest unanswered first — those are the most overdue
    candidates.sort(key=lambda m: (not m["is_vip"], -m["age_days"]))
    return candidates[:limit]


def pass_outgoing(service, founder_email: str, vips: set[str],
                  patterns: list[str], limit: int) -> list[dict]:
    """Pass C: threads where [FOUNDER NAME] sent and got crickets."""
    query = "from:me newer_than:14d"
    msgs = fetch_messages(service, query, max_results=50)

    by_thread: dict[str, dict] = {}
    for msg in msgs:
        tid = msg.get("threadId")
        if tid not in by_thread or msg.get("internalDate", 0) > by_thread[tid].get("internalDate", 0):
            by_thread[tid] = msg

    candidates = []
    for tid in by_thread:
        last = fetch_thread_last_message(service, tid)
        if not last:
            continue
        last_from = _extract_email(header(last, "From"))
        if last_from != founder_email:
            continue  # someone replied, not crickets
        # The last message in the thread is from the founder — no reply yet
        n = normalize_message(last, founder_email, vips, patterns, include_question_check=False)
        if not n:
            continue
        if n["age_days"] < 2:
            continue  # too fresh to nudge
        # Surface only if VIP recipient, asked a question, or referenced a date
        if n["is_vip"] or find_question(n["snippet"]) or _references_deadline(n["snippet"]):
            n["nudge_age_days"] = n["age_days"]
            candidates.append(n)

    candidates.sort(key=lambda m: (not m["is_vip"], -m["age_days"]))
    return candidates[:limit]


def _references_deadline(text: str) -> bool:
    patterns = [
        r"\bby (mon|tue|wed|thu|fri|sat|sun)", r"\bby (jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)",
        r"\bby end of (week|month|quarter)", r"\bbefore (next|this) (week|month)",
        r"\beod\b", r"\beow\b", r"\beom\b", r"\bdeadline\b",
    ]
    return any(re.search(p, text, flags=re.IGNORECASE) for p in patterns)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pass", dest="which",
                        choices=["overnight", "incoming", "outgoing", "all"],
                        required=True,
                        help="Which sweep pass to run")
    parser.add_argument("--limit", type=int, default=5,
                        help="Max items per pass (default 5)")
    args = parser.parse_args()

    creds = load_credentials()
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    founder_email = get_user_email(service)
    vips = get_vip_set()
    patterns = get_newsletter_patterns()

    runners = {
        "overnight": pass_overnight,
        "incoming":  pass_incoming,
        "outgoing":  pass_outgoing,
    }

    if args.which == "all":
        result = {
            "overnight": pass_overnight(service, founder_email, vips, patterns, args.limit),
            "incoming":  pass_incoming(service, founder_email, vips, patterns, args.limit),
            "outgoing":  pass_outgoing(service, founder_email, vips, patterns, args.limit),
        }
        result["counts"] = {k: len(v) for k, v in result.items() if isinstance(v, list)}
        json.dump(result, sys.stdout, indent=2)
    else:
        result = runners[args.which](service, founder_email, vips, patterns, args.limit)
        json.dump(result, sys.stdout, indent=2)

    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
