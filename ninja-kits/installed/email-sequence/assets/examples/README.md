# Example Sequences — [CLIENT NAME]

Drop [CLIENT NAME]'s 2-3 best-performing past sequences here per type, anonymized if needed. These are the highest-fidelity calibration the skill has — they trump every framework file when present.

## Suggested structure

```
.claude/skills/email-sequence/assets/examples/
  welcome/
    2025-q4-welcome-v3.md          # the actual sequence that performed well
    metrics.md                      # what it converted at, what beats worked
  abandoned-cart/
    current.md
    metrics.md
  launch/
    2025-spring-launch.md
    metrics.md
  …
```

## What to include in each example

For every example sequence, copy in:
- All emails — subject, preview, body, CTA, send timing
- Personalization tokens used
- Audience segment it was sent to
- Performance: open rate, click rate, conversion rate, revenue (per email + total)

Anonymize customer names, internal product names, or any details [CLIENT NAME] doesn't want in agent training context — but keep enough specificity that the voice and structure remain learnable.

## Why this matters

When the skill drafts a new sequence, it reads:
1. The framework file for that sequence type (`frameworks/{type}.md`)
2. Any winner / example sequences here
3. The Voice Bible + recent winners files

Examples in this folder override the framework defaults. A real past performer in [VOICE OWNER]'s voice always beats a generic best-practice arc.

## Calibration loop

After each new sequence ships:
1. Wait 14-30 days for performance data
2. If it outperformed the previous best, save it here
3. Update `metrics.md` with the new baseline
4. The next sequence draft uses this as the new floor

This is how the skill gets better over time — not by being smarter, but by accumulating ground-truth examples of what works for [CLIENT NAME] specifically.
