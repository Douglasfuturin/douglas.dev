# Brand Visual Identity — [CLIENT NAME]

The source of truth for [CLIENT NAME]'s visual aesthetic. Every image generated through `brand-image` reads this file and injects these anchors into the prompt.

Fill in every `[BRACKETED]` value during onboarding.

---

## Brand essence

- **One-line aesthetic:** [e.g., "dark, cinematic, premium with restrained orange accents"]
- **Audience-facing personality:** [expert / friend / challenger / authority / innovator]
- **Brand archetype:** [The Sage / The Hero / The Outlaw / The Magician / The Everyman / The Creator]

---

## Color palette

### Primary (logo + key accents)
- **Primary:** `[HEX]` — [usage notes — e.g., "logo, key emphasis, single accent in compositions"]
- **Secondary:** `[HEX]` — [usage notes — e.g., "supporting accents, hover states"]

### Atmospheric (background tones)
- **Dominant background:** `[HEX]` — typically `#0A0B12` for dark brands, `#FAFAFA` for light
- **Mid-tone backdrop:** `[HEX]` — secondary backdrop, slightly raised
- **Atmospheric accent:** `[HEX]` — subtle glow/wash color used in atmospheric backgrounds

### Forbidden colors
Colors that NEVER appear in [CLIENT NAME] imagery:
- `[HEX or descriptive]` — [reason — e.g., "competitor-associated"]

---

## Photo style

### Lighting
- **Default lighting:** [e.g., "dramatic side-lit, single warm key light, deep shadows for contrast"]
- **Acceptable variants:** [e.g., "golden hour outdoor, soft window light for interviews, blue-hour cinematic"]
- **Forbidden lighting:** [e.g., "studio overhead even lighting — too commercial / stock-photo"]

### Color grading
- **Tone:** [e.g., "warm cinematic, slight orange-teal contrast, deep blacks"]
- **Saturation:** [low / medium / high]
- **Contrast:** [low / medium / high]
- **Black point:** [crushed / natural / lifted]

### Composition
- **Framing:** [e.g., "tight close-ups for faces, mid-shots for environments, wide for context"]
- **Negative space:** [e.g., "comfortable around subjects, never tight to edges"]
- **Rule preferences:** [rule of thirds / symmetry / centered / leading lines]

### Subject style
- **People:** [e.g., "natural, candid, real — never posed-stock / smiling-at-camera"]
- **Environments:** [e.g., "real workspaces, lived-in, signs of actual use — not staged"]
- **Objects:** [e.g., "products in real context, never floating on white"]
- **Hands / gesture:** [e.g., "natural mid-action, holding things, never empty pointing"]

### Photo references
List 3-5 photographers or aesthetic anchors whose work matches [CLIENT NAME]:
- [Reference 1] — [why]
- [Reference 2] — [why]
- [Reference 3] — [why]

---

## Illustration style

### Default illustration type
- [flat / line art / hand-drawn / isometric / character / editorial / collage]

### Line / stroke
- **Weight:** [thick consistent / variable / sketchy / no outline]
- **Style:** [geometric / organic / sketchy / clean]

### Color application
- **Fills:** [solid / gradient / hatched / none]
- **Palette in illustrations:** [refer to brand palette / limited to 2-3 colors / monochromatic + 1 accent]

### Character style (if any)
- [e.g., "simple geometric faces, no detailed features, single accent color, expressive postures"]

### Illustration references
- [Illustrator 1 / aesthetic 1] — [why]
- [Illustrator 2 / aesthetic 2] — [why]

---

## Background / atmospheric imagery rules

When generating an image used BEHIND TEXT (slide overlay, hero section, sectional backdrop), it must do two things: **visibly fill the whole frame edge to edge**, and **stay quiet enough that text reads on top.**

### The filling problem — read this first
A background that is mostly black (light flares, bokeh, glows on a black field) *looks like it doesn't fill the slide* — the black image area is indistinguishable from the black slide behind it. The image technically covers the frame, but the eye sees a small glow floating in a void. **The fix is texture or detail that is visible edge to edge.** Always.

### Required anchors (always inject)
- "Fills the entire frame, edge to edge"
- "Visible texture or detail across the whole frame — no large empty black areas"
- "Dark and low-key, but not pure black"
- "No text, no words, no letters, no numbers, no logos"

### The three approved background kinds

**1. Dark paper texture**
> "A dark charcoal crinkled paper texture filling the entire frame edge to edge, soft raking light catching the deep folds and creases, near-black with subtle warm-grey tonal variation, matte and tactile, no subject, slightly darker toward the lower-left."

**2. Dark grid / graph paper**
> "A dark near-black surface covered edge to edge with a precise fine grid of faint thin light-grey lines, like dark graph paper or blueprint paper, evenly lit, minimal and technical, the grid fading slightly darker into the lower-left."

**3. Darkened illustrative image** (a real scene that illustrates the slide)
> "A heavily darkened, low-key photograph of [scene relevant to the slide], cinematic and muted, the subject and its light concentrated on the [side opposite the text — usually upper-right], the [text side — usually lower-left] falling into deep shadow. Fills the entire frame edge to edge."

### Composition rule for darkened-illustrative backgrounds
Text on slide overlays sits **bottom-left**. So the image's visual emphasis (subject, light, detail) goes **top-right**, and the bottom-left falls into shadow. The image and the text never fight for the same corner.

### NEVER for backgrounds
- Light flares, lens flares, bokeh, glows on a black field (the "doesn't fill" problem)
- Large empty black areas
- Cityscapes / identifiable places (too busy, compete with text)
- People in sharp focus (eyes pull attention off the text)
- Anything with text, signage, or recognizable logos

---

## Mood / tone keywords

Choose 5-8 keywords that describe the brand's emotional fingerprint. These get injected into prompts as style anchors:

- [keyword 1 — e.g., cinematic]
- [keyword 2 — e.g., understated]
- [keyword 3 — e.g., confident]
- [keyword 4 — e.g., warm]
- [keyword 5 — e.g., authoritative]
- [keyword 6 — e.g., restrained]
- [keyword 7 — e.g., earned]
- [keyword 8 — e.g., proven]

---

## Forbidden elements

Things that NEVER appear in [CLIENT NAME] imagery, generated or otherwise:

- [e.g., Stock-photo handshakes]
- [e.g., Generic "diverse team smiling at laptop" tropes]
- [e.g., Lens flares / overly cinematic VFX]
- [e.g., Words / text / logos in generated images]
- [e.g., Confetti / celebration tropes]
- [e.g., Emojis or icons embedded in scenes]
- [e.g., Cliché "lightbulb moment" / brain / gear / puzzle iconography]
- [e.g., Hands holding tablets with floating UI elements]

The forbidden list is the brand's visual immune system. Every item should be a real pattern the brand has explicitly rejected, not a hypothetical.

---

## Reference images

Drop 5-10 real on-brand images into `assets/style-references/`. These get passed as `--reference` to Gemini Nano Banana Pro for style anchoring during generation.

### Suggested categories
- 2-3 background / atmospheric examples
- 2-3 founder / people examples (real photos of [VOICE OWNER] / [CLIENT NAME] team)
- 1-2 illustration examples (past on-brand illustrations)
- 1-2 product / environment examples
- 1-2 ad creative / past-performer examples

The references are stronger than any text description. Once they're in place, the generation script leans on them heavily for style consistency.

### File naming convention
```
assets/style-references/
  bg-atmospheric-01.jpg          # backgrounds
  bg-atmospheric-02.jpg
  bg-grain-texture.jpg
  founder-01.jpg                 # people / scenes
  founder-02.jpg
  team-environment.jpg
  illustration-flat-01.png       # illustrations
  illustration-character.png
  product-mockup-01.jpg          # products
  ad-past-winner-01.jpg          # references for ad creative
```

---

## Provider-specific style notes

Different providers respond to slightly different prompt languages. If [CLIENT NAME]'s style needs provider-specific tuning, document here:

### Gemini Nano Banana Pro
- Default. Use these prompt phrasings: [...]
- Avoid these phrasings (they trigger common Gemini failures): [...]

### OpenAI gpt-image-1
- Used for illustrations + edits. Use these phrasings: [...]
- Avoid: [...]

### Imagen 4 (if used)
- Use these phrasings: [...]
- Avoid: [...]

---

## Customization checklist

- [ ] Replace all `[BRACKETED]` values
- [ ] Confirm color palette HEX values match logo / brand guide
- [ ] Drop 5-10 reference images into `assets/style-references/`
- [ ] Test a generation in each category (background / scene / illustration); spot-check that output matches the aesthetic description above
- [ ] If style drifts in generated output, tighten the photo-style or illustration-style sections
- [ ] Populate forbidden-elements list with real past rejections (not hypotheticals)
- [ ] Add provider-specific style notes if a non-default provider is used regularly
