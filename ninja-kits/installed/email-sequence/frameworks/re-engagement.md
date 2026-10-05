# Re-engagement Sequence Framework

> **Goal:** wake up subscribers who haven't opened in 60+ days, OR sunset them. Either outcome is good — deliverability improves with both.

A bloated list of non-openers wrecks inbox placement for the engaged subs. Re-engagement is partly a recovery play, partly a list hygiene play. Both outcomes are wins.

## Default arc — 4 emails over 10 days

| # | Day | Beat | Body purpose | Length |
|---|-----|------|--------------|--------|
| 1 | 0 | **Pattern interrupt** | acknowledge the silence; ask if they still want emails | 100-200 words |
| 2 | 3 | **Best of** | the 3-5 best pieces of content from the past N months | 250-400 words |
| 3 | 6 | **Personal check-in** | feels like a 1-on-1 message, not a marketing email | 150-300 words |
| 4 | 10 | **Final sunset** | "I'm taking you off the list unless you click this" — real | 80-150 words |

## Psychology of each beat

**Email 1 — Pattern interrupt:**
The subject line should signal something different ("Should I stop emailing you?", "Quick question", "You okay?"). The body acknowledges they've been quiet and gives them an easy escape AND an easy stay. The whole email is one paragraph and one clear binary: click to stay, ignore to leave.

**Email 2 — Best of:**
For the ones who didn't click but might still be there. Show them what they've been missing. Pick 3-5 of the highest-performing recent pieces (most clicks, most replies, most-shared) — not "favorites," actual data. Each piece gets a one-line tease and a link.

**Email 3 — Personal check-in:**
Tone shifts dramatically. This email should read like [VOICE OWNER] hit "compose new" in their personal inbox, not like a broadcast. Short. Conversational. One specific question. "What are you working on right now?" or "What's the biggest thing in your way?" Often gets reply rates 5-10× a normal broadcast.

**Email 4 — Final sunset:**
Honest, direct. "I'm removing you from my list on [date] unless you click this link." No emotion. No guilt. Just a clean exit ramp. Whoever clicks is now an engaged sub again. Whoever doesn't gets sunsetted automatically — which is the right outcome for everyone.

## Rules

- **Mark openers and re-tag.** Anyone who opens any of these 4 emails goes back into "engaged" status. Anyone who doesn't open all 4 gets sunsetted.
- **Sunset means SUPPRESS, not delete.** Move them to a suppressed segment, don't hard-delete. They might come back via a future opt-in.
- **The sunset is real.** If email 4 says "I'm taking you off the list" and you don't actually remove them, the sequence doesn't work next time you run it. The credibility carries forward.
- **Don't run this sequence during a launch.** A non-engaged sub who happens to open a launch email is gold — re-engagement during launch costs revenue. Run re-engagement in slow periods.
- **Run quarterly.** Lists rot continuously. Once a quarter is the standard cadence.

## Sunset decision matrix

After email 4 fires, segment dormant subs:

| Behavior across all 4 emails | Action |
|------------------------------|--------|
| Opened ≥ 1 email | Re-tag as engaged, keep on main list |
| No opens, but clicked the "I want to stay" link in email 1 | Re-tag as engaged, keep on main list |
| No opens, no clicks | Move to suppressed segment (don't delete) |

## Common failure modes

| Failure | Why it kills the sequence |
|---------|---------------------------|
| Email 1 sounds like guilt-trip | "We miss you!" feels saccharine — open rate tanks |
| "Best of" links to gated content | Reader has to opt-in again to read — friction kills clicks |
| Personal email is signed by the brand instead of [VOICE OWNER] | Breaks the "this is a real message" frame |
| Sunset is performative — sender never actually removes anyone | The audience learns the threat is empty; future re-engagements stop working |
| Running re-engagement during a launch | Costs revenue from launch + dilutes re-engagement signal |
| Sending to recently-engaged subs by mistake | Filter must be "no opens in 60+ days" — connector needs to enforce this |

## Connector requirements

- Segment subscribers by "last open date < N days"
- Tag openers during the sequence to re-classify them
- Suppress (not delete) the non-openers at the end
- Exclude recently-engaged subs from receiving this sequence by accident

## Calibration

If `brains/email/winners/re-engagement.md` doesn't exist yet, run this sequence once with the defaults and log results — which email re-engaged the most subs, which subject lines opened. Re-engagement sequences improve more from iteration than any other type.
