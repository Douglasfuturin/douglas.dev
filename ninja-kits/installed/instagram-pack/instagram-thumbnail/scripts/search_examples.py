#!/usr/bin/env python3
"""
Search Instagram for high-performing reels on a topic and download their cover images
as style examples for cover generation.

Uses the Scrape Creators API to find reels, sorts by view count, and downloads
the top cover images.

Usage:
    python3 search_examples.py --query "ai agents automation" --top 5
    python3 search_examples.py --query "claude code" --top 3 --min-views 50000

Environment:
    SCRAPECREATORS_API_KEY must be set (or present in .env).

Output:
    Downloads cover images to workspace/examples/instagram/ and prints a JSON manifest
    to stdout with metadata about each downloaded cover.
"""

import argparse
import io
import json
import os
import re
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

from PIL import Image


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


def search_instagram_reels(query, api_key):
    """Search Instagram reels via Scrape Creators API."""
    encoded_query = urllib.parse.quote(query)
    url = f"https://api.scrapecreators.com/v1/instagram/reels/search?query={encoded_query}"

    req = urllib.request.Request(url, headers={"x-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Error: API returned {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def download_cover(url, output_path):
    """Download an Instagram reel cover image, convert to JPEG via Pillow."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read()

        if b"<!DOCTYPE" in data[:256] or b"<html" in data[:256]:
            print(f"  Warning: Got HTML instead of image from {url[:80]}...", file=sys.stderr)
            return False

        if len(data) < 100:
            print(f"  Warning: File too small ({len(data)} bytes)", file=sys.stderr)
            return False

        img = Image.open(io.BytesIO(data))
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        img.save(str(output_path), "JPEG", quality=90)
        return True

    except Exception as e:
        print(f"  Warning: Failed to download cover: {e}", file=sys.stderr)
        return False


def slugify(text, max_len=40):
    """Convert text to a filename-safe slug."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "-", text).strip("-")
    return text[:max_len]


def main():
    parser = argparse.ArgumentParser(description="Search Instagram for high-performing reel cover examples")
    parser.add_argument("--query", required=True, help="Search query (reel topic)")
    parser.add_argument("--top", type=int, default=5, help="Number of top covers to download (default: 5)")
    parser.add_argument("--min-views", type=int, default=0, help="Minimum view count filter (default: 0)")
    parser.add_argument("--output-dir", default="workspace/examples/instagram", help="Output directory")
    args = parser.parse_args()

    load_dotenv()

    api_key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not api_key:
        print("Error: SCRAPECREATORS_API_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    print(f"Searching Instagram reels for: {args.query}", file=sys.stderr)
    data = search_instagram_reels(args.query, api_key)

    if not data.get("success"):
        print("Error: API returned unsuccessful response.", file=sys.stderr)
        sys.exit(1)

    reels = data.get("reels", [])
    if not reels:
        print("No reels found for this query.", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(reels)} reels", file=sys.stderr)

    # Parse view counts and filter
    for r in reels:
        r["_views"] = r.get("video_view_count") or r.get("video_play_count") or 0
    reels = [r for r in reels if r["_views"] >= args.min_views]
    reels.sort(key=lambda r: r["_views"], reverse=True)

    if not reels:
        print(f"No reels found with >= {args.min_views} views.", file=sys.stderr)
        sys.exit(1)

    top_reels = reels[:args.top]

    print(f"\nTop {len(top_reels)} reels by views:", file=sys.stderr)
    for i, r in enumerate(top_reels):
        owner = r.get("owner", {})
        caption_preview = (r.get("caption") or "")[:60]
        print(f"  {i+1}. [{r['_views']:,} views] @{owner.get('username', '?')} — {caption_preview}...", file=sys.stderr)

    # Download covers
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    query_slug = slugify(args.query)

    manifest = []
    for i, r in enumerate(top_reels):
        # Prefer display_url (full resolution) over thumbnail_src (cropped)
        cover_url = r.get("display_url") or r.get("thumbnail_src") or ""
        if not cover_url:
            print(f"  Skipping reel {i+1}: no cover URL", file=sys.stderr)
            continue

        filename = f"{query_slug}-{i+1}.jpg"
        output_path = output_dir / filename

        owner = r.get("owner", {})
        print(f"  Downloading cover {i+1}: @{owner.get('username', '?')}...", file=sys.stderr)
        if download_cover(cover_url, output_path):
            manifest.append({
                "path": str(output_path),
                "caption": (r.get("caption") or "")[:200],
                "views": r["_views"],
                "likes": r.get("like_count", 0),
                "comments": r.get("comment_count", 0),
                "username": owner.get("username", ""),
                "url": r.get("url", ""),
            })

    if not manifest:
        print("Error: Failed to download any covers.", file=sys.stderr)
        sys.exit(1)

    print(f"\nDownloaded {len(manifest)} covers to {output_dir}/", file=sys.stderr)

    # Print manifest to stdout (machine-readable)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
