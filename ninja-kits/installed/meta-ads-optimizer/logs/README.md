# Session Logs

Each optimization session writes one JSON file to `sessions/<session_id>.json` and appends a one-line entry to `index.md`.

## Why these exist

The whole point of the skill is to **learn from what it recommended before**. Without these logs, every session starts from zero. With them, the skill can:

- Tell you which frameworks have been earning their keep (recommendations that the user accepted AND that improved the metric)
- Tell you which frameworks keep producing rejects or no-ops
- Avoid re-recommending things you already turned down
- Measure outcome impact over multiple weeks

## Schema

```json
{
  "session_id": "2026-05-20-1430",
  "started_at": "2026-05-20T14:30:00-07:00",
  "lookback_window": {
    "since": "2026-05-13",
    "until": "2026-05-20"
  },
  "ad_account_id": "act_…",
  "snapshot_summary": {
    "spend": 4823.10,
    "impressions": 612430,
    "purchases": 184,
    "purchase_value": 18222.50,
    "roas": 3.78,
    "cpa": 26.21,
    "link_ctr": 0.018
  },
  "what_we_learned": "3-5 sentences summarizing past-session outcomes that informed this session's recommendations.",
  "recommendations": [
    {
      "id": "rec-1",
      "framework": "Kill the Drainers",
      "target_type": "adset",
      "target_id": "1234567890",
      "target_name": "Broad LAL 1% — Hero Tee",
      "action": "Pause",
      "evidence": "Spent $312 (4.2× target CPA) with 0 purchases over 6 days.",
      "confidence": "high",
      "expected_impact": "Stops ~$50/day bleed; reallocate to scaling Adset X.",
      "success_metric": "Account-level CPA improves by ≥ $2 within 4 days.",
      "risk_if_wrong": "If the audience was about to convert, we miss it — but $312 with zero conversions strongly suggests it isn't.",
      "snapshot_at_recommendation": {
        "spend": 312.04,
        "purchases": 0,
        "frequency": 2.1,
        "link_ctr": 0.009
      }
    }
  ],
  "considered_and_skipped": [
    {
      "framework": "Audience Saturation",
      "target_id": "...",
      "reason": "Frequency 4.3 but ROAS still 3.1 — not declining. Watch list."
    }
  ],
  "user_decisions": [
    {
      "rec_id": "rec-1",
      "decision": "accepted",
      "decided_at": "2026-05-20T14:48:00-07:00",
      "note": ""
    }
  ],
  "outcomes": []
}
```

`outcomes` is populated by `measure_outcomes.py` when a later session looks back at this one.

## index.md

One line per session for fast scanning. Example:

```
- 2026-05-20-1430 — 5 recs (3 accepted, 1 rejected, 1 deferred) — spend $4.8k, ROAS 3.78
- 2026-05-13-1015 — 4 recs (4 accepted) — spend $4.2k, ROAS 3.41
```

You can grep this for fast history. Don't edit it by hand — `log_session.py` maintains it.
