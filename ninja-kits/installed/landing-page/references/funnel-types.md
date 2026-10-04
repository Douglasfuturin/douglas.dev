# Funnel Types & Page Archetypes

A taxonomy of direct-response landing pages, grouped by intent. Pick the archetype first, then assemble blocks from [building-blocks.md](building-blocks.md).

The right archetype is determined by THREE inputs:
1. **Traffic temperature** — cold (paid ads) / warm (email, podcast) / hot (existing customers)
2. **Offer price + complexity** — free / sub-$100 / $100-1000 / high-ticket ($1K+) / enterprise
3. **CTA goal** — email opt-in / call book / apply / purchase / register

---

## Tier 1 — Lead Capture (top of funnel)

Goal: get an email or contact. Low commitment, low information delivered.

### 1.1 Squeeze page (single-screen)
**Use when**: warm traffic (podcast / email) for a free lead magnet. Visitor came specifically for one thing.

**Anatomy** (`min-height: 100vh`):
- Logo top-left
- Headline + 3 curiosity-loop bullets on the left
- Lead magnet mockup + email form on the right
- ONE CTA — no scroll required

**Live example**: Collective Genius / Jason Lewis (real estate playbook for podcast listeners).

**Conversion rate benchmark**: 35-60% to email opt-in for matched traffic. Below 30%, the headline or magnet is off.

**Anti-pattern**: adding social proof, FAQ, or testimonials to a squeeze. If you need them, it's not a squeeze — use 1.2 instead.

---

### 1.2 Opt-in with supporting details (short page)
**Use when**: colder traffic that needs more convincing than a pure squeeze, but the ask is still just an email.

**Anatomy** (one fold of scroll):
- Hero (headline + sub + form/CTA)
- 3-5 proof bullets or 1 testimonial
- Lead magnet mockup
- Trust strip (logos or "X subscribers")
- Form

**Conversion rate benchmark**: 25-45%.

**Variant — Two-step opt-in**: Replace the inline form with a button that opens a modal form. Reduces visible friction; lifts conversion 10-30% in many tests. The modal IS the form.

---

### 1.3 Quiz funnel
**Use when**: you can segment a heterogeneous audience into 3-5 distinct buckets, each of which deserves a different offer/message.

**Anatomy**:
- Hero: "Take the 60-second {topic} assessment to get your personalized {output}"
- One CTA → quiz starts
- 5-10 multi-choice questions (use progress bar)
- Email gate at the end (right before the result)
- Personalized result screen → tailored offer/next-step

**Why it works**: commitment-consistency (visitor invested 60-90 seconds answering) + reciprocity (personalized output) + segmentation (each bucket gets the right pitch).

**Conversion rate benchmark**: 60-80% complete the quiz; of those, 35-55% give email.

**Tools**: Typeform, ScoreApp, Interact, Outgrow, or custom React multi-step.

---

### 1.4 Survey funnel
**Use when**: you want to qualify AND collect data for a downstream sales conversation. Distinct from quiz in that there's no "personalized result" — the survey itself is the conversion path.

**Anatomy**:
- Hero: a real problem statement + "answer 5 questions to {get the thing}"
- Multi-step questions, each tying to a real qualifier (revenue band, role, current tool stack)
- Email + name at the end
- Either: routes to a calendar (high-ticket) or to a free resource (mid-ticket)

**Live example**: Evan Carmichael's `/content-strategy` uses a 2-step survey before showing the application call.

**Conversion rate benchmark**: 40-65% complete.

---

## Tier 2 — Education-Heavy / Long-Form (cold-traffic conversion)

Goal: take a stranger and educate/persuade them enough to act in a single page session.

### 2.1 VSL page (Video Sales Letter)
**Use when**: cold paid traffic for a $500-$5,000 offer or high-ticket call. The page lives or dies by the video.

**Anatomy**:
- Eyebrow qualifier ("For {tribe} making over ${revenue}")
- Hero headline + VSL embed (autoplay muted or click-to-play)
- ONE CTA directly under the video
- CTA-banner repeat below
- Problem agitation (3-col or stacked)
- Mechanism reveal (named system)
- Social proof (testimonial wall + results screenshots)
- Authority (founder cred bar)
- Offer / what's included (price-anchored stack)
- Risk reversal / guarantee
- Urgency (cohort or scarcity)
- FAQ
- Final CTA banner
- Footer cred

**Live examples**: Voics/Apex, Unorthodox Digital, Evan Carmichael.

**Conversion rate benchmark**: 1-5% to booked call from cold ad traffic. Above 5% the VSL is exceptional.

**VSL length**: 15-45 minutes for high-ticket. 5-15 minutes for mid-ticket. Anything under 5 min usually underperforms because there's not enough belief-building time.

---

### 2.2 Long-form text VSL (no video)
**Use when**: same goal as a VSL page but the offer creator either can't/won't shoot video, or the audience is text-preferring (e.g. older investors, financial buyers).

Same anatomy as 2.1 but the VSL slot is replaced with a 1500-3000 word sales letter. Heavy use of:
- Story-arc framing (origin story → revelation → method → results)
- Subheadlines every 2-3 paragraphs to support skim-readers
- Pull-quotes / bolded key sentences
- Inline screenshots and bullets every 4-5 paragraphs

**Live example**: Marketing.mba (KFC Method) — text-only, no VSL, still long-form.

---

### 2.3 Webinar registration page
**Use when**: the offer requires more time/teaching than a VSL allows, AND the host can build a list of registrants for follow-up. Lower commitment than buying = higher opt-in rate.

**Anatomy** (short page, single fold or slight scroll):
- Hero: date + time + headline benefit + CTA → modal form
- "What you'll learn" (3-5 bullets, curiosity-loop)
- Host credibility (photo + bio bar)
- CTA banner repeat
- Social proof (1-2 testimonials + quantified track record)
- Final CTA + urgency ("Doors close {date}" or "Only 200 seats")

**Live example**: Grant Cardone 10X BLT (free webinar registration with red aggressive CTAs).

**Conversion rate benchmark**: 25-45% reg rate from matched paid traffic.

**Variant — Live workshop vs. evergreen webinar**: the page is structurally identical, but live = real urgency, evergreen = "starts in X minutes" perpetual urgency (lower-trust but higher-volume).

---

### 2.4 Challenge funnel
**Use when**: you want a multi-day immersive lead nurture that warms a cold visitor to a higher-ticket back-end.

**Anatomy**:
- Hero with cohort dates + countdown + CTA
- "What you'll learn over 5 days" stack
- Instructor cred bar
- Past-cohort testimonial wall (specifically from prior challenges)
- Results screenshots
- Seat scarcity banner
- Offer recap + price ("free" or low-ticket like $47)
- FAQ
- Final register CTA with live countdown

**Live example**: Client Ascension / challenge (challenge → back-end coaching ascension).

**Conversion rate benchmark**: 30-55% reg from matched traffic; 5-15% of challenge attendees buy the back-end offer.

---

## Tier 3 — High-Ticket / Qualified (filtering serious buyers)

Goal: filter for high-intent buyers and route them into a sales conversation. Volume is irrelevant — quality is everything.

### 3.1 Application page
**Use when**: $5K+ offer with a sales call before purchase. Need to filter time-wasters before the call.

**Anatomy**:
- Eyebrow qualifier (filter in/out at line 1)
- Hero one-line promise + ONE CTA → form
- Logo wall or celebrity association
- Mechanism / what you get
- Disqualifier list ("Not for you if…")
- Stacked testimonials with named results
- Multi-step application form:
  - Step 1: email + name
  - Step 2: business stage / revenue (qualifier)
  - Step 3: biggest challenge (data + commitment)
  - Step 4: book a call slot
- Final CTA / what happens next

**Live examples**: Passionate Few ($4,999+ paid podcast spots), Voics/Apex.

**Conversion rate benchmark**: 0.5-3% of cold traffic submits a full application. Of those, 30-60% book a call. Of booked calls, 20-40% close (varies by offer/sales process).

**Form length tradeoff**: more questions = fewer applicants but higher quality. For premium offers, ask budget + revenue + a "why now" qualifier. For ultra-premium ($25K+), ask 8-12 questions.

---

### 3.2 Direct call booker (calendar-first)
**Use when**: warm/referred traffic where the visitor already knows they want to talk. No persuasion needed — just remove friction.

**Anatomy**:
- Brief header (logo, optional 1-line value prop)
- Big calendar widget embedded inline (iClosed, Calendly, SavvyCal)
- Trust strip below (1-3 logos or quantified result)
- That's it

**Live example**: Studio Flow's `#schedule` anchor — iClosed widget inline, no popup, no email gate.

**Conversion rate benchmark**: 35-70% book rate from warm traffic.

---

### 3.3 Interstitial / personalized AI page
**Use when**: dynamic offer generation. The page is personalized to the visitor based on submitted data, or a sales call is being prepared.

**Anatomy**:
- Glassmorphic card / dark premium aesthetic
- Animated loader / sparkle / progress text
- "We're preparing your personalized {output}" copy
- Fallback CTA: "Book a call with our team" → calendar (in case the AI fails)

**Live example**: Acquisition.com ACE interstitial — when their AI personalized-offer page can't render, the failure state becomes a calendar-booking funnel.

**Key insight**: the failure state IS a conversion opportunity. Design for the failure.

---

## Tier 4 — Direct Purchase (transactional)

Goal: take the credit card on the same page. No call, no email gate.

### 4.1 Long-form sales page (direct-to-cart)
**Use when**: $97-$2,000 offer that doesn't justify a sales call but needs heavy persuasion.

**Anatomy**:
- Hero with headline + sub + first CTA → checkout
- Pain agitation
- Mechanism / story
- What's included (modular breakdown)
- Bonus stack
- Social proof / testimonial wall
- Price anchor → discounted price → CTA
- Risk reversal / money-back banner
- Urgency
- FAQ
- Final CTA
- Footer

**Conversion rate benchmark**: 1-4% to purchase from cold traffic.

**Critical difference vs VSL page**: the CTA goes directly to a Stripe/checkout page, not a calendar or form. Every CTA must deeplink into a pre-filled checkout.

---

### 4.2 Tripwire / low-ticket entry ($7 – $97)
**Use when**: convert visitors to BUYERS as fast as possible. Real money matters (not "free") because a $7 buyer behaves more like a $7,000 buyer than like an opt-in visitor.

**Anatomy**:
- Hero: one specific deliverable + price ("Get the playbook for $7")
- 3-5 bullets of what's inside
- One screenshot/mockup
- Single CTA → checkout
- Trust strip + guarantee microcopy below button
- Optional: 1-2 testimonials below the fold

**Live example**: Unorthodox Digital's $97 tripwire (anchored to their $5K+ tier three separate times so the visitor sees the ascension path).

**Why $7-$97**: low enough to be impulse-friendly, high enough to filter for real money. $1 trials and "free trials" attract a worse downstream cohort.

**Ascension play**: every tripwire page should mention the upgrade tier explicitly so buyers see where they're going.

---

### 4.3 Book funnel / Free + Shipping
**Use when**: the offer creator wrote a book that doubles as a lead magnet. "Free" book — visitor pays $7-15 shipping. Card-on-file enables upsell sequence.

**Anatomy**:
- Hero: 3D book mockup + "Free book — just pay shipping"
- Bullets: what you'll learn
- Author cred + testimonials
- Checkout form on the same page (shipping address + card)
- Order bump: "Add the audio companion for $19?"
- Post-purchase upsell page: "While we ship your book, would you like…"

**Conversion rate benchmark**: 4-12% to claim the book. 15-30% take the order bump. 5-15% take the upsell.

---

### 4.4 Bridge / pre-sell page
**Use when**: you're an affiliate or driving traffic from a content platform (YouTube, podcast) to a 3rd-party checkout. The bridge page warms the visitor before the actual sales page.

**Anatomy**:
- Hero: "If you're here from {source}, here's what you need to know"
- 1-2 minute "context video" or short text
- One CTA → external sales page / affiliate link

Short, dense, almost-but-not-quite a squeeze.

---

## Tier 5 — Event / Live (in-person or live-stream)

Goal: ticket sale or registration for a live event.

### 5.1 Live event registration
**Use when**: in-person seminar, conference, mastermind weekend.

**Anatomy**:
- Hero with date / city / venue / CTA
- Speaker grid (headshots + bios)
- Agenda / schedule
- Past-event photos + testimonials
- Ticket tiers + early-bird pricing tiers
- Hotel / travel info
- Final CTA

**Conversion rate benchmark**: 0.5-3% from cold traffic; warm traffic (email list) often 5-15%.

---

### 5.2 Live workshop / online seminar
Similar to 2.3 (webinar reg) but with a paid ticket and a longer-form agenda. Treat it as a hybrid: web reg structure + ticket pricing tiers.

---

## Picking the right archetype (decision tree)

```
Is the offer free?
├── Yes
│   ├── Email-only ask?
│   │   ├── Single specific magnet → 1.1 Squeeze
│   │   ├── Needs more convincing → 1.2 Opt-in with details
│   │   ├── Multi-segment audience → 1.3 Quiz
│   │   └── Pre-qualify for sales → 1.4 Survey
│   ├── Webinar reg → 2.3 Webinar
│   └── Multi-day event → 2.4 Challenge
└── No (paid offer)
    ├── Under $97 → 4.2 Tripwire OR 4.3 Book funnel
    ├── $97-$2K → 4.1 Long-form sales page (direct-to-cart)
    ├── $2K-$5K
    │   ├── Cold traffic → 2.1 VSL page
    │   └── Warm traffic → 3.1 Application or 3.2 Call booker
    ├── $5K+
    │   ├── Cold traffic → 2.1 VSL → 3.1 Application
    │   ├── Referred / warm → 3.2 Direct call booker
    │   └── Enterprise / custom → 3.3 Interstitial / personalized
    └── Live event ticket → 5.1 Event reg
```

---

## Mixing archetypes (multi-step funnels)

The best operators chain these. Examples from the wild:

- **VSL → Application**: Voics/Apex puts the VSL up top, but the actual conversion is the embedded application iframe below.
- **Challenge → High-ticket**: Client Ascension uses the free challenge as the front door; the back-end ascension into $30K+ coaching happens during/after the challenge.
- **Tripwire → Upsell ladder**: Unorthodox Digital's $97 tripwire is positioned 3 times against their $5K+ tier — every buyer sees the next rung.
- **Quiz → Personalized result → Application**: route different quiz outcomes to different application pages with tailored offers.

When building a landing page, ask the user: **"Is this page the WHOLE funnel, or step 1 of a longer sequence?"** Build the page differently if there's a follow-up step (lighter persuasion, more focus on the single next action).
