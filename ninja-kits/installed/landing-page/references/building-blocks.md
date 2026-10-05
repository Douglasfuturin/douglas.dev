# Section Building Blocks

A catalog of section types observed on high-converting landing pages, written as conceptual patterns — not scaffolded code. Pick the blocks that fit the page type and brand. Mix and match.

## Skeleton recipes by page type

### VSL page (cold traffic, e.g. Voics/Apex, Unorthodox Digital, Evan Carmichael)
```
1. Eyebrow qualifier band ("For coaches and agency founders making over $30k/mo")
2. Hero headline + VSL embed + ONE CTA directly under video
3. CTA banner (repeat CTA, add microcopy/guarantee tag)
4. Problem agitation (3-column or stacked, name the pain in their words)
5. Mechanism reveal (the named method or 3-pillar system)
6. Social proof (testimonial wall, marquee, or stacked grid)
7. Results screenshots (Stripe / dashboard / DM proofs)
8. Authority section (founder cred, press, named affiliations)
9. Offer / what's included
10. Risk reversal + guarantee
11. Urgency (cohort date / seat cap)
12. FAQ
13. Final CTA banner
14. Footer with cred
```

### Application page (warm/qualified, e.g. Passionate Few, Voics/Apex)
```
1. Eyebrow qualifier (filters in/out before the read)
2. Hero one-line promise + ONE CTA
3. Logo wall (celebrity / brand association)
4. Mechanism / what you get
5. Disqualifier ("Not for you if…")
6. Stacked testimonials with named results
7. Multi-step application form (qualifying questions = commitment device)
8. Final CTA / what happens next
```

### Challenge funnel (e.g. Client Ascension /challenge)
```
1. Hero with countdown + cohort dates + CTA
2. "What you'll learn" 3-5 bullet stack
3. Instructor cred bar
4. Testimonial wall (specifically from past cohorts)
5. Results screenshots
6. Seat scarcity banner
7. Offer recap + price (if disclosed) or "free" framing
8. FAQ
9. Final register CTA with countdown
```

### Webinar registration (e.g. Grant Cardone 10X BLT)
```
1. Hero (date + time + headline benefit + ONE CTA → modal form)
2. "What you'll learn" (3-5 bullets)
3. Host credibility (photo + bio bar)
4. CTA banner
5. Social proof (testimonial row + quantified track record)
6. Final CTA
```

### Squeeze / lead magnet (e.g. Collective Genius / Jason Lewis)
```
1. Hero (single screen, 100vh):
   - Logo top-left
   - Headline + 3 curiosity bullets on the left
   - Lead magnet mockup + form on the right
   - Form has ONE CTA
2. (Optional) tiny footer with cred
```
That's it. No scroll required.

### High-ticket interstitial (e.g. Acquisition.com ACE)
```
1. Brand bar / logo
2. Glassmorphic card with:
   - Animated sparkle / loader
   - "We're preparing your personalized…" copy
   - Fallback: "Book a call with our team" CTA → calendar
```
The page itself IS the conversion event — even the failure state is a funnel.

---

## Block library (mix and match)

### B1. Qualifier eyebrow pill
The very first thing the visitor reads. Filters in/out.

> "For coaches and agency founders making over $30k/mo"
> "For real estate investors who already mail 5,000+ postcards/month"
> "For SaaS founders at $10K–$100K MRR"

Visual: small pill above the headline, brand color or muted, 12-14px, uppercase optional.

### B1a. Bloomberg-terminal status pill (Client Ascension signature)
A premium variant of B1 that doubles as section eyebrows. Used to chapter the page and stack urgency.

> ● LIVE EVENT     ● LIMITED SPOTS AVAILABLE     ● SIGNUPS CLOSING SOON     ● URGENT

```css
.status-pill {
  font-family: "Geist Mono", monospace;
  font-size: 12px;
  letter-spacing: -1px;        /* the secret — negative tracking on mono */
  text-transform: uppercase;
  color: #FF0004;
  border: 1px solid #FF0004;
  border-radius: 999px;
  padding: 6px 12px;
}
.status-pill::before { content: "● "; }
```

The negative letter-spacing on a monospace font is the move — it reads as "data terminal", not "code". Use the same pill style for the page eyebrow AND for every section header.

### B2. Hero headline (the one-line promise)
The boldest line on the page. Loud, specific, outcome-focused.

Variants:
- Contrarian: "Stop chasing leads. This converts the ones you already have."
- Promise + timeframe: "Book 12 sales calls in 30 days — without paid ads."
- Named mechanism: "The KFC Method: How we turn cold strangers into $5K clients in under 14 days."
- Negation of dream: "Getting more leads isn't going to save your business."
- Highlighted clause: "Stop chasing views and **Start Building a pipeline**." (with the second clause in brand color)

### B3. Hero subheadline
Answers "and what does that mean specifically?"

> "We build a YouTube engine that brings you 5-figure clients while you sleep. Or you simply don't pay. In writing."

### B4. Hero CTA + microcopy
ONE button. Specific verb. Microcopy below the button removes friction.

```
[ Apply Now → ]
30-day money-back guarantee. No credit card required.
```

### B5. VSL embed wrapper
16:9 responsive, 56.25% padding-top wrapper. Auto-play muted (with prominent unmute UI), or click-to-play with a custom poster.

Pattern: `<div class="vsl-wrap"><iframe ... /></div>` with `.vsl-wrap { position: relative; padding-top: 56.25%; }` and `.vsl-wrap iframe { position: absolute; inset: 0; width: 100%; height: 100%; }`.

Bonus: add a pulsing brand-color glow behind the wrapper. (Unorthodox Digital does this with `vsl-pulse` animation.)

### B6. CTA-banner-below-video
Right after the VSL — a band with the same CTA again, plus a guarantee tag underneath.

```
[ Yes — Book my Strategy Call → ]
Unlimited revisions. Refund guarantee.
```

### B7. Logo wall (celebrity / client / press)
A row of 6-12 logos. Greyscale or single-color. Equal visual weight.

If real client logos available: use them.
If positioning by association (e.g. Passionate Few uses Hormozi/Robbins/Cardone): use celebrity logos with implicit "we work in the same world" framing.
If neither: skip the section.

### B8. Pain agitation (3-column or stacked)
Name the pain in the visitor's own words. Specific, visceral.

3-column:
```
[ "You spent $4,300       [ "Your offer worked         [ "You're the bottleneck.
   on ads last month         a year ago. Now              Every $1 needs an
   and got 6 calls."         conversions are dead."       hour of your time." ]
```

### B9. Mechanism reveal (3-pillar system)
The named mechanism is your IP. It separates you from the generic.

```
The KFC Method:
1. Key — find the keyword nobody's targeting
2. First click — own that keyword's #1 spot
3. Conversion — turn that click into a $5K call
```

Always 3 pillars. Always memorable. Always named.

### B10. Social proof — testimonial card (named, photo, specific)
The atomic unit of social proof.

```
[Photo]   "I went from $0 to $34K MRR in 90 days using this exact playbook.
           Closed two deals from a single LinkedIn DM template."
           — Sarah K., Real Estate Coach, Austin
           [Result badge: $34K MRR]
```

Don't ship testimonials without all four: photo, name, role/location, specific result with a number.

### B11. Social proof — marquee testimonial wall
For pages with 20+ testimonials. 3-4 rows of cards scrolling at variable speeds (50s / 65s / 42s / 58s) so it feels organic, not robotic.

Voics/Apex uses this with text-only cards.
Views-to-Clients uses this with screenshot proofs.

CSS: `@keyframes scroll { from { transform: translateX(0) } to { transform: translateX(-50%) } }` on a duplicated track.

### B12. Results screenshots (proof stack)
2-6 screenshots of real results. Stripe payments, calendar bookings, DM screenshots, dashboard wins.

Each screenshot should be:
- Visually distinct (chart, dashboard, DM, Stripe, calendar — vary)
- Captioned with what it shows
- Sized consistently in a row

If generating fakes: clear "Example" watermark + believable but specific numbers.

### B13. Authority bar (founder cred)
Single row: founder photo + 3-5 credentials.

```
[Photo]   Jake Trinder
          Built and exited 2 agencies ($4M+ revenue)
          $47M in client revenue generated
          Featured in Inc, Forbes, Entrepreneur
```

### B14. "Who this is for / not for" split
Two-column compare. Green checks on the left, red X's on the right.

```
THIS IS FOR YOU IF                   THIS IS NOT FOR YOU IF
✓ You run an established business    ✗ You're looking for get-rich-quick
✓ You have a working offer           ✗ You need someone to do the work
✓ You can invest in growth           ✗ You think tactics > strategy
```

### B15. Offer stack (price anchor)
Itemized deliverables with right-aligned dollar values. Total at the bottom. Discounted current price below.

```
Module 1: Foundation                  ($2,997)
Module 2: Outreach System             ($4,997)
Module 3: Sales Framework             ($1,997)
Bonus: Weekly 1:1 coaching            ($9,997)
Bonus: Template library               ($1,497)
                                      ─────────
                                      Total: $21,485

Your investment today: $4,997
```

### B16. Risk reversal banner
Bold guarantee. Specific. Visible.

```
🛡 The "Money Back, Plus" Guarantee
If you don't book 5 qualified calls in 30 days, we'll refund every dollar
AND give you our full sales playbook ($2,000 value) to keep.
```

(Use the shield emoji ONLY if the brand allows emoji. Otherwise inline SVG icon.)

### B17. Urgency / scarcity banner
Real urgency only. Specific dates and numbers.

```
COHORT STARTS APRIL 19, 2026  ·  47 of 200 seats remaining
```

### B18. FAQ (objection-handler, not curiosity)
Each FAQ should handle a specific objection — not ask "is this for me?" but answer "what if X goes wrong?".

Accordion pattern. 5-8 questions max. The most common objection should be #1.

Good FAQ questions:
- "What happens if I can't make the live calls?"
- "How is this different from [obvious competitor]?"
- "What if it doesn't work for my specific niche?"
- "How much time per week does this require?"
- "Can I get a refund if I change my mind?"

### B19. Final CTA banner
The bottom-of-page closer. Bigger than mid-page CTAs. Often full-bleed with brand-color background.

```
        You've seen the results. You've seen the system.
        Now it's time to decide.

              [ Book My Strategy Call → ]

        47 seats remaining · Cohort starts April 19
```

### B20. Footer cred bar
Minimal. Logo + 1-2 lines + copyright. Optionally a small "as seen in" press strip.

### B21. Sticky pill nav with glass blur
Premium dark pages. Sits at top, `backdrop-filter: blur(20px)`, transparent background with `border: 1px solid rgba(255,255,255,0.08)`. Holds: logo + 2-4 nav items + CTA button.

### B22. Multi-step application form
Used for high-ticket application pages. Each step is a micro-commitment.

Step 1: email + name
Step 2: business stage / revenue (qualifier)
Step 3: what's your biggest challenge?
Step 4: book a call slot

Progress bar at the top. Each step has its own headline (e.g. "Quick — what's your monthly revenue?") to keep momentum.

### B23. Calendar widget (call booker)
iClosed, Calendly, SavvyCal, or a custom widget. Inline embed, brand-colored.

If the offer is high-ticket, the calendar should appear AFTER a qualifier step — not as the first interaction.

### B24. Animated counter
Numbers ticking up on scroll-into-view. Used for "$47M generated", "4,217 founders served", etc.

JS: IntersectionObserver fires once → rAF interpolation from 0 to target.

### B25. Faint diagonal grid / dot grid background
Subtle hero background. 1px lines or 1px dots at 6deg rotation, 4% opacity, on a dark surface.

### B26. Floating UI mockup / dashboard screenshot
Tilted slightly (`transform: perspective(1000px) rotateX(8deg) rotateY(-4deg)`), with a soft shadow. Used to showcase a product or system.

### B27. Glassmorphic card
Used for hero CTAs, app interstitials, premium dark themes. `backdrop-filter: blur(20px)`, semi-transparent surface, soft border, soft glow.

### B28. Ambient gradient orbs (background atmosphere)
1-3 large soft-blurred radial gradients (brand color, 20-30% opacity) positioned absolutely behind the hero. Animate slowly with `animate-float` (subtle translateY + rotate over 12-20s).

### B29. Loading dots / "AI preparing your offer" pattern
For interstitial/preparation pages. Shimmer text + animated dots + a fallback CTA.

Used by Acquisition.com when their personalized-offer page fails — the failure becomes a calendar-booking conversion event.

### B30. Sticky bottom mobile CTA
On mobile, after the user scrolls past the hero, a sticky bar appears at the bottom of the viewport with the primary CTA. Disappears when the user scrolls back to the hero (no double-CTA confusion).

---

## Conversion stacking rules

When picking blocks, observe these stacking patterns from the best-converting pages:

1. **CTA every 1-1.5 viewport heights.** Long pages need 5-8 CTA placements. Short pages need 2-3. Never make the visitor scroll up to find the button.
2. **First proof block within 1 viewport of the hero.** Don't make the visitor wait for social proof.
3. **Risk reversal BEFORE the final CTA, not after.** Visitors who've decided to convert don't need the guarantee anymore — visitors who are hovering do.
4. **Urgency at the END.** Front-load the value, back-load the deadline. Reversed kills trust.
5. **One CTA destination per page.** If the page has multiple buttons, every button must lead to the same action.

## Anti-blocks (don't ship these)

- Generic "Our Process" with 4 numbered steps and abstract icons
- "Our Values" section on a sales page
- "Meet the team" headshots grid (unless authority is the whole pitch)
- Newsletter signup CTA mixed in with the primary CTA (one goal per page)
- "Subscribe to our podcast" / "Follow us on social" anywhere above the fold
- A blog teaser carousel ("From our blog")
- Cookie banner with three buttons (use the smallest possible compliance widget)
