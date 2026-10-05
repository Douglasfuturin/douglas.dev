# Design System Defaults

When a brand guide exists, follow it. When one doesn't (or you've been told "make it look good"), use this as your default playbook.

## Five-second design principles

1. **One brand color** — used for ALL CTAs and key accents. Not two. Not "primary + secondary". One.
2. **High contrast on CTAs** — saturated brand color against neutral background. The CTA must read at the edge of peripheral vision.
3. **Heavy heading weight** — display fonts should be 700+ for headlines. Thin display fonts are an aesthetic choice that costs you conversion.
4. **Tight headline / loose body** — headlines at 1.05-1.15 line-height. Body at 1.5-1.7. Mixing these two rhythms creates editorial polish.
5. **Vertical rhythm > horizontal symmetry** — don't obsess about centering. Obsess about consistent spacing between sections (typically 80px / 120px / 160px between sections).

## Color systems by page mood

### Dark / serious / premium (financial, B2B SaaS, agency)
```
--bg:           #0a0a0a  (near black, never pure #000)
--surface:      #141414  (one tick lighter)
--border:       rgba(255, 255, 255, 0.08)
--text:         #ededed
--text-muted:   #8a8a8a
--brand:        [one saturated color — see palette below]
--brand-hover:  [10% lighter version]
```

### Light / approachable / modern (coach, info-product, course)
```
--bg:           #ffffff or #fafafa
--surface:      #f5f5f5
--border:       #e8e8e8
--text:         #0a0a0a
--text-muted:   #5a5a5a
--brand:        [one saturated color]
```

### Editorial / luxury / high-ticket
```
--bg:           #f8f5f0  (warm off-white)
--surface:      #ffffff
--border:       #e6dfd4
--text:         #1a1a1a
--text-muted:   #6a6a6a
--brand:        #c9a36e (warm gold) OR #0a0a0a (black-on-cream)
```

## Brand color palette (when you need to pick one)

Use ONE of these. Don't mix more than one saturated color on the page.

| Color | Hex | Best for |
|-------|-----|----------|
| Conversion orange | `#FF5C00` | High-energy, action-oriented, ecom |
| Stripe purple | `#635BFF` | SaaS, fintech, premium B2B |
| Hot pink | `#F982AA` | Direct-response, lifestyle, creator |
| Lime green | `#92C329` | Bold, contrarian, attention-grab |
| Fire red | `#E60000` | Urgency, masculine offers, sales-heavy |
| Cardone red | `#D1242A` | Aggressive, finance/sales, deep red |
| Trustworthy blue | `#0066FF` | B2B, fintech, healthcare |
| Money green | `#0CCA4A` | Finance, results-driven |
| Warm gold | `#C9A36E` | Luxury, editorial, high-ticket |

## Typography pairings (steal-worthy defaults)

| Heading | Body | Vibe |
|---------|------|------|
| Plus Jakarta Sans (700-900) | Plus Jakarta Sans (400-500) | Modern, friendly, SaaS |
| Inter (700-900) | Inter (400-500) | Clean, neutral, tech |
| Sora (700-800) | Sora (400) | Editorial-tech crossover |
| SF Pro Display (700) | SF Pro Text (400) | Apple-clean, premium |
| Montserrat (700-900) | Lato (400) | Bold, sales-oriented |
| DM Sans (700) | DM Sans (400) | Modern, B2B, neutral |
| Manrope (700-800) | Manrope (400) | Tech-forward, balanced |
| Playfair Display (700) | Inter (400) | Editorial, high-ticket |
| Tungsten / Druk Wide | Lato | Bold display, event/seminar |

For ONE accent word in italic serif inside a sans headline (a pattern Marketing.mba uses):
> Heading sans + accent word in `Source Serif 4` italic, same size, slight color shift.

## Spacing rhythm

Use a consistent vertical scale. Don't free-style spacing.

```
--space-1:   4px
--space-2:   8px
--space-3:   12px
--space-4:   16px
--space-6:   24px
--space-8:   32px
--space-12:  48px
--space-16:  64px
--space-20:  80px
--space-24:  96px
--space-32:  128px
```

Between sections: `--space-24` to `--space-32` on desktop, half on mobile.
Within sections: `--space-12` to `--space-16` between major blocks.
Within blocks: `--space-4` to `--space-6`.

## Container widths

```
--container-narrow:   640px   (forms, FAQ, single-column copy)
--container-default:  960px   (text + image blocks, testimonials)
--container-wide:     1200px  (hero, full sections)
--container-full:     100%    (full-bleed bands, marquees)
```

Most sections should sit at `--container-default` or `--container-wide`. Vary between adjacent sections to break monotony.

## Button defaults

Primary CTA — the workhorse:

```css
.cta {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 16px 28px;
  font-size: 16px;
  font-weight: 600;
  letter-spacing: -0.01em;
  border-radius: 8px;
  background: var(--brand);
  color: #ffffff;
  border: none;
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.12s ease;
  box-shadow: 0 4px 16px -4px rgba(0, 0, 0, 0.15);
}
.cta:hover {
  transform: translateY(-1px);
  box-shadow: 0 8px 24px -4px rgba(0, 0, 0, 0.2);
}
```

For aggressive / sales-heavy pages (Cardone-style): zero border-radius, all-caps, heavy weight.
For modern SaaS / agency: 8-12px border-radius, sentence-case, slightly tighter padding.

### "Hot iron" CTA — gradient + halo glow (Client Ascension)
For dark / premium pages where the CTA needs to glow off a true-black background. Use sparingly — it's a pattern interrupt.

```css
.cta-hot {
  background: linear-gradient(180deg, #A30003 0%, #FF0004 100%);
  color: #fff;
  font-weight: 700;
  padding: 18px 32px;
  border-radius: 999px;            /* fully rounded */
  box-shadow: 0 0 20px rgba(255, 0, 4, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.08);
}
.cta-hot:hover {
  box-shadow: 0 0 36px rgba(255, 0, 4, 0.4);
}
```

Pair with a "SIGNUPS CLOSING SOON" red-block progress bar directly below it. The combo is what made the Client Ascension page feel urgent without being cheap. Repeat the CTA 8-12 times down the page — each instance reinforces the deadline.

Swap `#FF0004` for the brand color if not using red.

## Section-rhythm rules (anti-AI-slop)

The fastest tell of an AI-generated landing page is monotonous section rhythm: every section has the same padding, same width, same alignment, same vibe. Break it.

- Alternate full-bleed bands with contained sections
- Alternate background color: page → tinted → page → tinted
- Sections with a single image should sometimes be left-aligned, sometimes right-aligned, sometimes centered
- Marquee scrollers are full-bleed by default
- The hero should have more vertical breathing room than any other section
- The CTA-banner sections should be tight and dense (compress everything inward)

## Mobile rules

Build mobile-first. At 375px width:
- Headline must fit without breaking awkwardly (test with the longest headline you write)
- CTA must be ≥48px tall (thumb-friendly)
- Body text minimum 16px (never 14px on mobile)
- Side padding: 20-24px minimum
- Section vertical padding: 48-64px (half of desktop)
- No horizontal scrolling unless explicitly a marquee
- Sticky CTA at bottom of viewport on long pages (use sparingly — only if scroll depth is part of the conversion flow)

## Component patterns to default to

| Pattern | When | Notes |
|---------|------|-------|
| Sticky pill nav with glass blur | Premium dark pages | Use `backdrop-filter: blur(20px)` + transparent bg |
| 4-column testimonial marquee (variable speed) | Pages with 20+ testimonials | Multiple rows scrolling at different speeds (50s / 65s / 42s) feels organic |
| Inline VSL with 56.25% padding-top wrapper | VSL pages | Standard 16:9 responsive video wrapper |
| 3-column problem stack | Below hero | Each column gets icon + 1 line headline + 2 lines body |
| Side-by-side "for you / not for you" | Above the offer | Two-column compare; left list checkmarks green, right list X's red |
| Price-anchor stack | Offer section | Bullet list with right-aligned dollar values; total at the bottom; current price in larger weight |
| Bracket-pattern CTA (1 above fold + 1 mid + 1 below offer + 1 in footer) | All pages | Minimum 3 CTAs |
| Faint diagonal grid background | Hero on dark themes | 1px lines at 6deg rotation, very low opacity |
| Glow / ambient gradient on hero | Premium dark pages | Single radial gradient behind CTA, brand color, 20% opacity |
| Floating UI mockup / dashboard screenshot | Below hero | Tilted slightly (`transform: perspective(1000px) rotateX(8deg) rotateY(-4deg)`) |

## Anti-defaults (banned patterns)

These scream "template" / "AI-built". Don't ship them:

- Gradient CTA buttons (use solid colors)
- Purple gradient blob backgrounds
- "Lorem ipsum" or any filler text
- Three identical-height feature cards
- Emoji as section headers
- Stock photo of "team meeting"
- Generic 3-step "How it works" with car/plane/rocket icons
- Centered everything (mix alignment)
- Same border-radius on every component
- "Get started" as primary CTA
