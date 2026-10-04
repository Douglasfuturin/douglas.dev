---
name: landing-page
description: Build conversion-optimized landing pages (VSL, application, challenge, webinar, opt-in, application funnel) for agency/coach/info-product clients. Pulls from a brand guide when one exists, otherwise infers a brand from context or invents a fitting one. Always generates images — real where possible, clearly-fake placeholders (testimonial avatars, results screenshots, charts, logo walls, trust badges) when not. Use when the user says: build a landing page, VSL page, opt-in, lead magnet page, application funnel, challenge page, webinar registration, or asks to clone/recreate a competitor page.
---

# Landing Page Skill

Build a single high-converting landing page end-to-end. Output is a self-contained directory with a Next.js page (or static HTML if requested), every image rendered, every section copy written.

This skill is opinionated. It is not a generic web-design skill — it is a **direct-response conversion** skill. Every choice serves the CTA.

## Non-negotiables

1. **Always generate every image.** Never leave an `<img src="placeholder.jpg">`. If you don't have a real photo, render a clearly-marked fake (testimonial avatar with "DEMO" overlay, chart with "EXAMPLE DATA" watermark, results screenshot with fake-but-plausible numbers). The page must look populated when it loads. See [references/images.md](references/images.md).
2. **Brand guide first.** Before writing any copy or picking any colors, check for a brand guide. If one exists, use it strictly. If not, infer from context. See [references/brand-guide.md](references/brand-guide.md).
3. **Conversion before aesthetics.** Pretty is a bonus. The page must move the visitor toward ONE action. One primary CTA goal per page. Every section earns its place by contributing to that conversion.
4. **Copy is the product.** The headline matters more than the hero image. Write the copy first, design around it.
5. **No placeholder text.** Lorem ipsum, "your headline here", "Feature one" are banned. Write the real copy.

## When to invoke

User says: "build a landing page", "VSL page", "opt-in page", "application funnel", "challenge page", "webinar registration", "lead magnet page", "clone this landing page", "recreate {competitor} for {my client}".

Also infer the skill is needed when: the user has a brand guide + an offer + wants a page to drive paid traffic to.

## Workflow

### Step 1 — Intake (60 seconds)

Establish these five things before writing anything. Ask the user only what you can't infer:

1. **Page type** — VSL / application / challenge / webinar reg / opt-in / sales page / interstitial
2. **Offer** — what's being sold, price (if disclosed), audience
3. **CTA goal** — book a call / apply / opt-in for free thing / register / buy
4. **Traffic source** — cold ads / warm email / organic / podcast → affects copy temperature
5. **Brand guide** — where does it live? If none, ask: "Use {client name}'s existing aesthetic, invent one, or copy {reference brand}?"

### Step 2 — Page Type → Section Skeleton

Pick the archetype based on traffic temperature, offer price, and CTA goal. See [references/funnel-types.md](references/funnel-types.md) for the full taxonomy (12+ archetypes grouped into 5 tiers: lead capture, long-form education, high-ticket qualified, direct purchase, live event) with a decision tree at the bottom.

Then assemble blocks from [references/building-blocks.md](references/building-blocks.md). The funnel-types doc tells you the skeleton; the building-blocks doc gives you the modular pieces.

Quick reference — most common archetypes:
- **Squeeze** (single-screen opt-in) → Tier 1.1
- **VSL page** (cold-traffic education + call book) → Tier 2.1
- **Webinar registration** → Tier 2.3
- **Challenge funnel** → Tier 2.4
- **Application page** (high-ticket gate) → Tier 3.1
- **Direct call booker** (warm traffic, calendar inline) → Tier 3.2
- **Long-form sales page** (direct-to-cart) → Tier 4.1
- **Tripwire** ($7-$97 entry) → Tier 4.2

### Step 3 — Brand Guide → Design System

Load the brand guide if it exists. Otherwise see [references/brand-guide.md](references/brand-guide.md) for the fallback protocol: infer from existing client site / social presence / niche conventions, or generate a quick guide.

Lock in before writing code:
- Brand color (CTA color, usually 1 saturated brand color + neutrals)
- Headline font + body font
- Container max-width and base spacing rhythm
- Light theme or dark theme
- Photography style (real portraits / 3D renders / illustrations / screenshots only)

See [references/design-system.md](references/design-system.md) for the defaults to fall back on.

### Step 4 — Copy (do this before code)

Write every line of copy as markdown FIRST. No design, no code. Just copy.

For each section, write:
- Section name
- Eyebrow (if any)
- Headline
- Subheadline
- Body / bullets
- CTA button text
- Caption / fine print

See [references/copy-patterns.md](references/copy-patterns.md) for proven formulas (headline templates, CTA verb stack, objection-handling phrases, urgency lines).

The headline alone should be tested against 3-5 alternatives. Generate options, then pick.

### Step 5 — Marketing Psychology Pass

Before locking copy, run it through the persuasion-principle checklist. See [references/psychology.md](references/psychology.md). At minimum the page should explicitly activate:

- **Social proof** (testimonials with names + photos + specifics)
- **Authority** (named credentials, results, who-they've-worked-with)
- **Scarcity** (cohort limit, seat limit, deadline)
- **Specificity** (real numbers, never round, never vague)
- **Risk reversal** (guarantee, "what if it doesn't work")

If a section doesn't activate at least one principle, ask why it's on the page.

### Step 6 — Images (always real OR clearly-fake-but-believable)

Plan every image before building. List them with their purpose and source strategy. See [references/images.md](references/images.md).

Categories:
- Hero asset (VSL poster / product mockup / portrait)
- Testimonial avatars (real if client supplies, else AI-generated with clear "Demo" badge)
- Logo wall (real logos if available; if generating fake ones, label "Demo brands")
- Results screenshots (charts, dashboards, payment notifications — generate with realistic-looking fake data + a small "Example" mark)
- Trust badges (Trustpilot/G2/etc. — only show real ones the client actually has)
- Author/founder portrait (real photo, no exceptions for "the face" of the page)

### Step 7 — Build

Default output: Next.js page at `workspace/{project-slug}/` if the user is building a project, or static HTML at `workspace/{project-slug}/index.html` for one-off landing pages. Ask if not specified.

Build rules:
- One file per section component (HeroVSL.tsx, ProblemStack.tsx, etc.) so the user can rearrange
- Real copy, real images — no placeholders escape to the user
- Mobile-first responsive (every section must work at 375px)
- The primary CTA must appear at minimum 3 times on the page (above fold, mid-page after social proof, at the bottom)
- Form submission stub: log to console + show success state — wire to real backend only if user provides one
- Track event hooks (`onCTAClick`, `onFormSubmit`) so analytics can be wired later, but DON'T import any analytics SDK

### Step 8 — QA Pass (before declaring done)

Before saying "done", walk the page yourself:
- Open the rendered page (or describe each section if you can't run a browser)
- Every image loaded? No broken `src`?
- Headline punches you in the face within 2 seconds?
- CTA visible above the fold?
- All testimonials have a name + photo + result + specificity?
- Mobile width (375px) doesn't break any layout?
- Every link goes somewhere (CTA → form / form action → success state)?

If anything fails, fix it before reporting completion.

## Output Format

When you finish, report:
1. Path to the built page
2. Page type chosen and why
3. Brand color + fonts used
4. Image manifest (what was real, what was AI/fake-generated, what came from stock)
5. The headline you landed on + 2 alternatives you considered
6. What conversion features are wired (form, CTA tracking hooks, etc.)
7. What's NOT wired yet (real form backend, real analytics, real domain)

## Anti-patterns

These kill conversion. Never ship them:

- Multiple competing CTAs above the fold (one CTA, repeated, wins)
- Generic stock photos of "diverse business people pointing at laptop"
- Testimonials with no name, no photo, or no specific result
- Round-number results ("Made $100k") — use "$104,287" instead
- Hero headline that describes the product instead of the outcome ("AI-powered platform" vs "Book 12 sales calls in 30 days, guaranteed")
- "Click here" or "Submit" as CTA text
- An FAQ that asks the user's questions instead of handling the objection ("Is this for me?")
- A "features" section on a direct-response page (sell the outcome, not the feature)
- Body copy in italic for emphasis (use bold; italic kills readability)
- Walls of text without a single image or break for >300 words
