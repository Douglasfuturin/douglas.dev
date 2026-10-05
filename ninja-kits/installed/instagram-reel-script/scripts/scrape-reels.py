#!/usr/bin/env python3
"""
Scrape Instagram reels by topic or handle and extract captions + metadata
for voice analysis.

Uses the Scrape Creators API to find reels, sorts by view count, and outputs
a JSON manifest with full captions and engagement metrics.

Usage:
    python3 scrape-reels.py --query "ai agents automation" --top 20
    python3 scrape-reels.py --handle "thepaulalex_" --top 15
    python3 scrape-reels.py --query "claude code" --top 10 --min-views 50000

Environment:
    SCRAPECREATORS_API_KEY must be set (or present in .env).

Output:
    Prints a JSON manifest to stdout with full captions, engagement metrics,
    and metadata for each reel. Designed for voice analysis pipelines.
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path


def load_dotenv():
    """Load .env file from project root if it exists."""
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())


def search_reels(query, api_key):
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


def fetch_user_reels(handle, api_key):
    """Fetch reels from a specific Instagram user via Scrape Creators API."""
    clean_handle = handle.lstrip("@")
    encoded_handle = urllib.parse.quote(clean_handle)
    url = f"https://api.scrapecreators.com/v1/instagram/reels/search?query={encoded_handle}"

    req = urllib.request.Request(url, headers={"x-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode())

        # Filter to only reels from this user
        reels = data.get("reels", [])
        filtered = [
            r for r in reels
            if (r.get("owner", {}).get("username", "")).lower() == clean_handle.lower()
        ]

        # If strict filtering returns too few, also try partial match
        if len(filtered) < 3:
            filtered = [
                r for r in reels
                if clean_handle.lower() in (r.get("owner", {}).get("username", "")).lower()
            ]

        # If still too few, return all results (the query was the handle,
        # so results should be relevant)
        if len(filtered) < 3:
            filtered = reels

        data["reels"] = filtered
        return data

    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else ""
        print(f"Error: API returned {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: API request failed: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Instagram reels and extract captions for voice analysis"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--query", help="Search query (topic or keyword)")
    group.add_argument("--handle", help="Instagram handle (e.g., @username or username)")
    parser.add_argument("--top", type=int, default=20, help="Number of top reels to return (default: 20)")
    parser.add_argument("--min-views", type=int, default=0, help="Minimum view count filter (default: 0)")
    args = parser.parse_args()

    load_dotenv()

    api_key = os.environ.get("SCRAPECREATORS_API_KEY")
    if not api_key:
        print("Error: SCRAPECREATORS_API_KEY environment variable not set.", file=sys.stderr)
        print("Set it in your .env file or export it as an environment variable.", file=sys.stderr)
        sys.exit(1)

    # Fetch reels
    if args.handle:
        clean_handle = args.handle.lstrip("@")
        print(f"Fetching reels from @{clean_handle}...", file=sys.stderr)
        data = fetch_user_reels(args.handle, api_key)
    else:
        print(f"Searching reels for: {args.query}", file=sys.stderr)
        data = search_reels(args.query, api_key)

    if not data.get("success"):
        print("Error: API returned unsuccessful response.", file=sys.stderr)
        sys.exit(1)

    reels = data.get("reels", [])
    if not reels:
        print("No reels found.", file=sys.stderr)
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
        print(
            f"  {i+1}. [{r['_views']:,} views] @{owner.get('username', '?')} — {caption_preview}...",
            file=sys.stderr,
        )

    # Build manifest with full captions
    manifest = []
    for r in top_reels:
        owner = r.get("owner", {})
        manifest.append({
            "caption": r.get("caption") or "",
            "views": r["_views"],
            "likes": r.get("like_count", 0),
            "comments": r.get("comment_count", 0),
            "username": owner.get("username", ""),
            "full_name": owner.get("full_name", ""),
            "url": r.get("url", ""),
            "timestamp": r.get("taken_at_timestamp") or r.get("taken_at", ""),
        })

    # Summary stats
    total_views = sum(r["views"] for r in manifest)
    total_likes = sum(r["likes"] for r in manifest)
    avg_views = total_views // len(manifest) if manifest else 0
    captions_with_text = sum(1 for r in manifest if len(r["caption"]) > 10)

    print(f"\nSummary:", file=sys.stderr)
    print(f"  Reels collected: {len(manifest)}", file=sys.stderr)
    print(f"  Reels with captions: {captions_with_text}", file=sys.stderr)
    print(f"  Total views: {total_views:,}", file=sys.stderr)
    print(f"  Average views: {avg_views:,}", file=sys.stderr)
    print(f"  Total likes: {total_likes:,}", file=sys.stderr)

    # Print manifest to stdout (machine-readable)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
