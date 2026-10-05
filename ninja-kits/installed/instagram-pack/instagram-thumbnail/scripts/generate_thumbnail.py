#!/usr/bin/env python3
"""
Generate an Instagram reel cover using Gemini 3 Pro Image Preview (Nano Banana Pro).

Usage:
    python3 generate_thumbnail.py \
        --headshot path/to/headshot.png \
        --prompt "detailed prompt text" \
        --output path/to/output.png

    With reference image (for iteration):
    python3 generate_thumbnail.py \
        --headshot path/to/headshot.png \
        --reference path/to/previous-cover.png \
        --prompt "edit instruction" \
        --output path/to/output-v2.png

    With example covers from high-performing reels:
    python3 generate_thumbnail.py \
        --headshot path/to/headshot.png \
        --examples path/to/example1.jpg path/to/example2.jpg \
        --prompt "detailed prompt text" \
        --output path/to/output.png

Environment:
    GEMINI_API_KEY must be set.
"""

import argparse
import os
import sys
from pathlib import Path

from google import genai
from google.genai import types
from PIL import Image


def parse_args():
    parser = argparse.ArgumentParser(description="Generate Instagram reel cover via Gemini")
    parser.add_argument(
        "--headshot", required=True, nargs="+",
        help="Path(s) to headshot reference image(s)"
    )
    parser.add_argument(
        "--reference", nargs="*", default=[],
        help="Path(s) to additional reference images (e.g., previous cover for iteration)"
    )
    parser.add_argument(
        "--examples", nargs="*", default=[],
        help="Path(s) to example covers from high-performing reels (style inspiration)"
    )
    parser.add_argument(
        "--prompt", required=True,
        help="Detailed prompt for cover generation"
    )
    parser.add_argument(
        "--output", required=True,
        help="Output file path for the generated cover"
    )
    parser.add_argument(
        "--no-style", action="store_true",
        help="Skip appending the brand style guide to the prompt"
    )
    return parser.parse_args()


def validate_image_file(path):
    """Check that a file is actually an image, not HTML or other junk from a failed download."""
    p = Path(path)
    if not p.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(p, "rb") as f:
        header = f.read(256)
    if b"<!DOCTYPE" in header or b"<html" in header or b"<HTML" in header:
        print(
            f"Error: '{path}' is an HTML file, not an image. "
            f"The download URL likely returned a web page instead of the actual image. "
            f"Try downloading from a different source.",
            file=sys.stderr,
        )
        sys.exit(1)
    if len(header) < 8:
        print(f"Error: '{path}' is too small to be a valid image ({len(header)} bytes).", file=sys.stderr)
        sys.exit(1)


def resize_if_needed(img, max_edge=2048):
    """Resize image if larger than max_edge on any side."""
    w, h = img.size
    if max(w, h) > max_edge:
        ratio = max_edge / max(w, h)
        new_size = (int(w * ratio), int(h * ratio))
        return img.resize(new_size, Image.LANCZOS)
    return img


def load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def main():
    args = parse_args()

    load_dotenv()

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    # Build contents: prompt text + headshot images + reference images + examples
    prompt = args.prompt

    # Append brand style guide unless --no-style is set
    if not args.no_style:
        # Check instagram skill directory first, then fall back to youtube skill
        style_path = Path(__file__).resolve().parent.parent / "brand-style.md"
        if not style_path.exists():
            style_path = Path(__file__).resolve().parent.parent.parent / "youtube-thumbnail" / "brand-style.md"
        if style_path.exists():
            style_text = style_path.read_text().strip()
            prompt += (
                "\n\nBRAND STYLE GUIDE (follow these rules):\n"
                f"{style_text}"
            )

    if args.examples:
        prompt += (
            "\n\nSTYLE EXAMPLES:\n"
            "The final attached images are covers from high-performing Instagram reels "
            "on this topic. Study their composition, color usage, text placement, and visual "
            "hierarchy — then apply those patterns to create an ORIGINAL cover. "
            "Do NOT copy these covers. Use them as inspiration for what works."
        )

    contents = [prompt]

    for headshot_path in args.headshot:
        validate_image_file(headshot_path)
        img = resize_if_needed(Image.open(headshot_path))
        contents.append(img)

    for ref_path in args.reference:
        validate_image_file(ref_path)
        img = resize_if_needed(Image.open(ref_path))
        contents.append(img)

    for ex_path in args.examples:
        validate_image_file(ex_path)
        img = resize_if_needed(Image.open(ex_path))
        contents.append(img)

    # Generate with 9:16 vertical aspect ratio
    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
            image_config=types.ImageConfig(
                aspect_ratio="9:16",
            ),
        ),
    )

    # Process response
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    image_saved = False
    text_response = ""

    for part in response.candidates[0].content.parts:
        if hasattr(part, "inline_data") and part.inline_data is not None:
            img = part.as_image()
            img.save(str(output_path))
            image_saved = True
            print(f"Cover saved to: {output_path}")
        elif hasattr(part, "text") and part.text is not None:
            text_response += part.text

    if text_response:
        print(f"\nModel notes: {text_response}")

    if not image_saved:
        print("Error: No image was generated in the response.", file=sys.stderr)
        if text_response:
            print(f"Response text: {text_response}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
