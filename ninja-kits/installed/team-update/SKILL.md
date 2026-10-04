---
name: team-update
description: Draft a weekly internal team update from [FOUNDER NAME] — what got decided this week, what's coming, what's the team's job to push on, and which wins / blockers deserve acknowledgment. Different from the WBR (which is for [FOUNDER NAME]'s eyes); team-update is for the team's eyes — communicates context they need, not just metrics. Use when the user types /team-update, asks "draft the team update", "Friday team email", "weekly team note", or it's the scheduled team-update day and one hasn't been drafted. Pulls decisions from the week, wins worth recognition, and the WBR's "decisions queued" as the forward-looking section.
---

# /team-update — Weekly Team Communication

The team-update is [FOUNDER NAME]'s direct line to the team. Done well, it does four things:

1. **Closes information loops** — what got decided this week, by whom, why
2. **Names what's coming** — what the team should be working toward next week
3. **Recognizes contribution** — specific, named, non-perfunctory
4. **Forces transparency** — when leadership writes weekly, the team trusts what they read

Done badly, it becomes "this week in metrics" — which the team already knows and doesn't need restated.

## The contract — context > metrics
- **The team has the metrics already.** Don't republish the WBR scorecard. Give them the *context* the WBR doesn't give: why we made certain calls, what we're worried about, what we need their help on.
- **Recognition with substance.** "Big shoutout to <person> for crushing it" is empty. *"<Person> shipped the X integration that unblocked 3 enterprise deals — that's worth $40k MRR if they all close."* is real.
- **Forward > backward.** What's coming next gets more space than what already happened.
- **[FOUNDER NAME]'s voice.** This is not corporate comms. If [FOUNDER NAME] writes like a human, the update should sound like one.

## When to invoke
- `/team-update`
- "draft the team update", "Friday team email", "weekly team note", "team comms for this week"
- Scheduled on [TEAM UPDATE DAY] when one hasn't been drafted

## Inputs to load

1. **This week's WBR** — particularly the "decisions made" and "decisions queued" sections
2. **Decisions log** — `/agents/executive/log/decisions/` filtered to this week — which got committed, killed, held
3. **Team activity snapshot** — `team-activity.json` across the week. Look for "what shipped" and "who unblocked what"
4. **Last week's team update** — `/agents/executive/log/team-updates/<last>.md`. Maintain format consistency; check whether last week's "what's coming" actually happened
5. **Optional input from [FOUNDER NAME]** — if they want to add a personal note / context / direct ask of the team

## Structure — the five-section update

### Opening (1-2 sentences, conversational)
The week, named. Not "Hi team!" — something the team will actually read. *"Short week — the launch dominated everything else. Here's what changed."*

### Decisions made (3-5 bullets)
Each one: what got decided, by whom, the one-line reason. The team doesn't need the full memo; they need to know enough to do their work without re-asking.

> *"Decided to ship enterprise tier in Q3 (was Q2). Reason: SDR transition cost us 4 weeks. [FOUNDER NAME] owns the customer comms; Diego owns the sprint shift."*

### Wins (2-4 named, specific)
Real contributions from real people. Not motivational fluff.

> *"Maya closed the Initech renewal — $180k ARR, after a 90-day churn-signal flag. Onboarding revamp paid off."*
> *"Diego shipped the API rate-limit fix that 14 enterprise customers had been waiting on for 6 weeks."*

If [FOUNDER NAME] doesn't have specifics, ask. *"What 2-3 things shipped this week that you want the team to know mattered?"*

### What's coming next week (3-5 items)
Specific commitments — what the team is meant to push on. Each gets an owner.

### What I need help with (1-2 items, optional)
This is the team-update analog of investor-update's "asks." Where does [FOUNDER NAME] need the team to lean in this week?

> *"I need every PM to talk to 3 enterprise customers this week — we need ground-truth on the pricing pivot before Thursday's call."*

End with: *"Update again Friday."*

## Output template

```
# Team update — week of <date>

<opening 1-2 sentences in [FOUNDER NAME]'s voice>

## Decided this week
- <decision — who decided, one-line why>
- <decision>
- <decision>

## Wins
- <named person> — <specific accomplishment, why it mattered>
- <named person> — <specific accomplishment, why it mattered>

## What's coming next week
- <commitment — owner>
- <commitment — owner>

## What I need from you
<1-2 specific asks of the team, or skip if nothing this week>

— [FOUNDER NAME]
Update again <next update day>.
```

## Voice

- Match [VOICE FOR EXECUTIVE COMMS] — if [FOUNDER NAME] is dry, be dry. If direct, be direct. Never corporate.
- Skip "team!" "rockstar" "crushing it" and other empty intensifiers
- Specific names, specific numbers, specific things shipped
- 300-500 words. If team-update is longer than a coffee read, it gets skimmed

## Step-by-step process

1. **Pull the week's decisions** from `/agents/executive/log/decisions/`
2. **Pull `team-activity.json` snapshots across the week** — look for shipped features, blockers cleared, deals closed
3. **Read last week's team update** to maintain format + grade against "what's coming" promises
4. **Identify the 2-4 most material wins** with specific people attached
5. **Draft the update** in [FOUNDER NAME]'s voice
6. **Surface what's missing** — if [FOUNDER NAME] should name a specific ask but the draft doesn't have one, push: *"Anything you want the team to lean in on this week?"*
7. **Compress to ~400 words**
8. **Save to `/agents/executive/log/team-updates/<YYYY-MM-DD>.md`** and deliver via [TEAM UPDATE CHANNEL]

## Anti-patterns
- **Don't republish the WBR scorecard.** The team has metrics; they want context.
- **Don't write generic recognition.** "Big shoutout to engineering" is worse than no recognition.
- **Don't bury bad decisions.** If a decision was hard or unpopular, the team needs to hear it explained — not absorbed by osmosis from changed priorities.
- **Don't ship the same content week-to-week.** If two updates in a row are saying the same thing, either the team is genuinely doing the same thing (fine, name it) or [FOUNDER NAME] isn't actually leading change (worth a `/priority-recheck`).
- **Don't use the team-update to deliver criticism.** If something needs to be addressed with a specific person, that's a 1:1, not a team-wide note.

## Post-action

After sending, log to `/shared-context/agent-notes/<TODAY>/team-update-sent.md` so other agents (Ops, especially) know what was communicated.

Track over time: are the "what's coming next week" items actually happening? If the same item shows up 3+ weeks running uncompleted, that's a signal worth surfacing in the next `/priority-recheck` or WBR.
