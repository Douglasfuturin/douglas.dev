# Post-Purchase Sequence Framework

> **Goal:** reduce refunds, increase usage, set up the next purchase. The single biggest determinant of customer LTV is what happens in the first 14 days after the order.

A great post-purchase sequence drops refund rate by 30-50% and lifts cross-sell take rate 2-3×. Most brands run a "thanks for your order" auto-reply and call it done — which is leaving compound money on the table.

## Default arc — 4 emails over 14 days

| # | Time after purchase | Beat | Body purpose | Length |
|---|--------------------|------|--------------|--------|
| 1 | within 5 min | **Confirm + first win** | order confirmation, access details, the one thing to do FIRST | 150-300 words |
| 2 | Day 2 | **How to get the most out of it** | best practices, common patterns, expectation-setting | 300-500 words |
| 3 | Day 7 | **Common mistakes / FAQ** | the top 3 things people get wrong, and how to avoid them | 300-450 words |
| 4 | Day 14 | **What's next** | natural upsell or referral request — only after value is delivered | 250-400 words |

## Psychology of each beat

**Email 1 — Confirm + first win:**
The buyer is at peak anticipation. They want to start using what they bought. Don't bury access details in fine print — lead with: "Here's how to log in" or "Here's where your tracking is." Then add ONE clear "do this first" instruction. Most buyer's remorse comes from not knowing where to start — kill that on email 1.

**Email 2 — How to get the most out of it:**
This is the expectation-setting email. What does success look like in week 1? What's normal? What should they NOT panic about? For physical products: how to use it / care for it. For digital: the best path through the content. For services: what happens next.

**Email 3 — Common mistakes / FAQ:**
By Day 7 the buyer has hit their first friction point. Beat them to it. Open with: "Here are the 3 things most people get wrong in the first week." This single email kills more refund-window cancellations than any other touchpoint.

**Email 4 — What's next:**
ONLY pitch the next thing after delivering on the current thing. By Day 14 the buyer either loves it (great, here's the next step) or hates it (the right move is to ask for feedback, not pitch). If LTV data shows refund cliff at Day 14, this email also serves as the "still happy?" check-in.

## Rules

- **Lead with value, not pitch.** Each email should give something concrete before asking for anything. Day 1 doesn't pitch. Day 2 doesn't pitch. Day 7 doesn't pitch. Only Day 14.
- **Segment by product.** A "how to get the most out of it" email is meaningless if it's generic — the post-purchase sequence must be different for each product.
- **Track refund window.** If the product has a 14-day refund window, Day 14's email is critically timed. Either capture the customer firmly before then, or proactively offer support.
- **Re-segment on completion.** When the customer hits a usage milestone (logged in, watched first lesson, used the product), tag them. The next email's content can branch on that tag.
- **Reply rate is the real KPI.** A post-purchase email that gets 5%+ reply rate is doing the relational work — track it alongside open/click.

## Common failure modes

| Failure | Why it costs money |
|---------|--------------------|
| Generic "thanks for your order" auto-reply | Misses the highest-attention moment in the customer lifecycle |
| Burying access info | Confused buyers refund within 48 hours — the #1 controllable refund cause |
| Pitching the upsell in Day 1-7 | Buyer hasn't received value yet; the upsell feels predatory |
| No FAQ email | Friction at Day 5-7 turns into refund tickets instead of "I figured it out" |
| Same sequence for all SKUs | Generic content gets ignored; segmented content converts |
| No completion tracking | Can't tell who got value vs. who's about to refund |

## Variants

**For high-ticket services / coaching:** stretch to 8 emails over 30 days. Add a Day 21 case-study email (someone like the buyer who succeeded) and a Day 30 community/connection email.

**For digital products with a usage curve (courses, software):** trigger Day 2 only if the buyer has logged in. If they haven't, send a "your account is waiting" recovery email instead. Most refunds in digital come from people who never logged in.

**For physical products:** add a "your order shipped" and "your order delivered" before email 1's content. Don't compress them into the same email — they each have a different purpose.

## Connector requirements

- Trigger on purchase event (per product or product category)
- Pull purchase metadata (`{product_name}`, `{order_id}`, `{access_url}`, `{tracking_url}`)
- Branch on usage events (login, first session, etc.) if the product can emit them
- Track refund / cancellation events to halt sequence on refund

## Calibration

If `brains/email/winners/post-purchase.md` exists, the past sequences should track refund-rate-per-email-sent — which email correlated with reduced refunds. Optimize against refund rate, not open rate (post-purchase emails open at 70-90%; the real signal is what happens after they read).
