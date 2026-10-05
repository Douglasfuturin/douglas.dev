---
name: webinar-deck
description: Use when the user wants to create a webinar deck, sales webinar, VSL slides, or a long-form presentation that sells. Builds a long-form (120-220+ slide, sized to the topic) deck blending Russell Brunson's Perfect Webinar structure and Alex Hormozi's Grand Slam Offer mechanics, rendered as clean modern HTML with minimal text per slide and AI-generated imagery, then exportable to PowerPoint.
---

# Webinar Deck Generator, [CLIENT NAME]

Builds full webinar decks, 120-220+ slides sized to the topic, 60-110 minutes, that educate, build belief, and drive a conversion (a purchase, or an application for a call). Output is a self-contained HTML deck: clean, modern, minimal text per slide, 16:9, keyboard-navigable, and exportable to a `.pptx`.

The deck structure is a research-backed blend of two frameworks:
- **Russell Brunson's Perfect Webinar**, narrative spine (Hook, Story, 3 Secrets, Stack, Closes)
- **Alex Hormozi's Grand Slam Offer**, proof density, value equation, risk reversal

## What lives in this skill folder

```
.claude/skills/webinar-deck/
├── SKILL.md                       # this file
├── config-schema.md               # the config.json format reference
├── example-config.json            # a 14-slide test deck
├── frameworks/
│   ├── brunson-perfect-webinar.md       # the Brunson framework, deep
│   ├── hormozi-grand-slam.md            # the Hormozi framework, deep
│   ├── composite-150-slide.md           # the merged 150-slide arc, slide by slide
│   ├── webinar-conversion-research.md   # data-backed pacing + conversion research
│   ├── stack-slide-anatomy.md           # the stack sequence
│   ├── three-closes.md                  # Money / Risk / Time closes
│   └── value-equation.md                # Hormozi's value equation applied
├── assets/
│   ├── slide-patterns.md                # the 53-pattern visual catalog
│   ├── transition-phrases.md            # bridge language between sections
│   ├── objection-bank.md                # objections + where each is handled
│   ├── topic-research.md                # the subject matter, researched + verified
│   ├── audience-research.md             # the audience's real objections + language
│   └── examples/                        # client's past performing decks
├── templates/
│   └── deck-template.html               # the HTML/CSS render template (53 patterns)
└── scripts/
    ├── render_deck.py                   # config.json -> deck.html
    ├── reddit_research.py               # Reddit topic + audience research (ScrapeCreators)
    └── requirements.txt
```

## How a deck gets built

A deck is authored as a `config.json` (see `config-schema.md`), then rendered:

```
config.json  ──>  render_deck.py  ──>  deck.html  ──>  html_to_pptx.py  ──>  deck.pptx
                        │
                        ├─> brand-image/generate_image.py     (slide background images)
                        └─> product-mockup (offer spread)     (the offer-mockup price slide)
```

`render_deck.py` reads the config, generates images for any slide with a `visual` block (calling the `brand-image` skill's generator, Gemini Nano Banana Pro), renders all slide patterns to HTML, and injects them into `deck-template.html`.

The **offer's price-reveal slide** is built with the `offer-mockup` pattern: a product-spread image of the whole offer, generated separately with the `product-mockup` skill, with the price beneath it. Do this on almost every deck (see Step 3).

## Process

### Step 1: Understand the webinar's job

Get from the user:
- **Goal**, what the webinar drives (direct purchase / application for a call / booked demo)
- **Offer**, what's ultimately being sold + price
- **Audience**, who's watching
- **Big Domino**, the one belief that, once installed, makes the offer obvious (see `frameworks/brunson-perfect-webinar.md`)
- **Proof**, real case studies, numbers, screenshots available

### Step 2: Research, topic, audience, performance (MANDATORY, every run)

A webinar deck is never authored from memory. Three research passes feed the config, **all three happen before a single slide of `config.json` is written.**

**2a. Topic research, what the webinar teaches.** An educational-first webinar lives or dies on whether the teaching is accurate and current. Research the actual subject matter the webinar covers:
- `WebSearch` every core claim, framework names, statistics, dates, any "newest thing" claim
- `python3 scripts/reddit_research.py --comments --queries "<the subject matter>"`, what people actually say about the topic
- `WebFetch` primary sources to verify

Synthesize into `assets/topic-research.md`. **Every statistic or factual claim that lands on a slide must trace to this file.** If the webinar teaches something the research can't confirm, it doesn't go on a slide.

**2b. Audience research, who's watching.** Learn the audience's real objections and language:
```
python3 scripts/reddit_research.py --comments --queries "<audience objections, pains, language>"
```
Synthesize into `assets/audience-research.md`. The deck defuses the *real* objections found there; the FAQ slide pulls its questions from them.

**2c. Read the frameworks + research:**
```
Read frameworks/composite-150-slide.md         (the master arc)
Read frameworks/webinar-conversion-research.md  (data-backed pacing + conversion, non-negotiable)
Read frameworks/brunson-perfect-webinar.md
Read frameworks/hormozi-grand-slam.md
Read frameworks/stack-slide-anatomy.md
Read frameworks/three-closes.md
Read assets/slide-patterns.md                   (the 53 pattern types)
Read assets/objection-bank.md                   (objections + where each is handled)
Read assets/topic-research.md                   (the subject matter, verified)
Read assets/audience-research.md                (the audience's real objections + language)
```

If `assets/examples/` has past decks for [CLIENT NAME], read those too, they override framework defaults.

Only after all three passes are done is the config authored (Step 3).

### Step 3: Author the deck spec (config.json)

Walk the 12 sections of `composite-150-slide.md` in order:
1. Cold Open · 2. Who Am I · 3. Big Domino · 4. Origin Story
5. Secret 1 · 6. Secret 2 · 7. Secret 3
8. Transition · 9. Offer Reveal · 10. The Stack
11. The 3 Closes · 12. FAQ + CTA

For each slide: pick a pattern from the catalog, write the content, and add a `visual` block where an image earns its place.

**Slide count is variable, let the content set it.** 150 is a baseline, not a target. Real decks run 120-220+ slides depending on how much the topic needs taught (see `composite-150-slide.md` → "Slide count scales with content"). The 12 sections never change; the slides-per-section does, the 3 secrets absorb most of the variance. Never pad to hit a number; never compress real teaching to fit one.

**Slide rules:**
- 1-7 words per slide on most slides (the stack is the exception)
- No bullet points, if you have 3 bullets, you have 3 slides
- One idea per slide
- Never an image-only slide, every slide carries words
- Mark image slides deliberately, backgrounds are dark paper texture / graph-paper grid / darkened-illustrative (never light flares), side-by-side images must be portrait

**Generate the offer spread (do this on almost every deck).** The price-reveal slide should be visual, not a bare text price. Before rendering:
1. Generate a product-spread mockup of the whole offer with the `product-mockup` skill (`--type spread`), one object per real offer component:
   ```bash
   python3 ../product-mockup/scripts/generate_mockup.py --type spread --aspect 3:2 \
     --background white --output workspace/{deck}/assets/offer-spread.png --prompt "..."
   python3 ../product-mockup/scripts/remove_background.py \
     --input workspace/{deck}/assets/offer-spread.png
   ```
2. In the config, make the price-reveal slide an `offer-mockup` pattern: `src` points at the `-cutout.png`, `struck_price` is the anchor (the build-it-custom value), `price` is the real price.

A visual offer, with the value crossed out next to the price, converts harder than a text price. Skip it only when there is genuinely no offer to show.

### Step 4: Smoke test (Stage 1)

```bash
python3 scripts/render_deck.py --config {config}.json --skip-images
```

Confirms the config parses and every slide renders. $0, instant. Open the output, page through, fix any structural issues.

### Step 5: Full render (Stage 2)

```bash
python3 scripts/render_deck.py --config {config}.json
```

Generates all images via Gemini Nano Banana Pro, embeds them, writes the final `deck.html`. Images are cached, re-runs are free unless `--regenerate-images` is passed. A deck with ~25-40 image slides costs roughly $1.50-$3 and takes 10-20 minutes.

### Step 6: Review + iterate

Open `deck.html`, present it (press F for fullscreen). Iterate by editing the config and re-rendering, cached images mean only changed slides regenerate.

### Step 7: Export to PowerPoint (final step)

Once the deck is approved, convert it to a `.pptx` for delivery and offline presenting:

```bash
python3 scripts/html_to_pptx.py --deck workspace/{deck}/deck.html
```

Each slide is screenshotted at 1920×1080 via headless Chromium and placed full-bleed on a 16:9 PowerPoint slide. Pixel-perfect; opens in PowerPoint or Keynote; works for a deck of any slide count. Text is not editable in the `.pptx`, to change content, edit `config.json`, re-render, and re-export. Requires `playwright` (run `playwright install chromium` once) and `python-pptx`, both in `requirements.txt`.

## Hard rules

- **Educational-first.** The webinar must genuinely teach. Each secret is a real, usable lesson, valuable even to a viewer who never buys. Don't over-specify the offer early; the product gets named at the reveal (Section 9), not in the cold open. Teach hard, reveal late.
- **Research before authoring, every run.** Before writing `config.json`: research the topic (WebSearch + `reddit_research.py` → `topic-research.md`), research the audience (`reddit_research.py` → `audience-research.md`), and read `webinar-conversion-research.md`. The teaching must be accurate and current, the objections real, the pacing data-backed, never authored from memory. Every statistic on a slide traces to `topic-research.md`.
- **Read `composite-150-slide.md` before authoring.** Don't build the arc from memory, the slide-by-slide structure is the framework.
- **The Big Domino carries the deck.** Identify it before writing slide 1. If you can't state it in one sentence, the webinar has no spine.
- **Minimal text per slide.** The slide reinforces the spoken word, it isn't the script. 1-7 words on most slides.
- **Never use em dashes in slide copy.** Not anywhere in the deck. Use a period, a comma, a colon, or an ellipsis instead. (A lead-in line that continues onto the next slide ends with an ellipsis; a completed thought ends with a period.)
- **Never an image-only slide.** Every slide carries words. Use `photo-text-overlay`, `image-split`, or `image-hero`, never the bare `photo-full`.
- **Backgrounds are atmospheric, never busy.** Image slides behind text must be low-information (see `brand-image` skill).
- **Every bonus on the stack solves a specific objection** (see `stack-slide-anatomy.md` + `objection-bank.md`).
- **The price reveal is visual.** On almost every deck, the price-reveal slide uses the `offer-mockup` pattern: a product-spread image of the offer (generated with the `product-mockup` skill) plus the price, the anchor value struck through next to it. Don't reveal a price as bare text when there's an offer to show.
- **The webinar always carries a special promotional price.** A standard price (anchor) and a webinar-only price (real, time-bound), see `three-closes.md`.
- **Scarcity and urgency must be real.** Manufactured deadlines destroy trust and damage every future launch.
- **Smoke test before spending on images.** Always run `--skip-images` first.

## Anti-patterns

- Authoring the arc from memory instead of from `composite-150-slide.md`
- Paragraphs of text on a slide, it's a deck, not a document
- Busy photographic backgrounds behind overlay text
- Stack values that are obviously inflated
- Manufactured urgency
- Skipping the Stage 1 smoke test and generating images on a broken config

## Customization checklist (Friday Labs onboarding)

- [ ] Replace `[CLIENT NAME]` / `[VOICE OWNER]` placeholders
- [ ] Confirm `GEMINI_API_KEY` is in `.env` (image generation)
- [ ] Confirm the `brand-image` skill is present (this skill calls its generator)
- [ ] Fill `brand-image/brand-style.md` so generated imagery is on-brand
- [ ] Drop any past-performing decks into `assets/examples/`
- [ ] Run the example config end-to-end to verify the pipeline
