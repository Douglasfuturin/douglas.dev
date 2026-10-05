# Abandoned Cart Sequence Framework

> **Goal:** recover the order. ~70% of carts get abandoned across e-commerce; a well-tuned 3-email recovery sequence typically pulls back 10-20% of those.

This is the highest-ROI sequence in the system. The reader was 30 seconds from buying — they don't need to be sold, they need to be reminded, reassured, and given a reason to come back now.

## Default arc — 3 emails over 72 hours

| # | Time after abandon | Beat | Body purpose | Length |
|---|--------------------|------|--------------|--------|
| 1 | 1 hour | **Friendly reminder** | "did something go wrong?" — soft, helpful, low-pressure | 80-150 words |
| 2 | 24 hours | **Objection handling + proof** | the most common reason this product gets second-guessed, addressed head-on | 200-350 words |
| 3 | 72 hours | **Real urgency or final nudge** | either real scarcity (stock, price expiry) or "last reminder before we stop emailing about this" | 80-180 words |

## Psychology of each beat

**Email 1 (1 hour) — Friendly reminder:**
At 1 hour the cart is still warm. The reader probably got distracted — phone died, slack pinged, kid yelled. Don't sell. Just remind. Lead with: "saw you didn't finish — anything I can help with?" plus the cart link. The shorter and more human, the better.

**Email 2 (24 hours) — Objection handling + proof:**
By 24 hours the reader has had time to second-guess. They're not distracted anymore — they're hesitating. Surface the most common objection for this product and address it directly. Include one specific proof point (review quote, return policy, shipping speed, whatever the objection is).

**Email 3 (72 hours) — Final nudge:**
The reader is either coming back or they're gone. This is the last shot. Either:
- **Real scarcity option:** product is selling out, price is expiring, free shipping window is closing — must be TRUE, not manufactured
- **Honest last-call option:** "I won't email you about this again — here's the cart link one more time, and here's why I think it'll work for you"

**Never invent urgency.** Fake scarcity in abandoned cart emails is the #1 cause of trust collapse — buyers see through it instantly, and one bad experience kills repeat purchase.

## Rules

- **Cart link in every email.** Don't bury it. Pin it visually near the top and again at the bottom.
- **Show the product visually.** Image + name + price. The reader's brain needs to re-recognize what they almost bought.
- **No discount until email 3 (and even then, only if necessary).** Discounting on email 1 trains buyers to abandon-then-wait — a margin disaster at scale.
- **Personalization is allowed here.** First name, product name, even "you were looking at the [color] one" — the reader expects this; it's transactional.
- **Stop the sequence on purchase.** Connector must check purchase state before sending each email. Sending email 3 after they bought = trust collapse.

## Discounting strategy (optional)

If the business model supports discounting:
- **Email 1:** never discount
- **Email 2:** never discount
- **Email 3:** small discount (5-10%) IF the cart value justifies the margin hit. Frame as "here's a small thank you for coming back."

If the business model does not support discounting (premium / handmade / capacity-limited):
- All 3 emails sell on value, not price. The "last nudge" email leans on real-product scarcity or expertise instead.

## Common failure modes

| Failure | Why it kills recovery |
|---------|----------------------|
| Email 1 is too sales-y | Reader thinks "ugh, marketing" and archives — they wanted a reminder, not a pitch |
| All 3 emails look the same | No new information across the sequence → reader stops opening after email 1 |
| Discount in email 1 | Trains the audience to abandon-then-wait; destroys long-term margin |
| Manufactured urgency in email 3 | "Only 2 left!" when stock is 50 → trust collapse, refund risk |
| Sending email 3 after purchase | Connector didn't check state; reader feels harassed |
| Missing cart link | Reader has to remember what they were looking at and find it again — most won't |

## Connector requirements

This sequence ONLY works if the [EMAIL PLATFORM] connector can:
- Trigger on the abandoned-cart event from the e-commerce platform
- Inject `{cart_url}`, `{product_name}`, `{product_image}`, `{cart_value}` personalization tokens
- Halt the sequence on purchase event

Confirm these are wired before drafting. If the connector can't halt on purchase, do not deploy this sequence — the reputational damage from emails-after-purchase is worse than the recovery upside.

## Calibration

If `brains/email/winners/abandoned-cart.md` exists, the language and timing in those past winners are usually better calibrated than the defaults — the abandon-cart audience is unusually homogeneous per business, so winners replicate well.
