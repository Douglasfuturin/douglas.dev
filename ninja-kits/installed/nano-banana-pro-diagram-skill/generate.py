#!/usr/bin/env python3
"""
Generate hand-drawn diagrams using Nano Banana Pro (Gemini).

Two modes:
  SVG mode (default):  SVG blueprint → extract image placeholders → Tavily search → Nano Banana Pro
  Text mode:           Text prompt → Nano Banana Pro

Usage:
  python generate.py --svg input.svg --output output.png
  python generate.py --svg input.svg --output output.png --no-images
  python generate.py --prompt "describe the diagram" --output output.png
  python generate.py --svg input.svg --prompt "extra instructions" --output output.png

Environment variables (or .env file):
  GEMINI_API_KEY   - Required
  TAVILY_API_KEY   - Required for image placeholder resolution
"""

import argparse
import os
import re
import sys
import time
from io import BytesIO
from pathlib import Path

import requests
from google import genai
from google.genai import types


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

MODEL = "nano-banana-pro-preview"

STYLE_PROMPT_HEADER = """Generate a hand-drawn conceptual diagram in the PaperBanana / sketchy whiteboard illustration style shown in the reference images.

Style requirements:
- Hand-drawn / sketchy whiteboard aesthetic
- Black ink outlines on light/cream background
- Thick wobbly outlines, dashed connectors, expressive arrows
- Bold uppercase section headers
- Small doodle icons (lightbulbs, gears, magnifying glasses, documents)
- Stick figures for people
- Speech bubbles, thought clouds
- Clear information hierarchy with flow arrows
- Information-dense but readable, like an editorial illustration
"""

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

def load_env(env_path=".env"):
    """Load key=value pairs from .env file into a dict (does not pollute os.environ)."""
    env = {}
    path = Path(env_path)
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def get_key(name, env):
    """Get key from os.environ or .env dict."""
    return os.environ.get(name) or env.get(name)


# ---------------------------------------------------------------------------
# Reference images (style guides)
# ---------------------------------------------------------------------------

def load_style_refs(ref_dir="ref"):
    """Load PaperBanana style reference images from ref/ directory."""
    parts = []
    ref_path = Path(ref_dir)
    if not ref_path.exists():
        return parts

    for f in sorted(ref_path.iterdir()):
        if f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp"):
            mime = "image/png" if f.suffix.lower() == ".png" else "image/jpeg"
            parts.append(types.Part.from_bytes(data=f.read_bytes(), mime_type=mime))
            print(f"  [style-ref] {f.name} ({f.stat().st_size // 1024}KB)")

    return parts


# ---------------------------------------------------------------------------
# SVG placeholder parsing
# ---------------------------------------------------------------------------

# Matches: <!-- IMAGE: description of what to search for -->
IMAGE_PLACEHOLDER_RE = re.compile(
    r"<!--\s*IMAGE:\s*(.+?)\s*-->", re.IGNORECASE
)


def extract_image_placeholders(svg_content):
    """Extract IMAGE placeholder descriptions from SVG comments.

    Syntax in SVG:
        <!-- IMAGE: developer typing at a dark terminal -->
        <!-- IMAGE: cloud computing infrastructure -->

    Returns list of unique search queries.
    """
    matches = IMAGE_PLACEHOLDER_RE.findall(svg_content)
    # Deduplicate while preserving order
    seen = set()
    queries = []
    for m in matches:
        m = m.strip()
        if m and m.lower() not in seen:
            seen.add(m.lower())
            queries.append(m)
    return queries


# ---------------------------------------------------------------------------
# Tavily image search
# ---------------------------------------------------------------------------

def search_images_tavily(query, api_key, max_results=3):
    """Search Tavily for images matching query. Returns list of image URLs."""
    try:
        r = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": api_key,
                "query": query,
                "search_depth": "basic",
                "include_images": True,
                "max_results": max_results,
            },
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("images", [])[:max_results]
    except Exception as e:
        print(f"  [tavily] Warning: search failed for '{query}': {e}")
        return []


def download_image(url, timeout=10):
    """Download image from URL. Returns (bytes, mime_type) or (None, None)."""
    try:
        r = requests.get(url, timeout=timeout, headers={
            "User-Agent": "Mozilla/5.0 (compatible; DiagramGenerator/1.0)"
        })
        r.raise_for_status()
        content_type = r.headers.get("content-type", "image/jpeg")
        if "png" in content_type:
            mime = "image/png"
        elif "webp" in content_type:
            mime = "image/webp"
        elif "gif" in content_type:
            mime = "image/gif"
        else:
            mime = "image/jpeg"
        return r.content, mime
    except Exception as e:
        print(f"  [download] Warning: failed to download {url[:80]}: {e}")
        return None, None


def resolve_image_placeholders(queries, tavily_key):
    """For each query, search Tavily and download the best image.

    Returns list of (query, image_bytes, mime_type) tuples.
    """
    results = []
    for query in queries:
        print(f"  [tavily] Searching: '{query}'")
        urls = search_images_tavily(query, tavily_key)

        found = False
        for url in urls:
            img_bytes, mime = download_image(url)
            if img_bytes and len(img_bytes) > 1000:  # Skip tiny/broken images
                results.append((query, img_bytes, mime))
                print(f"  [tavily] Found image for '{query}' ({len(img_bytes) // 1024}KB)")
                found = True
                break

        if not found:
            print(f"  [tavily] No usable image found for '{query}'")

    return results


# ---------------------------------------------------------------------------
# Gemini generation
# ---------------------------------------------------------------------------

def generate_from_svg(
    svg_content,
    output_path,
    gemini_key,
    tavily_key=None,
    style_refs=None,
    extra_prompt="",
    skip_images=False,
    aspect_ratio=None,
):
    """SVG-guided generation: SVG blueprint → Nano Banana Pro hand-drawn diagram.

    1. Parses SVG for <!-- IMAGE: ... --> placeholders
    2. Searches Tavily for matching reference images
    3. Sends everything to Nano Banana Pro
    """
    client = genai.Client(api_key=gemini_key)
    parts = []

    # Style reference images
    if style_refs:
        parts.extend(style_refs)

    # Resolve image placeholders
    placeholder_images = []
    if not skip_images and tavily_key:
        queries = extract_image_placeholders(svg_content)
        if queries:
            print(f"\n[placeholders] Found {len(queries)} image placeholder(s)")
            placeholder_images = resolve_image_placeholders(queries, tavily_key)

    # Add found images with labels
    for query, img_bytes, mime in placeholder_images:
        parts.append(types.Part.from_text(text=f"Reference image for '{query}':"))
        parts.append(types.Part.from_bytes(data=img_bytes, mime_type=mime))

    # Build the prompt
    prompt_parts = [STYLE_PROMPT_HEADER]
    prompt_parts.append(
        f"""I have an SVG diagram that serves as a BLUEPRINT for the layout and content.
Redraw this diagram in the hand-drawn PaperBanana / sketchy whiteboard style shown in the reference images.

IMPORTANT: Preserve the same information architecture, flow, text labels, and spatial layout from the SVG.
Render it as a beautiful hand-drawn illustration — as if someone sketched it on a whiteboard with markers.

SVG Blueprint:
```svg
{svg_content}
```"""
    )

    if placeholder_images:
        prompt_parts.append(
            "\nI've also included reference images for the IMAGE placeholders in the SVG. "
            "Incorporate visual elements inspired by these references into the corresponding "
            "areas of the diagram."
        )

    if extra_prompt:
        prompt_parts.append(f"\nAdditional instructions: {extra_prompt}")

    parts.append(types.Part.from_text(text="\n\n".join(prompt_parts)))

    # Generate
    print(f"\n[gemini] Generating with {MODEL}...")
    t0 = time.time()

    config_kwargs = {
        "response_modalities": ["image", "text"],
        "temperature": 1.0,
    }
    if aspect_ratio:
        config_kwargs["image_config"] = types.ImageConfig(aspect_ratio=aspect_ratio)

    response = client.models.generate_content(
        model=MODEL,
        contents=types.Content(role="user", parts=parts),
        config=types.GenerateContentConfig(**config_kwargs),
    )

    elapsed = time.time() - t0
    print(f"[gemini] Generation completed in {elapsed:.1f}s")

    return _save_response(response, output_path)


def generate_from_prompt(
    prompt,
    output_path,
    gemini_key,
    tavily_key=None,
    style_refs=None,
    aspect_ratio=None,
):
    """Text-only generation: prompt → Nano Banana Pro."""
    client = genai.Client(api_key=gemini_key)
    parts = []

    # Style reference images
    if style_refs:
        parts.extend(style_refs)

    # Build prompt
    full_prompt = STYLE_PROMPT_HEADER + "\n\n" + prompt
    parts.append(types.Part.from_text(text=full_prompt))

    # Generate
    print(f"\n[gemini] Generating with {MODEL} (text-only mode)...")
    t0 = time.time()

    config_kwargs = {
        "response_modalities": ["image", "text"],
        "temperature": 1.0,
    }
    if aspect_ratio:
        config_kwargs["image_config"] = types.ImageConfig(aspect_ratio=aspect_ratio)

    response = client.models.generate_content(
        model=MODEL,
        contents=types.Content(role="user", parts=parts),
        config=types.GenerateContentConfig(**config_kwargs),
    )

    elapsed = time.time() - t0
    print(f"[gemini] Generation completed in {elapsed:.1f}s")

    return _save_response(response, output_path)


def _save_response(response, output_path):
    """Extract image from Gemini response and save to disk."""
    saved = False
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            ext = ".png" if "png" in (part.inline_data.mime_type or "") else ".png"
            out = Path(output_path)
            out.write_bytes(part.inline_data.data)
            size_kb = len(part.inline_data.data) // 1024
            print(f"\n[output] Saved: {out} ({size_kb}KB, {part.inline_data.mime_type})")
            saved = True
        elif part.text:
            print(f"[gemini] Note: {part.text[:300]}")

    if not saved:
        print("[error] No image was generated in the response")
        return False

    return True


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate hand-drawn diagrams with Nano Banana Pro",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # SVG blueprint → hand-drawn diagram (default)
  python generate.py --svg diagram.svg -o output.png

  # SVG mode without image placeholder resolution
  python generate.py --svg diagram.svg -o output.png --no-images

  # Text-only mode
  python generate.py --prompt "A diagram showing how microservices communicate" -o output.png

  # SVG + extra instructions
  python generate.py --svg diagram.svg --prompt "Make it more colorful" -o output.png
        """,
    )
    parser.add_argument("--svg", help="Path to SVG blueprint file")
    parser.add_argument("--prompt", help="Text prompt (used alone for text-only mode, or as extra instructions with --svg)")
    parser.add_argument("-o", "--output", required=True, help="Output image path (.png)")
    parser.add_argument("--no-images", action="store_true", help="Skip Tavily image search for placeholders")
    parser.add_argument("--aspect-ratio", default=None, choices=["1:1", "16:9", "4:3", "3:4"], help="Output aspect ratio (default: model decides)")
    parser.add_argument("--ref-dir", default="ref", help="Directory containing style reference images (default: ref/)")
    parser.add_argument("--env", default=".env", help="Path to .env file (default: .env)")

    args = parser.parse_args()

    if not args.svg and not args.prompt:
        parser.error("Provide --svg, --prompt, or both")

    # Load keys
    env = load_env(args.env)
    gemini_key = get_key("GEMINI_API_KEY", env)
    tavily_key = get_key("TAVILY_API_KEY", env)

    if not gemini_key:
        sys.exit("[error] GEMINI_API_KEY not found in environment or .env")

    # Load style refs
    print("[refs] Loading style references...")
    style_refs = load_style_refs(args.ref_dir)
    if not style_refs:
        print("[refs] Warning: No reference images found in ref/ directory")

    # Generate
    if args.svg:
        svg_path = Path(args.svg)
        if not svg_path.exists():
            sys.exit(f"[error] SVG file not found: {svg_path}")

        svg_content = svg_path.read_text()
        print(f"[svg] Loaded {svg_path} ({len(svg_content)} chars)")

        success = generate_from_svg(
            svg_content=svg_content,
            output_path=args.output,
            gemini_key=gemini_key,
            tavily_key=tavily_key if not args.no_images else None,
            style_refs=style_refs,
            extra_prompt=args.prompt or "",
            skip_images=args.no_images,
            aspect_ratio=args.aspect_ratio,
        )
    else:
        if not tavily_key:
            print("[warn] TAVILY_API_KEY not set — image search disabled")

        success = generate_from_prompt(
            prompt=args.prompt,
            output_path=args.output,
            gemini_key=gemini_key,
            tavily_key=tavily_key,
            style_refs=style_refs,
            aspect_ratio=args.aspect_ratio,
        )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
