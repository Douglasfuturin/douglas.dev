# Composite 150-Slide Framework

> A long-form webinar deck blending Brunson's narrative spine, Hormozi's proof density, and modern minimalist visual language. Built for [VOICE OWNER] / [CLIENT NAME]. **150 slides is a baseline, not a target**, real decks run 120 to 220+ depending on how much the topic needs taught (see "Slide count scales with content" below). Pacing averages ~30 seconds per slide, slower on dense teaching, faster on punctuation/hero slides.

## At a glance

| Section | Slides | Time | Purpose | Source framework |
|---------|--------|------|---------|-----------------|
| 1. Cold Open | 1-8 | 3 min | Hook + commitment ritual | Brunson Hook |
| 2. Who Am I | 9-20 | 5 min | Earn permission with proof | Hormozi proof density |
| 3. Big Domino | 21-30 | 4 min | Name the load-bearing belief | Brunson Big Domino |
| 4. Origin Story | 31-50 | 8 min | Bond via Epiphany Bridge | Brunson Epiphany Bridge |
| 5. Secret 1, Vehicle | 51-75 | 12 min | External: "this method works" | Brunson Secret 1 + Hormozi proof |
| 6. Secret 2, Internal | 76-95 | 10 min | Internal: "I can do this" | Brunson Secret 2 |
| 7. Secret 3, External | 96-110 | 8 min | External: "circumstances won't stop me" | Brunson Secret 3 |
| 8. Transition | 111-115 | 2 min | Permission to sell | Brunson Permission |
| 9. Offer Reveal | 116-125 | 5 min | What it is + naming | Hormozi MAGIC |
| 10. The Stack | 126-140 | 8 min | Value buildup | Brunson Stack |
| 11. The 3 Closes | 141-148 | 6 min | Money + Risk + Time | Brunson 3 Closes + Hormozi guarantee |
| 12. FAQ + CTA | 149-150 | 2 min | Last objections + button | Both |

**Baseline total:** ~150 slides, ~75 min (sections breathe live), this scales, see below.

---

## Slide count scales with content

**150 is a baseline, not a rule.** It was a round estimate. A real deck is as long as the topic genuinely needs, typically **120 to 220+ slides**:

- **Lighter topic / colder audience** → ~100-130 slides (~50-65 min)
- **Standard** → ~140-170 slides (~70-85 min)
- **Information-dense topic** (lots to teach, multiple frameworks, deep proof) → **180-220+ slides** (~90-110 min)

What scales is the **slide count per section**, never the arc. The 12 sections and their order are fixed. How many slides each section gets is not:

- The **3 secrets** (Sections 5-7) absorb most of the variance. A topic with three meaty lessons and deep proof might run those sections 40-60 slides each, well past the baseline.
- The **origin story** stretches when the narrative is rich (e.g. a multi-era evolution to walk through).
- The **cold open, transition, and FAQ** stay roughly fixed, a bigger topic doesn't need a longer cold open.

**Let the content set the count.** One idea per slide, minimal text per slide. If a teaching section needs 50 slides to land honestly, it gets 50. If the FAQ needs 4, it gets 4. Never pad to hit a number; never compress real teaching to fit one.

Every slide number used below (slide 22, slide 134, etc.) describes the **150-baseline reference deck**. On a 200-slide deck the Big Domino still lands ~15% of the way in, read each slide number as **proportional, not absolute**. The render pipeline doesn't care: `config.json` simply has however many slides it has.

---

## Educational-first, the core philosophy

The best webinars don't feel like webinars. They feel like the most useful free training the viewer has watched all year. The offer is real, but it is *earned*. By the time it's revealed, the audience is leaning in and asking for it.

This changes how every section is built:

**Teach genuinely.** Every secret contains a real, usable lesson. If the viewer took notes, closed the tab, and never bought, they should still have gotten something genuinely valuable. That generosity is what makes the offer land, you've proven you know the space and you give without holding back.

**Don't over-specify the offer early.** The cold open, the who-am-I, the big domino, none of these name the product or its mechanics. Don't name your specific deliverables (component counts, build timelines, feature lists) in the first 30 slides. Naming the solution early turns education into a pitch and the audience feels the switch. Build curiosity instead. The mechanics get *taught* in the secrets; the product gets *named* at the reveal (Section 9).

**Teach the category's evolution.** One of the most powerful educational moves: walk the audience through how the space got to where it is, the past approaches, why each fell short, and what the current frontier is. This genuinely educates, positions the presenter as someone who sees the whole landscape, and naturally sets up the solution as "the current frontier" without pitching anything. Place this beat in Section 3 (Big Domino) and let it carry into Section 4. Shape: "Approach A solved X but broke at Y → Approach B fixed Y but couldn't do Z → the current frontier finally does Z, and here's what that unlocks."

**The 3 secrets teach the WHY behind the offer.** Each secret is a genuine lesson, and the lesson naturally implies why a solution would have to be built a certain way. By the time the viewer reaches the reveal, they already understand why the offer is architected the way it is. You never argued them into it; you taught them, and the offer became the obvious conclusion.

**Reveal the offer at the end, as the natural next step.** After three real lessons, the viewer is asking "okay, how do I actually get this done?" The offer answers a question they're now asking, not one you forced on them.

**The webinar always carries special promotional pricing.** The offer has a standard price and a webinar-only price. The promo is genuine and time-bound, it creates legitimate urgency because it really does expire. See `three-closes.md` for how to structure it.

**Vary the treatment, don't ship a template.** The 12-section arc is fixed; the *execution* is not. The exact wording, the transitional beats, the pattern choices, the recurring phrasings, the one-word pattern break, the commitment-ritual line, the "grab a pen" instruction, are examples, not mandatory boilerplate. A viewer who has seen one of these webinars should never feel they are watching the same deck with the words swapped. The arc carries; the surface is fresh every time.

Educational-first is not "soft." It out-converts hard-pitch webinars because trust is the actual bottleneck. Teach hard, reveal late, price with a real deadline.

---

## Section 1, Cold Open (slides 1-8)

The first 90 seconds determine the next 90 minutes. The audience is deciding "is this another generic webinar or is this guy different?" Win by being specific and direct.

| # | Slide content | Pattern | Why |
|---|---------------|---------|-----|
| 1 | **The title slide IS the promise**, the descriptive headline ("How to X without Y") set big, with credits (training name · presenter) small underneath. No separate short brand title. | `title` | The opening hook and the title are the same thing. A short brand name ("The AI OS") teaches the viewer nothing, the descriptive promise does. |
| 2 | A pattern-break / re-hook beat, vary it every webinar | `mono-word` / `mono-line` | Creates a pause after the title; never the identical word twice across decks |
| 3 | Lead-in to the agenda, "By the end of today, you'll know..." | `mono-line` | Sets up the three-line agenda that follows |
| 4 | The agenda, three short lines | `three-lines` | Anchors the value, sets expectation |
| 5 | **Payoff promise for staying**, "stay to the very end and you'll get [X], only available tonight" | `permission` | NOT a commitment ask. Promise a real, time-bound reward for staying to the end; never reveal what it is (curiosity). A payoff promise out-holds "will you commit?" by a wide margin. |
| 6 | A behavioral-activation beat, e.g. "Grab a pen", vary it | `instruction` | They invest a small action, they stay |
| 7 | One specific result, "$2.4M generated by people who learned this" | `proof-number` | Hormozi specificity, preview of credibility |
| 8 | "Quick intro then we dive in." | `bridge` | Bridge to next section |

**Slide rules for this section:**
- No bullet points
- One idea per slide
- The title slide's headline must be a SPECIFIC outcome, not "transform your life"
- Do NOT name the product or its mechanics here. The promise is an outcome, not a feature list. The product gets named at Section 9.
- Slide 5 is a *payoff promise*, not a "will you stay?" question, promise something the viewer only gets by staying to the end tonight.

---

## Section 2, Who Am I (slides 9-20)

The audience needs to know why to listen to you for the next hour. This is permission-by-proof, not permission-by-credentials. Specific numbers + photos > job titles + adjectives.

| # | Slide content | Pattern |
|---|---------------|---------|
| 9 | "I'm [Name]." | `mono-name` |
| 10 | Photo, real, full-bleed, no logo overlay | `photo-full` |
| 11 | One-line credibility number ("$12.4M in client revenue, 2024") | `proof-number` |
| 12 | Logo wall, 6-12 client logos or press logos | `logo-wall` |
| 13 | One specific case study, one slide ("Lauren, $0 → $50k MRR in 6 months") | `case-study-headline` |
| 14 | Second photo, real life context (with family / on stage / at work) | `photo-full` |
| 15 | Another specific number ("237 students, 89% completion") | `proof-number` |
| 16 | Why I'm sharing this, REAL reason | `why-share` |
| 17 | Who this is for, specific avatar | `avatar` |
| 18 | Who this is NOT for | `not-for` |
| 19 | What we'll cover, three secrets, named | `agenda` |
| 20 | "But first..." | `bridge` |

**Slide 16 critical move:** "Why I'm sharing this" can't be "because I want to help people." It must be a REAL reason, "because most of what's taught about X is wrong and it costs my industry millions," or "because I made every mistake possible and I'm sick of seeing others repeat them." Specific and slightly contrarian.

**Slide 18 critical move:** "Not for" is a Hormozi trust signal. By disqualifying the wrong audience you increase the right audience's belief that you understand them.

---

## Section 3, The Big Domino (slides 21-30)

You name the one belief everything hinges on. The next 60 minutes are dedicated to knocking it over.

| # | Slide content | Pattern |
|---|---------------|---------|
| 21 | "Here's the thing." | `mono-line` |
| 22 | The Big Domino, stated as a claim, no qualifier | `big-claim` |
| 23 | Visual metaphor for the domino (image or graphic) | `metaphor` |
| 24 | What happens IF this belief is true (downstream effect) | `if-true` |
| 25 | The common belief that contradicts it | `vs-belief` |
| 26 | What people who believe the alternative do | `alt-behavior` |
| 27 | What it costs them (specific number or outcome) | `cost-of-alt` |
| 28 | "If I could show you this is true, would you {act}?" | `reframe-permission` |
| 29 | "Let me show you how I figured this out." | `bridge-to-story` |
| 30 | Date + location ("2019. Boise.") on black | `scene-setter` |

**The Big Domino slide (22) carries the entire webinar.** Spend extra time on this one. Test it before you build the deck. Read it aloud, does it land?

---

## Section 4, Origin Story (slides 31-50)

The Epiphany Bridge. 20 slides over 8 minutes, the longest narrative stretch in the deck.

### Backstory (31-33)
- 31: Who I was, one line ("I was a broke 24-year-old with $48k in credit card debt")
- 32: Photo, real, awkward, not staged
- 33: What I thought I knew, the false belief I held

### The Wall (34-37)
- 34: What I tried first
- 35: What happened (specific failure)
- 36: Try again, different angle
- 37: Worst moment, specific scene, low point

### The Epiphany (38-40)
- 38: "Then one day...", set the scene
- 39: What I noticed (the specific observation)
- 40: The realization, full screen, big text

### The Plan (41-44)
- 41: I started doing X
- 42: Then Y
- 43: Then Z
- 44: First result, specific number with date

### The Conflict (45-47)
- 45: What almost stopped me, specific moment
- 46: What I had to give up / change
- 47: The decision I made

### The Achievement (48-50)
- 48: The result, specific number, real screenshot if possible
- 49: The transformation, life now vs. life before
- 50: "And it all started with that one realization." Callback to slide 40.

**Pacing note:** the epiphany slide (40) is the emotional peak of the entire first half. Land it. Hold it. Don't rush.

---

## The 3 secrets, genuine lessons, not pitches

Sections 5-7 are the heart of the webinar. Brunson's model frames them as belief-breaking (Vehicle / Internal / External). That lens still works, but in an educational-first webinar, lead with the *teaching*, not the belief-break.

Each secret should be a real lesson the viewer can act on. The strongest secrets share a shape:

1. **It teaches something true and useful**, the viewer learns a genuine principle about the space.
2. **It implies why the solution must be built a certain way**, the lesson naturally reveals an architectural requirement, so when the offer is revealed it matches what the viewer now believes is necessary.
3. **It builds on the one before it**, secret 2 only matters once secret 1 has landed; secret 3 completes the picture.

Map the three secrets so that, taken together, they fully explain why the offer is the way it is. The viewer should reach Section 8 thinking "if I were going to do this properly, it would have to work exactly like what they've described", before the offer is even named.

Keep the Brunson section scaffolding below (reveal → mini-story → teaching → proof → transition). Just remember: the goal of each secret is that the viewer *learns*, not that they're *handled*.

---

## Section 5, Secret 1: The Vehicle (slides 51-75)

External belief: "this method/vehicle doesn't work" OR "the right method for me is something else."

### Reveal (51-52)
- 51: "Secret #1" | The named secret
- 52: One-line statement of the secret

### Mini-story (53-56)
- 53: Meet [Person], specific name
- 54: Where they were before
- 55: What they tried (proof of the wrong path)
- 56: What changed when they applied Secret 1

### Teaching (57-62)
- 57: The mechanism, named framework or model
- 58: Step 1 of the framework
- 59: Step 2
- 60: Step 3
- 61: How it actually works (one-paragraph visual)
- 62: Common misconception, "Most people think... but actually..."

### Proof (63-67)
- 63: Case study #1, name, number, date
- 64: Screenshot or chart
- 65: Case study #2
- 66: Screenshot or chart
- 67: Aggregate result ("Across 47 students who applied this, average X = Y")

### Why this is different (68-72)
- 68: vs. the conventional advice
- 69: Why the conventional advice fails (specific failure mode)
- 70: Why this works where that doesn't
- 71: What you'd have to give up to apply this
- 72: What you'd gain

### Transition (73-75)
- 73: "Okay so Secret #1, [restate]"
- 74: "But here's what I see all the time..."
- 75: Setup for Secret 2, name the internal objection

**Slide 67 critical move:** aggregate results across multiple students = Hormozi-style undeniable proof. If you have it, use it. If you don't, this slide becomes a third individual case study instead.

---

## Section 6, Secret 2: Internal Beliefs (slides 76-95)

Internal: "Even if your method works, I can't do it because I'm not [smart/funded/young/connected/disciplined/etc] enough."

### Reveal (76-77)
- 76: "Secret #2"
- 77: One-line statement

### Mini-story (78-82)
- 78: Meet [Person], chosen specifically to mirror the internal objection
- 79: Why they thought they couldn't
- 80: What happened when they did anyway
- 81: Screenshot / proof
- 82: Their result + quote

### Teaching (83-87)
- 83: The internal block (named)
- 84: Why the block is real
- 85: Why it doesn't matter (the reframe)
- 86: The shift in identity required
- 87: How to make the shift in practice

### Proof (88-92)
- 88: Case study (different demographic from Secret 1)
- 89: Screenshot
- 90: Another case (different age / industry / background)
- 91: Screenshot
- 92: Aggregate proof if available

### Transition (93-95)
- 93: "So Secret #2, [restate]"
- 94: "But there's one more thing in the way..."
- 95: Setup for Secret 3

---

## Section 7, Secret 3: External Beliefs (slides 96-110)

External world: "The market is saturated / algorithm is broken / I don't have time / economy / etc."

### Reveal (96-97)
- 96: "Secret #3"
- 97: One-line statement

### Mini-story (98-101)
- 98: Meet [Person]
- 99: The external thing they thought was stopping them
- 100: What was actually happening
- 101: Their result after applying Secret 3

### Teaching (102-105)
- 102: The external excuse (named)
- 103: Why most people stop at this excuse
- 104: The reframe
- 105: How to use the "obstacle" as an advantage

### Proof (106-108)
- 106: Case study
- 107: Screenshot
- 108: Aggregate result

### Transition (109-110)
- 109: "So now you know all 3 secrets..."
- 110: Bridge to the offer

---

## Section 8, Transition / Permission (slides 111-115)

The most dangerous moment in the deck. Mishandled = audience feels betrayed. Handled well = audience requests the pitch.

| # | Content | Notes |
|---|---------|-------|
| 111 | "What we just covered is the WHAT." | Frame the shift |
| 112 | "You're probably wondering about the HOW." | Address the felt need |
| 113 | "Would it be okay if I showed you the exact system I built?" | Explicit permission ask |
| 114 | Black slide, hold | Pause for permission signals (chat, polls) |
| 115 | "Okay, let me introduce you to..." | Bridge |

**Critical:** Slide 114 isn't decorative. Use it. Pause the deck and wait for chat replies or poll responses before advancing.

---

## Section 9, Offer Reveal (slides 116-125)

The offer enters. Named, framed, and positioned before any price is mentioned.

| # | Slide |
|---|-------|
| 116 | Offer name, full screen, no logo |
| 117 | Avatar + outcome + interval ("For [avatar] who want [outcome] in [interval]") |
| 118 | One-line description |
| 119 | "Here's what's inside..." |
| 120 | Component 1 (named, visual) |
| 121 | Component 2 |
| 122 | Component 3 |
| 123 | Component 4 (if applicable) |
| 124 | What you'll have at the end |
| 125 | "Now let me show you everything you get..." (bridge to stack) |

**Naming check:** the offer name should pass MAGIC, Magic outcome, Avatar, Goal, Interval, Container. If the name applies to 100 niches it's too generic.

---

## Section 10, The Stack (slides 126-140)

The visual climax. Each line is built up LIVE, the audience watches the value pile up.

| # | Slide |
|---|-------|
| 126 | "Let me show you what's included..." |
| 127 | Core thing, name + $X,XXX value |
| 128 | Add bonus 1 (now showing 2 lines) |
| 129 | Add bonus 2 (3 lines) |
| 130 | Add bonus 3 (4 lines) |
| 131 | Add bonus 4 (5 lines) |
| 132 | Add bonus 5 (6 lines) |
| 133 | Add bonus 6 (7 lines, if applicable) |
| 134 | Total value: $XX,XXX (the BIG number) |
| 135 | "But you won't pay anywhere close to that..." |
| 136 | "You won't even pay half of that..." |
| 137 | **The price reveal, as an `offer-mockup` slide:** a product-spread image of the whole offer (generated with the `product-mockup` skill), with the price beneath it, the anchor value struck through next to the real price. This is the standard way to reveal the price, do it on almost every deck. |
| 138 | Payment plan option (if any) |
| 139 | Comparison anchor, "vs. an agency at $5k/mo, vs. doing it yourself for 18 months" |
| 140 | "Worth it? Let me show you why..." (bridge to closes) |

**Stack slide rules:**
- Each bonus must solve a specific objection (see `assets/objection-bank.md`)
- Values must be defensible, no inflated $50,000 line items
- Build up live, never reveal all lines at once
- The total reveal (134) is the visual peak, biggest typography, longest hold
- The price revealed is the **webinar-only promotional price**, always anchor the standard price first, then reveal the webinar price below it. See `three-closes.md`.
- **Make the price reveal visual.** Use the `offer-mockup` pattern: a product-spread image of the whole offer (generated by the `product-mockup` skill, `--type spread`) with the price beneath it, the anchor price struck through next to the real price. Seeing the stack as physical/digital products makes the value land harder than a list of line items.

See `stack-slide-anatomy.md` for the full anatomy of this section.

---

## Section 11, The 3 Closes (slides 141-148)

### Close 1: Money (141-142)
- 141: ROI math, specific calculation
- 142: Cost of NOT solving, annualized pain

### Close 2: Risk (143-144)
- 143: The guarantee, headline
- 144: Guarantee details, conditional, specific

### Close 3: Time (145-146)
- 145: Urgency reason, the webinar-only promotional price is the primary, always-present source. Cohort capacity / bonus expiry stack on top if genuinely real.
- 146: Specific deadline for the promo ("This price holds until [deadline]"), real and enforced

### Action (147-148)
- 147: "Here's what to do right now", 3-step action plan
- 148: BUTTON SLIDE, URL, big, hold

See `three-closes.md` for full anatomy.

---

## Section 12, FAQ + Final CTA (slides 149-150)

| # | Slide |
|---|-------|
| 149 | Top 5 FAQ on one slide, quick answers |
| 150 | Final CTA, URL big, "See you on the other side." |

The FAQ slide catches stragglers. Pull from `assets/objection-bank.md` for the top 5, they should be REAL objections from prior runs or sales-call recordings, not invented ones.

---

## Slide design principles (applies to all 150)

- **1-7 words per slide** on most slides
- **Stack slide is the exception**, it has line items
- **Black background** by default; white text; ONE accent color (default `#FF5C28`)
- **Helvetica Now / Inter / SF Pro**, clean modern sans-serif
- **96-180pt** for hero text; 40-60pt for body; 24-32pt for fine print
- **Never an image-only slide.** Every slide carries words. A bare photo with no text is a dead beat, the viewer can't tell what they're looking at or why. Use `photo-text-overlay` (image + headline), `image-split` (image + text panel), or `image-hero` (image + caption). The bare `photo-full` pattern is deprecated for this reason.
- **No bullet points anywhere.** If you have 3 bullets, you have 3 slides.
- **Transitions:** instant cut or fade only. No slide-in, no spin, no animation.
- **Aspect ratio:** 16:9, 1920×1080 minimum

See `assets/slide-patterns.md` for the full catalog of slide pattern types and how to render each one.

---

## Pacing rules

- Hero slides (slide 2 promise, slide 22 Big Domino, slide 40 epiphany, slide 134 total, slide 137 price): hold 5-10 seconds before advancing
- Mono-word slides ("Today." "Listen.") hold 2-3 seconds for pattern break
- Stack build-up slides (127-134): hold 8-12 seconds each, give the value math time to land
- Teaching slides (framework / mechanism): hold 30-60 seconds, this is where the presenter actually talks
- Transition slides ("Now what we covered..."): advance briskly, 5-10 seconds

Total runtime budget: 75-90 minutes. If pacing drifts long, the closer sections suffer (this is where revenue happens), protect the back half.

---

## How the skill uses this file

The `webinar-deck` skill reads this file as the master arc. It uses the slide-by-slide breakdown to generate:
1. A deck spec markdown (one slide per block)
2. An HTML render of the deck using `templates/deck-template.html`
3. A pre-render checklist that flags missing elements (no Big Domino, no Stack bonuses tied to objections, etc.)

Customization happens at the inputs level, topic, offer, avatar, niche, voice, not by editing this file. This file is the framework. The inputs are the variables.
