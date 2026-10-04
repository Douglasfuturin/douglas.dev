---
name: copy-website
description: Exact website cloner. Takes a URL, uses Playwright to reverse-engineer every visual and content detail (colors, fonts, layout, spacing, images, copy, interactions), builds a pixel-perfect Next.js replica, then uses Playwright visual QA to compare and iterate until it matches exactly. Use when the user says "copy website", "clone website", "replicate website", "mirror website", "duplicate this site".
---

# Copy Website Skill

Produce a pixel-perfect Next.js clone of any website. The process is: deep Playwright extraction → reverse brand guide → asset acquisition → build → Playwright visual QA loop until exact match.

**Never skip extraction or QA.** The whole point is fidelity — work until the screenshots match.

---

## Step 1: Full-Site Playwright Extraction

Navigate to the target URL with Playwright. Your goal is to reverse-engineer **everything** — not just a summary. Extract exhaustively.

### 1a. Screenshot the full page

Take a full-page screenshot at 1440px viewport width. Save it mentally as your ground truth. Also screenshot at 375px (mobile) and 768px (tablet).

### 1b. Extract design tokens via JavaScript

Run this in the browser console via `browser_evaluate` to extract computed styles from every major element:

```javascript
// Run this to extract the full design system
const extract = () => {
  const result = {
    fonts: new Set(),
    colors: new Set(),
    borderRadius: new Set(),
    spacing: {},
    fontSizes: new Set(),
    fontWeights: new Set(),
    lineHeights: new Set(),
    letterSpacing: new Set(),
    shadows: new Set(),
    transitions: new Set(),
    zIndexes: new Set(),
    elements: {}
  };

  // Sample all elements
  const elements = document.querySelectorAll('*');
  elements.forEach(el => {
    const cs = window.getComputedStyle(el);
    const tag = el.tagName.toLowerCase();

    // Collect fonts
    result.fonts.add(cs.fontFamily);

    // Collect colors
    if (cs.color !== 'rgba(0, 0, 0, 0)') result.colors.add(cs.color);
    if (cs.backgroundColor !== 'rgba(0, 0, 0, 0)') result.colors.add(cs.backgroundColor);
    if (cs.borderColor !== 'rgba(0, 0, 0, 0)') result.colors.add(cs.borderColor);

    // Collect typography
    result.fontSizes.add(cs.fontSize);
    result.fontWeights.add(cs.fontWeight);
    result.lineHeights.add(cs.lineHeight);
    result.letterSpacing.add(cs.letterSpacing);

    // Collect effects
    if (cs.borderRadius !== '0px') result.borderRadius.add(cs.borderRadius);
    if (cs.boxShadow !== 'none') result.shadows.add(cs.boxShadow);
    if (cs.transition !== 'all 0s ease 0s') result.transitions.add(cs.transition);
  });

  // Get key elements by tag
  ['h1','h2','h3','h4','p','a','button','nav','header','footer','section'].forEach(tag => {
    const el = document.querySelector(tag);
    if (el) {
      const cs = window.getComputedStyle(el);
      result.elements[tag] = {
        fontFamily: cs.fontFamily,
        fontSize: cs.fontSize,
        fontWeight: cs.fontWeight,
        lineHeight: cs.lineHeight,
        letterSpacing: cs.letterSpacing,
        color: cs.color,
        backgroundColor: cs.backgroundColor,
        padding: cs.padding,
        margin: cs.margin,
      };
    }
  });

  return {
    fonts: [...result.fonts],
    colors: [...result.colors],
    borderRadius: [...result.borderRadius],
    fontSizes: [...result.fontSizes].sort(),
    fontWeights: [...result.fontWeights],
    lineHeights: [...result.lineHeights],
    letterSpacing: [...result.letterSpacing],
    shadows: [...result.shadows],
    transitions: [...result.transitions],
    elements: result.elements
  };
};
JSON.stringify(extract(), null, 2);
```

### 1c. Extract layout structure

```javascript
// Map the page sections and their layout
const mapLayout = () => {
  const sections = [];

  // Find major structural sections
  const sectionEls = document.querySelectorAll('section, [class*="section"], [class*="hero"], [class*="banner"], [id*="section"], main > div, header, footer, nav');

  sectionEls.forEach(el => {
    const rect = el.getBoundingClientRect();
    const cs = window.getComputedStyle(el);
    sections.push({
      tag: el.tagName.toLowerCase(),
      id: el.id || null,
      classes: [...el.classList].join(' '),
      width: rect.width,
      height: rect.height,
      display: cs.display,
      flexDirection: cs.flexDirection,
      gridTemplateColumns: cs.gridTemplateColumns,
      maxWidth: cs.maxWidth,
      padding: cs.padding,
      margin: cs.margin,
      backgroundColor: cs.backgroundColor,
      backgroundImage: cs.backgroundImage,
      innerText: el.innerText?.slice(0, 200),
      childCount: el.children.length,
    });
  });

  return sections;
};
JSON.stringify(mapLayout(), null, 2);
```

### 1d. Extract all images

```javascript
// Get every image with context
const getImages = () => {
  const imgs = [];
  document.querySelectorAll('img').forEach(img => {
    const rect = img.getBoundingClientRect();
    imgs.push({
      src: img.src,
      alt: img.alt,
      width: rect.width,
      height: rect.height,
      naturalWidth: img.naturalWidth,
      naturalHeight: img.naturalHeight,
      classList: [...img.classList].join(' '),
      parentTag: img.parentElement?.tagName,
      parentClass: [...(img.parentElement?.classList || [])].join(' '),
    });
  });

  // Also find background images
  const bgImgs = [];
  document.querySelectorAll('*').forEach(el => {
    const bg = window.getComputedStyle(el).backgroundImage;
    if (bg && bg !== 'none' && bg.includes('url(')) {
      bgImgs.push({
        element: el.tagName.toLowerCase(),
        class: [...el.classList].join(' '),
        backgroundImage: bg,
        width: el.offsetWidth,
        height: el.offsetHeight,
      });
    }
  });

  return { imgs, bgImgs };
};
JSON.stringify(getImages(), null, 2);
```

### 1e. Extract all text content by section

```javascript
// Structured text extraction
const getText = () => {
  const nav = document.querySelector('nav') || document.querySelector('header');
  const footer = document.querySelector('footer');
  const main = document.querySelector('main') || document.body;

  return {
    title: document.title,
    metaDescription: document.querySelector('meta[name="description"]')?.content,
    nav: nav ? [...nav.querySelectorAll('a')].map(a => ({ text: a.innerText.trim(), href: a.href })) : [],
    headings: [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(h => ({
      level: h.tagName,
      text: h.innerText.trim(),
    })),
    ctaButtons: [...document.querySelectorAll('button, [class*="btn"], [class*="cta"], a[class*="button"]')].map(b => b.innerText.trim()),
    footer: footer ? footer.innerText.slice(0, 1000) : null,
    allText: main.innerText.slice(0, 5000),
  };
};
JSON.stringify(getText(), null, 2);
```

### 1f. Extract SVG icons and inline SVGs

```javascript
const getSVGs = () => {
  const svgs = [];
  document.querySelectorAll('svg').forEach(svg => {
    svgs.push({
      outerHTML: svg.outerHTML.slice(0, 2000),
      width: svg.getAttribute('width') || svg.clientWidth,
      height: svg.getAttribute('height') || svg.clientHeight,
      parentClass: [...(svg.parentElement?.classList || [])].join(' '),
    });
  });
  return svgs;
};
JSON.stringify(getSVGs(), null, 2);
```

### 1g. Crawl additional pages

After extracting the homepage, navigate to each page linked from the main nav and repeat the screenshot + layout extraction. Minimum: all pages listed in the nav. Use `browser_navigate` for each.

### 1h. Extract CSS source files (if accessible)

```javascript
// Get all linked stylesheets
[...document.styleSheets].map(ss => {
  try { return { href: ss.href, rules: ss.cssRules.length }; }
  catch(e) { return { href: ss.href, blocked: true }; }
});
```

If any stylesheets are accessible (same-origin or CORS-open), fetch them with `browser_navigate` to read the raw CSS — this reveals CSS custom properties, media queries, and keyframe animations.

---

## Step 2: Reverse Brand Guide

From the extraction data, build a complete **Reverse Brand Guide**. This replaces the invented brand guide in web-design — everything here is derived from what you measured.

Format it as:

```
## Reverse Brand Guide: {site name}

### Brand Identity
- Site name:
- Tagline:
- Category: (SaaS / Agency / E-commerce / Portfolio / etc.)

### Color System
- Background: {hex}           (from body background)
- Surface: {hex}              (from card/panel backgrounds)
- Primary brand: {hex}        (main CTA / accent)
- Secondary: {hex}
- Text primary: {hex}
- Text secondary: {hex}
- Text muted: {hex}
- Border: {hex}
- Success/Error colors if present

### Typography
- Display font: {family} — used for: {h1, h2, hero text}
- Body font: {family} — used for: {p, nav, body}
- Mono font: {family} (if present)
- H1: {size} / {weight} / {line-height} / {letter-spacing}
- H2: {size} / {weight} / {line-height} / {letter-spacing}
- H3: {size} / {weight} / {line-height}
- Body: {size} / {weight} / {line-height}
- Small/Caption: {size}
- Button: {size} / {weight} / {text-transform}

### Spacing & Shape
- Container max-width: {value}
- Container padding: {value}
- Section padding (vertical): {value}
- Card border-radius: {value}
- Button border-radius: {value}
- Standard border-radius: {value}

### Effects
- Primary shadow: {box-shadow value}
- Card shadow: {box-shadow value}
- Button hover: {transition / transform}
- Focus ring: {outline style}

### Component Inventory
List every distinct component type seen:
- Nav: {sticky/fixed/static, transparent/solid, hamburger on mobile}
- Hero: {layout, background treatment, CTA count}
- Feature sections: {grid cols, card style}
- Testimonials: {layout style}
- CTA sections: {background, button style}
- Footer: {column count, content breakdown}
- Any unique/unusual components

### Animation & Motion
- Scroll animations: {yes/no, type if yes}
- Hover transitions: {duration, properties}
- Page load animations: {yes/no, type}

### Image Style
- Photography vs illustration vs abstract
- Color treatment (warm, cool, high-contrast, muted, dark overlay)
- Aspect ratios used
- Image count per section type

### Page List
- / (home)
- /about
- /services or /products
- etc.
```

---

## Step 3: Asset Acquisition

For each image identified in extraction:

1. **Downloadable originals** — if the image URL is a CDN (Cloudinary, imgix, Unsplash, etc.), use WebFetch to download it directly. Save to `workspace/{project-name}/public/images/`.

2. **Stock photo replacements** — if images are proprietary/locked, find visually similar replacements:
   - Search Unsplash API: `https://unsplash.com/s/photos/{descriptive-query}`
   - Search Pexels: `https://www.pexels.com/search/{descriptive-query}/`
   - Match: subject matter, color temperature, composition style, aspect ratio

3. **Generated images** — if no stock match is close enough, use the image generation tool with a prompt that captures: subject, style (photorealistic/illustration/abstract), color palette, mood, composition.

4. **SVG icons** — copy inline SVG source from extraction. For icon sets (Heroicons, Lucide, etc.), identify the set by the SVG paths and use the matching library.

5. **Video/media** — if the original has hero videos or background videos:
   - Check if the video URL is directly accessible (fetch it)
   - If not, source a similar free stock video from a search
   - Note: video embedding is always from `<video>` tag with `autoplay muted loop playsInline`

Build an **Asset Manifest** before coding:
```
## Asset Manifest

### Images
| Asset | Original URL | Local Path | Source Method |
|-------|-------------|------------|---------------|
| Hero background | cdn.example.com/hero.jpg | /images/hero.jpg | downloaded |
| Team photo | proprietary | /images/team.jpg | Unsplash match |
| Feature icon 1 | inline SVG | component | copied SVG |

### Fonts
| Font | Source | Import Method |
|------|--------|---------------|
| Inter | Google Fonts | next/font/google |
| Neue Haas | Custom | local font file |
```

---

## Step 4: Scaffold & Configure

Same as web-design Step 5, but configured to match the extracted design system:

```bash
cd workspace
npx create-next-app@latest {project-name}-clone --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
```

### Configure Tailwind to match extracted tokens

Update `tailwind.config.ts` with the exact values from the reverse brand guide:

```typescript
// tailwind.config.ts — values must match reverse brand guide exactly
theme: {
  extend: {
    colors: {
      background: 'hsl(var(--background))',
      surface: 'hsl(var(--surface))',
      primary: 'hsl(var(--primary))',
      // ... all brand colors as CSS var references
    },
    fontFamily: {
      display: ['var(--font-display)', ...fontFallbacks],
      body: ['var(--font-body)', ...fontFallbacks],
    },
    fontSize: {
      // Extracted sizes mapped to semantic names
    },
    borderRadius: {
      // Extracted radius values
    },
    boxShadow: {
      // Extracted shadow values
    },
    maxWidth: {
      container: '{extracted container max-width}',
    },
  }
}
```

Set CSS custom properties in `globals.css`:

```css
:root {
  /* Exact values from extraction */
  --background: {h s l};
  --surface: {h s l};
  --primary: {h s l};
  --text-primary: {h s l};
  /* etc. */

  --font-display: '{display font name}';
  --font-body: '{body font name}';

  --radius-card: {value};
  --radius-button: {value};

  --shadow-card: {value};
  --shadow-primary: {value};

  --container-max: {value};
  --section-padding: {value};
}
```

---

## Step 5: Build the Clone

Follow the web-design skill's Step 6 component hierarchy, but every decision is dictated by the reverse brand guide — no creative choices.

### Fidelity checklist per component:

**Navigation:**
- [ ] Same logo position (left/center)
- [ ] Same nav link count and labels
- [ ] Same sticky/fixed behavior
- [ ] Same mobile breakpoint behavior
- [ ] Exact background + border treatment

**Hero:**
- [ ] Same layout (centered / split / fullscreen / asymmetric)
- [ ] Same heading hierarchy and approximate copy
- [ ] Same CTA button count, position, and style
- [ ] Same background (image / gradient / video / solid)
- [ ] Same vertical padding

**Every section:**
- [ ] Same number of columns in grids
- [ ] Same card style (bordered / shadowed / flat)
- [ ] Same section background treatment
- [ ] Same content density
- [ ] Same heading → body → CTA structure

**Footer:**
- [ ] Same column count
- [ ] Same link groupings
- [ ] Same background color
- [ ] Same social icon set

### Copy fidelity:
- Use the exact text extracted where it fits (headings, nav items, button labels, footer)
- For longer body copy, paraphrase to match the tone and length precisely
- Keep all heading text identical unless it contains a proper business name you want to replace

---

## Step 6: Playwright Visual QA Loop

This is the critical differentiator. Do not skip this. Repeat until screenshots match.

### Launch local dev server

```bash
cd workspace/{project-name}-clone && npm run dev
```

The dev server runs at `http://localhost:3000`.

### QA comparison protocol

For each page:

1. **Screenshot original** at 1440px: navigate to the original URL, `browser_screenshot`
2. **Screenshot clone** at 1440px: navigate to `localhost:3000`, `browser_screenshot`
3. **Compare section by section** — look for discrepancies in:
   - Header height and logo treatment
   - Hero section: text size, alignment, CTA styling, background
   - Each feature/content section: grid layout, card styling, spacing
   - Color accuracy: backgrounds, text, buttons
   - Typography: weight, size, spacing
   - Footer: column layout, colors
4. **List every discrepancy** with specificity:
   ```
   Discrepancies found:
   - Hero heading: 72px on original, ~60px on clone → fix
   - CTA button: original has no border-radius (sharp corners), clone has rounded → fix
   - Feature section: 3 columns on original, 2 on clone → fix
   - Background: original hero is dark navy (#0A0F1E), clone is wrong shade → fix
   - Nav: original is transparent on scroll, clone is always solid → fix
   ```

5. **Fix all discrepancies** — edit the relevant components
6. **Re-screenshot and compare again**
7. **Repeat** until you find no visible differences

### Mobile QA (375px viewport)

Repeat the same process at 375px. Common mobile discrepancies:
- Font sizes not scaling down
- Sections not stacking properly
- Nav hamburger not styled correctly
- Images not resizing

### QA pass criteria

Consider the clone complete when:
- [ ] Color palette: all backgrounds, text colors, and accent colors match within ~5% perceived difference
- [ ] Typography: font families, approximate sizes, and weights all match
- [ ] Layout: section structure and grid columns match on both desktop and mobile
- [ ] Components: every nav item, button, card, and footer element is present
- [ ] Spacing: section padding and component spacing is visually equivalent
- [ ] Images: every image position has a visual asset (same aspect ratio, similar subject/style)

---

## Step 7: Final Polish

After QA passes:

1. **Metadata** — set page `<title>`, `<meta description>` to match the original
2. **Favicon** — if the original favicon is accessible, download and use it. Otherwise use `browser_screenshot` to grab just the favicon area and recreate as SVG.
3. **Responsive check at 1024px** — a commonly missed breakpoint
4. **Hover states** — verify all interactive hover styles match (button hover colors, nav link underlines, card hover effects)
5. **Scroll behavior** — check if original has smooth scroll, sticky nav changes, or scroll-triggered animations. Implement with CSS `scroll-behavior: smooth` and Intersection Observer if needed.
6. **Loading performance** — ensure all images use `next/image` with correct `sizes` props

---

## Reference: Quick JS Snippets for Common Extractions

```javascript
// Get exact body background
window.getComputedStyle(document.body).backgroundColor

// Get all Google Font links
[...document.querySelectorAll('link[href*="fonts.googleapis.com"]')].map(l => l.href)

// Get all CSS custom properties defined on :root
const root = document.documentElement;
const styles = window.getComputedStyle(root);
[...document.styleSheets].flatMap(ss => {
  try {
    return [...ss.cssRules]
      .filter(r => r.selectorText === ':root')
      .flatMap(r => r.cssText.match(/--[\w-]+:\s*[^;]+/g) || []);
  } catch(e) { return []; }
});

// Get exact hero section dimensions and styles
const hero = document.querySelector('[class*="hero"], [id*="hero"], header + section, main > section:first-child');
if (hero) {
  const cs = window.getComputedStyle(hero);
  JSON.stringify({
    height: hero.offsetHeight,
    background: cs.background,
    backgroundImage: cs.backgroundImage,
    paddingTop: cs.paddingTop,
    paddingBottom: cs.paddingBottom,
  });
}

// Check for scroll-based nav behavior
// Look for classList changes on scroll in the original site's JS
window.onscroll = null; // Then check event listeners on nav/header

// Get all animation keyframes
[...document.styleSheets].flatMap(ss => {
  try {
    return [...ss.cssRules]
      .filter(r => r instanceof CSSKeyframesRule)
      .map(r => r.cssText.slice(0, 500));
  } catch(e) { return []; }
});
```

---

## Notes on Specific Site Types

**Sites with auth walls / paywalls:** Extract as much as visible without logging in. Note what sections are gated.

**SPAs with client-side rendering:** Wait for the page to fully load before extracting. Use `browser_evaluate` with a delay: `await new Promise(r => setTimeout(r, 2000)); return extract();`

**Sites with lazy-loaded images:** Scroll to the bottom first to trigger all lazy loads before extracting image sources.

**Video backgrounds:** Check if the `<video>` src is accessible. Try downloading it. If blocked, source equivalent stock footage.

**Custom fonts (not Google):** Check if the font files are hosted on the site's CDN and accessible. If so, download the .woff2 files and use `next/font/local`. If blocked, find the closest Google Font equivalent.

**Dark mode sites:** Extract both light and dark mode values if `prefers-color-scheme` is implemented. Check for a theme toggle button.
