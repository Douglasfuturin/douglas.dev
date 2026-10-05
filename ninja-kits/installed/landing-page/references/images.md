# Image Strategy

The page must never load with a broken `src` or a placeholder gray box. Every image — even the fake ones — must be rendered before you ship.

## The hierarchy: real → AI → stock → "obvious demo"

1. **Real client assets** — if the user/client supplies real photos, testimonial avatars, screenshots, logos: use those. Always preferred.
2. **AI-generated photorealistic** — for testimonial avatars, founder portraits, hero imagery. Use Nano Banana / Imagen / similar.
3. **Stock + edited** — for hero backgrounds, abstract visuals, generic objects. Pexels/Unsplash + small edits.
4. **"Obvious demo" placeholders** — when you can't get a real or believable image, render an explicitly-fake one with a "DEMO" / "EXAMPLE" badge. Never pretend.

Rule: **a clearly-fake image with a "DEMO" badge is more honest than a stock photo that's trying to look real.** Visitors detect generic stock photos instantly and lose trust.

## What images to plan (every landing page)

A direct-response landing page typically needs all of these. Plan the manifest before building.

| Slot | Purpose | Strategy |
|------|---------|----------|
| Hero asset | VSL poster OR product mockup OR founder portrait | Real if possible; else AI-generated photorealistic |
| Founder portrait | Authority + liking | Always real — must match the actual founder. If unknown, use AI-generated headshot with explicit "Demo founder" note in dev comments |
| Logo wall (5-12 logos) | Social proof | Real client logos if disclosed; else generate "Demo brand" SVG monograms (e.g. Acme, Apex, Vertex) clearly labeled |
| Testimonial avatars (4-8) | Social proof | Real if supplied; else AI-generated portraits with diversity, all marked "Demo testimonial" in alt text |
| Results screenshots (2-4) | Specificity + proof | Generate fake Stripe / dashboard / calendar / DM screenshot with believable numbers; add small "Example" watermark |
| Chart / graph (1-2) | Authority + data | Use real data if disclosed; else inline SVG chart with "Sample data" label |
| Trust badges (Trustpilot/G2) | Authority | Only if the client genuinely has the rating. Otherwise SKIP — fake badges destroy trust. |
| Before/after | Pain agitation + outcome | Same as results screenshots — fake but specific |
| Bonus stack mockups | Offer | Render fake ebook/course covers, bonus-bundle stacks. Always label "Illustration" |
| OG / social share image | Sharing | 1200x630, brand-color background, headline overlay |

## AI image generation prompts (drop-in)

### Testimonial avatar (professional headshot)
> "Professional studio headshot of [age range, gender, ethnicity if relevant], natural smile, looking slightly off-camera, soft window light, neutral grey background, sharp focus on eyes, 50mm lens. Realistic photograph, not stylized."

Vary specifics per testimonial so the set looks like real different people, not 4 versions of the same prompt.

### Founder portrait
> "Confident professional portrait of [role: founder/CEO/coach], natural lighting, modern office background slightly blurred, looking directly at camera, warm but serious expression, 35mm lens, photorealistic."

### Results screenshot (Stripe-style)
> "Photorealistic screenshot of a Stripe payments dashboard showing daily revenue $4,837 with a 30-day chart trending upward. White interface, Stripe brand colors (purple accent), sharp typography, 1440x900 resolution."

Add a small `<span class="demo-watermark">EXAMPLE</span>` overlay before shipping.

### Slack-message proof screenshot (Client Ascension signature)
> "Photorealistic screenshot of a Slack DM thread on dark mode. Username 'sarah.k' with avatar, timestamp '2:47 PM', message reads: 'just closed my 3rd $5K retainer this week 🔥 the cold outreach script you gave me is unreal — wasn't expecting this in week 2'. Show the Slack UI chrome (sidebar partially visible, reaction emoji on the message). 1200x600px."

Slack-message screenshots are higher-trust than testimonial cards on dark/premium pages because they feel like organic chat traffic, not curated marketing. Client Ascension uses these as their entire social-proof stack — no Forbes logos, no glossy stock photos, just 20+ Slack screenshots. Generate with realistic-but-clearly-not-real usernames + the "DEMO" badge.

### Bonus stack mockup
> "3D render of [ebook / course bundle / planner], floating on transparent background, soft drop shadow, matte cover with [brand color] accent, isometric angle, studio lighting."

## The "Demo" badge

When you ship clearly-fake imagery, add a small visible badge. This is the trust play — visitors who notice respect the honesty, and the page still looks complete.

```html
<img src="testimonial-avatar-1.jpg" alt="Sarah K., demo testimonial" />
<span class="demo-badge">DEMO</span>
```

```css
.demo-badge {
  position: absolute;
  top: 8px;
  right: 8px;
  font-size: 10px;
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 3px 6px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  border-radius: 4px;
  text-transform: uppercase;
}
```

For results screenshots, use a diagonal watermark:

```css
.example-watermark::after {
  content: "EXAMPLE";
  position: absolute;
  inset: 0;
  display: grid;
  place-content: center;
  font-size: 48px;
  font-weight: 700;
  color: rgba(0, 0, 0, 0.08);
  transform: rotate(-15deg);
  pointer-events: none;
}
```

## Trust badges — only if real

Trustpilot, G2, Capterra, BBB ratings: only show them if the client actually has them. A real client landing page should pull the badge directly from the source. Fake trust badges are a trust killer the second a visitor clicks through.

If the client doesn't have ratings yet, replace the trust strip with named press logos, founder credential bar, or quantified result ("$47M in client revenue generated").

## Logo wall (client logos)

If real client logos available: use them at consistent height (typically 32-48px tall), grayscale or single-color, on a neutral background, with consistent spacing.

If generating fake logos for a demo:
- Use brand-monogram SVGs (1-2 letters + a simple geometric mark)
- 6-12 logos, varied shapes and sizes
- Label the row "Demo client brands" or include a footnote: "Logos shown for illustration"

Never use real Fortune 500 logos as fake client proof — that's fraud.

## Photography style guidance (for AI generation)

Direct-response pages need a specific photo aesthetic. Avoid the "diverse business people pointing at laptop" stock-photo trap.

**Good direction:**
- Real-feeling candid moments, not posed
- Single subject, clear focal point
- Natural light, not harsh studio
- Office or home-office settings — not abstract gradient backgrounds
- Subjects looking off-camera or down at work, not straight at lens

**Bad direction:**
- Anything that screams "stock photo" — handshakes, fist bumps, group laughter at a meeting
- Hyper-glossy 3D renders for the founder section
- Cartoon illustrations for testimonials
- Generic "businessperson with arms crossed"

## Chart / data viz

For results-related charts, generate inline SVG (not images). Easier to tweak, scales perfectly, and you can label the data.

```html
<figure class="results-chart">
  <svg viewBox="0 0 400 200">
    <!-- bars / line / area chart with realistic numbers -->
  </svg>
  <figcaption>MRR growth over 90 days — example data</figcaption>
</figure>
```

Always label the figcaption. Always include "example data" if the data isn't from a real client.

## VSL poster

If the page has a VSL, the poster is the highest-leverage image on the page. It must:
- Show the founder (face = liking + authority)
- Have a play button overlay
- Optionally have a single line of text ("Watch how we get 30 calls/month — 4:37")
- Be 1280x720 or 1920x1080
- Be lightweight (< 200KB) — preload it

When the user supplies a VSL, ALWAYS extract a poster frame. Don't ship an embedded video without a poster.

## Pre-flight image checklist

Before shipping:
- [ ] Every `<img>` has a real `src` that loads
- [ ] Every `<img>` has an `alt` attribute with meaningful text
- [ ] No image is over 500KB (compress)
- [ ] Hero image is in WebP or AVIF with JPEG fallback
- [ ] Demo/example badges are visible on any non-real imagery
- [ ] No real Fortune 500 logos used as fake client proof
- [ ] No real-person photos used without permission
