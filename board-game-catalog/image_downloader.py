#!/usr/bin/env python3
"""
Board Game Image Downloader
Downloads and converts images to WebP format for board game JSON data.
Automatically opens BoardGameGeek search pages to help find images.
"""

import json
import sys
import os
import requests
from PIL import Image
from urllib.parse import urlparse, quote_plus
import tempfile
from pathlib import Path
import webbrowser
import time


def load_json_file(filepath):
    """Load and parse the JSON file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{filepath}': {e}")
        sys.exit(1)


def check_image_exists(image_path):
    """Check if the image file exists."""
    return os.path.exists(image_path)


def get_user_input(game_name):
    """Get image URL from user input."""
    print(f"\nImage not found for '{game_name}'")
    
    # Auto-open BGG search page
    try:
        encoded_name = quote_plus(game_name)
        bgg_url = f"https://boardgamegeek.com/geeksearch.php?action=search&objecttype=boardgame&q={encoded_name}"
        print(f"Opening BGG search for '{game_name}'...")
        webbrowser.open(bgg_url)
        time.sleep(1)  # Brief pause to let browser open
    except Exception as e:
        print(f"Could not open browser: {e}")
    
    print("Tip: Right-click on the game's cover image and select 'Copy image address'")
    url = input(f"Enter image URL for '{game_name}' (or press Enter to skip): ").strip()
    return url if url else None


def download_image(url, temp_path):
    """Download image from URL to temporary path."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(temp_path, 'wb') as f:
            f.write(response.content)
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False


def convert_to_webp(input_path, output_path, quality=85):
    """Convert image to WebP format."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with Image.open(input_path) as img:
            # Convert RGBA to RGB if necessary (WebP supports both, but RGB is smaller)
            if img.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            elif img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGB')
            
            # Save as WebP
            img.save(output_path, 'WebP', quality=quality, optimize=True)
        
        return True
        
    except Exception as e:
        print(f"Error converting image to WebP: {e}")
        return False


def get_file_extension(url):
    """Extract file extension from URL."""
    parsed = urlparse(url)
    path = parsed.path
    return os.path.splitext(path)[1].lower()


def process_games(games_data):
    """Process all games in the JSON data."""
    total_games = len(games_data)
    processed = 0
    downloaded = 0
    skipped = 0
    
    print(f"Processing {total_games} games...")
    
    for i, game in enumerate(games_data, 1):
        game_name = game.get('name', f'Game {i}')
        image_path = game.get('image', '')
        
        if not image_path:
            print(f"[{i}/{total_games}] Skipping '{game_name}' - no image path specified")
            skipped += 1
            continue
        
        print(f"[{i}/{total_games}] Checking '{game_name}'...")
        
        if check_image_exists(image_path):
            print(f"  ✓ Image already exists: {image_path}")
            processed += 1
            continue
        
        # Get URL from user
        url = get_user_input(game_name)
        if not url:
            print(f"  - Skipped '{game_name}'")
            skipped += 1
            continue
        
        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            print(f"  ✗ Invalid URL format for '{game_name}'")
            skipped += 1
            continue
        
        # Create temporary file for download
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            print(f"  Downloading from: {url}")
            if download_image(url, temp_path):
                print(f"  Converting to WebP...")
                if convert_to_webp(temp_path, image_path):
                    print(f"  ✓ Successfully saved: {image_path}")
                    downloaded += 1
                else:
                    print(f"  ✗ Failed to convert image for '{game_name}'")
                    skipped += 1
            else:
                print(f"  ✗ Failed to download image for '{game_name}'")
                skipped += 1
        
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_path)
            except OSError:
                pass
        
        processed += 1
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SUMMARY:")
    print(f"Total games processed: {processed}")
    print(f"Images downloaded: {downloaded}")
    print(f"Games skipped: {skipped}")
    print(f"{'='*50}")


def main():
    """Main function."""
    if len(sys.argv) != 2:
        print("Usage: python image_downloader.py <json_file>")
        print("Example: python image_downloader.py games.json")
        sys.exit(1)
    
    json_file = sys.argv[1]
    
    # Check if required modules are available
    try:
        import requests
        from PIL import Image
    except ImportError as e:
        print(f"Missing required module: {e}")
        print("Please install required packages:")
        print("  pip install requests pillow")
        sys.exit(1)
    
    print("Board Game Image Downloader")
    print("="*40)
    print("Note: BGG search pages will auto-open for missing images")
    print()
    
    # Load JSON data
    games_data = load_json_file(json_file)
    
    if not isinstance(games_data, list):
        print("Error: JSON file should contain a list of games.")
        sys.exit(1)
    
    # Process all games
    process_games(games_data)


if __name__ == "__main__":
    main()