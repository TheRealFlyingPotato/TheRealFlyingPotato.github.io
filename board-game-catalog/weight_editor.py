#!/usr/bin/env python3
"""Weight Editor — click a 1-5 radio button to instantly update a game's weight in boardgames.json."""

import json
import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk

JSON_PATH = Path(__file__).parent / "boardgames.json"
TILE_SIZE  = 150
GRID_COLS  = 6

BG       = "#1a1a1a"
CARD_BG  = "#242424"
INNER_BG = "#111111"

WEIGHT_COLORS = {1: "#52b788", 2: "#95d5b2", 3: "#f4a261", 4: "#e76f51", 5: "#c1121f"}


class WeightEditor:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Weight Editor")
        self.root.geometry("1140x700")
        self.root.configure(bg=BG)

        self.games: list[dict] = []
        self._photos: dict[int, ImageTk.PhotoImage] = {}
        self._weight_vars: dict[int, tk.IntVar] = {}

        self._build_ui()
        self._load()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        top = tk.Frame(self.root, bg=BG, padx=12, pady=8)
        top.pack(fill="x")
        tk.Label(top, text="Weight Editor", bg=BG, fg="#ccc",
                 font=("Segoe UI", 11, "bold")).pack(side="left")
        self.status_var = tk.StringVar(value="Loading…")
        tk.Label(top, textvariable=self.status_var, bg=BG, fg="#666",
                 font=("Segoe UI", 8)).pack(side="right", padx=8)

        cf = tk.Frame(self.root, bg=INNER_BG)
        cf.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        cf.rowconfigure(0, weight=1)
        cf.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(cf, bg=INNER_BG, highlightthickness=0)
        vsb = tk.Scrollbar(cf, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.inner = tk.Frame(self.canvas, bg=INNER_BG)
        self._win_id = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=(0, 0, e.width, e.height)))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(
            self._win_id, width=e.width))
        self._bind_scroll(self.canvas)
        self._bind_scroll(self.inner)

    def _bind_scroll(self, widget):
        widget.bind("<MouseWheel>", self._on_scroll)

    def _on_scroll(self, e):
        self.canvas.yview_scroll(int(-1 * e.delta / 120), "units")

    # ── Data ──────────────────────────────────────────────────────────────────

    def _load(self):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                self.games = json.load(f)
        except Exception as e:
            self.status_var.set(f"Error: {e}")
            return
        self._preload_images()
        self._render_grid()
        self.status_var.set(f"{len(self.games)} games  •  click a number to change weight, saves instantly")

    def _save(self):
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
            self.status_var.set("Saved.")
        except Exception as e:
            self.status_var.set(f"Save failed: {e}")

    # ── Images ────────────────────────────────────────────────────────────────

    def _preload_images(self):
        placeholder = Image.new("RGB", (TILE_SIZE, TILE_SIZE), (40, 40, 40))
        for game in self.games:
            img_rel = game.get("image", "")
            img_full = JSON_PATH.parent / img_rel if img_rel else None
            try:
                src = Image.open(img_full).convert("RGB").resize(
                    (TILE_SIZE, TILE_SIZE), Image.LANCZOS)
            except Exception:
                src = placeholder
            self._photos[game["id"]] = ImageTk.PhotoImage(src)

    # ── Grid ──────────────────────────────────────────────────────────────────

    def _render_grid(self):
        for w in self.inner.winfo_children():
            w.destroy()
        self._weight_vars.clear()

        for i, game in enumerate(sorted(self.games, key=lambda g: g.get("name", "").lower())):
            gid   = game["id"]
            row, col = divmod(i, GRID_COLS)
            self._make_card(game, gid, row, col)

    def _make_card(self, game: dict, gid: int, row: int, col: int):
        card = tk.Frame(self.inner, bg=CARD_BG, padx=4, pady=6)
        card.grid(row=row, column=col, padx=4, pady=4, sticky="n")

        img_lbl = tk.Label(card, image=self._photos.get(gid), bg=CARD_BG, bd=0)
        img_lbl.pack()

        tk.Label(card, text=game.get("name", "?"), bg=CARD_BG, fg="#bbb",
                 font=("Segoe UI", 7), wraplength=TILE_SIZE - 4,
                 justify="center").pack(pady=(3, 1))

        var = tk.IntVar(value=game.get("weight", 1))
        self._weight_vars[gid] = var

        radio_row = tk.Frame(card, bg=CARD_BG)
        radio_row.pack()

        for val in range(1, 6):
            rb = tk.Radiobutton(
                radio_row, text=str(val), variable=var, value=val,
                bg=CARD_BG, fg=WEIGHT_COLORS[val],
                selectcolor="#333333",
                activebackground=CARD_BG, activeforeground=WEIGHT_COLORS[val],
                font=("Segoe UI", 8, "bold"),
                command=lambda g=game, v=var: self._on_weight_change(g, v),
            )
            rb.pack(side="left", padx=1)
            self._bind_scroll(rb)

        self._bind_scroll(card)
        self._bind_scroll(img_lbl)

    def _on_weight_change(self, game: dict, var: tk.IntVar):
        game["weight"] = var.get()
        self._save()


def main():
    root = tk.Tk()
    WeightEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
