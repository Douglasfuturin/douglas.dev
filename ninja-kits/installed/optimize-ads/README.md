# optimize-ads

A Claude Code skill that audits a Meta Ads account, recommends optimizations using editable frameworks, logs each session, and learns from the last 3-5 sessions to sharpen future recommendations.

**Recommend-only.** The skill never touches Ads Manager. It reads data, thinks, and writes recommendations. You apply them by hand.

---

## Install

Drop the `optimize-ads/` folder into your project at `.claude/skills/optimize-ads/`. That's it — Claude Code picks up the skill from `skill.md` automatically. Python 3.9+ stdlib only, no `pip install` needed.

```
your-project/
└── .claude/
    └── skills/
        └── optimize-ads/    ← drop the folder here
```

## First-run setup

```bash
python3 .claude/skills/optimize-ads/scripts/setup.py
```

The wizard walks you through creating a Meta Business Manager **System User token** (the kind that doesn't expire), finding your ad account ID, and verifies the credentials with a real API call. It writes:

- `META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`, `META_API_VERSION` → your project's `.env`
- `config/config.json` (copied from the example, with your account ID patched in)

If your `.env` doesn't exist yet, setup creates it.

## Daily use

Just say it: **"optimize ads"**, **"check our Meta ads"**, **"audit ads manager"**, etc. The skill kicks off and walks through:

1. Loads the last 3-5 sessions, measures what your past recommendations actually did, writes a "What we learned" preamble
2. Pulls insights from Meta since the last session (or 7 days back on first run)
3. Applies the frameworks → produces 3-7 ranked recommendations with framework name, evidence, confidence, expected impact, and a success metric to check next time
4. Logs the session to `logs/sessions/<id>.json` and asks you which ones you applied so the next session can learn

## What you customize

Three editable docs the skill re-reads every session — your edits take effect immediately, no restart:

| File | What lives here |
|---|---|
| [`references/frameworks.md`](references/frameworks.md) | The optimization patterns the skill applies. 7 to start; add, edit, delete freely. The skill only uses what's in this file and cites the framework by name in every recommendation. |
| [`references/guidelines.md`](references/guidelines.md) | Hard guardrails — what the skill must not recommend (e.g., don't touch ads with < $50 spend, no budget changes > 20%, no pausing always-on campaigns). |
| [`references/kpi_targets.md`](references/kpi_targets.md) | Target ROAS / CPA / CTR by campaign objective. Defaults are industry-rough — tune to your business. Supports per-campaign overrides. |
| [`config/config.json`](config/config.example.json) | Which campaigns are always-on (off-limits for pause), which to ignore entirely, primary KPI per objective, what action type counts as a purchase (`omni_purchase` vs `purchase`), min-spend thresholds. |

## How the learning actually works

Each session log records the metric snapshot at the time of every recommendation. When the next session runs, [`measure_outcomes.py`](scripts/measure_outcomes.py) pulls current metrics for any **accepted** recommendation's target and compares against that snapshot. It classifies each as `worked` / `didn't_work` / `inconclusive` using per-framework heuristics:

- **Kill the Drainers** → did the spend on that target actually stop?
- **Scale the Winners** → did ROAS hold within ±15% at higher spend?
- **Creative Fatigue** → did link CTR recover ≥20%?
- **Audience Saturation** → did frequency drop?
- **Consolidation** → did CPA improve?

These verdicts flow into the next session's "What we learned" preamble. After 5-10 sessions you'll see which frameworks consistently earn their keep on your account — and which you should sharpen or delete.

## Files

```
optimize-ads/
├── README.md                       # this file
├── skill.md                        # the workflow Claude follows
├── references/
│   ├── meta_api_guide.md           # API auth, endpoints, common errors
│   ├── frameworks.md               # ← edit
│   ├── guidelines.md               # ← edit
│   └── kpi_targets.md              # ← edit
├── scripts/
│   ├── setup.py                    # one-time auth + config wizard
│   ├── pull_performance.py         # fetches insights snapshot
│   ├── load_history.py             # loads last N session logs
│   ├── measure_outcomes.py         # classifies past recs as worked/didn't
│   └── log_session.py              # writes session log + decisions
├── config/
│   ├── config.example.json
│   └── config.json                 # ← created by setup.py
└── logs/                           # session history accumulates here
    ├── index.md                    # one-line summary per session
    └── sessions/
        └── <session-id>.json
```

## Privacy & security notes

- Credentials live in your project's `.env`. The skill never sends them anywhere except `graph.facebook.com`.
- Session logs in `logs/` contain ad performance data (spend, conversions, campaign names). Consider whether you want this committed to version control — many people add `logs/sessions/` to `.gitignore`.
- The skill never calls update/pause/PATCH endpoints. It uses `ads_read` for the read path; `ads_management` is requested at setup only so you can flip to auto-apply mode later if you ever want to (you'd have to edit `skill.md` to enable that — not a default).

## Troubleshooting

- **"META_ACCESS_TOKEN not set"** → run `setup.py`
- **`(#190) Error validating access token`** → token expired or scopes wrong. Re-run setup.
- **`(#17) User request limit reached`** → Meta rate-limit. The pull script retries with backoff; if it still fails, narrow the date range with `--since`.
- **Skill produced 0 recommendations** → check the snapshot — if spend was tiny or there were no conversions, the guidelines (correctly) refuse to recommend on noise. See `references/guidelines.md` to relax thresholds if needed.
- **A framework keeps producing bad calls** → look at the session logs' `outcomes[]`. If it's consistently flagged `didn't_work`, sharpen the signal in `frameworks.md` or delete the framework entirely.

## License

MIT — do whatever, attribution appreciated.
