#!/usr/bin/env python3
"""
fetch_calendar.py — standardized Google Calendar fetch for the morning-brief skill.

Two modes:
  --today                 Today's events (full day, [FOUNDER NAME]'s timezone)
  --lookahead DAYS        Events in the next DAYS days, only ones the brief cares about
                          (external, high-stakes, first-time, prep-flagged)

Outputs JSON to stdout. Designed to be consumed by morning-brief/SKILL.md.

Env vars (set in .env at the repo root or workspace):
  GOOGLE_CALENDAR_ID        Target calendar — defaults to "primary"
  GOOGLE_CREDENTIALS_PATH   Path to OAuth client_secret.json (for first-time auth)
  GOOGLE_TOKEN_PATH         Path to cached token.json (created on first run)
  FOUNDER_DOMAINS           Comma-separated internal domains (e.g. "acme.com,acme.co")
                            used to flag attendees as external

First run is interactive (opens a browser for OAuth). Subsequent runs use the
cached token.

Schema returned (JSON list of events):
  {
    "id":            str,
    "title":         str,
    "start":         ISO8601 str,
    "end":           ISO8601 str,
    "duration_min":  int,
    "location":      str | None,
    "meet_link":     str | None,
    "description":   str | None,
    "attendees":     [{"email": str, "name": str, "is_external": bool, "response": str}],
    "is_external":   bool,    # any external attendee
    "is_recurring":  bool,
    "classified_type": "sales" | "investor" | "partner" | "vendor" |
                       "team" | "1:1" | "first-time" | "personal" | "unknown",
    "is_high_stakes": bool,
    "prep_keywords": [str],   # title tokens used by skill to look up prior prep
    "html_link":     str
  }
"""

from __future__ import annotations

import argparse
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

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

# Keyword sets used to classify event type and high-stakes flag.
# Edit these during onboarding to fit [CLIENT NAME]'s vocabulary.
KEYWORDS = {
    "investor":   ["board", "investor", "lp", "vc", "demo day", "fundraise", "pitch deck"],
    "sales":      ["demo", "discovery", "pricing", "renewal", "qbr", "deal review",
                   "prospect", "customer call"],
    "partner":    ["partnership", "partner", "collab", "alliance", "intro", "exploration"],
    "vendor":     ["vendor", "agency", "renewal review", "contract", "msa", "sow"],
    "team":       ["standup", "weekly", "team", "all-hands", "sprint", "retro"],
    "1:1":        ["1:1", "1on1", "1-on-1", "one on one"],
}

# Title tokens that always indicate a high-stakes external meeting,
# regardless of attendee count.
HIGH_STAKES_TITLE_TOKENS = [
    "board", "investor", "kickoff", "launch", "signing", "contract",
    "pitch", "demo day", "earnings", "press", "podcast", "interview",
    "negotiation", "termination", "review with", "presentation to",
]


def load_credentials() -> Credentials:
    """Load OAuth credentials, refreshing or running flow as needed."""
    token_path = os.environ.get("GOOGLE_TOKEN_PATH", "credentials/google_token.json")
    creds_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials/google_client_secret.json")

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
                    f"Set GOOGLE_CREDENTIALS_PATH or place a client_secret.json there.\n"
                )
                sys.exit(2)
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        Path(token_path).parent.mkdir(parents=True, exist_ok=True)
        Path(token_path).write_text(creds.to_json())

    return creds


def get_internal_domains() -> set[str]:
    raw = os.environ.get("FOUNDER_DOMAINS", "")
    return {d.strip().lower() for d in raw.split(",") if d.strip()}


def classify_event(event: dict, internal_domains: set[str]) -> tuple[str, bool, list[str]]:
    """Return (classified_type, is_high_stakes, prep_keywords)."""
    title = (event.get("summary") or "").lower()
    description = (event.get("description") or "").lower()
    haystack = f"{title} {description}"
    attendees = event.get("attendees", []) or []

    # Strip [FOUNDER NAME] from organizer-side attendee list when counting
    external_count = sum(
        1 for a in attendees
        if not is_internal(a.get("email", ""), internal_domains)
        and not a.get("self", False)
    )

    classified = "unknown"
    for label, terms in KEYWORDS.items():
        if any(t in haystack for t in terms):
            classified = label
            break

    if classified == "unknown":
        if external_count == 0 and len(attendees) > 1:
            classified = "team"
        elif external_count == 0 and len(attendees) <= 2:
            classified = "1:1"
        elif external_count >= 1:
            classified = "first-time"  # external but unrecognized — treat carefully
        else:
            classified = "personal"

    # High-stakes signals
    is_high_stakes = (
        classified in ("investor", "first-time")
        or any(tok in haystack for tok in HIGH_STAKES_TITLE_TOKENS)
        or external_count >= 2
        or _duration_minutes(event) >= 120 and external_count >= 1
        or "[prep:yes]" in (event.get("description") or "").lower()
    )

    # Extract title tokens that future-you can use to look up prep notes
    prep_keywords = _tokenize(event.get("summary") or "")

    return classified, is_high_stakes, prep_keywords


def is_internal(email: str, internal_domains: set[str]) -> bool:
    if not email or not internal_domains:
        return False
    domain = email.split("@", 1)[-1].lower()
    return domain in internal_domains


def _duration_minutes(event: dict) -> int:
    start = event.get("start", {}).get("dateTime")
    end = event.get("end", {}).get("dateTime")
    if not start or not end:
        return 0
    s = datetime.fromisoformat(start.replace("Z", "+00:00"))
    e = datetime.fromisoformat(end.replace("Z", "+00:00"))
    return int((e - s).total_seconds() / 60)


def _tokenize(title: str) -> list[str]:
    # Lowercase, strip emoji and punctuation, drop very short tokens.
    cleaned = re.sub(r"[^\w\s]", " ", title.lower())
    return [t for t in cleaned.split() if len(t) > 2]


def normalize_event(event: dict, internal_domains: set[str]) -> dict[str, Any]:
    start = event.get("start", {})
    end = event.get("end", {})
    start_iso = start.get("dateTime") or start.get("date")
    end_iso = end.get("dateTime") or end.get("date")

    attendees = []
    for a in event.get("attendees", []) or []:
        email = a.get("email", "")
        attendees.append({
            "email": email,
            "name": a.get("displayName", ""),
            "is_external": not is_internal(email, internal_domains) and not a.get("self", False),
            "response": a.get("responseStatus", "needsAction"),
        })

    classified, high_stakes, prep_keywords = classify_event(event, internal_domains)

    return {
        "id": event.get("id"),
        "title": event.get("summary", "(no title)"),
        "start": start_iso,
        "end": end_iso,
        "duration_min": _duration_minutes(event),
        "location": event.get("location"),
        "meet_link": _extract_meet_link(event),
        "description": event.get("description"),
        "attendees": attendees,
        "is_external": any(a["is_external"] for a in attendees),
        "is_recurring": bool(event.get("recurringEventId")),
        "classified_type": classified,
        "is_high_stakes": high_stakes,
        "prep_keywords": prep_keywords,
        "html_link": event.get("htmlLink"),
    }


def _extract_meet_link(event: dict) -> str | None:
    if "hangoutLink" in event:
        return event["hangoutLink"]
    cep = event.get("conferenceData", {}).get("entryPoints", [])
    for ep in cep:
        if ep.get("entryPointType") == "video":
            return ep.get("uri")
    return None


def fetch_events(time_min: datetime, time_max: datetime) -> list[dict]:
    creds = load_credentials()
    service = build("calendar", "v3", credentials=creds, cache_discovery=False)
    calendar_id = os.environ.get("GOOGLE_CALENDAR_ID", "primary")

    try:
        result = service.events().list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy="startTime",
            maxResults=250,
        ).execute()
    except HttpError as err:
        sys.stderr.write(f"Calendar API error: {err}\n")
        sys.exit(1)

    return result.get("items", [])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--today", action="store_true", help="Fetch today's events only")
    group.add_argument("--lookahead", type=int, metavar="DAYS",
                       help="Fetch high-stakes events in next N days")
    parser.add_argument("--include-all", action="store_true",
                        help="With --lookahead, include all events, not just high-stakes")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    internal_domains = get_internal_domains()

    if args.today:
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        events = fetch_events(start_of_day, end_of_day)
        normalized = [normalize_event(e, internal_domains) for e in events]
    else:
        time_min = now
        time_max = now + timedelta(days=args.lookahead)
        events = fetch_events(time_min, time_max)
        normalized = [normalize_event(e, internal_domains) for e in events]
        if not args.include_all:
            normalized = [e for e in normalized if e["is_high_stakes"]]

    json.dump(normalized, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
