#!/usr/bin/env python3
"""
Search Google Images via Tavily for relevant presentation visuals.

Uses the Tavily Search API with include_images to find high-quality images,
then downloads and converts to JPEG for universal PowerPoint/Keynote compatibility.

Usage:
    python3 search_images.py --query "marketing dashboard screenshot" \
        --output "presentations/slug-assets/img-0-dashboard.jpg"

    python3 search_images.py --query "AI robot illustration" \
        --top 3 --output-dir "presentations/slug-assets/"

Environment:
    TAVILY_API_KEY must be set (or present in .env).
    Get a key at: https://tavily.com/
"""

import argparse
import io
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path

from PIL import Image

# Enable AVIF/WebP support
try:
    import pillow_avif  # noqa: F401
except ImportError:
    pass


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


def search_tavily_images(query, api_key):
    """Search for images via Tavily Search API."""
    payload = json.dumps({
        "query": query,
        "include_images": True,
        "include_image_descriptions": True,
        "search_depth": "basic",
        "max_results": 5,
    }).encode()

    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Error: Tavily API returned {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Tavily API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def download_image(url, output_path, min_width=640):
    """Download an image and convert to JPEG.

    Validates the download is a real image (not HTML from hotlink blocking).
    Converts to JPEG for universal PowerPoint/Keynote compatibility.
    """
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()

        # Validate it's actually an image, not HTML
        if b"<!DOCTYPE" in data[:256] or b"<html" in data[:256].lower():
            print(f"  Warning: Got HTML instead of image from {url[:80]}", file=sys.stderr)
            return False

        if len(data) < 500:
            print(f"  Warning: File too small ({len(data)} bytes)", file=sys.stderr)
            return False

        # Open with Pillow and re-save as JPEG
        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        # Skip if too small for a presentation
        if img.width < min_width:
            print(f"  Warning: Image too small ({img.width}x{img.height}), skipping", file=sys.stderr)
            return False

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "JPEG", quality=90)
        return True

    except Exception as e:
        print(f"  Warning: Failed to download {url[:80]}: {e}", file=sys.stderr)
        return False


def slugify(text, max_len=40):
    """Convert text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:max_len]


def main():
    parser = argparse.ArgumentParser(description="Search Google Images via Tavily for presentation visuals")
    parser.add_argument("--query", required=True, help="Image search query")
    parser.add_argument("--output", help="Output path for single image download")
    parser.add_argument("--output-dir", help="Output directory for multiple images")
    parser.add_argument("--top", type=int, default=1, help="Number of images to download (default: 1)")
    args = parser.parse_args()

    load_dotenv()

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("Error: TAVILY_API_KEY not set in environment or .env", file=sys.stderr)
        print("Get a key at: https://tavily.com/", file=sys.stderr)
        sys.exit(1)

    if not args.output and not args.output_dir:
        print("Error: Must specify --output or --output-dir", file=sys.stderr)
        sys.exit(1)

    print(f"Searching images for: {args.query}", file=sys.stderr)
    data = search_tavily_images(args.query, api_key)

    images = data.get("images", [])
    if not images:
        print(f"No images found for: {args.query}", file=sys.stderr)
        print(json.dumps([]))
        sys.exit(1)

    print(f"Found {len(images)} image results", file=sys.stderr)

    manifest = []
    downloaded = 0

    for i, img_item in enumerate(images):
        if downloaded >= args.top:
            break

        # Tavily returns images as either strings (URLs) or objects with url/description
        if isinstance(img_item, str):
            image_url = img_item
            description = ""
        elif isinstance(img_item, dict):
            image_url = img_item.get("url", "")
            description = img_item.get("description", "")
        else:
            continue

        if not image_url:
            continue

        # Determine output path
        if args.output and args.top == 1:
            output_path = args.output
        else:
            output_dir = args.output_dir or str(Path(args.output).parent)
            query_slug = slugify(args.query)
            output_path = str(Path(output_dir) / f"img-{query_slug}-{downloaded}.jpg")

        desc_preview = (description or image_url or "")[:60]
        print(f"  Downloading {downloaded + 1}: {desc_preview}...", file=sys.stderr)

        if download_image(image_url, output_path):
            manifest.append({
                "path": output_path,
                "description": description,
                "source_url": image_url,
            })
            downloaded += 1

    if not manifest:
        print("Error: Failed to download any images.", file=sys.stderr)
        print(json.dumps([]))
        sys.exit(1)

    print(f"\nDownloaded {len(manifest)} image(s)", file=sys.stderr)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
