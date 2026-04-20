#!/usr/bin/env python3
"""
Board Game Category Manager
Left panel  — category list; add / delete.
Right panel — image tile grid; green = in category, click to toggle.
"""

import json
import tkinter as tk
from tkinter import messagebox, simpledialog
from pathlib import Path
from PIL import Image, ImageTk

JSON_PATH  = Path(__file__).parent / "boardgames.json"
TILE_SIZE  = 250          # px per tile (square)
GRID_COLS  = 5
GREEN      = (45, 106, 79)   # #2d6a4f
TINT_ALPHA = 0.55


class CategoryManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Category Manager")
        self.root.geometry("860x600")
        self.root.configure(bg="#1a1a1a")
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        self.games: list[dict] = []
        self.dirty = False
        self._active_category: str | None = None

        # game_id → (normal_photo, tinted_photo)
        self._tile_photos: dict[int, tuple] = {}
        # game_id → Label widget (current tile)
        self._tile_labels: dict[int, tk.Label] = {}
        # game_id → bool (in active category)
        self._game_states: dict[int, bool] = {}

        self._build_ui()
        self._load()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        top = tk.Frame(self.root, bg="#1a1a1a", padx=12, pady=8)
        top.pack(fill="x")

        tk.Label(top, text="Category Manager", bg="#1a1a1a", fg="#ccc",
                 font=("Segoe UI", 11, "bold")).pack(side="left")

        tk.Button(top, text="Save", command=self._save,
                  bg="#2d6a4f", fg="#fff", relief="flat",
                  padx=14, pady=4, font=("Segoe UI", 9, "bold"),
                  activebackground="#40916c").pack(side="right")

        self.status_var = tk.StringVar(value="")
        tk.Label(top, textvariable=self.status_var, bg="#1a1a1a", fg="#666",
                 font=("Segoe UI", 8)).pack(side="right", padx=12)

        main = tk.Frame(self.root, bg="#1a1a1a")
        main.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        main.columnconfigure(0, weight=0)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        self._build_left(main)
        self._build_right(main)

    def _build_left(self, parent):
        left = tk.Frame(parent, bg="#242424", padx=10, pady=10, width=200)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        left.grid_propagate(False)
        left.rowconfigure(1, weight=1)

        tk.Label(left, text="Categories", bg="#242424", fg="#aaa",
                 font=("Segoe UI", 9, "bold")).grid(
                 row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))

        lb_frame = tk.Frame(left, bg="#242424")
        lb_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        lb_frame.rowconfigure(0, weight=1)
        lb_frame.columnconfigure(0, weight=1)

        self.cat_listbox = tk.Listbox(
            lb_frame, bg="#1a1a1a", fg="#ddd",
            selectbackground="#2d6a4f", selectforeground="#fff",
            relief="flat", bd=0, font=("Segoe UI", 9), activestyle="none")
        vsb = tk.Scrollbar(lb_frame, command=self.cat_listbox.yview)
        self.cat_listbox.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        self.cat_listbox.grid(row=0, column=0, sticky="nsew")
        self.cat_listbox.bind("<<ListboxSelect>>", self._on_cat_select)

        btn_row = tk.Frame(left, bg="#242424")
        btn_row.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        tk.Button(btn_row, text="+ New", command=self._add_category,
                  bg="#3a3a3a", fg="#ccc", relief="flat",
                  font=("Segoe UI", 8), padx=10, pady=3,
                  activebackground="#505050").pack(side="left")

        tk.Button(btn_row, text="Delete", command=self._delete_category,
                  bg="#3a3a3a", fg="#c77", relief="flat",
                  font=("Segoe UI", 8), padx=10, pady=3,
                  activebackground="#505050").pack(side="right")

    def _build_right(self, parent):
        right = tk.Frame(parent, bg="#1a1a1a")
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        hdr = tk.Frame(right, bg="#1a1a1a", pady=4)
        hdr.grid(row=0, column=0, sticky="ew")

        self.right_label = tk.Label(hdr, text="← select a category",
                                     bg="#1a1a1a", fg="#aaa",
                                     font=("Segoe UI", 9, "bold"))
        self.right_label.pack(side="left")

        self.none_btn = tk.Button(hdr, text="None", command=self._select_none,
                                   bg="#3a3a3a", fg="#ccc", relief="flat",
                                   font=("Segoe UI", 8), padx=6, pady=2,
                                   activebackground="#505050", state="disabled")
        self.none_btn.pack(side="right", padx=(4, 0))

        self.all_btn = tk.Button(hdr, text="All", command=self._select_all,
                                  bg="#3a3a3a", fg="#ccc", relief="flat",
                                  font=("Segoe UI", 8), padx=6, pady=2,
                                  activebackground="#505050", state="disabled")
        self.all_btn.pack(side="right")

        cf = tk.Frame(right, bg="#111111")
        cf.grid(row=1, column=0, sticky="nsew")
        cf.rowconfigure(0, weight=1)
        cf.columnconfigure(0, weight=1)

        self.game_canvas = tk.Canvas(cf, bg="#111111", highlightthickness=0)
        vsb = tk.Scrollbar(cf, command=self.game_canvas.yview)
        self.game_canvas.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")
        self.game_canvas.grid(row=0, column=0, sticky="nsew")

        self.game_inner = tk.Frame(self.game_canvas, bg="#111111")
        self._game_win = self.game_canvas.create_window(
            (0, 0), window=self.game_inner, anchor="nw")

        self.game_inner.bind("<Configure>", lambda e: self.game_canvas.configure(
            scrollregion=(0, 0, e.width, e.height)))
        self.game_canvas.bind("<Configure>", lambda e: self.game_canvas.itemconfig(
            self._game_win, width=e.width))
        self.game_canvas.bind("<MouseWheel>", lambda e: self.game_canvas.yview_scroll(
            int(-1 * e.delta / 120), "units"))

    # ── Data ──────────────────────────────────────────────────────────────────

    def _load(self):
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                self.games = json.load(f)
        except Exception as e:
            messagebox.showerror("Error", f"Could not load boardgames.json:\n{e}")
            return
        self._preload_tile_photos()
        self._refresh_cat_list()
        self.status_var.set(f"{len(self.games)} games loaded")

    def _save(self):
        for game in self.games:
            if "category" in game and not game["category"]:
                del game["category"]
        try:
            with open(JSON_PATH, "w", encoding="utf-8") as f:
                json.dump(self.games, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Save failed", str(e))
            return
        self.dirty = False
        self.status_var.set("Saved.")
        self._refresh_cat_list(keep_selection=True)

    def _on_close(self):
        if self.dirty:
            if not messagebox.askyesno("Unsaved changes",
                                        "You have unsaved changes. Quit anyway?"):
                return
        self.root.destroy()

    # ── Tile image pre-loading ────────────────────────────────────────────────

    def _preload_tile_photos(self):
        self._tile_photos.clear()
        for game in self.games:
            gid = game["id"]
            img_path = game.get("image", "")
            normal, tinted = self._make_tile_images(img_path)
            self._tile_photos[gid] = (normal, tinted)

    def _make_tile_images(self, image_path: str):
        placeholder = Image.new("RGB", (TILE_SIZE, TILE_SIZE), (30, 30, 30))
        full = JSON_PATH.parent / image_path if image_path else None

        if full and full.exists():
            try:
                src = Image.open(full).convert("RGB")
                src = src.resize((TILE_SIZE, TILE_SIZE), Image.LANCZOS)
            except Exception:
                src = placeholder
        else:
            src = placeholder

        # Tinted version: blend with green
        green_layer = Image.new("RGB", (TILE_SIZE, TILE_SIZE), GREEN)
        tinted = Image.blend(src, green_layer, TINT_ALPHA)

        return ImageTk.PhotoImage(src), ImageTk.PhotoImage(tinted)

    # ── Category list ─────────────────────────────────────────────────────────

    def _all_categories(self) -> list[str]:
        cats: set[str] = set()
        for g in self.games:
            cats.update(g.get("category", []))
        return sorted(cats)

    def _refresh_cat_list(self, keep_selection=False):
        prev = self._active_category if keep_selection else None
        self.cat_listbox.delete(0, "end")
        for cat in self._all_categories():
            self.cat_listbox.insert("end", cat)
        if prev and prev in self._all_categories():
            idx = self._all_categories().index(prev)
            self.cat_listbox.selection_set(idx)
            self.cat_listbox.see(idx)

    def _on_cat_select(self, _event):
        sel = self.cat_listbox.curselection()
        if not sel:
            return
        cat = self.cat_listbox.get(sel[0])
        self._active_category = cat
        self._render_tile_grid(cat)

    def _add_category(self):
        name = simpledialog.askstring("New Category", "Category name:",
                                       parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()
        if name in self._all_categories():
            messagebox.showinfo("Already exists", f'"{name}" already exists.')
            self._select_cat(name)
            return
        all_cats = sorted(self._all_categories() + [name])
        self.cat_listbox.delete(0, "end")
        for c in all_cats:
            self.cat_listbox.insert("end", c)
        self._select_cat(name)

    def _select_cat(self, name: str):
        items = list(self.cat_listbox.get(0, "end"))
        if name in items:
            idx = items.index(name)
            self.cat_listbox.selection_clear(0, "end")
            self.cat_listbox.selection_set(idx)
            self.cat_listbox.see(idx)
        self._active_category = name
        self._render_tile_grid(name)

    def _delete_category(self):
        sel = self.cat_listbox.curselection()
        if not sel:
            return
        cat = self.cat_listbox.get(sel[0])
        if not messagebox.askyesno("Delete category",
                                    f'Remove "{cat}" from all games?'):
            return
        for game in self.games:
            cats = game.get("category", [])
            if cat in cats:
                cats.remove(cat)
        self.dirty = True
        self._active_category = None
        self._refresh_cat_list()
        self.right_label.config(text="← select a category")
        for w in self.game_inner.winfo_children():
            w.destroy()
        self._tile_labels.clear()
        self._game_states.clear()
        self.all_btn.config(state="disabled")
        self.none_btn.config(state="disabled")
        self.status_var.set("Unsaved changes")

    # ── Tile grid ─────────────────────────────────────────────────────────────

    def _render_tile_grid(self, category: str):
        self.right_label.config(text=f'"{category}"')
        self.all_btn.config(state="normal")
        self.none_btn.config(state="normal")

        for w in self.game_inner.winfo_children():
            w.destroy()
        self._tile_labels.clear()
        self._game_states.clear()

        sorted_games = sorted(self.games, key=lambda g: g.get("name", "").lower())

        for i, game in enumerate(sorted_games):
            gid = game["id"]
            in_cat = category in game.get("category", [])
            self._game_states[gid] = in_cat

            row, col = divmod(i, GRID_COLS)
            normal, tinted = self._tile_photos.get(gid, (None, None))
            photo = tinted if in_cat else normal

            lbl = tk.Label(self.game_inner, image=photo, bg="#111111",
                           cursor="hand2", bd=0)
            lbl.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            lbl.bind("<Button-1>",
                     lambda e, g=game, c=category: self._toggle_tile(g, c))

            # Bind scroll on tiles too
            lbl.bind("<MouseWheel>", lambda e: self.game_canvas.yview_scroll(
                int(-1 * e.delta / 120), "units"))

            self._tile_labels[gid] = lbl

    def _toggle_tile(self, game: dict, category: str):
        gid = game["id"]
        now_in = not self._game_states.get(gid, False)
        self._game_states[gid] = now_in

        cats: list = game.setdefault("category", [])
        if now_in:
            if category not in cats:
                cats.append(category)
                cats.sort()
        else:
            if category in cats:
                cats.remove(category)

        # Swap image
        normal, tinted = self._tile_photos.get(gid, (None, None))
        lbl = self._tile_labels.get(gid)
        if lbl:
            lbl.config(image=tinted if now_in else normal)

        self.dirty = True
        self.status_var.set("Unsaved changes")

        # Persist new category to listbox if needed
        if category not in list(self.cat_listbox.get(0, "end")):
            self._refresh_cat_list()
            self._select_cat(category)

    def _select_all(self):
        cat = self._active_category
        if not cat:
            return
        for game in self.games:
            gid = game["id"]
            cats: list = game.setdefault("category", [])
            if cat not in cats:
                cats.append(cat)
                cats.sort()
            self._game_states[gid] = True
            _, tinted = self._tile_photos.get(gid, (None, None))
            lbl = self._tile_labels.get(gid)
            if lbl and tinted:
                lbl.config(image=tinted)
        self.dirty = True
        self.status_var.set("Unsaved changes")

    def _select_none(self):
        cat = self._active_category
        if not cat:
            return
        for game in self.games:
            gid = game["id"]
            cats = game.get("category", [])
            if cat in cats:
                cats.remove(cat)
            self._game_states[gid] = False
            normal, _ = self._tile_photos.get(gid, (None, None))
            lbl = self._tile_labels.get(gid)
            if lbl and normal:
                lbl.config(image=normal)
        self.dirty = True
        self.status_var.set("Unsaved changes")


def main():
    root = tk.Tk()
    CategoryManager(root)
    root.mainloop()


if __name__ == "__main__":
    main()
