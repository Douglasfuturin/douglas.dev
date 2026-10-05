# Image Prompt Engineering

> The difference between "a founder at a laptop" and a brand-aligned photorealistic image worth shipping is prompt engineering. Image generation models respond to specific phrasings, structures, and detail levels. This file is the deep playbook for writing prompts that consistently produce on-brand output.

---

## The 8-element prompt structure

Every image prompt should contain 8 distinct elements. Missing elements lead to generic output; over-specifying constrains the model. The right balance is "specific about what matters, open about what doesn't."

```
1. Subject — what is depicted (specific, vivid, named)
2. Style — photographic / illustration / character / etc.
3. Composition — framing, focal point, depth, balance
4. Lighting — direction, quality, mood
5. Color — palette anchors (often from brand-style.md)
6. Camera/lens — for photo style (35mm wide, 85mm portrait, 50mm natural)
7. Mood descriptors — atmospheric vibe words
8. Negative prompts — always-on exclusions ("no text, no watermark")
```

Different providers respond to slightly different orderings. Gemini and Imagen prefer descriptive natural language; OpenAI also accepts structured-list style. For maximum portability across providers, write in flowing natural language with each element as its own clause.

---

## Element 1: Subject

The subject is the WHAT. Specific subjects produce specific images. Vague subjects produce stock photography.

### Weak vs. strong subjects

| Weak | Strong |
|------|--------|
| A person at a laptop | A 30-year-old founder in a worn navy hoodie, leaning toward a 16-inch laptop screen, mid-typing |
| Office building | Modern open-plan loft office with exposed brick, weathered hardwood floor, single brass pendant lamp |
| Beautiful sunset | Last-light golden hour on a coastal cliff in Big Sur, low haze, sun just touching the horizon |

### Rules
- **Be specific about details that anchor the visual:** age range, clothing texture, posture, action.
- **Use proper nouns sparingly** (specific places sometimes trigger over-fitting; "a moody warehouse loft" usually beats "a Brooklyn warehouse loft").
- **Avoid abstract descriptors as the subject:** "success", "innovation", "growth" — these are concepts, not subjects. If the brief requires conveying success, pick a concrete subject that embodies it.

---

## Element 2: Style

The style anchors HOW the image is rendered.

### Style categories

**Photographic:**
- `photorealistic photograph`
- `cinematic photography`
- `documentary photography`
- `editorial photography`
- `lifestyle photography`
- `studio photography`

**Illustration:**
- `flat illustration`
- `line illustration` / `line art`
- `editorial illustration`
- `hand-drawn illustration`
- `isometric illustration`
- `character illustration`

**Hybrid / abstract:**
- `3d render`
- `clay render`
- `painting` / `oil painting`
- `watercolor`
- `collage`

### Rules
- **Pick one style and commit.** Mixing "photorealistic flat illustration" produces incoherent output.
- **Match the style to the use case.** Backgrounds → photographic. Diagrams → illustration. Mascots → character illustration. Product mockups → 3d render or photographic.
- **Brand-style.md overrides.** If `brand-style.md` specifies the default illustration style for [CLIENT NAME], use that.

---

## Element 3: Composition

Composition is the spatial structure of the image — what's where, framing, depth.

### Framing
- `close-up` — face fills frame, shoulders just visible
- `medium close-up` — chest up
- `mid-shot` — waist up
- `medium wide` — full body, some environment
- `wide shot` — body in environment
- `establishing shot` — full scene, subject small

### Focal point
- `subject in sharp focus, background blurred`
- `everything in focus, deep depth of field`
- `selective focus on the eyes, soft elsewhere`
- `bokeh background, single in-focus subject`

### Compositional rules
- `rule of thirds with subject in left third`
- `centered symmetrical composition`
- `leading lines from bottom-right to top-left`
- `low angle looking up`
- `eye level`
- `high angle looking down`

### Depth
- `shallow depth of field`
- `deep depth of field`
- `foreground, midground, and background layers`
- `flat composition` (for illustrations)

### Rules
- **Specify framing and focal point at minimum.** These two alone solve 70% of composition problems.
- **For backgrounds: prioritize negative space.** "Subject offset to left third, large empty space right side" gives the destination text somewhere to live.
- **Match composition to aspect ratio.** Portrait aspect → vertical compositional energy. Landscape → horizontal. Don't fight the canvas.

---

## Element 4: Lighting

Lighting is the most underused lever in image prompts. The same subject + same composition + different lighting = completely different mood.

### Direction
- `side-lit from camera left`
- `back-lit, subject silhouetted with rim light`
- `top-lit, dramatic shadows under brow`
- `front-lit, even illumination`
- `golden hour low side light`
- `blue hour ambient light`

### Quality
- `soft diffused lighting`
- `hard directional lighting`
- `dappled light through trees / blinds`
- `bounced light, soft fill`
- `single point source, deep shadows`

### Time of day / scene-specific
- `golden hour, warm orange-gold`
- `blue hour, cool blue-violet`
- `overcast, even soft light`
- `studio strobe, controlled`
- `candlelight, warm orange flicker`
- `screen glow, blue cast`
- `streetlight at night, sodium-vapor orange`

### Mood-driven
- `cinematic chiaroscuro`
- `Rembrandt lighting on the subject's face`
- `noir lighting with venetian blind shadows`
- `Vermeer-style window light`

### Rules
- **Specify direction AND quality.** "Dramatic lighting" alone produces inconsistent output. "Single warm key from camera right, hard directional, deep shadows" is reproducible.
- **Lighting drives mood more than any other element.** When you want atmospheric/cinematic, specify lighting in detail.
- **For backgrounds: lighting defines the entire feel.** A "warm bokeh" background is really "out-of-focus scene with warm point lights" — the lighting carries the look.

---

## Element 5: Color

Anchor to brand-style.md's palette. Specific hex values work in prompts — most providers respect them.

### Direct palette anchors
- `dominant color: deep navy (#0A0B2E)`
- `accent color: warm orange (#FF5C28)`
- `monochromatic in the brand primary color`

### Color grading / mood
- `warm orange-teal color grading`
- `desaturated, muted tones`
- `high saturation, vivid pop`
- `cool blue tones throughout`
- `warm cinematic grade, deep blacks`

### Rules
- **Always anchor to brand palette.** Pull HEX values from brand-style.md and embed them.
- **Use 1-2 dominant colors.** Multi-color compositions feel cluttered. Brand consistency comes from limited palettes.
- **Color grading > literal color.** "Warm cinematic grade" is more controllable than "make it orange-tinted."

---

## Element 6: Camera / lens (for photo style)

Specifying camera and lens characteristics dramatically improves photo realism. The model has learned what 35mm vs. 85mm output looks like.

### Lens choices
- `35mm wide angle lens` — wide, immersive, slight edge distortion, good for environments
- `50mm natural lens` — eye-natural perspective, good for portraits and mid-shots
- `85mm portrait lens` — flattering for faces, compressed background, classic portrait look
- `135mm telephoto` — heavily compressed background, isolated subject
- `24mm wide` — very wide, dramatic perspective
- `100mm macro` — close-up detail

### Camera body cues (subtle but help)
- `shot on Leica Q3` — clean documentary look
- `Hasselblad medium format` — high-detail editorial
- `Sony A7 IV` — modern hybrid look
- `film photography` — grain, color shifts, organic feel
- `Kodak Portra 400` — specific film stock, warm skin tones
- `Cinestill 800T` — moody tungsten-balanced cinematic

### Lens behaviors to invoke
- `f/1.4 shallow depth of field, melting bokeh`
- `f/8 deep focus, everything sharp`
- `slight chromatic aberration`
- `lens compression`
- `light leak`

### Rules
- **For portraits: 85mm or 50mm.** These produce flattering, natural-looking faces.
- **For environments / wide scenes: 35mm or 24mm.** Wider lenses pull the viewer in.
- **Film stocks anchor color.** "Kodak Portra 400" or "Cinestill 800T" gives more consistent color grading than generic descriptors.

---

## Element 7: Mood descriptors

A short stack of evocative words that signal atmosphere. Drawn from brand-style.md's mood/tone keywords.

### Common useful descriptors

**Atmospheric:**
- `cinematic, atmospheric, moody, restrained`
- `quiet, contemplative, considered`
- `gritty, lived-in, unpolished`

**Energy:**
- `intense, focused, kinetic`
- `calm, deliberate, unhurried`
- `urgent, momentum, alive`

**Tone:**
- `warm, approachable, human`
- `cool, clinical, precise`
- `confident, earned, proven`
- `playful, optimistic, irreverent`

**Quality:**
- `premium, considered, intentional`
- `documentary, authentic, real`
- `editorial, sophisticated, restrained`

### Rules
- **Pull from brand-style.md.** The mood keywords there are the brand's emotional fingerprint. Use those, not generic ones.
- **Stack 3-6 descriptors max.** More than 6 becomes noise.
- **Avoid contradictions.** "Cinematic and minimal and busy" is incoherent. Pick a direction.

---

## Element 8: Negative prompts (always on)

Things the model should NOT produce. These get appended to every prompt automatically by `generate_image.py`.

### Universal negatives (always included)
- `no text, no words, no letters, no numbers, no symbols, no characters, no writing`
- `no logos, no watermarks, no signatures`
- `no captions, no labels, no UI elements`

### Context-specific negatives

**For backgrounds:**
- `no people in focus`
- `no recognizable scenes, no landmarks`
- `no focal subject`
- `no busy patterns`

**For photo-style:**
- `no over-saturation`
- `no plastic skin, no airbrushed look`
- `no stock-photo handshakes / smiling at camera`
- `no clichéd composition`

**For illustration:**
- `no photorealistic elements`
- `no gradient overuse`
- `no cluttered details`

**Per [CLIENT NAME] brand:**
Pull from `brand-style.md` forbidden-elements list. Example:
- `no confetti, no celebration tropes`
- `no lightbulb / brain / gear iconography`
- `no diverse-team-smiling-at-laptop stock tropes`

### Rules
- **Always include "no text" negatives.** Text in generated images is universally garbled across all providers.
- **Include brand-specific negatives from brand-style.md.** This is the brand's visual immune system.
- **Don't over-negate.** 8-12 negative items is plenty. Too many makes the model anxious.

---

## Provider-specific prompt patterns

### Gemini Nano Banana Pro

Gemini prefers:
- Flowing natural-language prompts (not lists)
- Specific subject + environment + lighting + mood in that order
- Reference images attached separately via `contents=[prompt, image]`
- "Photorealistic" or "cinematic photograph" as style anchor

Example Gemini-tuned prompt:
```
A 30-year-old founder in a worn navy hoodie leaning toward a 16-inch laptop screen,
mid-typing in a quiet open-plan loft office. Single warm key light from camera right,
hard directional, deep shadows. Shot on Leica Q3, 35mm, f/2.0, shallow depth of field
with bokeh background. Warm cinematic color grading, deep blacks, dominant tones of
deep navy (#0A0B2E) and warm orange highlight. Cinematic, atmospheric, restrained,
documentary-feel. No text, no words, no logos, no watermark.
```

### OpenAI gpt-image-1

OpenAI accepts both natural language and structured prompts. For clean illustrations, structured tends to work better:

```
Subject: Three abstract human figures, geometric, simplified.
Style: Flat illustration, minimal line work, two-tone.
Composition: Centered, symmetrical, evenly spaced figures.
Colors: Deep navy (#0A0B2E) figures on warm cream (#FAF5EB) background, single orange (#FF5C28) accent.
Mood: Editorial, restrained, confident.
Negative: No text, no detailed faces, no shading gradients.
```

### Imagen 4

Imagen prefers extreme specificity and benefits from compound descriptors:

```
Photorealistic editorial portrait of a 30-year-old founder, worn navy hoodie,
leaning into a laptop screen, mid-typing, intense focused expression, eyes on screen.
Quiet open-plan loft office environment, exposed brick wall background, dramatically
out-of-focus. Single warm directional key light from camera right at 45 degrees,
hard quality, deep contrasty shadows. 85mm portrait lens, f/1.4, shallow depth of
field, melted bokeh. Warm orange-teal cinematic color grade, deep blacks, Kodak
Portra 400 film stock aesthetic. Editorial, cinematic, restrained, documentary.
```

---

## Reference image use

References are stronger than text descriptions. When generating in [CLIENT NAME]'s style, pass real on-brand images via `--reference`. Provider behavior:

### Gemini Nano Banana Pro — reference images
- Pass via `contents=[prompt, PIL_image, PIL_image2, ...]`
- Mention in prompt: "Use the attached image as a style reference for lighting and color grading"
- For likeness preservation: "Use the attached photo of [Person]'s face — match their exact likeness"
- Can pass 1-5 references, more reduces signal per reference

### OpenAI gpt-image-1 — reference images
- For edits: use `images.edit` endpoint with input image + optional mask
- For style transfer: pass reference as part of a multi-image prompt (limited support)
- Generally weaker than Gemini for reference-style work — use Gemini for reference-driven generation

### Reference image quality
- Higher resolution = better (up to ~2048px on long edge)
- Clean, on-brand examples — not noisy or mixed-style
- Match the use case (background reference for background generation, scene reference for scene generation)

---

## Iteration prompt patterns

After the initial 4-variation generation, the user picks a direction. Iteration patterns:

### Pattern: "Like #2 but..."
```
[Original prompt]

EDIT INSTRUCTIONS:
- Keep overall composition and subject from the reference image
- Change: [specific change — "more orange tone", "tighter framing on face", "background less busy"]
```

Pass the chosen variant as `--reference`. The model uses it as the starting point.

### Pattern: "Different angle / different moment"
```
Same scene as the reference image, but [new angle / new moment].
Reference image is the visual style anchor — match lighting and color grading.
[Updated subject description for the new angle]
```

### Pattern: "Wrong direction, start over"
Don't pass the reference. Re-prompt from scratch with corrected understanding. Sometimes the original prompt had a subtle error (wrong style, wrong mood) that's easier to fix from a blank slate than to argue with the model.

---

## Common prompt failure modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Generic stock-photo output | Vague subject + no specific lighting | Make subject concrete, specify lighting direction + quality |
| Garbled text in image | Text in prompt was interpreted as text-to-render | Move text-related references to negative prompt; "no text in image" |
| Wrong color cast | Color named vaguely or competing colors | Use HEX values, limit to 1-2 dominant colors |
| Subject doesn't look like reference person | Reference image not strong enough or prompt overrides likeness | Pass reference via Gemini; add "match the exact likeness from the attached photo" |
| Image too busy / cluttered | Subject + too many composition elements | Strip composition to single subject + clear background |
| Background dominates the subject | No focal point specified | Add "subject in sharp focus, background blurred" + framing instruction |
| Image looks plastic / over-rendered | Default model output for "photorealistic" | Add film stock + lens + grain references; "shot on Leica Q3" or "Kodak Portra 400" |
| Mood is off | Missing or contradictory mood descriptors | Pull 3-5 mood words from brand-style.md, stack them at the end |

---

## Prompt quality checklist

Before sending to the generator, check that the prompt has:

- [ ] Subject specific enough to picture before generating
- [ ] Style explicit (photo / illustration / character / etc.)
- [ ] Composition (framing + focal point at minimum)
- [ ] Lighting (direction + quality)
- [ ] Color anchor (HEX values from brand-style.md)
- [ ] Camera/lens (if photo style)
- [ ] 3-6 mood descriptors from brand-style.md
- [ ] Negative prompts (universal + context-specific + brand-specific)
- [ ] Reference image attached (when generating in a defined style)
- [ ] Aspect ratio matches destination (16:9, 9:16, 1:1, etc.)

If any element is missing, expect generic or off-brand output. The cost of writing a thorough prompt once is far less than the cost of 4 generations of mediocre output.
