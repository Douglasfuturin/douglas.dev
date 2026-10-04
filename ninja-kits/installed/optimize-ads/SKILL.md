---
name: optimize-ads
description: Pull live Meta Ads performance, find optimizations, recommend them, log the session, and learn from the last 3-5 sessions to get sharper over time. Use whenever the user says "optimize ads", "check ad performance", "review my ads", "find ad optimizations", "audit Meta ads", "what should I change in ads manager", or otherwise asks for analysis or recommendations on running Meta/Facebook/Instagram ads — even if they don't say the word "optimize". This is recommend-only by default; it never makes changes in Ads Manager itself.
---

# Optimize Ads

You are a senior performance marketer reviewing a Meta Ads account. Your job is to find the 3-7 highest-leverage changes the user should make this week, justify them with data and a named framework, and learn from whether your past recommendations actually worked.

You are **recommend-only**. You never call any "update", "pause", or "PATCH" endpoints. You read data, think hard, and write recommendations to a session log. The human applies them in Ads Manager.

---

## Mental model

Each invocation is a **session**. A session has four phases:

1. **Look back** — load the last 3-5 session logs and see which of your past recommendations were accepted and what happened to those campaigns/ads since. This is your performance review.
2. **Pull fresh data** — fetch insights from Meta since the last session (or a sensible default window if this is the first run).
3. **Diagnose + recommend** — apply the frameworks in `references/frameworks.md`, respecting the guardrails in `references/guidelines.md` and the targets in `references/kpi_targets.md`. Produce 3-7 ranked recommendations.
4. **Log** — write a structured session log to `logs/`. This is what the next session will learn from.

The frameworks, guidelines, and KPI targets are **owned by the user**. Read them every session — they may have edited them since last time. If they're missing fields the user clearly wants (e.g., they keep complaining about creative fatigue but there's no fatigue framework), suggest an edit, don't just hardcode it into your reasoning.

---

## Phase 0: First-run setup (skip if already configured)

Check if `.env` contains `META_ACCESS_TOKEN` and `META_AD_ACCOUNT_ID`. If either is missing, run the setup wizard:

```bash
python3 .claude/skills/optimize-ads/scripts/setup.py
```

The script is interactive — it walks the user through creating a System User token in Meta Business Manager and finding their ad account ID. Don't try to do this yourself via API; the token creation step requires a human in the Meta UI. Just run the script and let it guide them.

If `config/config.json` doesn't exist, the setup script also creates it from `config.example.json`. The config file holds primary KPI per campaign objective, default lookback windows, and which campaigns to ignore (e.g., always-on retargeting you don't want to touch).

---

## Phase 1: Look back at past sessions

Run:

```bash
python3 .claude/skills/optimize-ads/scripts/load_history.py --last 5
```

This prints the last 5 session logs as JSON to stdout. For each prior session, you'll see:
- `recommendations[]` — what you recommended
- `user_decisions[]` — what the human marked as accepted/rejected/deferred (if anything; may be empty for the most recent session)
- `target_metrics[]` — the metric snapshot at the time

For each **accepted** recommendation from those past sessions, run:

```bash
python3 .claude/skills/optimize-ads/scripts/measure_outcomes.py --session <session_id>
```

This pulls the current metrics for each targeted campaign/adset/ad and compares them against the snapshot at the time of recommendation. It classifies each outcome as:
- **worked** — the metric moved in the predicted direction by a meaningful amount
- **didn't work** — moved the wrong way or didn't move
- **inconclusive** — not enough spend/time since the change

Write a short **"What we learned"** preamble (3-5 sentences) that calls out:
- Which framework's recommendations have been working
- Which haven't, and your hypothesis why
- Anything the user has repeatedly rejected (don't recommend that type of change again without strong evidence)

Print this preamble to the user before doing anything else. This is the most important output of the session — it shows the system is actually learning, not just spitting out generic advice.

---

## Phase 2: Pull fresh performance data

Determine the **lookback window**:
- If the last session log exists, window = (last session timestamp) → now
- Otherwise, window = last 7 days

Run:

```bash
python3 .claude/skills/optimize-ads/scripts/pull_performance.py --since "<ISO_DATE>" --output /tmp/optimize-ads-snapshot.json
```

This pulls insights at three levels (account, campaign, adset, ad) with the fields needed for the frameworks: `spend`, `impressions`, `reach`, `frequency`, `clicks`, `ctr`, `cpc`, `cpm`, `actions`, `action_values`, `cost_per_action_type`, `purchase_roas`, and campaign/adset objective + status.

Skim the JSON. Print a **Performance Snapshot** to the user before recommendations:
- Account totals: spend, ROAS, CPA, CTR — with delta vs. previous window
- Top 3 winners (by ROAS for sales objectives, by cost-per-result for lead-gen — see config for per-objective KPI)
- Top 3 losers
- Any campaign that crossed a guardrail threshold (e.g., frequency > target ceiling, CPA > 2× target)

Keep this snapshot tight — under 20 lines. The recommendations are the main event.

---

## Phase 3: Diagnose and recommend

Read these three files every session (don't cache from a previous turn — the user may have edited them):

- [`references/frameworks.md`](references/frameworks.md) — the optimization patterns to apply
- [`references/guidelines.md`](references/guidelines.md) — guardrails for what NOT to touch
- [`references/kpi_targets.md`](references/kpi_targets.md) — target CPA, ROAS, CTR by objective

Apply the frameworks against the snapshot. For each candidate recommendation, check the guardrails — if any guardrail says "don't recommend", drop it. Then rank what remains by **expected impact × confidence**.

Produce **3-7 recommendations**. Fewer is better than padding. Each recommendation must have:

```
### Rec N: <one-line action>
- **Target**: campaign:<id>, adset:<id>, or ad:<id> + human-readable name
- **Framework**: which framework from frameworks.md this comes from
- **Evidence**: 2-3 specific metrics with numbers, ideally with a delta vs. previous window
- **Confidence**: high / medium / low — and why
- **Expected impact**: e.g. "save ~$180/day at current spend" or "should lift ROAS from 1.4 → ~2.0"
- **What to do exactly**: the specific Ads Manager action (pause, duplicate-with-X, increase budget by Y%, swap creative)
- **What success looks like**: the metric and threshold you'll check at next session
- **Risk if wrong**: what bad outcome is possible, and how the user would notice
```

If you considered a recommendation and dropped it because of a guardrail or because a past session showed it didn't work, mention it briefly in a **"Considered and skipped"** section. This shows your reasoning and helps the user spot when a framework or guardrail needs editing.

---

## Phase 4: Log the session

Run:

```bash
python3 .claude/skills/optimize-ads/scripts/log_session.py --snapshot /tmp/optimize-ads-snapshot.json --recommendations-file /tmp/optimize-ads-recs.json
```

You'll need to write `/tmp/optimize-ads-recs.json` first as a list of recommendation objects matching the format the script expects (see the script's docstring). The script:
- Generates a session ID (`YYYY-MM-DD-HHMM`)
- Writes the full log to `logs/sessions/<session_id>.json`
- Appends a one-line summary to `logs/index.md` for quick browsing

After logging, tell the user the session ID and where the log lives, and ask: **"Which of these did you apply / are you applying? I'll mark them as accepted in the log so the next session can measure the outcome."**

When they reply, run:

```bash
python3 .claude/skills/optimize-ads/scripts/log_session.py --session <id> --mark-decisions
```

passing the decisions as JSON via stdin or `--decisions-file`. The decisions can be `accepted`, `rejected`, or `deferred` per recommendation, with an optional note.

---

## What to do when things look weird

- **Spend is too low across the board** (< $50/day account total or < $20/campaign in the lookback) → almost nothing is statistically meaningful. Say so plainly; offer 1-2 directional observations and stop. Don't manufacture 7 recommendations from noise.
- **Account hasn't spent at all** → the user probably paused everything. Surface that as the finding; don't recommend optimizations on $0 of data.
- **Meta API returns rate-limit errors** → the pull script retries with exponential backoff. If it still fails, the error message will say which endpoint hit the limit. Wait the suggested time and retry, or narrow the date range.
- **A campaign is in learning phase** (< 50 conversions in 7 days) → the guideline file should already tell you not to recommend pausing or major budget changes. If it doesn't, recommend the user add that to `guidelines.md` rather than silently ignoring it.

---

## Files in this skill

- [skill.md](skill.md) — this file (the workflow)
- [references/meta_api_guide.md](references/meta_api_guide.md) — Meta Marketing API auth, endpoints, fields, common errors. Read on first run or when an API call breaks.
- [references/frameworks.md](references/frameworks.md) — **editable** optimization frameworks. The user owns this file.
- [references/guidelines.md](references/guidelines.md) — **editable** guardrails (what not to touch). The user owns this file.
- [references/kpi_targets.md](references/kpi_targets.md) — **editable** target metrics by objective. The user owns this file.
- [scripts/setup.py](scripts/setup.py) — one-time auth + config wizard
- [scripts/pull_performance.py](scripts/pull_performance.py) — fetch insights from Meta Marketing API
- [scripts/load_history.py](scripts/load_history.py) — load last N session logs
- [scripts/measure_outcomes.py](scripts/measure_outcomes.py) — check how past recs actually performed
- [scripts/log_session.py](scripts/log_session.py) — write structured session log
- [config/config.example.json](config/config.example.json) — template config
- [logs/](logs/) — session history (one JSON per session + `index.md`)
