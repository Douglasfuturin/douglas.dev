# Example Webinar Decks, [CLIENT NAME]

Drop [CLIENT NAME]'s best-performing past webinar decks here (or aspirational references). These calibrate the skill to [CLIENT NAME]'s actual voice, aesthetic, and proven conversion structure.

## Suggested structure

```
.claude/skills/webinar-deck/assets/examples/
  README.md
  {2025-q3-launch-deck}/
    deck-spec.md         # the structured markdown spec
    deck.html            # the rendered deck
    metrics.md           # show-up rate, conversion, revenue per registrant
    notes.md             # what worked, what to keep, what to change next time
  {client-name-current}/
    ...
```

## What to include in metrics.md per example

```markdown
# {Webinar Name}, performance

- Registrations: {N}
- Show-up rate: {%}
- Stay-to-pitch rate: {%}  (% who stayed past the offer reveal)
- Conversion rate: {%}     (% of attendees who bought)
- Revenue per registrant: ${X}
- Revenue per attendee: ${X}
- Total revenue: ${X}
- Refund rate (60-day window): {%}

## What worked
- {Specific slide or section}
- {Specific transition}
- {Specific stack bonus that converted}

## What to change
- {Specific slide or section}
- {Specific objection that came up that wasn't handled}
```

## Why this matters

When the skill builds a new deck, it reads:
1. The frameworks (universal best practices)
2. Any example decks in this folder (client-specific patterns that have shipped and converted)
3. The Voice Bible + brand assets

Examples here override framework defaults. A real performing deck in [VOICE OWNER]'s voice is always more valuable than a textbook arc.

## Calibration loop

After each new webinar runs:
1. Wait 14-30 days for performance data
2. If it outperformed previous, save it here with metrics + notes
3. The next deck build uses this as the new floor

This is how the skill compounds quality over time, not by getting smarter, but by accumulating ground-truth examples of what works for [CLIENT NAME] specifically.

## Anonymization

If a past deck contains client/student names or proprietary data [CLIENT NAME] doesn't want in agent training context, replace specifics with placeholders BUT keep enough structural specificity that the voice and rhythm are still learnable. The point of the example is structure + voice, not the literal numbers.
