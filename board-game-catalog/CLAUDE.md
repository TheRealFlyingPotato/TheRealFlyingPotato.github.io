# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a static board game catalog site hosted on GitHub Pages. There is no build step — edit files and push to deploy. Open `index.html` directly in a browser to preview locally.

## Data: `boardgames.json`

All game data lives in `boardgames.json`. Each entry uses this structure:

```json
{
  "id": 1,
  "name": "Game Name",
  "color": "#7f5539",
  "image": "images/filename.webp",
  "genre": "Dungeon Crawler",
  "description": "Short description shown on card hover.",
  "player count": "1-4",
  "cooperative": true,
  "competitive": false,
  "weight": 4,
  "notes": "Optional notes shown on card hover."
}
```

- `id` must be unique and sequential
- `image` paths are relative to `board-game-catalog/` — store images in `images/` as `.webp`
- `weight` is 1–5 (complexity scale)
- `player count` supports formats: `"2-4"`, `"1-4"`, `"3"`, `"4+"`
- `color` sets the top border accent of the card

## Adding Images

Use `image_downloader.py` to fetch and convert images to WebP:

```bash
cd board-game-catalog
python image_downloader.py boardgames.json
```

This iterates through all entries, skips games that already have local images, auto-opens BoardGameGeek search for missing ones, prompts for an image URL, downloads it, and converts it to WebP (quality 85). Requires `pip install requests pillow`.

## Architecture

**Data flow:** `index.js` fetches `boardgames.json` from the GitHub raw URL at page load, then calls `displayBoardGames()` which builds Bootstrap card elements via jQuery DOM construction.

**Filtering (`applyFilters`):** Runs on every keystroke across 5 inputs (name, player count, genre, weight, ID). Filter logic:
- Name/genre/description/notes: text substring match; supports `,` (OR) and `&` (AND)
- Player count: parses ranges like `2-4` into arrays, supports `+` suffix (max 8), `=N` for exact match
- Weight: range/OR/AND same as player count but matches a single integer
- ID filter: comma-separated exact integer match; synced to the `?ids=` URL query param

**URL state:** The `ids` query parameter persists selected game IDs across page loads (used for sharing a filtered view). Clicking a card toggles its ID in the URL. The ID filter input also writes to the URL.

**Print mode:** `beforeprint` event builds a `<table class="print-table">` from currently visible cards and injects it after `.boardgames`. The card grid is hidden via `@media print` CSS so only the table prints.

## Key Selectors / Data Attributes

Card elements have class `game-card` and carry all filterable data as `data-*` attributes (`data-id`, `data-name`, `data-genre`, `data-description`, `data-player-count`, `data-weight`, `data-notes`). Filter logic reads these, not the JSON, so they must stay in sync with `createGameCard()`.
