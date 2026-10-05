# Deliverability Rules

> The fastest way to wreck an email program is great copy that never reaches the inbox. Every sequence this skill drafts must pass these rules before being pushed to [EMAIL PLATFORM].

## Hard rules — refuse to ship if violated

These are non-negotiable. The skill should not push to [EMAIL PLATFORM] if any are present:

- **No misleading subject lines.** "RE:" or "Fwd:" prefixes when there's no actual thread. "Your order has shipped" when nothing shipped. These trigger spam filters AND damage long-term sender reputation.
- **No deceptive sender names.** Sender must match [VOICE OWNER] or a clearly-identified team member — never a fake person, never a generic "Team" alias if the body is written first-person.
- **No image-only emails.** At minimum 3:1 text-to-image ratio. Pure-image emails get classified as promotional or spam.
- **No URL shorteners (bit.ly, tinyurl, etc).** Spam filters flag them. Use the [EMAIL PLATFORM] native tracking or a branded short domain.
- **Working unsubscribe link in every email.** Not optional. Legally required (CAN-SPAM, GDPR, CASL). [EMAIL PLATFORM] handles this — confirm it's enabled before pushing.
- **Real physical address in footer.** CAN-SPAM requirement. [EMAIL PLATFORM] usually handles this — confirm it's populated.
- **No attachments.** Spam filters flag every attachment. Always use a hosted link instead.

## Soft rules — flag and warn

These don't block sending but should be flagged to the user before push:

- **Subject lines over 7 words.** Cut on mobile, lower opens.
- **Spam trigger words in subjects** ("FREE", "GUARANTEED", "ACT NOW", "LIMITED TIME", multiple "!", ALL CAPS, "$$$"). Filters are smarter than they used to be, but stacking these increases promotions-tab placement.
- **More than 3 links in a single email.** Filters interpret high link density as promotional.
- **Sending to a segment with <10% engagement in last 90 days.** Sending to dead segments tanks domain reputation. Suggest running `/email re-engagement` first.
- **No plain-text version.** [EMAIL PLATFORM] should auto-generate but confirm it's enabled — pure-HTML emails get spam-filtered more often.
- **Sending more than 1 broadcast per day from the same domain.** Frequency above this raises spam complaint rate dramatically.

## Subject line filters — strip these patterns

Before pushing, strip or warn on subjects containing:

- Excessive punctuation (`!!!`, `???`, `!!`)
- ALL CAPS words (more than one uppercase word in a row)
- Currency symbols followed by numbers (`$100`, `€50`)
- Specific spam-tripwire phrases: "FREE", "ACT NOW", "LIMITED TIME OFFER", "CONGRATULATIONS", "WINNER", "GUARANTEED"
- `RE:` or `Fwd:` prefixes when there's no actual thread

Many of these are valid in certain contexts (e.g., a price drop email can mention "$50 off"). The skill should warn rather than block — the user makes the call.

## Body content filters

- **No "Click here" link text.** Use descriptive anchor text. "Click here" both kills accessibility and trips spam filters.
- **No invisible-text tricks.** White text on white background, 1px text, etc. are old spam-evasion tricks and get caught instantly.
- **Image alt text on every image.** Required for accessibility AND for the email to render meaningfully when images are blocked (most corporate inboxes block by default).
- **HTML must be clean.** No leftover tracking pixels from a previous platform, no broken tags, no inline styles that don't render in Outlook. [EMAIL PLATFORM]'s test send should be the final check.

## Pre-send checklist

The skill must run this before any push to [EMAIL PLATFORM] as a draft:

- [ ] All hard rules pass
- [ ] Soft rules: warnings surfaced to user
- [ ] Unsubscribe link present and working
- [ ] Physical address in footer
- [ ] All links are real (no broken URLs, no `{placeholder}` tokens left unfilled)
- [ ] All personalization tokens have fallbacks (`{first_name|Friend}`)
- [ ] Plain-text version generated
- [ ] Test send to [VOICE OWNER]'s own inbox FIRST
- [ ] Test send opens correctly in: Gmail (web + mobile), Outlook, Apple Mail
- [ ] Subject and preview text don't repeat each other

## Per-platform notes

Different [EMAIL PLATFORM]s have different deliverability behaviors:

**ActiveCampaign:** strong reputation if list hygiene is maintained. Has built-in spam check — run it.

**Klaviyo:** good for e-commerce. Aggressive engagement-based throttling — old subs get suppressed automatically. Monitor the "engagement score" segments.

**ConvertKit:** creator-focused; usually clean. Doesn't have built-in spam scoring — rely on this checklist.

**Customer.io:** B2B SaaS focus. Easy to send too-often via behavioral triggers. Watch the frequency caps.

**HighLevel / GoHighLevel:** shared IP pools — domain reputation can swing based on other senders. Use a dedicated IP if budget allows.

## Domain warm-up

If [CLIENT NAME] is sending from a new domain or new dedicated IP:

- **Week 1:** ≤ 500 sends/day to only most-engaged segment
- **Week 2:** ≤ 1,500 sends/day, still engaged segments
- **Week 3:** ≤ 5,000 sends/day, broader segments
- **Week 4+:** full sending, but monitor bounce + complaint rates

If bounce rate > 2% or complaint rate > 0.1%, pause sends and audit. These are the metrics ESPs use to flag senders.
