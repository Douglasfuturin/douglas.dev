#!/usr/bin/env python3
"""
render_deck.py, turn a config.json deck spec into a finished deck.html.

Pipeline:
  1. Parse config.json (deck metadata + per-slide pattern/content/visual)
  2. For slides with a `visual` (or `visuals`) block, generate images via the
     brand-image generator (Gemini Nano Banana Pro)
  3. Render each slide to HTML using the template's pattern classes
  4. Inject all slides between the BEGIN-SLIDES / END-SLIDES markers in
     templates/deck-template.html
  5. Write the finished, self-contained deck.html

Usage:
  python3 render_deck.py --config example-config.json
  python3 render_deck.py --config example-config.json --skip-images
  python3 render_deck.py --config example-config.json --regenerate-images

Run from the marketing template root so relative output paths resolve sensibly.
"""

import argparse
import html
import json
import re
import sys
from pathlib import Path

# Slide numbers whose image generation failed during this run.
_IMAGE_FAILURES = set()

# ---- locate sibling skills -------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent                       # .../skills/webinar-deck
SKILLS_ROOT = SKILL_DIR.parent                      # .../skills
TEMPLATE_PATH = SKILL_DIR / "templates" / "deck-template.html"

# brand-image owns image generation, import its generator
sys.path.insert(0, str(SKILLS_ROOT / "brand-image" / "scripts"))
try:
    from generate_image import generate_image
    _HAS_GENERATOR = True
except ImportError:
    _HAS_GENERATOR = False


# ---- helpers ---------------------------------------------------------------
def esc(s):
    """HTML-escape a plain string."""
    return html.escape(str(s) if s is not None else "", quote=True)


def accent(s):
    """Allow <accent>...</accent> and <arrow>...</arrow> inline markup.

    Everything outside those tags is assumed already safe (caller controls it).
    """
    s = s or ""
    s = re.sub(r"<accent>(.*?)</accent>", r'<span class="accent">\1</span>', s)
    s = re.sub(r"<arrow>(.*?)</arrow>", r'<span class="arrow">\1</span>', s)
    return s


def _section(pattern, inner):
    return f'    <section class="slide pattern-{pattern}">\n{inner}\n    </section>'


# ---- per-pattern renderers -------------------------------------------------
# Each renderer takes (content: dict, srcs: list[str]) and returns HTML.

def r_title(c, s):
    # The title slide is the descriptive headline (the promise) + meta.
    # No separate short brand title.
    parts = []
    if c.get("meta_main"):
        parts.append(esc(c["meta_main"]))
    if c.get("meta_accent"):
        parts.append(f'<span class="accent">{esc(c["meta_accent"])}</span>')
    if c.get("meta_secondary"):
        parts.append(esc(c["meta_secondary"]))
    meta = " &middot; ".join(parts)
    title_html = accent(c["title_html"]) if c.get("title_html") else esc(c.get("title", ""))
    meta_div = f'\n      <div class="deck-meta">{meta}</div>' if meta else ""
    return _section("title",
        f'      <div class="deck-title">{title_html}</div>{meta_div}')


def _r_text(pattern):
    def render(c, s):
        text = accent(c["text_html"]) if "text_html" in c else esc(c.get("text", ""))
        return _section(pattern, f'      <div class="text">{text}</div>')
    return render


def r_three_lines(c, s):
    rows = []
    for i, line in enumerate(c.get("lines", []), 1):
        if isinstance(line, dict):
            num, text = line.get("number", f"{i}."), esc(line.get("text", ""))
        else:
            num, text = f"{i}.", esc(line)
        rows.append(f'        <div class="line"><span class="line-number">{esc(num)}</span>{text}</div>')
    return _section("three-lines", '      <div class="lines">\n' + "\n".join(rows) + '\n      </div>')


def r_permission(c, s):
    hint = f'\n      <div class="hint">{esc(c["hint"])}</div>' if c.get("hint") else ""
    return _section("permission", f'      <div class="question">{esc(c.get("question",""))}</div>{hint}')


def r_instruction(c, s):
    reason = f'\n      <div class="reason">{esc(c["reason"])}</div>' if c.get("reason") else ""
    return _section("instruction", f'      <div class="action">{esc(c.get("action",""))}</div>{reason}')


def _r_proof(pattern):
    def render(c, s):
        return _section(pattern,
            f'      <div class="number">{esc(c.get("number",""))}</div>\n'
            f'      <div class="label">{esc(c.get("label",""))}</div>')
    return render


def r_case_study_headline(c, s):
    return _section("case-study-headline",
        f'      <div class="headline">{accent(c.get("headline_html", esc(c.get("headline",""))))}</div>')


def r_photo_full(c, s):
    src = esc(s[0] if s else c.get("src", ""))
    return _section("photo-full", f'      <img class="photo" src="{src}" alt="" />')


def r_photo_text_overlay(c, s):
    src = esc(s[0] if s else c.get("src", ""))
    return _section("photo-text-overlay",
        f'      <img class="photo" src="{src}" alt="" />\n'
        f'      <div class="overlay">{esc(c.get("overlay_text",""))}</div>')


def r_image_split(c, s):
    src = esc(s[0] if s else c.get("src", ""))
    return _section("image-split",
        f'      <div class="split-image"><img src="{src}" alt="" /></div>\n'
        f'      <div class="split-content">\n'
        f'        <div class="title">{esc(c.get("title",""))}</div>\n'
        f'        <div class="body">{esc(c.get("body",""))}</div>\n'
        f'      </div>')


def r_image_hero(c, s):
    src = esc(s[0] if s else c.get("src", ""))
    caption = f'\n      <div class="caption">{esc(c["caption"])}</div>' if c.get("caption") else ""
    return _section("image-hero",
        f'      <div class="image-container"><img src="{src}" alt="" /></div>{caption}')


def r_image_mosaic_above(c, s):
    imgs = s if s else c.get("srcs", [])
    items = "\n".join(
        f'        <img class="mosaic-item" src="{esc(src)}" alt="" />' for src in imgs)
    sub = f'\n      <div class="subtitle">{esc(c["subtitle"])}</div>' if c.get("subtitle") else ""
    return _section("image-mosaic-above",
        f'      <div class="mosaic">\n{items}\n      </div>\n'
        f'      <div class="title">{accent(c.get("title_html", esc(c.get("title",""))))}</div>{sub}')


def r_logo_wall(c, s):
    logos = s if s else c.get("logos", [])
    items = "\n".join(f'        <img class="logo" src="{esc(l)}" alt="" />' for l in logos)
    return _section("logo-wall", f'      <div class="logos">\n{items}\n      </div>')


def r_agenda(c, s):
    items = "\n".join(
        f'        <div class="item"><span class="item-number">{i}.</span>{esc(it)}</div>'
        for i, it in enumerate(c.get("items", []), 1))
    return _section("agenda", f'      <div class="items">\n{items}\n      </div>')


def r_bridge(c, s):
    return _section("bridge", f'      <div class="text">{esc(c.get("text",""))}</div>')


def r_big_claim(c, s):
    return _section("big-claim",
        f'      <div class="claim">{accent(c.get("claim_html", esc(c.get("claim",""))))}</div>')


def r_vs_belief(c, s):
    return _section("vs-belief",
        f'      <div class="label">{esc(c.get("label","Most people believe"))}</div>\n'
        f'      <div class="belief">{esc(c.get("belief",""))}</div>')


def r_scene_setter(c, s):
    lines = "\n".join(f'        <div class="scene-line">{esc(l)}</div>' for l in c.get("lines", []))
    return _section("scene-setter", f'      <div class="scene">\n{lines}\n      </div>')


def r_framework_named(c, s):
    return _section("framework-named",
        f'      <div class="name">{accent(c.get("name_html", esc(c.get("name",""))))}</div>')


def r_offer_mockup(c, s):
    # Product spread image (from the product-mockup skill) + struck price + price.
    src = esc(s[0] if s else c.get("src", ""))
    tag = f'      <div class="tag">{esc(c["tag"])}</div>\n' if c.get("tag") else ""
    struck = (f'<span class="struck">{esc(c["struck_price"])}</span>'
              if c.get("struck_price") else "")
    return _section("offer-mockup",
        f'{tag}'
        f'      <div class="mockup-image"><img src="{src}" alt="" /></div>\n'
        f'      <div class="price-block">{struck}<span class="price">'
        f'{esc(c.get("price",""))}</span></div>')


def r_framework_step(c, s):
    return _section("framework-step",
        f'      <div class="step-number">{esc(c.get("step_number",""))}</div>\n'
        f'      <div class="step-name">{esc(c.get("step_name",""))}</div>\n'
        f'      <div class="step-description">{esc(c.get("step_description",""))}</div>')


def r_misconception(c, s):
    return _section("misconception",
        f'      <div class="block">\n'
        f'        <div class="label">{esc(c.get("wrong_label","Most people think"))}</div>\n'
        f'        <div class="text">{esc(c.get("wrong_text",""))}</div>\n'
        f'      </div>\n'
        f'      <div class="block">\n'
        f'        <div class="label">{esc(c.get("correct_label","But actually"))}</div>\n'
        f'        <div class="text correct">{esc(c.get("correct_text",""))}</div>\n'
        f'      </div>')


def r_screenshot(c, s):
    src = esc(s[0] if s else c.get("src", ""))
    caption = f'\n      <div class="caption">{esc(c["caption"])}</div>' if c.get("caption") else ""
    return _section("screenshot", f'      <img class="screenshot" src="{src}" alt="" />{caption}')


def r_quote(c, s):
    return _section("quote",
        f'      <div class="quote-text">&ldquo;{esc(c.get("quote",""))}&rdquo;</div>\n'
        f'      <div class="quote-attribution">&mdash; {esc(c.get("attribution",""))}</div>')


def _r_list(pattern, default_label):
    def render(c, s):
        items = "\n".join(f'        <div class="item">{esc(it)}</div>' for it in c.get("items", []))
        return _section(pattern,
            f'      <div class="label">{esc(c.get("label", default_label))}</div>\n'
            f'      <div class="items">\n{items}\n      </div>')
    return render


def r_stack_line(c, s):
    rows = []
    for row in c.get("rows", []):
        cls = " bonus" if row.get("bonus") else ""
        desc = (f'\n            <div class="stack-description">{esc(row["description"])}</div>'
                if row.get("description") else "")
        rows.append(
            f'        <div class="stack-row{cls}">\n'
            f'          <div>\n'
            f'            <div class="stack-name">{esc(row.get("name",""))}</div>{desc}\n'
            f'          </div>\n'
            f'          <div class="stack-value">{esc(row.get("value",""))}</div>\n'
            f'        </div>')
    return _section("stack-line", '      <div class="stack-list">\n' + "\n".join(rows) + '\n      </div>')


def r_stack_total(c, s):
    return _section("stack-total",
        f'      <div class="total-label">{esc(c.get("label","Total value"))}</div>\n'
        f'      <div class="total-amount">{esc(c.get("amount",""))}</div>')


def r_stack_anchor(c, s):
    return _section("stack-anchor", f'      <div class="text">{esc(c.get("text",""))}</div>')


def r_price_reveal(c, s):
    return _section("price-reveal",
        f'      <div class="label">{esc(c.get("label","Today’s price"))}</div>\n'
        f'      <div class="price">{esc(c.get("price",""))}</div>')


def r_payment_plan(c, s):
    return _section("payment-plan",
        f'      <div class="separator">{esc(c.get("separator","or"))}</div>\n'
        f'      <div class="plan">{esc(c.get("plan",""))}</div>')


def r_comparison_anchor(c, s):
    rows = []
    for row in c.get("rows", []):
        cls = " this" if row.get("this") else ""
        rows.append(
            f'        <div class="compare-row{cls}">\n'
            f'          <div>{esc(row.get("label",""))}</div>\n'
            f'          <div class="compare-value">{esc(row.get("value",""))}</div>\n'
            f'        </div>')
    return _section("comparison-anchor", '      <div class="compare-list">\n' + "\n".join(rows) + '\n      </div>')


def r_roi_math(c, s):
    rows = []
    for row in c.get("rows", []):
        cls = " result" if row.get("result") else ""
        rows.append(
            f'        <div class="roi-row{cls}">\n'
            f'          <div class="roi-label">{esc(row.get("label",""))}</div>\n'
            f'          <div class="roi-value">{esc(row.get("value",""))}</div>\n'
            f'        </div>')
    return _section("roi-math", '      <div class="roi-list">\n' + "\n".join(rows) + '\n      </div>')


def r_cost_of_not(c, s):
    items = "\n".join(f'        <div class="consequence">{esc(x)}</div>' for x in c.get("consequences", []))
    return _section("cost-of-not",
        f'      <div class="label">{esc(c.get("label","If you don’t fix this"))}</div>\n'
        f'      <div class="consequences">\n{items}\n      </div>')


def r_guarantee_headline(c, s):
    return _section("guarantee-headline",
        f'      <div class="guarantee">{accent(c.get("guarantee_html", esc(c.get("guarantee",""))))}</div>')


def r_guarantee_details(c, s):
    rows = "\n".join(
        f'        <div class="condition"><span class="condition-number">{i}.</span>{esc(x)}</div>'
        for i, x in enumerate(c.get("conditions", []), 1))
    return _section("guarantee-details",
        f'      <div class="label">{esc(c.get("label","Here’s how it works"))}</div>\n'
        f'      <div class="conditions">\n{rows}\n      </div>')


def r_urgency_reason(c, s):
    return _section("urgency-reason",
        f'      <div class="label">{esc(c.get("label","Why now"))}</div>\n'
        f'      <div class="reason">{esc(c.get("reason",""))}</div>')


def r_deadline(c, s):
    return _section("deadline",
        f'      <div class="label">{esc(c.get("label","Doors close"))}</div>\n'
        f'      <div class="deadline-text">{esc(c.get("deadline_text",""))}</div>')


def r_action_plan(c, s):
    steps = "\n".join(
        f'        <div class="step"><span class="step-number">{i}.</span>{esc(x)}</div>'
        for i, x in enumerate(c.get("steps", []), 1))
    return _section("action-plan",
        f'      <div class="label">{esc(c.get("label","Right now"))}</div>\n'
        f'      <div class="steps">\n{steps}\n      </div>')


def r_button(c, s):
    url = esc(c.get("url", "#"))
    return _section("button", f'      <a class="url" href="{url}">{url}</a>')


def r_final_cta(c, s):
    url = esc(c.get("url", "#"))
    signoff = f'\n      <div class="signoff">{esc(c["signoff"])}</div>' if c.get("signoff") else ""
    return _section("final-cta", f'      <a class="url" href="{url}">{url}</a>{signoff}')


def r_faq_grid(c, s):
    items = []
    for it in c.get("items", []):
        cls = " full-width" if it.get("full_width") else ""
        items.append(
            f'        <div class="faq-item{cls}">\n'
            f'          <div class="faq-q">Q: {esc(it.get("q",""))}</div>\n'
            f'          <div class="faq-a">A: {esc(it.get("a",""))}</div>\n'
            f'        </div>')
    return _section("faq-grid", '      <div class="faq-list">\n' + "\n".join(items) + '\n      </div>')


def r_testimonial_single(c, s):
    src = esc(s[0] if s else c.get("avatar", ""))
    return _section("testimonial-single",
        f'      <img class="avatar" src="{src}" alt="" />\n'
        f'      <div class="quote">&ldquo;{esc(c.get("quote",""))}&rdquo;</div>\n'
        f'      <div class="attribution">\n'
        f'        <div class="name">{esc(c.get("name",""))}</div>\n'
        f'        <div class="role">{esc(c.get("role",""))}</div>\n'
        f'      </div>')


def r_testimonial_grid(c, s):
    cards = []
    for card in c.get("cards", []):
        cards.append(
            f'        <div class="testimonial-card">\n'
            f'          <div class="card-head">\n'
            f'            <img class="card-avatar" src="{esc(card.get("avatar",""))}" alt="" />\n'
            f'            <div class="card-meta">\n'
            f'              <div class="card-name">{esc(card.get("name",""))}</div>\n'
            f'              <div class="card-role">{esc(card.get("role",""))}</div>\n'
            f'            </div>\n'
            f'          </div>\n'
            f'          <div class="card-quote">&ldquo;{esc(card.get("quote",""))}&rdquo;</div>\n'
            f'        </div>')
    return _section("testimonial-grid", '      <div class="grid">\n' + "\n".join(cards) + '\n      </div>')


def r_testimonial_screenshot(c, s):
    src = esc(s[0] if s else c.get("src", ""))
    return _section("testimonial-screenshot",
        f'      <div class="screenshot-side"><img src="{src}" alt="" /></div>\n'
        f'      <div class="quote-side">\n'
        f'        <div class="quote-text">&ldquo;{esc(c.get("quote_text",""))}&rdquo;</div>\n'
        f'        <div>\n'
        f'          <div class="name">{esc(c.get("name",""))}</div>\n'
        f'          <div class="role">{esc(c.get("role",""))}</div>\n'
        f'        </div>\n'
        f'      </div>')


def r_before_after(c, s):
    before, after = c.get("before", {}), c.get("after", {})
    b_img = f'\n        <img class="ba-image" src="{esc(s[0])}" alt="" />' if len(s) > 0 else ""
    a_img = f'\n        <img class="ba-image" src="{esc(s[1])}" alt="" />' if len(s) > 1 else ""
    return _section("before-after",
        f'      <div class="ba-side ba-before">\n'
        f'        <div class="ba-label">{esc(before.get("label","Before"))}</div>{b_img}\n'
        f'        <div class="ba-text">{esc(before.get("text",""))}</div>\n'
        f'      </div>\n'
        f'      <div class="ba-side ba-after">\n'
        f'        <div class="ba-label">{esc(after.get("label","After"))}</div>{a_img}\n'
        f'        <div class="ba-text">{esc(after.get("text",""))}</div>\n'
        f'      </div>')


def r_stat_row(c, s):
    stats = []
    for st in c.get("stats", []):
        stats.append(
            f'        <div class="stat">\n'
            f'          <div class="stat-number">{esc(st.get("number",""))}</div>\n'
            f'          <div class="stat-label">{esc(st.get("label",""))}</div>\n'
            f'        </div>')
    return _section("stat-row", '      <div class="stat-group">\n' + "\n".join(stats) + '\n      </div>')


def r_section_divider(c, s):
    return _section("section-divider",
        f'      <div class="divider-eyebrow">{esc(c.get("eyebrow",""))}</div>\n'
        f'      <div class="divider-title">{esc(c.get("title",""))}</div>')


def r_timeline(c, s):
    nodes = []
    for node in c.get("nodes", []):
        nodes.append(
            f'        <div class="timeline-node">\n'
            f'          <div class="timeline-date">{esc(node.get("date",""))}</div>\n'
            f'          <div class="timeline-bar"></div>\n'
            f'          <div class="timeline-event">{esc(node.get("event",""))}</div>\n'
            f'        </div>')
    return _section("timeline", '      <div class="timeline-track">\n' + "\n".join(nodes) + '\n      </div>')


def r_callout_box(c, s):
    source = f'\n        <div class="callout-source">{esc(c["source"])}</div>' if c.get("source") else ""
    return _section("callout-box",
        f'      <div class="callout">\n'
        f'        <div class="callout-text">{accent(c.get("callout_html", esc(c.get("callout",""))))}</div>{source}\n'
        f'      </div>')


RENDERERS = {
    "title": r_title,
    "big-text": _r_text("big-text"),
    "mono-word": _r_text("mono-word"),
    "mono-line": _r_text("mono-line"),
    "mono-name": _r_text("mono-name"),
    "bridge": r_bridge,
    "stack-anchor": r_stack_anchor,
    "three-lines": r_three_lines,
    "permission": r_permission,
    "instruction": r_instruction,
    "proof-number": _r_proof("proof-number"),
    "proof-stat": _r_proof("proof-stat"),
    "case-study-headline": r_case_study_headline,
    "photo-full": r_photo_full,
    "photo-text-overlay": r_photo_text_overlay,
    "image-split": r_image_split,
    "image-hero": r_image_hero,
    "image-mosaic-above": r_image_mosaic_above,
    "logo-wall": r_logo_wall,
    "agenda": r_agenda,
    "big-claim": r_big_claim,
    "vs-belief": r_vs_belief,
    "scene-setter": r_scene_setter,
    "framework-named": r_framework_named,
    "framework-step": r_framework_step,
    "offer-mockup": r_offer_mockup,
    "misconception": r_misconception,
    "screenshot": r_screenshot,
    "quote": r_quote,
    "avatar": _r_list("avatar", "This is for"),
    "not-for": _r_list("not-for", "This is NOT for"),
    "stack-line": r_stack_line,
    "stack-total": r_stack_total,
    "price-reveal": r_price_reveal,
    "payment-plan": r_payment_plan,
    "comparison-anchor": r_comparison_anchor,
    "roi-math": r_roi_math,
    "cost-of-not": r_cost_of_not,
    "guarantee-headline": r_guarantee_headline,
    "guarantee-details": r_guarantee_details,
    "urgency-reason": r_urgency_reason,
    "deadline": r_deadline,
    "action-plan": r_action_plan,
    "button": r_button,
    "final-cta": r_final_cta,
    "faq-grid": r_faq_grid,
    "testimonial-single": r_testimonial_single,
    "testimonial-grid": r_testimonial_grid,
    "testimonial-screenshot": r_testimonial_screenshot,
    "before-after": r_before_after,
    "stat-row": r_stat_row,
    "section-divider": r_section_divider,
    "timeline": r_timeline,
    "callout-box": r_callout_box,
}


# ---- image generation ------------------------------------------------------
def generate_slide_images(slide, assets_dir, regenerate):
    """Generate images for a slide that has `visual` or `visuals`. Returns src list."""
    n = slide["n"]
    visuals = []
    if "visual" in slide:
        visuals = [slide["visual"]]
    elif "visuals" in slide:
        visuals = slide["visuals"]
    if not visuals:
        return []

    if not _HAS_GENERATOR:
        raise RuntimeError(
            "Cannot generate images: brand-image/scripts/generate_image.py "
            "could not be imported. Check the skill folder layout.")

    srcs = []
    failures = []
    multi = len(visuals) > 1
    for i, v in enumerate(visuals):
        fname = f"slide-{n:03d}-{i+1}.png" if multi else f"slide-{n:03d}.png"
        path = assets_dir / fname
        if path.exists() and not regenerate:
            print(f"  slide {n:03d}: image cached ({fname})")
        else:
            print(f"  slide {n:03d}: generating image ({v.get('aspect','16:9')})...")
            try:
                generate_image(
                    v["prompt"], path,
                    aspect_ratio=v.get("aspect", "16:9"),
                    references=v.get("references"),
                )
            except Exception as e:  # noqa: BLE001, one bad image must not kill the render
                print(f"  slide {n:03d}: IMAGE FAILED, {e}", file=sys.stderr)
                print(f"  slide {n:03d}: rendering without this image; "
                      f"re-run to retry just this slide.", file=sys.stderr)
                failures.append(n)
                continue
        srcs.append(f"assets/{fname}")
    if failures:
        _IMAGE_FAILURES.update(failures)
    return srcs


# ---- render pipeline -------------------------------------------------------
def render_slide(slide):
    pattern = slide["pattern"]
    if pattern not in RENDERERS:
        raise ValueError(f"Slide {slide.get('n','?')}: unknown pattern '{pattern}'. "
                         f"Known patterns: {', '.join(sorted(RENDERERS))}")
    content = slide.get("content", {})
    srcs = slide.get("_visual_srcs", [])
    return RENDERERS[pattern](content, srcs)


def render_deck(config_path, skip_images=False, regenerate=False):
    config = json.loads(Path(config_path).read_text())
    deck = config.get("deck", {})
    slides = config.get("slides", [])
    if not slides:
        raise ValueError("config has no slides")

    output_dir = Path(deck.get("output_dir", "workspace/deck"))
    output_dir.mkdir(parents=True, exist_ok=True)
    assets_dir = output_dir / "assets"
    assets_dir.mkdir(exist_ok=True)

    print(f"Rendering {len(slides)} slides -> {output_dir}/deck.html")

    slide_htmls = []
    img_count = 0
    for slide in slides:
        if not skip_images:
            srcs = generate_slide_images(slide, assets_dir, regenerate)
            if srcs:
                slide["_visual_srcs"] = srcs
                img_count += len(srcs)
        slide_htmls.append(render_slide(slide))

    if skip_images:
        print("  (--skip-images: image slides will have empty src attributes)")
    else:
        print(f"  {img_count} image(s) ready")
        if _IMAGE_FAILURES:
            failed = ", ".join(str(n) for n in sorted(_IMAGE_FAILURES))
            print(f"  WARNING: image generation failed for slide(s): {failed}", file=sys.stderr)
            print(f"  Re-run `render_deck.py` to retry, cached images are kept, "
                  f"only the missing ones regenerate.", file=sys.stderr)

    # Inject slides into the template
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"Template not found: {TEMPLATE_PATH}")
    template = TEMPLATE_PATH.read_text()

    slides_block = "<!-- BEGIN-SLIDES -->\n\n" + "\n\n".join(slide_htmls) + "\n\n    <!-- END-SLIDES -->"
    deck_html = re.sub(
        r"<!-- BEGIN-SLIDES.*?-->.*?<!-- END-SLIDES -->",
        lambda _: slides_block,
        template, flags=re.DOTALL)

    # Deck title
    title = deck.get("title", "Webinar Deck")
    deck_html = re.sub(r"<title>.*?</title>", f"<title>{esc(title)}</title>",
                       deck_html, count=1, flags=re.DOTALL)

    # Accent color
    accent_color = deck.get("accent_color", "#FF5C28")
    deck_html = re.sub(r"--accent:\s*#[0-9A-Fa-f]+;",
                       f"--accent: {accent_color};", deck_html, count=1)

    out_path = output_dir / "deck.html"
    out_path.write_text(deck_html)
    print(f"Done: {out_path}")
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Render a webinar deck from config.json")
    parser.add_argument("--config", required=True, help="Path to config.json")
    parser.add_argument("--skip-images", action="store_true",
                        help="Skip image generation (Stage 1 smoke test)")
    parser.add_argument("--regenerate-images", action="store_true",
                        help="Regenerate images even if cached")
    args = parser.parse_args()

    try:
        render_deck(args.config, args.skip_images, args.regenerate_images)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
