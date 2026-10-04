---
name: morning-brief
description: Generate [FOUNDER NAME]'s daily executive brief — a five-minute, decision-first, evidence-cited intelligence product for [CLIENT NAME]. Decisions today → what changed overnight → today's calendar → **proactive 2-3 week lookahead** (upcoming board / investor / launch events with prep status, stale goals, firing tripwires, owed replies) → goals → risks → closing line. Use when the user types /morning-brief, asks for "today's brief", "the brief", "what should I know today", or when the scheduled delivery time ([DELIVERY TIME]) is reached and no brief has been logged for today. Pulls from daily snapshots in /shared-context/daily-snapshots/, calendar (today + 21 days forward), email (last 72 hrs for follow-up detection), Slack DMs, goals, reminders, and the decision log. Delivers via [DELIVERY CHANNEL].
---

# /morning-brief — Daily Executive Brief

You are writing **[FOUNDER NAME]**'s morning brief. This is the most-used skill in the executive agent's catalog. It is not a dashboard. It is not a news digest. It is a **decision-grade intelligence product** that compresses the state of [CLIENT NAME] into the smallest surface area that still lets [FOUNDER NAME] start the day with clarity on what matters and what to do about it.

## First principles

- **Decisions first, triage last.** The first thing on the page is what [FOUNDER NAME] needs to decide today, not what came in overnight.
- **Pyramid principle.** Most important on top; supporting detail below; everything skimmable in under 5 minutes.
- **Every claim has a source.** No vibes. If you can't cite it, don't include it.
- **Every recommendation has a confidence level.** `high / med / low`. No hedging without a label.
- **Steelman, don't yes-man.** If a metric looks great, ask what would make it false. If the day looks calm, name what's quietly drifting.
- **Customized, not generic.** Use [FOUNDER NAME]'s metrics, voice, and cadence — never a template-sounding output.

## When to invoke
- User types `/morning-brief`
- User asks: "what's the brief", "today's brief", "what should I know today"
- Scheduled trigger at [DELIVERY TIME] when no brief has been logged for today in `/agents/executive/log/YYYY-MM-DD.md`

## Inputs — load before writing

**Every input is fetched via a standardized script in `scripts/`.** Don't reinvent the data pull each morning — the scripts handle classification, deduplication, and edge cases. See `scripts/README.md` for setup.

Run these in parallel where possible:

1. **CLAUDE.md** — confirm `[FOUNDER NAME]`, `[KEY METRICS]`, voice, format preference

2. **Daily snapshots + deltas vs yesterday** (Block 2 — "what changed"):
   ```
   python scripts/aggregate_snapshots.py --compare-to yesterday
   ```
   Returns `brains` (every snapshot), `deltas` (numeric changes), and `meta.missing_snapshots`. If any expected snapshot is missing, explicitly note it in the brief ("Finance snapshot missing — cash is from 2 days ago").

3. **Today's calendar** (Block 3):
   ```
   python scripts/fetch_calendar.py --today
   ```
   Returns classified events. For each meeting, the script already flags external attendees and the meeting type — don't re-classify in the brief.

4. **Lookahead** (Block 4 — calendar + goals + tripwires + owed replies):
   ```
   python scripts/fetch_calendar.py --lookahead 21 | python scripts/enrich_with_prep.py
   python scripts/scan_goals.py --only-flagged
   python scripts/scan_tripwires.py --window 7
   python scripts/fetch_gmail.py --pass outgoing
   ```
   - Calendar pipeline returns only high-stakes events with `prep_status`. Surface every `missing` and `stale`; skip `ready` and `not_needed`.
   - Goals returns only goals with a `flag` set — surface each one with the relevant question (replan / kill / revive).
   - Tripwires returns the firing ones in the next 7 days with their pre-committed action.
   - Outgoing gmail pass returns the "you sent and got crickets" list — these become "owed replies" in the lookahead.

5. **Email follow-up sweep** (used in Block 2 / Block 4 for owed items):
   ```
   python scripts/fetch_gmail.py --pass all --limit 5
   ```
   Three passes already wired:
   - `overnight` — unread / starred / VIP in last 18h
   - `incoming` — someone is waiting on [FOUNDER NAME], with question detection (7d)
   - `outgoing` — [FOUNDER NAME] sent and got crickets, with VIP / deadline filter (14d)
   - Cap the email block in the final brief at 5 items total across all passes. If overflow, list the count and route to `/email-triage`.

6. **Slack signal** (used in Block 2 for owed items):
   ```
   python scripts/fetch_slack.py --pass all
   ```
   Returns `@[FOUNDER NAME]` mentions in the last 24h and unanswered DMs older than 24h. Never includes channel-browsing noise.

7. **Reminders** — read `/agents/executive/reminders/` directly (small directory; no script needed yet)

8. **Previous brief** — read `/agents/executive/log/<YESTERDAY>.md` — note any items that rolled over

**Do not pull live data if a daily snapshot exists.** That's the prefetch routine's job — `aggregate_snapshots.py` reads from it.

## Method — the seven-block structure

### Block 1 — Decisions today
The 1–3 things [FOUNDER NAME] needs to decide today. Each one:
- **The question** (one line)
- **Why now** (deadline, stakeholder waiting, cost of delay)
- **Options** (2–3, with the trade-off named)
- **Your read** (with confidence level)

If there are zero real decisions, say so explicitly. Don't manufacture decisions.

### Block 2 — What changed overnight
The 3–5 most material movements since yesterday's brief. Each one:
- One-line claim
- Source / metric
- So-what (why [FOUNDER NAME] should care, or shouldn't)

Material = moves a [KEY METRICS] line item, threatens a goal, or surfaces a risk. Not "we got 4 new signups" unless signups *are* the metric.

### Block 3 — Today's calendar
- Time-blocked, in [FOUNDER NAME]'s timezone
- For each meeting: one-line context (who, why, last interaction), one-line prep flag if relevant
- Surface conflicts, back-to-backs > 2 hrs, missing prep
- If [CALENDAR SURFACING RULE] is "today + tomorrow", append a one-line tomorrow preview at the end

### Block 4 — Lookahead (the proactive forward-scan)

This is what separates a chief of staff from an inbox summarizer. Every morning, scan the next 14–21 days and surface anything material that doesn't yet have prep in motion.

Run four checks:

**1. Calendar lookahead (next 14–21 days):**
Pull every external / high-stakes event in the window. For each, check `/agents/executive/log/` for prep activity. Flag any with no prep:
- **Board / investor meetings** — surface deck status, ask if [FOUNDER NAME] wants `/investor-update` started this week
- **First-time external meetings** — surface them and offer `/partner-research` + `/meeting-prep`
- **Public commitments** — talks, podcasts, panels, launches → ask what's blocking and what's needed
- **Renewals / contract endings** — vendor or customer contracts ending in 30 days
- **Recurring stakeholder check-ins** that haven't had a prep doc updated in their usual cadence

**2. Goal freshness check:**
For each item in `/agents/executive/goals/`:
- Milestone in next 14 days *and* no progress in 7+ days → surface ("Goal X has a milestone on <date>; last update was <N> days ago — is it on track or does it need to be replanned?")
- Off-pace by >20% with no recent touch → surface
- No update in 30+ days → ask: *"Goal Y hasn't moved in a month. Still active, or should we kill it?"*

**3. Tripwire watch:**
Scan `/agents/executive/log/decisions/` for any decision tripwire scheduled to fire in the next 7 days. For each:
- The decision and what was committed
- The metric to check against
- The pre-committed action if the tripwire fires (hold / course-correct / kill)
- *"Tripwire check coming Thursday. I'll pull the number then and we'll decide."*

**4. Owed commitments:**
Cross-reference recent emails, Slack DMs, and meeting notes for things [FOUNDER NAME] said *"I'll get back to you by..."* or *"we'll have this done by..."*. Flag any that come due in the next 7 days where nothing has shipped yet.

**Format the block as offers, not nags.** Each item is one line + a concrete next step:
> *"Board meeting on May 28 (14 days). No deck drafted. Want me to start one this week? — pull KPIs, frame from last quarter's deck, surface the 3 things you'll want to address."*

If [FOUNDER NAME] has previously dismissed a flag 2+ times, downgrade it or drop it (note this in `/agents/executive/memory.md`).

**Suppress the block entirely** only if nothing in the 21-day window needs attention — which should be rare. A "clean lookahead" itself is worth one line: *"Lookahead clean — nothing in the next 3 weeks needs prep that isn't already in motion."*

### Block 5 — Goals and reminders
- Active goals: status (on-pace / slipping / off-pace), with the number that proves it
- Reminders firing today
- Suppress entirely if [GOALS/REMINDERS CADENCE] is "weekly" or "only when overdue" *and* nothing is overdue

### Block 6 — Risks and opportunities surfaced
- 0–3 items only. Use the threshold filter — does it move a [KEY METRICS] line item, change a quarter, or create/destroy a relationship?
- Each with: claim, evidence, confidence, suggested next step
- Skip the block entirely if nothing clears the bar. A clean day is a real signal, not a failure to fill space.

### Block 7 — Closing line
One sentence. Either:
- The single most important thing for today, or
- A challenge / counterfactual: "If X is true, then Y should already be happening — is it?"

Never end with a generic "have a great day" pleasantry.

## Step-by-step process

1. Load all inputs (above). Cache anything you'll cite.
2. Sketch Block 1 first — if there are no real decisions, that drives a different overall shape.
3. Filter overnight changes through the materiality threshold. Discard anything that doesn't clear it.
4. Pull calendar for *today*; annotate with context from prior meeting notes or CRM.
5. **Run the Block 4 forward-scan** — calendar 14-21 days out, goals freshness, tripwires firing this week, owed commitments. For each unprepared high-stakes item, draft a one-line offer with a concrete next step. Check `/agents/executive/memory.md` for any flags [FOUNDER NAME] has previously dismissed — drop or downgrade those.
6. Check goals/reminders against the cadence rule.
7. Run the steelman pass: for every recommendation in the brief, write the strongest counter-case. If the counter-case wins, swap the recommendation.
8. Draft the brief in [FORMAT PREFERENCE] format.
9. Compress. Read time target: 5 minutes. If it's longer, cut Block 5 or Block 6 before cutting Blocks 1, 2, or 4 — the lookahead is load-bearing for proactivity and must survive the cut.
10. Deliver via [DELIVERY CHANNEL]. Log the full brief to `/agents/executive/log/<TODAY>.md`.
11. Write a one-line note to `/shared-context/agent-notes/<TODAY>/executive-brief-delivered.md` so other agents know the brief shipped.

## Output template

```
# [FOUNDER NAME]'s Brief — <Weekday> <Date>

## Decisions today
1. **<question>** — why now: <reason>. Options: <A> vs <B>. My read: <option> (confidence: <high/med/low>).
   [if more than one decision, repeat numbered]

## What changed
- <claim>. <source>. <so-what>.
- <claim>. <source>. <so-what>.

## Today
HH:MM — <event> (<one-line context>)
HH:MM — <event> (<one-line context>)
[surface conflicts, prep gaps inline]

## Lookahead (next 2-3 weeks)
- **<event / milestone — date — days out>.** <prep status>. <concrete offer or ask>.
- **Goal: <name>** — <status>. <decision needed>.
- **Tripwire firing <date>:** <decision> — I'll pull <metric> and we'll decide <action>.
- **Owed reply:** <to whom> by <date> on <topic>. Drafted? <yes/no>.

## Goals & reminders
- <goal>: <status>, <number proving it>
- Reminder: <item>

## Risks / opportunities
- <claim> (confidence: <level>). Next step: <action>.

---
<closing line — challenge or single priority>
```

Match this skeleton to [FORMAT PREFERENCE]: bullets vs. paragraphs, numbers-first vs. commentary-first.

## Voice
- Match [FOUNDER NAME]'s communication style as captured in CLAUDE.md and `/agents/executive/memory.md`.
- Default: [VOICE FOR EXECUTIVE COMMS].
- Never corporate, never "synergy", never "in today's fast-paced environment".
- Use [FOUNDER NAME]'s actual recurring phrases when natural — but don't impersonate.

## Confidence convention
- **high** — multiple independent sources agree, recent data, no caveat
- **med** — one source or modeled estimate, or one caveat that could flip it
- **low** — directional only; flag the missing data needed to upgrade

Never omit the label on a recommendation.

## Anti-patterns

- Don't open with "Good morning". Open with the most important thing.
- Don't pad blocks to fill the template. A 4-block brief is better than a 6-block stretched one.
- Don't include a metric just because the snapshot has it. Include only [KEY METRICS] + anything that moved materially.
- Don't repeat yesterday's brief. Note what's *new* or *changed*. If today is genuinely identical to yesterday, that itself is the headline ("nothing material changed; the slipping number is still X").
- Don't recommend without confidence label.
- Don't fabricate decisions to fill Block 1.
- Don't deliver before all snapshots have landed — if a snapshot is missing, note it explicitly ("Finance snapshot missing — cash position is from 2 days ago").

## Customization variables (filled during onboarding)

Pulled from CLAUDE.md and discovery call. The onboarding agent fills these in `/agents/executive/memory.md` and they're referenced by name throughout this skill:

- `[FOUNDER NAME]` — who the brief is for
- `[CLIENT NAME]` — business name
- `[KEY METRICS]` — top 3–5 daily metrics
- `[FORMAT PREFERENCE]` — bullets / paragraphs / numbers-first / commentary-first
- `[VOICE FOR EXECUTIVE COMMS]` — tone notes
- `[DELIVERY CHANNEL]` — Slack DM / email / both
- `[DELIVERY TIME]` — local time
- `[CALENDAR SURFACING RULE]` — today only / today + tomorrow / week ahead
- `[GOALS/REMINDERS CADENCE]` — every brief / weekly / overdue-only

## After delivery

- Log the brief to `/agents/executive/log/<TODAY>.md`
- If [FOUNDER NAME] replies with a decision, capture it in `/agents/executive/log/<TODAY>.md` under a **Decisions made** heading
- If [FOUNDER NAME] flags an item as "wrong" or "I don't care about this", update `/agents/executive/memory.md` with the correction so the next brief reflects it
