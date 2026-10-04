# Webinar Sequence Framework

> **Goal:** maximize show-up rate to a live or evergreen webinar, then convert attendees into buyers in the post-webinar window.

Show-up rate is the single biggest determinant of webinar revenue. Industry average is 30-40% live show-up; a well-tuned sequence pushes this to 50-60%. After show-up, the post-webinar 48-hour window typically does 70-90% of the total revenue.

## Default arc — 8 emails over 14 days

### Pre-webinar (5 emails)

| # | Time before webinar | Beat | Body purpose | Length |
|---|---------------------|------|--------------|--------|
| 1 | within 5 min of registration | **Confirm + add to calendar** | confirmation, calendar links, what to expect | 200-300 words |
| 2 | 3 days before | **Curiosity + agenda** | tease 3 specific things they'll learn | 300-450 words |
| 3 | 1 day before | **Story + commitment** | one story that proves why they should show up; ask them to block the time | 350-500 words |
| 4 | 1 hour before | **Last reminder** | short — "we start in 1 hour, here's the link" | 80-150 words |
| 5 | 10 min before | **We're starting** | very short — "we're live, click here" | 40-80 words |

### Post-webinar (3 emails)

| # | Time after webinar | Beat | Body purpose | Length |
|---|--------------------|------|--------------|--------|
| 6 | 1 hour after | **Replay + first pitch** | replay link, summary of what they missed, offer link | 350-500 words |
| 7 | 24 hours after | **Objections + Q&A** | top 5 questions asked during the live, answered | 400-600 words |
| 8 | 48 hours after | **Final close** | cart closing tonight, real scarcity, link | 200-350 words |

## Psychology of each beat

**Email 1 (instant confirm):**
Set the expectation that this isn't just-another-webinar. Mention something specific they'll learn — not the topic, an actual takeaway. Include calendar links for Google / Apple / Outlook because friction on calendar-adding directly drops show-up rate.

**Email 2 (3 days before):**
The reader signed up 3 days ago and has already forgotten why. Re-sell the value. List 3 specific outcomes they'll get from showing up. The more concrete, the higher the show-up lift.

**Email 3 (1 day before):**
This email is about commitment, not information. The story should be about someone who almost didn't show up and how that one decision changed their trajectory. Ask the reader explicitly: "Block 60 minutes on your calendar right now."

**Email 4 (1 hour before):**
Short. Just the link and a "see you in 60 minutes." This email is the single biggest show-up lifter — many readers signed up days ago and have completely forgotten.

**Email 5 (10 min before):**
Even shorter. "We're live, click here." 1-2 sentences max. Subject line should signal urgency ("⏰ starting now").

**Email 6 (1 hour after):**
First conversion email and the most-opened post-webinar email. Open with the replay link (for the no-shows), then a 5-bullet summary of the webinar's key promises, then the offer. The reader is in maximum-attention mode — make the offer easy to find and easy to act on.

**Email 7 (24 hours after):**
By 24 hours the attendee is wavering. Address objections in their own words — use actual Q&A from the live event. "A lot of you asked X — here's the real answer." Reader sees themselves in the questions and the answers re-sell the offer.

**Email 8 (48 hours after):**
Final close. Real cart-close timestamp. Mention what they lose by waiting (bonuses expiring, cohort filling, next webinar isn't for 6 weeks — whatever's real). Short, urgent, link.

## Rules

- **Calendar links in email 1 are non-negotiable.** Every percentage point of calendar-add rate translates roughly 1:1 to show-up rate.
- **Send a separate SMS or push 10 min before** if the connector supports it. Email 5 alone won't catch everyone — multi-channel for the last reminder is industry standard.
- **The 1-hour-after email is the most important.** Most revenue from a webinar happens in the next 12 hours. Lead with the offer link.
- **Real scarcity only.** Bonus expiry, cart close, next cohort date. Fake "only 5 spots left!" on an evergreen webinar wrecks credibility.
- **Tag and exclude purchasers immediately.** Anyone who buys during the live should not get post-webinar emails 6-8.
- **No-show segment matters more than show segment.** No-shows convert at 30-60% of the show rate via replay — they're a big part of the revenue. Don't write them off.

## Variants

**Live webinar (real-time):** the default arc above works.

**Evergreen / on-demand webinar:** compress the pre-sequence to 3 emails (instant, 1 hour before show-time, 10 min before). The post-sequence is identical. Show-times are picked by the registrant at signup, so all timing is relative to their chosen slot.

**Workshop / multi-day event:** add a "Day 2 starts in 1 hour" email between each session. Post-event sequence starts after the FINAL session, not the first one.

## Common failure modes

| Failure | Why it costs revenue |
|---------|---------------------|
| No 1-hour-before reminder | Show-up rate drops 20-40% |
| Vague "what you'll learn" in email 2 | Reader doesn't re-commit; show-up rate drops |
| Long 10-min-before email | Reader skims and doesn't click — short = high CTR |
| 1-hour-after email leads with replay instead of offer | Buyers click the replay and never come back to the offer |
| No segmentation of attendees vs. no-shows | Attendees get told to "watch the replay" they just sat through |
| Post-webinar emails don't reference what was said live | Misses the chance to re-anchor to the live experience |
| Cart never actually closes | Trust collapse; harder to drive urgency on the next launch |

## Connector requirements

- Trigger on webinar registration event
- Pull webinar timestamp as a personalization token
- Tag attendees vs. no-shows from the webinar platform
- Halt sequence on purchase event
- Segment post-webinar emails by attendance status
- Calendar-link tokens (Google / Apple / Outlook)

## Calibration

If `brains/email/winners/webinar.md` exists, the show-up rate and post-webinar conversion rate per email should be tracked there. The "1 hour after" email is usually the highest-leverage one to iterate on — small subject line changes there can move total webinar revenue significantly.
