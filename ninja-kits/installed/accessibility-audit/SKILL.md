---
name: accessibility-audit
description: WCAG 2.1/2.2 accessibility audit for Next.js websites. Scans components, pages, and global styles for violations across perceivability, operability, understandability, and robustness. Produces a prioritized fix list scored by severity (Critical/High/Medium/Low). Use when the user says "accessibility audit", "a11y audit", "wcag check", "audit accessibility", "check accessibility", "fix a11y", "screen reader", "keyboard navigation", or "accessibility review".
---

# Accessibility Audit Skill

Audit a Next.js website for WCAG 2.1/2.2 compliance. Produce a scored report with every violation, its severity, the affected file/component, and an exact fix.

**Never produce a surface-level report.** Read every component. Every violation gets a file path, line reference, and a concrete code fix.

---

## Workflow Overview

1. **Inventory** — map all pages, components, and global styles
2. **Static Audit** — read every file and flag violations by category
3. **Contrast Audit** — check color pairs from the brand/CSS system
4. **Interaction Audit** — check keyboard, focus, and ARIA patterns
5. **Scoring** — tally issues, assign severity, produce a report
6. **Fix** — apply all fixes unless the user asks for report-only

---

## Step 1: Inventory

Glob the project to build a complete component map:

```
src/app/**/*.tsx
src/components/**/*.tsx
src/app/globals.css
tailwind.config.*
lib/config.*
```

List every file you'll audit. Note which are:
- Page-level (app router pages)
- Layout files (`layout.tsx`)
- Section components (Hero, Nav, Footer, Forms)
- UI atoms (Button, Input, Modal, Badge)

---

## Step 2: Static Audit

Read every file. Check each category below. For every violation, record:

```
| Severity | File | Line | Rule | Description | Fix |
```

### 2a. Semantic HTML

- `<div>` or `<span>` used as interactive elements (clickable divs, anchor-less links)
- Missing landmark regions: `<header>`, `<main>`, `<nav>`, `<footer>`, `<aside>`
- Heading hierarchy skipped (e.g., h1 → h3, missing h2)
- `<section>` and `<article>` without accessible names (`aria-label` or `aria-labelledby`)
- Lists rendered as `<div>` chains instead of `<ul>/<ol>/<li>`
- `<table>` missing `<caption>`, `<th scope>`, or `<thead>`
- Forms with `<input>` not associated to a `<label>` (either wrapping or `htmlFor`/`id`)
- `<button>` inside `<a>` or vice versa (interactive element nesting)

### 2b. Images and Media

- `<img>` or `next/image` missing `alt` prop
- `alt=""` used on non-decorative images (should be descriptive)
- Decorative images missing `alt=""` (should be empty, not absent)
- `<video>` missing `<track kind="captions">`
- CSS background images that convey meaning (should be `<img>` with alt)
- Icon-only buttons with no `aria-label` or visually hidden text

### 2c. Color and Typography

Flag for manual contrast check (Step 3):
- Every text/background color pair from CSS variables or Tailwind classes
- Placeholder text color vs input background
- Disabled state text vs background
- Link color vs surrounding text (distinguish without relying on color alone?)
- Focus ring color vs page background

Typography issues to flag statically:
- Font size below `16px` / `1rem` for body text
- Line height below `1.4` for paragraph text
- Letter spacing manipulated in ways that hinder readability

### 2d. Interactive Elements

- `<a>` tags with no `href` (use `<button>` instead)
- `<a>` tags with `href="#"` and no keyboard/click handler
- `onClick` on non-interactive elements without `role`, `tabIndex`, and keyboard handler
- Missing `onKeyDown`/`onKeyUp` paired with `onClick` for custom interactive components
- `tabIndex > 0` (breaks natural tab order)
- `tabIndex="-1"` on elements that should be focusable
- Modals/dialogs missing focus trap
- Dropdown menus without arrow-key navigation pattern

### 2e. ARIA Usage

- `aria-label` on a non-interactive element that already has visible text (redundant/conflicting)
- `aria-hidden="true"` on focusable elements
- `role="button"` without `tabIndex="0"` and keyboard handlers
- `aria-expanded`, `aria-haspopup`, `aria-controls` missing on toggle controls (menus, accordions)
- `aria-live` regions absent where dynamic content updates occur (toasts, form errors, loading states)
- `aria-describedby` pointing to an element that doesn't exist in DOM
- `aria-required` on form fields vs HTML `required` attribute (use both)

### 2f. Focus Management

- No visible focus indicator (check for `outline: none` / `focus:outline-none` without replacement)
- Focus not moved to modal/dialog on open
- Focus not returned to trigger element on modal close
- Skip navigation link absent (`<a href="#main-content" className="sr-only focus:not-sr-only">Skip to content</a>`)
- Animated elements that don't respect `prefers-reduced-motion`

### 2g. Page-level

- `<html>` missing `lang` attribute in `layout.tsx`
- `<title>` missing or generic ("Untitled" / same on every page)
- `<meta name="viewport">` with `user-scalable=no` (prevents zoom)
- Page without a single `<h1>`
- Multiple `<h1>` tags on one page

---

## Step 3: Contrast Audit

Extract all color pairs from CSS variables, Tailwind config, and `globals.css`.

For each pair compute the WCAG contrast ratio:

**Formula:**
```
L1 = relative luminance of lighter color
L2 = relative luminance of darker color
Ratio = (L1 + 0.05) / (L2 + 0.05)
```

**Thresholds:**
| Text Type | WCAG AA | WCAG AAA |
|---|---|---|
| Normal text (< 18pt / < 14pt bold) | 4.5:1 | 7:1 |
| Large text (≥ 18pt or ≥ 14pt bold) | 3:1 | 4.5:1 |
| UI components / graphical objects | 3:1 | — |
| Placeholder text | 4.5:1 | — |

Flag every pair that fails AA. Note which also fail AAA as a Medium priority item.

**Color pairs to always check:**
- Body text on page background
- Heading text on page background
- Link color on page background
- Button label on button background (default, hover, disabled states)
- Input text on input background
- Placeholder text on input background
- Badge/tag text on badge background
- Muted/secondary text on its background
- Focus ring on adjacent background

---

## Step 4: Interaction Audit

Beyond static analysis, simulate user flows:

### Keyboard Navigation Checklist
- [ ] Can all interactive elements be reached with Tab?
- [ ] Is Tab order logical (matches visual reading order)?
- [ ] Can menus/dropdowns be operated with arrow keys?
- [ ] Can modals be dismissed with Escape?
- [ ] Are carousels/sliders keyboard-operable?
- [ ] Can forms be submitted with Enter?
- [ ] Are date pickers or custom selects keyboard-accessible?

### Screen Reader Checklist
- [ ] Does every page have a meaningful `<title>`?
- [ ] Are form errors announced via `aria-live` or `aria-describedby`?
- [ ] Are loading states announced?
- [ ] Do icon-only controls have accessible names?
- [ ] Is the skip-to-content link present and functional?
- [ ] Are decorative images hidden from screen readers?

---

## Step 5: Scoring and Report

### Severity Definitions

| Severity | Definition | Examples |
|---|---|---|
| **Critical** | Completely blocks a user from completing a task | Missing form labels, no keyboard access to CTA, inaccessible modal |
| **High** | Significantly impairs usability for assistive tech users | Low contrast on body text, missing alt on informational image, broken focus trap |
| **Medium** | Creates friction or fails WCAG AA in a secondary context | Low contrast on muted text, missing landmark regions, redundant ARIA |
| **Low** | Best-practice violation, fails WCAG AAA, or minor friction | Missing AAA contrast, non-ideal heading structure, missing `<caption>` on data table |

### Report Format

Output the full report in this structure:

```markdown
# Accessibility Audit Report
**Project:** {project-name}
**Date:** {date}
**WCAG Standard:** 2.1 AA
**Overall Score:** {score}/100

## Summary
| Severity | Count |
|---|---|
| Critical | N |
| High | N |
| Medium | N |
| Low | N |

## Critical Issues
### [C1] {Issue title}
- **File:** `src/components/Nav.tsx:42`
- **Rule:** WCAG 2.1 — 4.1.2 Name, Role, Value
- **Problem:** Icon-only hamburger button has no accessible name.
- **Fix:**
  ```tsx
  // Before
  <button onClick={toggle}><MenuIcon /></button>

  // After
  <button onClick={toggle} aria-label="Open navigation menu">
    <MenuIcon aria-hidden="true" />
  </button>
  ```

## High Issues
...

## Medium Issues
...

## Low Issues
...

## Contrast Audit Results
| Pair | Ratio | AA Normal | AA Large | Status |
|---|---|---|---|---|
| Body text (#1a1a1a) on bg (#ffffff) | 19.1:1 | PASS | PASS | ✓ |
| Muted text (#9ca3af) on bg (#ffffff) | 2.85:1 | FAIL | PASS | ✗ |

## Keyboard Navigation Results
...

## Screen Reader Results
...

## Recommended Fix Order
1. [Critical] Fix all missing form labels → {files}
2. [Critical] Add skip-to-content link → layout.tsx
3. [High] Fix contrast on muted text → globals.css
...
```

### Scoring Formula

Start at 100. Deduct:
- Critical: −15 per issue (floor at 0)
- High: −8 per issue
- Medium: −3 per issue
- Low: −1 per issue

Score bands:
- **90–100** — Excellent (WCAG AA compliant)
- **75–89** — Good (minor issues)
- **50–74** — Needs Work (failing AA on key flows)
- **0–49** — Poor (critical barriers present)

---

## Step 6: Fix

Unless the user requests **report-only**, apply all Critical and High fixes immediately after the report.

For each fix:
1. Read the full file first
2. Apply the minimal change that resolves the violation
3. Do not refactor surrounding code
4. Mark the issue as fixed in the report

After fixing, re-check the specific lines to confirm the violation is resolved.

**Do not apply Medium/Low fixes without asking** — these often involve design decisions (color changes, restructuring) that require user input.

---

## Rules

- Read every file. Never audit from memory or assumptions.
- Every violation needs a file path + line number. "Check your buttons" is not a finding.
- Contrast ratios must be calculated, not guessed.
- ARIA is last resort — fix the HTML structure first, add ARIA only when native semantics are insufficient.
- Never add `aria-label` where visible text already provides the name.
- `tabIndex > 0` is almost always wrong — flag it.
- `outline: none` without a visible replacement is always a Critical.
- Respect `prefers-reduced-motion` — flag every animation that ignores it.
