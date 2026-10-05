---
name: goal-tracker
description: Log, update, pause, close, or list [FOUNDER NAME]'s goals — the goals that drive everything else in the executive agent (morning brief flags stale goals, WBR shows pace and auto-syncs current values, QBR scores them by final grade). CRUD interface for `/agents/executive/goals/`. Use when the user types /goal-tracker, /goal, says "add a goal", "update goal X", "pause that goal", "close out the X goal", "we hit X", "kill that goal", "show my goals", "is goal X still active", "I want to track Y", or when [FOUNDER NAME] states a number-they-want-to-hit during any other interaction.
---

# /goal-tracker — Goals CRUD

Goals are the spine of the executive agent. Almost every other skill references `/agents/executive/goals/` — morning brief flags stale ones, WBR shows pace and auto-updates linked metrics, decision-research checks goal alignment, QBR scores hit rate, priority-recheck asks if today's work is on the goal. So the goal store needs to be **clean, current, and honest**.

This skill is the only sanctioned way to mutate `/agents/executive/goals/`. Five operations: **list, add, update, pause/resume, close.**

## Goal file format

One file per goal at `/agents/executive/goals/<slug>.md`:

```markdown
---
name: Hit $50k MRR by end of Q2
slug: hit-50k-mrr-q2
target_value: 50000
current_value: 38000
unit: usd                      # usd | count | percent | ratio | months
target_date: 2026-06-30

status: active                 # active | paused | closed  (lifecycle only)
final_grade: null              # set ONLY when status=closed — see grading below
actual_value_at_close: null    # value snapshot at close (current_value can keep its own history)
outcome_summary: null          # one line: what actually happened
lessons: null                  # what to remember for the next round of goal-setting

stated_in_qbr: Q2-2026         # which QBR committed this goal — QBR Chapter I queries by this
linked_kpi: mrr                # optional — a field name in kpi_config.json; see "Linked KPIs" below

owner: [FOUNDER NAME]
why_it_matters: "Runway extends 8 months at this MRR; unlocks Series A conversation."
cadence_days: 14
last_update: 2026-05-04
status_changed_at: null        # date status last changed (paused / resumed / closed)
created: 2026-02-01
---

# Hit $50k MRR by end of Q2

[Free-form body — supporting context, sub-milestones, related decisions]

## Update log
- 2026-05-04: $38k (+$2k). Velocity stable; on track for $46-48k by Q-end.
- 2026-04-20: $36k.
- 2026-04-06: $34k.
```

The frontmatter is what `scan_goals.py` reads. The body is for [FOUNDER NAME] and the agent — free-form context.

### The two-axis model — lifecycle vs. grade

The most common goal-tracking mistake is conflating "where is this goal now" with "how did it end." This schema keeps them separate:

- **`status`** — the *lifecycle*. Only three values: `active`, `paused`, `closed`. `scan_goals.py` and the morning brief only process `active` goals.
- **`final_grade`** — the *outcome*. `null` while the goal is alive. Set exactly once, when `status` becomes `closed`. Four values — this is the vocabulary the QBR scores against:

| `final_grade` | Meaning |
|---|---|
| `hit` | Reached or exceeded `target_value` by `target_date` |
| `slipped` | Got close — missed the date, or fell short by a modest margin (roughly <15%) |
| `missed` | Fell materially short (roughly >15%), or abandoned without a pivot |
| `pivoted` | Target changed materially mid-flight — this goal closed, a successor was created |

A goal you "complete" → `status: closed`, `final_grade: hit`. A goal you "kill" → `status: closed`, `final_grade: missed`. The QBR needs this distinction; don't collapse it.

### Linked KPIs — kill the manual-update problem

If a goal's progress maps to a metric already tracked in the WBR (`kpi_config.json`), set `linked_kpi` to that metric's field name. When set:
- The WBR pipeline's `sync_goals_from_kpis.py` step auto-updates `current_value` + `last_update` after each weekly aggregation.
- `/goal-tracker` no longer needs manual progress updates for that goal — the number stays fresh on its own.
- Manual `update` operations still work (for re-spec), but routine progress is automatic.

Leave `linked_kpi` as `null` for goals with no tracked-metric equivalent (e.g. "Ship enterprise tier" — a milestone, not a metric).

## When to invoke
- `/goal-tracker`, `/goal`
- "add a goal", "track Y", "I want to hit $X by Z"
- "update goal X to <new number>", "the X goal moved to Y"
- "pause the X goal", "put X on hold" / "resume X", "X is active again"
- "close out X", "we hit X", "kill the X goal", "we're pivoting off X"
- "show my goals", "what are my goals", "is X still active"

**Implicit trigger:** if during *any other skill* [FOUNDER NAME] mentions a concrete number-they-want-to-hit by a date — like "we need $X by quarter-end" — offer to log it as a goal. *"Want me to add that as a tracked goal?"*

## The five operations

### 1. List
> *"Show my goals"*

Output every `status: active` goal in priority order (target-date soonest first). Show name, current vs target, % to target, days to target, last update. Note any `paused` goals separately at the bottom (one line — they're intentionally dormant, not surfaced as urgent).

```
Active:
1. Hit $50k MRR (76% there, 46 days left, last update 4 days ago) — linked to KPI, auto-synced
2. Ship enterprise tier (60% there per Linear, 89 days left, last update 11 days ago) ⚠ stale
3. Reduce churn to <1.5% (currently 2.4%, no date set) ⚠ no target date

Paused (1): "Launch affiliate program" — paused 2026-04-30, revisit after Q2
```

Use `scan_goals.py` to power this — it classifies pace and freshness.

### 2. Add
Required: **name, target_value, unit, target_date.**
Strongly suggested: **why_it_matters** (one sentence), **cadence_days**, **stated_in_qbr** (current quarter), **linked_kpi** (if a tracked metric exists).

If [FOUNDER NAME] gives a vague goal ("grow MRR"), push for the specifics:
- *"What's the number?"*
- *"By when?"*
- *"And in one sentence: why does this matter — what does hitting it unlock?"*

Don't let a goal land in the store without a `target_value` + `target_date`. Vague goals corrupt the rest of the system (the `scan_goals` classifier can't compute pace without numbers).

On add: set `status: active`, `final_grade: null`, `created: <today>`, `stated_in_qbr: <current quarter>`. Check `kpi_config.json` — if a metric matches this goal, set `linked_kpi` and tell [FOUNDER NAME] it'll auto-sync.

### 3. Update
Two flavors:
- **Progress update** — `current_value` and `last_update` change. Append to the body's `## Update log`. *For `linked_kpi` goals this happens automatically via the WBR sync — manual progress updates are only needed for unlinked goals.*
- **Re-spec** — the goal itself changes (different target, date, or scope). This is a *significant* event. If the change is material (target moved >15%, or scope genuinely shifted), don't re-spec in place — that's moving the goalpost. **Close the old goal as `pivoted` and add a new one.** Note the link in both `outcome_summary` fields.

If [FOUNDER NAME] is re-speccing more than once a quarter on the same goal → flag it. That's a sign the goal was poorly defined or the strategy is shifting.

### 4. Pause / Resume
**Pause** is for goals that are *intentionally dormant* but not abandoned — blocked on an external dependency, deprioritized for a quarter, waiting on a hire. Set `status: paused`, `status_changed_at: <today>`. Note why in the body.

Paused goals **drop out of the morning brief and WBR pace checks** (`scan_goals.py` only processes `active`). That's the point — they're not urgent. But they're still listed at the bottom of `/goal-tracker` list output so they don't get forgotten.

**Resume** flips `status` back to `active`, updates `status_changed_at`, and the goal re-enters the surfacing loop.

**Pause vs. close:** if there's a real chance [FOUNDER NAME] picks it back up this year, pause. If it's genuinely done, close it (`missed` or `pivoted`). Don't let "paused" become a graveyard — the morning brief won't nag, so a paused goal can rot silently. The QBR audits paused goals: any paused >90 days gets a "resume or close?" prompt.

### 5. Close
A goal closes exactly once. Required on close: `status: closed`, `final_grade`, `actual_value_at_close`, `outcome_summary`, `status_changed_at: <today>`. Strongly encouraged: `lessons`.

- **Hit it** → `final_grade: hit`. `actual_value_at_close` = the value reached. If hit early or above target, note that in `outcome_summary` — calibration data.
- **Close but short** → `final_grade: slipped`. Honest about the gap.
- **Materially short / abandoned** → `final_grade: missed`. Write the real reason in `outcome_summary`.
- **Pivoted** → `final_grade: pivoted`. `outcome_summary` names the successor goal. Create that successor as a new `add`.

Always write `lessons` on a `missed` or `slipped` close — that's the single most valuable field for the QBR's calibration analysis. *"Set the target before validating the channel; the channel never worked, so the goal was dead on arrival."*

## Output shape

For each operation, return:

```
✓ <operation> — <goal name>
<one-line summary of state>
[Updated file: <path>]
```

For listing, return the full table. For add, if pushing back on a vague goal:

```
🟡 Need more specifics before I can track this:
  • Target number: <?>
  • By when: <?>
  • Why it matters: <?>
```

## Step-by-step process

1. **Identify the operation.** If unclear, ask once.
2. **Check existing goals** for conflicts — if [FOUNDER NAME] says "add a goal to hit $50k MRR" but there's already an active $50k MRR goal, surface it before creating a duplicate.
3. **For add:** push for specifics if vague; set lifecycle fields; check `kpi_config.json` for a `linked_kpi` match. **For update:** append to the log; only mutate frontmatter, never overwrite the body. **For close:** fill all five required close fields.
4. **Write the file.** One file per goal at `/agents/executive/goals/<slug>.md`.
5. **For close (any grade) or significant re-spec:** log to `/agents/executive/memory.md` with a brief note. This is calibration data for the QBR.
6. **Run a quick `scan_goals.py`** after any change to confirm the file is well-formed and the classification looks right.

## Anti-patterns
- **Don't accept vague goals.** "Grow revenue" without a number is not a goal — it's a wish.
- **Don't conflate `status` and `final_grade`.** Lifecycle is where it is; grade is how it ended. The QBR needs both.
- **Don't silently re-spec a goal that's slipping.** Material change → close as `pivoted`, add a successor. Moving the goalpost in place is the worst pattern in goal-tracking.
- **Don't let "paused" become a graveyard.** Pause means "coming back to this." If it isn't, close it honestly.
- **Don't manually update `linked_kpi` goals' progress** — the WBR sync handles it. Manual updates there just create drift.
- **Don't create goals during a heated moment.** If [FOUNDER NAME] is frustrated and says "we need $1M by end of quarter," ask if they want it logged as a real commitment or if it's venting.
- **Don't tell [FOUNDER NAME] they're hitting too few goals** unless the QBR shows it as a pattern. One missed quarter is data; three is a pattern.

## Post-action — logging for QBR

Every goal mutation gets summarized in `/agents/executive/log/<today>.md` under `## Goal log`:

```
- Added: <goal> (target: <X> by <date>, stated_in_qbr: <Q>)
- Updated: <goal> ($X → $Y; pace: <on/slipping/off>)
- Paused: <goal> (reason: <one line>)
- Closed: <goal> — grade: <hit/slipped/missed/pivoted> (actual: <value>; <one-line outcome>)
```

The QBR reads this 90-day log plus the goal files themselves (querying `stated_in_qbr` for the prior quarter, reading `final_grade` for scoring) to compute goal hit rate, kill rate, and the calibration question: *was [FOUNDER NAME] setting realistic goals last quarter?*

## Related skills
- `/morning-brief` — flags stale / off-pace `active` goals (uses `scan_goals.py --only-flagged`)
- `/weekly-business-review` — surfaces pace movement; runs `sync_goals_from_kpis.py` to auto-update linked goals
- `/quarterly-business-review` — Chapter I scores goals by `final_grade`, queried via `stated_in_qbr`; Chapter VII commits next quarter's goals (which become new `add`s with `stated_in_qbr` set)
- `/decision-research` — checks if a decision serves an `active` goal
- `/priority-recheck` — asks "is today's work on the top goal"
