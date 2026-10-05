---
name: meme-ad-generator
description: Use when the user wants to generate meme-format ad creatives for any product. Generates 6 ads across cartoon memes (illustrated Drake, Expanding Brain, Virgin vs Chad, Wojak, etc.) and photorealistic memes (using actual photo templates). Branding is integrated naturally into meme panels — not slapped on as a footer. Uses Gemini image generation.
---

# Meme Ad Generator

Meme-format ads that feel native in feeds. People scroll past ads — they stop for memes. This skill generates two types: **cartoon memes** (illustrated/drawn templates) and **realistic memes** (photorealistic using actual template images). Branding is baked INTO the meme copy — not added as a logo bar.

---

## Ad Psychology for Memes

Meme ads work because they leverage **pattern recognition + pattern interruption**. The viewer recognizes the meme format instantly (dopamine hit from familiarity), then reads the custom labels (pattern interrupt that carries the marketing message). The result feels like organic content — not an ad.

### The 6 Psychological Triggers

1. **Transformation** — Show before/after. Drake rejecting old way, approving your product.
2. **Social Proof** — The crowd effect. "Everyone else already made the move."
3. **Curiosity Gap** — An incomplete thought that demands resolution. Use in the setup panel.
4. **FOMO/Scarcity** — Real momentum shown through meme format ("drawing 25 cards" instead of acting).
5. **Pain Point** — Call out the exact frustration. The audience sees themselves in the "before" panel.
6. **In-Group / Identity** — Memes that only YOUR target audience would get. Signals belonging.

### Meme Angle Selection Matrix

| Pain/Situation | Best Meme Format | Why |
|---|---|---|
| Old way vs new way | Drake | Two-panel rejection/approval |
| Refusing to act (avoidance) | UNO Draw 25 | "Rather do X than Y" |
| Everyone else moving on | Distracted Boyfriend | Attention pulled from status quo |
| Chaos / "I'm fine" denial | This Is Fine | Recognizable helplessness |
| Before/after evolution | Expanding Brain | Escalating levels of understanding |
| Fancy vs real talk | Tuxedo Winnie Pooh | Pretentious vs simple |
| Stepping in a trap | Stepped in Shit | Avoidable mistake they keep making |
| Better with you | Running Away Balloon | Leaving the old thing behind |
| Making a plan that fails | Gru's Plan | Setup + reality check |
| Old reliable | Spongebob Ol' Reliable | What they keep defaulting to |

### Text Rules for Memes

- **Max 8 words per panel label.** Memes are not ad copy.
- Labels go in the **standard position for that template** (top/bottom for Drake, above heads for Distracted Boyfriend, etc.)
- White Impact-style font with black outline for realistic photo memes
- Bold illustrated text for cartoon memes
- The product/brand name appears INSIDE the meme text — not as a watermark or footer
- Keep it punchy. The best meme copy sounds like something someone would actually share.

**The test:** Would someone repost this if they didn't know it was an ad?

---

## Process

### Step 1: Gather Product Info

Ask for the following if not provided:

- **Product name:** What are we advertising?
- **Core benefit:** What does it do for the customer? (one sentence)
- **Target audience:** Who is this for? (be specific — not "businesses", say "freelance designers" or "SaaS founders")
- **Pain point:** What problem does this solve? What do they struggle with before finding this?
- **The transformation:** What does their life/work look like AFTER using this?
- **Price point:** (optional but helps calibrate value messaging)
- **Brand assets available?** Logo PNG, product screenshot, mascot? (optional — memes can work without)

### Step 2: Define the Meme Angle

Based on the pain point and transformation, pick ONE primary angle for this batch:

- **Comparison** — Old way vs your way (Drake, Virgin vs Chad, Tuxedo Pooh)
- **Pain Point / Avoidance** — They know what to do but keep not doing it (UNO Draw 25, Gru's Plan)
- **FOMO** — Everyone else is moving on; they're falling behind (Distracted Boyfriend, Running Balloon)
- **In-Group** — Only your ideal customer will get this reference (niche-specific humor)
- **Aspiration** — Show the dream state via meme format (Expanding Brain escalation to the outcome)

### Step 3: Select 3 Cartoon Meme Templates

Cartoon memes = illustrated/drawn versions of meme templates. NOT photorealistic. Gemini generates these from scratch in a cartoon/illustrated style.

**Best templates by angle:**

**Comparison:**
- **Drake Hotline Bling** (two panels: reject / approve) — works for any "old way vs new way"
- **Virgin vs Chad** — when you want to show the contrast in character/mindset
- **Tuxedo Winnie Pooh** — two labels for the same thing: fancy phrasing vs blunt truth

**Pain Point / Avoidance:**
- **UNO Draw 25** — "Do [simple action] OR draw 25" — they keep choosing the hard path
- **Gru's Plan** — 4-panel: has a plan → plan requires effort → realizes problem → same plan anyway
- **This Is Fine** — sitting calmly while everything burns around them

**FOMO:**
- **Expanding Brain** — escalating tiers of understanding, your product = the evolved choice
- **Distracted Boyfriend** — their attention being pulled toward your product away from the old way

**In-Group:**
- **Wojak** — "me thinking about [niche problem]" — simple and relatable
- **Crying Wojak** — the "before" state of your audience
- **Galaxy Brain** — multi-panel escalating logic chain that leads to choosing your product

**Template reference images:** Several cartoon meme formats have matching photo templates in `brand-assets/meme-references/realistic/`. When available, **always pass the photo template as `--reference`** even for cartoon memes — Gemini uses it to nail the panel layout, composition, and character positions, then illustrates it in the target style. This produces far more accurate layouts than a text description alone.

| Cartoon Meme | Reference File Available |
|---|---|
| Drake Hotline Bling | `drake-template.jpg` ✓ |
| Distracted Boyfriend | `distracted-boyfriend-template.jpg` ✓ |
| UNO Draw 25 | `uno-draw-25-template.jpg` ✓ |
| This Is Fine | `this-is-fine-template.jpg` ✓ |
| Gru's Plan | `grus-plan-template.webp` ✓ |
| Tuxedo Winnie Pooh | `tuxedo-winnie-pooh-template.jpg` ✓ |
| Spongebob Burning Paper | `spongebob-burning-paper-template.jpg` ✓ |
| Note Passing | `note-passing-template.webp` ✓ |
| Running Away Balloon | `running-away-balloon-template.png` ✓ |
| Expanding Brain | ✗ — describe layout in prompt |
| Wojak / Crying Wojak | ✗ — describe layout in prompt |
| Virgin vs Chad | ✗ — describe layout in prompt |
| Galaxy Brain | ✗ — describe layout in prompt |

For each cartoon meme:
- Pass the template reference file when available (see table above)
- Specify "cartoon/illustrated style, NOT photorealistic — recreate the panel layout from the reference as a bold illustration"
- Branding goes IN the meme text (e.g., "[Product Name]" is the approved option in Drake panel)
- No logo overlays, no footer bars
- Keep panel labels to 2-6 words each

### Step 4: Select 3 Realistic Meme Templates

Realistic memes use the actual meme template photos as `--reference` images. Gemini matches the exact photographic format.

**Available templates in `brand-assets/meme-references/realistic/`:**

| File | Format | Best For |
|---|---|---|
| `drake-template.jpg` | Two panels: reject / approve | Comparison, old vs new |
| `distracted-boyfriend-template.jpg` | Three people on street | FOMO, attention shift |
| `uno-draw-25-template.jpg` | UNO card + person holding cards | Avoidance, pain point |
| `this-is-fine-template.jpg` | Dog in burning room | Denial, "I'm fine" |
| `bernie-asking-template.jpg` | Bernie Sanders at podium | Bold ask, value prop |
| `who-wants-to-be-a-millionaire-template.jpg` | Game show format | Quiz-style hook |
| `running-away-balloon-template.png` | Person releasing balloon | Leaving behind something |
| `loki-greatest-power-template.jpg` | Two people talking | Setup + reveal |
| `stepped-in-shit-template.jpg` | Person stepping in mess | Avoidable mistake |
| `spongebob-burning-paper-template.jpg` | Spongebob burning paper | Destroying old approach |
| `tuxedo-winnie-pooh-template.jpg` | Two Pooh versions | Fancy vs simple framing |
| `cnn-breaking-news-template.jpg` | News broadcast | Breaking announcement hook |
| `grus-plan-template.webp` | 4-panel Gru plan | Plan → reality check |
| `spongebob-ol-reliable-template.jpg` | Spongebob ol' reliable | Default behavior |
| `note-passing-template.webp` | Students passing a note | Sharing a secret/tip |

Pass the template image as `--reference` so Gemini recreates the EXACT format with new labels.

**Realistic meme generation rules:**
- Labels in white Impact font with black outline (standard meme text style)
- No logos or brand marks added — branding is in the label text only
- Tell Gemini: "Match the EXACT format, composition, and photographic style of the reference image. Recreate the scene with the same framing. Add labels: [TOP TEXT] / [BOTTOM TEXT]"
- No footer bars, watermarks, or call-to-action boxes

### Step 5: Generate All 6 Ads

Run all 6 generations concurrently.

**Cartoon meme command (with reference template):**
```bash
python3 scripts/generate_ad.py \
  --reference "brand-assets/meme-references/realistic/{template-file}" \
  --prompt "{detailed prompt}" \
  --aspect-ratio "1:1" \
  --output "workspace/{today}/ads/{product-slug}/memes/cartoon-v{N}-{template-name}.png"
```

**Cartoon meme command (no reference available):**
```bash
python3 scripts/generate_ad.py \
  --prompt "{detailed prompt}" \
  --aspect-ratio "1:1" \
  --output "workspace/{today}/ads/{product-slug}/memes/cartoon-v{N}-{template-name}.png"
```

**Realistic meme command:**
```bash
python3 scripts/generate_ad.py \
  --reference "brand-assets/meme-references/realistic/{template-file}" \
  --prompt "{detailed prompt}" \
  --aspect-ratio "1:1" \
  --output "workspace/{today}/ads/{product-slug}/memes/realistic-v{N}-{template-name}.png"
```

**Cartoon meme prompt structure (with reference image):**
```
The reference image shows the [TEMPLATE NAME] meme format. Recreate this exact panel layout and composition as a bold cartoon/illustrated scene — NOT photorealistic. Match the framing, panel divisions, and character positions from the reference, but render everything in a clean illustrated style with bold outlines and flat colors.

Panel 1: [character/label description]. Text: "[PANEL 1 TEXT]"
Panel 2: [character/label description]. Text: "[PANEL 2 TEXT]"

Style: Bold cartoon/illustrated. Clean, high-contrast illustration with solid colors and bold outlines.
White bold text with black outline on each panel label, positioned the same as the reference format.
Do NOT make it photorealistic — this should look like a drawn/illustrated cartoon.
Do NOT add any logos, watermarks, footer bars, or call-to-action buttons.
Do NOT add any text beyond the specified panel labels.
```

**Cartoon meme prompt structure (no reference available — describe layout):**
```
Illustrated cartoon meme in the [TEMPLATE NAME] format. [DESCRIBE THE PANEL LAYOUT — number of panels, how they're arranged, what characters/elements appear in each].

Panel 1: [character/label description]. Text: "[PANEL 1 TEXT]"
Panel 2: [character/label description]. Text: "[PANEL 2 TEXT]"

Style: Bold cartoon/illustrated, NOT photorealistic. Clean, high-contrast illustration with bold outlines.
White bold text with black outline on each panel label.
Do NOT add any logos, watermarks, footer bars, or call-to-action buttons.
Do NOT add any text beyond the specified panel labels.
```

**Realistic meme prompt structure:**
```
Recreate the meme format from the reference image with new text labels.
Match the EXACT photographic composition, framing, and style of the reference — same scene, same camera angle, same characters.

Add these labels in white Impact font with black outline (standard meme style):
Top: "[TOP TEXT]"
Bottom: "[BOTTOM TEXT]"
(adjust label positions to match the template's standard format)

Do NOT add any logos, watermarks, footer bars, or call-to-action buttons.
Do NOT add any text beyond the specified labels.
```

### Step 6: Review

For each generated meme, check:

**Click / Share test:**
- [ ] Would someone who doesn't know this is an ad actually share this?
- [ ] Is the joke/message clear in under 2 seconds?
- [ ] Does the marketing message land naturally — or does it feel forced?

**Quality gates:**
- [ ] Text is readable and correctly spelled
- [ ] Panel labels are in the right positions for the template
- [ ] No extra text, logos, or elements were added that weren't specified
- [ ] The brand/product name appears correctly in the label text
- [ ] Photorealistic memes match the reference template's format and framing

**Auto-reject and regenerate:**
- Any misspelled text in labels
- Logo/watermark appeared when not requested
- Panel text is in the wrong position
- Photorealistic meme doesn't match the reference template format
- The message is too vague (e.g., "Transform your business" with no specifics)
- Looks like an obvious ad, not a real meme

**Text rendering tips for regeneration:**
- Shorter labels = fewer typos. Cut to the minimum.
- Spell out critical brand names in the prompt: "The word ACME, spelled A-C-M-E"
- Repeat the label text twice in the prompt
- If a word keeps garbling after 2 tries, swap for a simpler synonym

### Step 7: Present

Show all 6 ads with:
- The ad image
- The meme template used and why it fits the angle
- Review status (pass/fail, any issues)
- Note any label text that needs post-production correction

Ask which directions resonate and offer to iterate.

---

## Key Principles

1. **The meme IS the brand.** Product/brand goes inside the label text — never as a logo slapped on the outside.
2. **Shareable first, branded second.** If it doesn't feel like a real meme, it fails as a meme ad.
3. **Angle before template.** Pick the right psychological angle first, then pick the template that best expresses it.
4. **Short labels win.** If the panel text needs more than 8 words, the angle is wrong.
5. **Realistic memes need reference images.** Always pass the template photo via `--reference` — don't try to describe it.

---

## What NOT to Do

- Logo bars or footer branding — ruins the meme feel instantly
- More than 8 words per panel label
- Trying to explain the product in the meme — the meme surfaces the pain, the caption does the selling
- Generic hooks ("This will change your business") — be specific to the pain point
- Corporate tone — memes must sound human

---

## Output

```
workspace/{today}/ads/{product-slug}/
  memes/
    cartoon-v1-{template-name}.png
    cartoon-v2-{template-name}.png
    cartoon-v3-{template-name}.png
    realistic-v1-{template-name}.png
    realistic-v2-{template-name}.png
    realistic-v3-{template-name}.png
  meme-brief.md        # Angle choice, template selections, label copy for each
  review-log.md        # What passed, what was regenerated, what changed
```
