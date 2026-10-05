---
name: brand-image
description: Use when the user wants to generate on-brand imagery — photos, illustrations, atmospheric backgrounds, scenes, characters, or product mockups. Reads the client's brand-style.md, picks the right provider (Gemini Nano Banana Pro / OpenAI gpt-image-1 / Imagen 4), constructs a brand-aligned prompt, generates 4 variations, supports iteration, and saves to the brand asset library. Used by webinar-deck, landing-page, sales-page, post-draft, ad-creative, and any other skill needing imagery.
---

# Brand Image Generator — [CLIENT NAME]

The central image generator for the [CLIENT NAME] AIOS. Every skill that needs imagery calls this one — never embeds image generation directly. That keeps brand consistency centralized and makes provider/model changes a single edit instead of a search-and-replace.

## What this skill owns

- Reading `brand-style.md` (the visual identity source of truth)
- Picking the right provider per use case (Gemini Nano Banana Pro / OpenAI gpt-image-1 / Imagen 4)
- Constructing prompts using deep prompt engineering (see `frameworks/prompt-engineering.md`)
- Generating 4 variations by default
- Supporting iteration (refinement, edit-style prompts, reference-image-driven changes)
- Saving to organized asset library with metadata sidecars

## Used by

| Caller skill | Typical image type | Aspect |
|--------------|--------------------|--------|
| `webinar-deck` | Slide backgrounds, scene photos, illustrations | 16:9 mostly, some 9:16 for split slides |
| `landing-page` / `sales-page` | Hero, section visuals, mockups | 16:9, 1:1, sometimes 4:5 |
| `post-draft` (IG/X/LinkedIn) | Social-native imagery | 1:1, 4:5, 9:16 |
| `email-broadcast` | Header images (sparingly — text emails convert better) | 16:9 or 3:1 banner |
| `ad-creative` | Paid social images | 1:1, 4:5, 9:16 |
| `thumbnail-concept` | NOT this skill — thumbnails have their own dedicated skill |

## Image categories

| Category | Primary use | Default provider | Aspect |
|----------|-------------|------------------|--------|
| **Background / atmospheric** | Behind text on slides, hero overlays | Gemini Nano Banana Pro | matches destination |
| **Scene / photograph** | Founders, environments, lifestyle, real moments | Gemini Nano Banana Pro | matches destination |
| **Illustration / character** | Mascots, brand characters, illustrated diagrams | OpenAI gpt-image-1 | matches destination |
| **Product / mockup** | Product shots, dashboard mockups, UI visuals | OpenAI gpt-image-1 | matches destination |
| **Texture / abstract** | Subtle patterns, grain, gradients with depth | Gemini Nano Banana Pro | matches destination |
| **Composite (reference-driven)** | Founder in a new scene, person + product combo | Gemini Nano Banana Pro | matches destination |

---

## The critical distinction: background vs. scene

**Background images** sit BEHIND text (slide overlay, hero section, sectional backdrop). They must be:
- Atmospheric, low information density
- Out-of-focus or textural
- Single dominant color tone (matching brand palette)
- No recognizable focal subject
- Negative space dominant

**Scene images** ARE the visual (no text overlay). They can be:
- Real subjects in focus
- Recognizable places / objects / people
- Rich visual detail
- Cinematic scenes

This distinction drives prompt construction. A "Boise cityscape at night" works as a scene but FAILS as a background because the recognizable city competes with overlay text. The same intent ("evoke 2019 Boise") rendered as a background would be: "warm orange streetlight glow filtered through window blinds, deep blacks, out-of-focus, atmospheric night interior, no recognizable scene."

See `frameworks/photo-style-guide.md` for the full breakdown of background-vs-scene prompts.

---

## Process

### Step 1: Understand the request

Get from the caller:
- **Intent** — what is this image for? (slide background / hero / testimonial avatar / product mockup / illustration)
- **Subject** — what's depicted?
- **Aspect ratio** — 16:9, 9:16, 1:1, 4:5, 3:4?
- **Destination context** — where will this image live? (determines background-vs-scene)

If the caller doesn't specify aspect ratio, derive from destination:
- Slide full bleed → 16:9
- Slide side-by-side (image-split, testimonial-screenshot) → 9:16 (portrait)
- Mosaic above text → 1:1
- Hero section → 16:9 or 4:3
- IG feed → 1:1
- IG story / Reels / TikTok → 9:16
- LinkedIn post → 1.91:1 or 1:1

### Step 2: Read brand-style.md

```
Read .claude/skills/brand-image/brand-style.md
```

Extract anchors:
- One-line aesthetic
- Color palette (primary, secondary, atmospheric)
- Photo style preferences (lighting, grading, composition)
- Illustration style preferences
- Forbidden elements
- Reference image paths from `assets/style-references/`

### Step 3: Pick the provider

Use `frameworks/provider-strengths.md` decision tree:

| Use case | Provider | Why |
|----------|----------|-----|
| Reference-image-driven (e.g., founder in new scene) | Gemini Nano Banana Pro | Best likeness preservation |
| Photorealistic background | Gemini Nano Banana Pro | Strong atmospheric output |
| Clean illustration | OpenAI gpt-image-1 | Better illustration aesthetics |
| Illustration with text | OpenAI gpt-image-1 | Best text rendering of any provider |
| Edit existing image | OpenAI gpt-image-1 | Native edit/inpainting |
| Maximum photorealism (no reference) | Imagen 4 OR Gemini | Both strong |
| Generic "I just need a thing" | Gemini Nano Banana Pro | Default workhorse |

### Step 4: Construct the prompt

Use the 8-element prompt structure from `frameworks/prompt-engineering.md`:

1. **Subject** — specific, vivid (not generic)
2. **Style** — photographic / illustration / character / etc.
3. **Composition** — framing, focal point, depth
4. **Lighting** — directional, mood-defining
5. **Color** — anchor to brand palette
6. **Camera/lens** — for photo (35mm wide, 85mm portrait, 50mm natural)
7. **Mood descriptors** — atmospheric vibe words
8. **Negative prompts** — always: "no text, no words, no letters, no numbers, no logos, no watermark"

Inject brand-style.md anchors automatically (palette HEX, mood keywords, photo style notes).

### Step 5: Generate 4 variations

```bash
python3 .claude/skills/brand-image/scripts/generate_image.py \
  --intent {background|scene|illustration|product|texture|composite} \
  --aspect 16:9 \
  --prompt "..." \
  --variations 4 \
  --provider gemini \
  --reference assets/style-references/founder-headshot.png \
  --output workspace/{project}/assets/{slug}/
```

The script:
- Reads brand-style.md and auto-injects anchors
- Calls the chosen provider 4 times in parallel
- Saves each variant + metadata sidecar (.json with prompt, provider, date, seed/parameters)
- Returns paths to all 4 variants

### Step 6: Present + iterate

Show the 4 variations. Three possible outcomes:

**A) Pick one and ship.** Save final to `assets/library/{category}/{slug}.png`.

**B) Refine a direction.** "I like #2 but more orange tone" or "less busy in the background." For refinement:
- Pass the chosen variant as a `--reference` image
- Add an edit instruction to the prompt
- Generate 2-4 refined variations
- Repeat until happy

**C) Start over.** The direction was wrong. Re-do step 4 with corrected understanding.

### Step 7: Save to brand library

When user picks a winner:
- `assets/library/{category}/{slug}.png` — final image
- `assets/library/{category}/{slug}.json` — metadata sidecar:
  ```json
  {
    "prompt": "the full prompt used",
    "provider": "gemini",
    "aspect": "16:9",
    "references_used": ["assets/style-references/founder.png"],
    "intent": "background",
    "date": "2026-05-14",
    "client_request": "slide 30 atmospheric backdrop for origin story"
  }
  ```

The metadata sidecar makes future similar requests faster — the agent can find past on-brand images for similar contexts and reuse or adapt.

---

## Hard rules

- **Read brand-style.md every time.** Don't generate from memory. Brand drift is the #1 way image generation breaks.
- **Background images must be atmospheric, never busy.** When the image will sit behind text, it MUST be low-information. No recognizable scenes, no focal subjects competing with the text.
- **Aspect ratio matches destination.** Don't generate a 16:9 image for a portrait slot. Match from generation, not via crop.
- **Always include "no text" in negative prompt.** Generated text is universally garbled across all providers. Overlay text via HTML/CSS in the destination.
- **Generate 4 variations on first pass.** Single-variation hides bad direction choices.
- **Save prompts as metadata.** Every kept image gets a `.json` sidecar with the prompt. Lets future similar requests pull from past wins.
- **Reference images > text description.** When generating in [CLIENT NAME]'s style, pass real on-brand images via `--reference` rather than describing the style in text. The visual reference is always stronger.

## Anti-patterns

- Generating from training memory instead of reading `brand-style.md`
- Using busy real-world photos as backgrounds for text overlays
- Generating landscape images for portrait slots (and vice versa)
- Defaulting to Gemini for everything when OpenAI is better for illustration / edits
- Including text inside generated images (always overlay via HTML/CSS at the destination)
- Skipping the 4-variant first pass and committing to one direction immediately
- Saving images without metadata sidecars (loses future re-use leverage)
- Ignoring forbidden-elements list from `brand-style.md`

## Customization checklist (Friday Labs onboarding)

- [ ] Fill `brand-style.md` with [CLIENT NAME]'s palette, mood, photo/illustration style
- [ ] Drop 5-10 reference images into `assets/style-references/` (real past on-brand images)
- [ ] Add `GEMINI_API_KEY` to `.env`
- [ ] Add `OPENAI_API_KEY` to `.env` (for illustration/edit workflows)
- [ ] Run a test generation in each category (background, scene, illustration) — confirm output matches `brand-style.md` aesthetic
- [ ] Update `frameworks/photo-style-guide.md` and `frameworks/illustration-style-guide.md` if [CLIENT NAME]'s style needs adjustments from defaults
- [ ] Verify `assets/library/` is empty and ready to be populated
