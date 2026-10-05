# Deck Config Schema

> The `config.json` format consumed by `scripts/render_deck.py`. A config describes a full deck: deck-level metadata plus an ordered list of slides. Each slide names a pattern and supplies the content that pattern needs.

## Top-level structure

```json
{
  "deck": { ... },
  "slides": [ { ... }, { ... } ]
}
```

## The `deck` object

| Field | Required | Description |
|-------|----------|-------------|
| `title` | yes | Deck title, sets the HTML `<title>` |
| `accent_color` | no | Hex color, default `#FF5C28`. Drives the `--accent` CSS variable |
| `output_dir` | yes | Where `deck.html` + `assets/` are written, relative to the cwd the script runs from |

## The `slides` array

Each slide is an object:

| Field | Required | Description |
|-------|----------|-------------|
| `n` | yes | Slide number (integer). Used for image filenames (`slide-007.png`) |
| `pattern` | yes | One of the 53 pattern names (see catalog below) |
| `content` | depends | The text/data the pattern renders (pattern-specific, see below) |
| `visual` | no | A single image to generate for this slide |
| `visuals` | no | A list of images (for multi-image patterns like `before-after`, `image-mosaic-above`) |

### The `visual` object

```json
"visual": {
  "prompt": "A detailed image generation prompt...",
  "aspect": "16:9",
  "references": ["path/to/style-ref.png"]
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `prompt` | yes | The image prompt. "No text" guidance is auto-appended by the generator |
| `aspect` | no | `16:9` (default) / `9:16` / `1:1` / `4:3` / `3:4` / `21:9` / `3:2` / `2:3` |
| `references` | no | Reference image paths for style/likeness anchoring |

`visuals` is the same object shape, in a list. The generated images are passed to the renderer in order (e.g., `before-after` uses `visuals[0]` for the before side, `visuals[1]` for the after side).

Generated images are saved to `{output_dir}/assets/slide-{n:03d}.png` (single) or `slide-{n:03d}-{i}.png` (multi). They are **cached**, re-running the render reuses them unless `--regenerate-images` is passed.

## Inline markup

Text fields ending in `_html` (e.g., `text_html`, `claim_html`) support two inline tags:
- `<accent>...</accent>` → renders in the accent color
- `<arrow>...</arrow>` → renders an accent arrow (used in `case-study-headline`)

Plain fields (no `_html` suffix) are HTML-escaped, safe for literal text.

## Pattern content reference

Each pattern and the `content` fields it expects. Patterns marked **(image)** also need a `visual` or `visuals`.

### Text / statement patterns
| Pattern | Content fields |
|---------|----------------|
| `title` | `title`, `meta_main`, `meta_accent`, `meta_secondary` |
| `big-text` | `text_html` or `text` |
| `mono-word` | `text` |
| `mono-line` | `text` |
| `mono-name` | `text` |
| `bridge` | `text` |
| `big-claim` | `claim_html` or `claim` |
| `stack-anchor` | `text` |
| `three-lines` | `lines` (list of strings, auto-numbered, or list of `{number, text}`) |
| `scene-setter` | `lines` (list of strings) |
| `vs-belief` | `label`, `belief` |
| `misconception` | `wrong_label`, `wrong_text`, `correct_label`, `correct_text` |
| `callout-box` | `callout_html` or `callout`, `source` |
| `section-divider` | `eyebrow`, `title` |

### Audience / engagement patterns
| Pattern | Content fields |
|---------|----------------|
| `permission` | `question`, `hint` |
| `instruction` | `action`, `reason` |
| `agenda` | `items` (list of strings) |
| `avatar` | `label`, `items` (list of strings) |
| `not-for` | `label`, `items` (list of strings) |

### Proof patterns
| Pattern | Content fields |
|---------|----------------|
| `proof-number` | `number`, `label` |
| `proof-stat` | `number`, `label` |
| `case-study-headline` | `headline_html` or `headline` |
| `stat-row` | `stats` (list of `{number, label}`) |
| `quote` | `quote`, `attribution` |
| `timeline` | `nodes` (list of `{date, event}`) |

### Framework / teaching patterns
| Pattern | Content fields |
|---------|----------------|
| `framework-named` | `name_html` or `name` |
| `framework-step` | `step_number`, `step_name`, `step_description` |

### Image patterns
| Pattern | Content fields | Visual |
|---------|----------------|--------|
| `photo-full` |, | `visual` (1) |
| `photo-text-overlay` | `overlay_text` | `visual` (1) |
| `image-split` | `title`, `body` | `visual` (1) |
| `image-hero` | `caption` | `visual` (1) |
| `image-mosaic-above` | `title_html` or `title`, `subtitle` | `visuals` (1-3) |
| `screenshot` | `caption` | `visual` (1) |
| `logo-wall` | `logos` (list of src strings) | or `visuals` |
| `before-after` | `before` `{label, text}`, `after` `{label, text}` | `visuals` (2) |

### Testimonial patterns
| Pattern | Content fields | Visual |
|---------|----------------|--------|
| `testimonial-single` | `quote`, `name`, `role` | `visual` (1, avatar) or `content.avatar` URL |
| `testimonial-grid` | `cards` (list of `{name, role, quote, avatar}`) | avatars as URLs in cards |
| `testimonial-screenshot` | `quote_text`, `name`, `role` | `visual` (1, screenshot) |

### Offer / close patterns
| Pattern | Content fields |
|---------|----------------|
| `stack-line` | `rows` (list of `{name, description, value, bonus}`, `bonus: true` adds the "+ BONUS" tag) |
| `stack-total` | `label`, `amount` |
| `price-reveal` | `label`, `price` |
| `payment-plan` | `separator`, `plan` |
| `comparison-anchor` | `rows` (list of `{label, value, this}`, `this: true` accent-highlights the row) |
| `roi-math` | `rows` (list of `{label, value, result}`, `result: true` accent-highlights) |
| `cost-of-not` | `label`, `consequences` (list of strings) |
| `guarantee-headline` | `guarantee_html` or `guarantee` |
| `guarantee-details` | `label`, `conditions` (list of strings) |
| `urgency-reason` | `label`, `reason` |
| `deadline` | `label`, `deadline_text` |
| `action-plan` | `label`, `steps` (list of strings) |
| `button` | `url` |
| `final-cta` | `url`, `signoff` |
| `faq-grid` | `items` (list of `{q, a, full_width}`) |

## Minimal example

```json
{
  "deck": {
    "title": "My Webinar",
    "accent_color": "#FF5C28",
    "output_dir": "workspace/my-deck"
  },
  "slides": [
    { "n": 1, "pattern": "title",
      "content": { "title": "My Webinar", "meta_accent": "2026" } },
    { "n": 2, "pattern": "big-text",
      "content": { "text_html": "The <accent>one idea</accent> that changes everything." } },
    { "n": 3, "pattern": "photo-full",
      "visual": { "prompt": "An atmospheric dark workspace, out of focus", "aspect": "16:9" } }
  ]
}
```

## Rendering

```bash
# Stage 1, smoke test, no image cost
python3 scripts/render_deck.py --config my-config.json --skip-images

# Stage 2, full render with image generation
python3 scripts/render_deck.py --config my-config.json

# Force-regenerate cached images
python3 scripts/render_deck.py --config my-config.json --regenerate-images
```

Run from the marketing template root so `output_dir` resolves correctly.
