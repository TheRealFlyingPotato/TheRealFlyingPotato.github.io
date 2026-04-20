#!/usr/bin/env python3
"""
BGG Link Fetcher
Automatically finds BoardGameGeek URLs for each game.
Uses a headless browser to bypass bot protection on BGG.
Saves results to the JSON under the "bggurl" key.

Requirements:
    pip install playwright
    playwright install chromium
"""

import json
import sys
import time
import re
from urllib.parse import quote_plus


BGG_SEARCH_URL = "https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q={query}"
BGG_BASE = "https://boardgamegeek.com"


def load_json_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json_file(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def find_bgg_url(page, name):
    """Search BGG for a game and return its URL, or None."""
    url = BGG_SEARCH_URL.format(query=quote_plus(name))
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=20000)
        # Wait for search results to render
        page.wait_for_selector('table#collectionitems, #noResults', timeout=10000)
    except Exception as e:
        print(f"  Page load error: {e}")
        return None

    # Check for no results
    no_results = page.query_selector('#noResults')
    if no_results:
        return None

    # Find the first result link matching /boardgame/<id>/<slug>
    links = page.query_selector_all('table#collectionitems td.collection_objectname a')
    for link in links:
        href = link.get_attribute('href') or ''
        if re.match(r'^/boardgame/\d+/', href):
            return BGG_BASE + href

    return None


def process_games(games_data, force=False):
    from playwright.sync_api import sync_playwright

    total = len(games_data)
    updated = 0
    skipped = 0
    failed = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800},
        )
        page = context.new_page()

        # Warm up — visit homepage to get cookies
        print("Warming up session...")
        try:
            page.goto('https://boardgamegeek.com/', wait_until='domcontentloaded', timeout=20000)
            time.sleep(1)
        except Exception:
            pass

        for i, game in enumerate(games_data, 1):
            name = game.get('name', f'Game {i}')

            if game.get('bggurl') and not force:
                print(f"[{i}/{total}] Skipping '{name}' — bggurl already set")
                skipped += 1
                continue

            print(f"[{i}/{total}] Searching for '{name}'...")
            bgg_url = find_bgg_url(page, name)

            if bgg_url:
                game['bggurl'] = bgg_url
                print(f"  Found: {bgg_url}")
                updated += 1
            else:
                print(f"  Not found: '{name}'")
                failed += 1

            time.sleep(0.75)  # Be polite

        browser.close()

    print(f"\n{'='*50}")
    print(f"Updated: {updated}  |  Skipped: {skipped}  |  Failed: {failed}")
    print(f"{'='*50}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python bgg_link_fetcher.py <json_file> [--force]")
        print("  --force  Re-fetch URLs even if bggurl already exists")
        sys.exit(1)

    json_file = sys.argv[1]
    force = '--force' in sys.argv

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Missing dependency. Install with:")
        print("  pip install playwright")
        print("  playwright install chromium")
        sys.exit(1)

    print("BGG Link Fetcher (headless browser)")
    print("=" * 40)

    games_data = load_json_file(json_file)
    if not isinstance(games_data, list):
        print("Error: JSON file should contain a list of games.")
        sys.exit(1)

    process_games(games_data, force)
    save_json_file(json_file, games_data)
    print(f"Saved results to {json_file}")


if __name__ == "__main__":
    main()
