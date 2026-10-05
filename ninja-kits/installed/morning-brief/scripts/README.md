# morning-brief — data scripts

Standardized data fetchers and scanners that feed the morning-brief skill. Every script writes JSON to stdout — the skill orchestrates them and synthesizes the brief.

Seven scripts:

| Script | Source | What it returns |
|---|---|---|
| `fetch_calendar.py` | Google Calendar API | Today's events / next-21-days high-stakes events with classification |
| `enrich_with_prep.py` | Local files | Adds `prep_status` to calendar events by cross-referencing `/agents/executive/log/` |
| `fetch_gmail.py` | Gmail API | 3-pass follow-up sweep (overnight / incoming / outgoing) |
| `fetch_slack.py` | Slack Web API | @mentions in last 24h + unanswered DMs |
| `aggregate_snapshots.py` | Local files | Merged daily snapshots from every brain + missing-snapshot flags |
| `scan_goals.py` | Local files | Active goals + pace/freshness classification |
| `scan_tripwires.py` | Local files | Decision tripwires firing in next N days |

---

## One-time setup

### Install Python deps

```bash
pip install -r .claude/skills/morning-brief/scripts/requirements.txt
```

### Google Cloud OAuth (calendar + gmail share one client)

1. https://console.cloud.google.com → create / pick project for [CLIENT NAME]
2. Enable APIs: **Google Calendar API** and **Gmail API**
3. APIs & Services → Credentials → Create Credentials → **OAuth client ID** → Desktop app
4. Download to `credentials/google_client_secret.json` (gitignore this directory)

### Slack tokens

For mentions across the workspace you need a **user token** (`xoxp-...`) with `search:read` scope. For DMs + channel messages a bot token (`xoxb-...`) with `im:history`, `channels:history`, `groups:history`, `users:read` works.

Create at https://api.slack.com/apps → your app → OAuth & Permissions.

### .env at workspace root

```bash
# Google (shared by calendar + gmail)
GOOGLE_CREDENTIALS_PATH="credentials/google_client_secret.json"
GOOGLE_TOKEN_PATH="credentials/google_calendar_token.json"
GMAIL_TOKEN_PATH="credentials/gmail_token.json"
GOOGLE_CALENDAR_ID="primary"
FOUNDER_DOMAINS="[FOUNDER DOMAIN].com"

# Gmail extras
GMAIL_VIP_SENDERS="investor@vc.com,key-customer@acme.com"
GMAIL_NEWSLETTER_FILTERS="@beehiiv.com,@substack.com"

# Slack
SLACK_BOT_TOKEN="xoxb-..."
SLACK_USER_TOKEN="xoxp-..."   # for mentions search
SLACK_USER_ID="U0XXXXXX"
SLACK_LOOKBACK_HOURS="24"
SLACK_DM_STALE_HOURS="24"

# Local data
SHARED_CONTEXT_ROOT="shared-context"
EXECUTIVE_LOG_ROOT="agents/executive/log"
GOALS_ROOT="agents/executive/goals"
DECISIONS_ROOT="agents/executive/log/decisions"
```

First run of any Google script opens a browser for OAuth consent. Token caches to disk and is reused.

---

## Usage — the full morning-brief pipeline

All seven scripts run in parallel during a brief generation. The skill calls them and synthesizes. Example invocations:

```bash
# Block 2 — what changed (snapshots + deltas vs yesterday)
python scripts/aggregate_snapshots.py --compare-to yesterday

# Block 3 — today's calendar
python scripts/fetch_calendar.py --today

# Block 4 — lookahead (calendar + goals + tripwires + email/slack follow-ups)
python scripts/fetch_calendar.py --lookahead 21 | python scripts/enrich_with_prep.py
python scripts/scan_goals.py --only-flagged
python scripts/scan_tripwires.py --window 7
python scripts/fetch_gmail.py --pass outgoing      # for "owed replies"

# Email follow-up sweep (used in the brief's email callouts)
python scripts/fetch_gmail.py --pass all --limit 5

# Slack — mentions and unanswered DMs
python scripts/fetch_slack.py --pass all
```

---

## Script-by-script

### `fetch_calendar.py`
```
--today                Today's events, full day, [FOUNDER NAME]'s timezone
--lookahead DAYS       Events in next N days, high-stakes only
  [--include-all]      Include everything in window, not just high-stakes
```

Classifies each event: `investor / sales / partner / vendor / team / 1:1 / first-time / personal / unknown`. Flags `is_high_stakes` based on title keywords (board, launch, signing, pitch, etc.), 2+ external attendees, or `[prep:yes]` tag in description.

### `enrich_with_prep.py`
Stdin → stdout filter. Reads `fetch_calendar.py` output, adds:
- `prep_status`: `ready / stale / in_progress / missing / not_needed`
- `prep_file`: path to the prep doc if one exists
- `prep_age_days`: how stale
- `days_until`: days from now to event

Surfaces `missing` and `stale` in Block 4 of the brief.

### `fetch_gmail.py`
```
--pass overnight       Unread / starred / important in last 18 hrs
--pass incoming        Threads where someone is waiting on [FOUNDER NAME] (7d)
--pass outgoing        Threads where [FOUNDER NAME] sent and got crickets (14d)
--pass all             All three, returned together
--limit N              Cap per pass (default 5)
```

`incoming` pass uses a question-detection heuristic (`can you`, `let me know`, `please review`, `?`) plus VIP/starred boost so [FOUNDER NAME] only sees emails actually asking for something.

`outgoing` pass surfaces threads where [FOUNDER NAME]'s last message was 2+ days ago AND included a question or deadline reference — the "you sent and got crickets, want to nudge?" detection.

### `fetch_slack.py`
```
--pass mentions        @[FOUNDER NAME] in last N hours across channels
--pass dms             Unanswered DMs (last msg not from founder, age > threshold)
--pass all             Both
```

Requires `SLACK_USER_TOKEN` for the mentions pass (Slack search is user-token only).

### `aggregate_snapshots.py`
```
--date YYYY-MM-DD          Date to read (default today)
--compare-to yesterday|N   Compute deltas vs that date
```

Returns:
- `brains`: every snapshot found, keyed by filename stem
- `meta.missing_snapshots`: list of expected snapshots not present (so the brief can explicitly call out "Finance snapshot missing — cash is from 2 days ago")
- `deltas`: per-brain numeric deltas vs the compare date

### `scan_goals.py`
```
--only-flagged    Return only goals with status_flag set
```

Reads goal markdown files with frontmatter (`name`, `target_value`, `current_value`, `target_date`, `status`, `last_update`, `cadence_days`). Computes:
- `pace`: on / slipping / off / unknown
- `freshness`: fresh / stale / very_stale
- `flag`: `milestone_soon_no_progress` / `off_pace_no_touch` / `stale_30d` / null

The brief surfaces every goal with a `flag` set.

### `scan_tripwires.py`
```
--window N        Days ahead to scan (default 7)
```

Reads decision memos in `/agents/executive/log/decisions/` with `tripwire_date` frontmatter or a "## Tripwires & kill criteria" section. Returns the ones firing in the window. Skipped if `status: killed` or `status: held`.

---

## Output schemas

Every script's full schema is documented at the top of its file. Run with `--help` for usage.

---

## Customization knobs

- **Calendar classification** — edit `KEYWORDS` and `HIGH_STAKES_TITLE_TOKENS` in `fetch_calendar.py`
- **Email question detection** — edit `QUESTION_MARKERS` in `fetch_gmail.py`
- **Newsletter filters** — env var `GMAIL_NEWSLETTER_FILTERS` (comma-separated patterns)
- **Expected snapshots** — env var `EXPECTED_SNAPSHOTS` (comma-separated filenames)
- **Goal frontmatter format** — `scan_goals.py` reads simple `key: value` frontmatter; if [CLIENT NAME] uses Notion / Linear / something else, swap the parsing function
- **Tripwire format** — same; structured frontmatter preferred, body-section fallback

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| "Missing Google API deps" | `pip install -r requirements.txt` |
| Calendar API 403 | Token missing calendar scope — delete token and re-auth |
| Gmail API 403 | Token missing gmail.readonly — delete token and re-auth |
| Slack mentions empty | Bot token used; need user token with `search:read` |
| Lookahead always empty | Default returns high-stakes only; pass `--include-all` |
| `prep_status` always "missing" | Wrong `EXECUTIVE_LOG_ROOT` |
| `is_external` wrong | Set `FOUNDER_DOMAINS` to internal domains |
| Goal pace always "unknown" | Goal frontmatter missing `target_value` / `current_value` / `target_date` |
| Snapshots empty | Snapshot directory doesn't exist yet — prefetch routine hasn't run |
