# Brand Guide Protocol

Every landing page invocation should start with: **"Where does the brand guide live?"**

## Where to look (in order)

1. **Explicit path** — user supplied a path. Use it.
2. **Project root** — look for `brand-guide.md`, `brand.md`, `BRAND.md`, or anything in `/brand/` or `/.brand/` in the current working directory.
3. **Client folder** — if the project is under `clients/{name}/`, look in that folder.
4. **Shared brand library** — check `~/.claude/brand-guides/{client-slug}.md` if it exists.
5. **Client's existing site** — if the user mentions a current website, fetch the homepage and infer brand tokens (palette, fonts, voice) from it.
6. **Social presence** — for solo creators, the Instagram / X / YouTube channel often defines the brand.
7. **Fallback: invent one** — see "Inventing a brand guide" below.

If you find a brand guide, follow it strictly. Don't second-guess color choices, font choices, or voice.

## Required brand-guide fields

A complete brand guide answers these. If a brand guide is missing fields, fill them in by inference and confirm with the user before using them.

```markdown
# {Brand Name} Brand Guide

## Identity
- **Name**: 
- **Tagline**: 
- **One-line positioning**: 

## Voice
- **Tone**: e.g. direct, confident, no-fluff
- **Reading level**: 6th grade / 10th grade / professional
- **Forbidden words**: e.g. "synergy", "leverage" (as verb), emojis
- **Loved words**: e.g. "build", "ship", "compound"
- **Person**: first-person ("I/we") vs third-person

## Visual
- **Brand color (HEX)**: ONE primary saturated color
- **Background mode**: light / dark / both
- **Typography**: heading font + body font (with font-display preferences)
- **Border-radius default**: e.g. 8px on cards, 12px on buttons, 0px (sharp)
- **Photography style**: real photos / 3D renders / illustrations / no people
- **Logo**: path or SVG inline

## CTA defaults
- **Verb stack**: e.g. "Apply now", "Book my call", "Get started"
- **Button style**: solid / outlined / pill / sharp rectangle
- **Sub-CTA microcopy**: e.g. "30-day money-back guarantee"

## Forbidden patterns
- e.g. "No emoji headers"
- e.g. "No stock photos of people"
- e.g. "Never use gradient buttons"
```

## Inventing a brand guide (fallback flow)

When no brand guide exists and the user just says "make it look good":

1. **Tell the user you're inventing the brand** so they know to push back if wrong.
2. **Ask 3 quick questions**:
   - Light or dark theme?
   - What feeling? (premium / aggressive / friendly / luxury / editorial)
   - Reference site they admire?
3. **Pick from the defaults** in [design-system.md](design-system.md) — one color, one heading/body pair, one container width.
4. **Write a minimal brand guide** to `{project-dir}/brand-guide.md` so future invocations stay consistent.
5. **Confirm before building** — paste the brand snapshot back to the user in one short summary.

Example invented-brand snapshot:

```
Invented brand for this landing page:
- Theme: dark
- Brand color: #FF5C00 (conversion orange)
- Heading font: Plus Jakarta Sans 800
- Body font: Plus Jakarta Sans 400
- Container max-width: 1200px
- Button style: 8px radius, solid brand, transform-on-hover
- Voice: direct, no fluff, founder-to-founder

Going to build with this. Push back if you want any of it changed.
```

## Inferring brand from an existing site

If the user points at an existing site as their brand source:

```bash
curl -sL -A 'Mozilla/5.0...' '{URL}' -o /tmp/brand-source.html
```

Then extract:
- Computed colors of body, headings, primary buttons (regex `color`, `background`)
- Font families from `font-family` declarations
- Logo from `<link rel="icon">` or the visible `<img>` in the header
- Voice — read 3-5 sections of body copy and characterize

Write it up as a brand guide and confirm.

## Brand guide hierarchy (when there's conflict)

If the brand guide says one thing and a competitive-reference page does another:
1. Brand guide wins.
2. UNLESS the user explicitly says "I want this section to look like {reference}".

Don't let conversion best practices override the brand guide silently. Make it explicit: "Your brand guide says X, but the {reference} page uses Y for the CTA — want me to deviate, or stick with the guide?"

## Saving an invented brand guide

When you invent one, write it to the project before generating code. That way:
- The user can edit it before building
- The next invocation of the skill on this project picks up the same guide
- You don't drift between sections

Default save location: `{project-dir}/brand-guide.md` or `workspace/{project-name}/brand-guide.md`.
