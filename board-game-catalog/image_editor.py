#!/usr/bin/env python3
"""
Board Game Image Editor
Crop and position game images into a 200x200 WebP for the catalog.
Drag to reposition, scroll to zoom, Save overwrites the original file.
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from pathlib import Path

IMAGES_DIR   = Path(__file__).parent / "images"
OUTPUT_SIZE  = 200   # saved file size
CANVAS_SIZE  = 400   # editor display size (2× output for easier control)
THUMB_SIZE   = 110
THUMB_COLS   = 3
BG_COLOR     = (17, 17, 17)   # #111 — matches catalog background
WEBP_QUALITY = 85


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Board Game Image Editor")
        self.root.configure(bg="#1a1a1a")
        self.root.geometry("940x660")
        self.root.minsize(720, 500)

        # Editor state
        self.source_image: Image.Image | None = None
        self.current_path: Path | None = None
        self.img_x = 0.0
        self.img_y = 0.0
        self.scale = 1.0
        self._drag_start: tuple[int, int] | None = None
        self._canvas_photo = None   # ImageTk ref — must stay alive
        self._thumb_refs:  list     = []

        self._build_ui()
        self._load_thumbnails()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ── Left panel: thumbnail browser ─────────────────────────────────
        left = tk.Frame(self.root, bg="#1a1a1a", width=508)
        left.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        left.grid_propagate(False)

        tk.Label(left, text="Images", bg="#1a1a1a", fg="#999",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        container = tk.Frame(left, bg="#1a1a1a")
        container.pack(fill="both", expand=True)

        self.thumb_canvas = tk.Canvas(container, bg="#1a1a1a",
                                       highlightthickness=0)
        vsb = tk.Scrollbar(container, orient="vertical",
                           command=self.thumb_canvas.yview)
        self.thumb_canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side="right", fill="y")
        self.thumb_canvas.pack(side="left", fill="both", expand=True)

        self.thumb_inner = tk.Frame(self.thumb_canvas, bg="#1a1a1a")
        self._thumb_window = self.thumb_canvas.create_window(
            (0, 0), window=self.thumb_inner, anchor="nw")
        self.thumb_inner.bind("<Configure>", self._on_thumb_configure)
        self.thumb_canvas.bind("<Configure>", lambda e: self.thumb_canvas.itemconfig(
            self._thumb_window, width=e.width))

        self.thumb_canvas.bind("<MouseWheel>", self._on_thumb_wheel)

        # ── Right panel: editor ────────────────────────────────────────────
        right = tk.Frame(self.root, bg="#242424", padx=20, pady=16)
        right.grid(row=0, column=1, sticky="nsew", padx=8, pady=8)
        right.columnconfigure(0, weight=1)

        tk.Label(right, text="Editor", bg="#242424", fg="#999",
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=(0, 4))

        self.filename_var = tk.StringVar(value="← select an image")
        tk.Label(right, textvariable=self.filename_var, bg="#242424",
                 fg="#ccc", font=("Segoe UI", 9)).pack(anchor="w", pady=(0, 12))

        # 200×200 canvas (the preview IS the output)
        canvas_wrap = tk.Frame(right, bg="#111111", bd=0,
                                highlightbackground="#555",
                                highlightthickness=1)
        canvas_wrap.pack()

        self.canvas = tk.Canvas(canvas_wrap, width=CANVAS_SIZE,
                                 height=CANVAS_SIZE, bg="#111111",
                                 cursor="fleur", highlightthickness=0)
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self._drag_start_cb)
        self.canvas.bind("<B1-Motion>",     self._drag_cb)
        self.canvas.bind("<MouseWheel>",    self._zoom_cb)

        tk.Label(right, text="drag to reposition   •   scroll to zoom",
                 bg="#242424", fg="#555",
                 font=("Segoe UI", 7)).pack(pady=(5, 0))

        # Buttons
        btn_row = tk.Frame(right, bg="#242424")
        btn_row.pack(pady=(20, 0))

        tk.Button(btn_row, text="Reset", command=self._reset,
                  bg="#3a3a3a", fg="#ccc", activebackground="#505050",
                  relief="flat", padx=14, pady=7,
                  font=("Segoe UI", 9)).pack(side="left", padx=(0, 10))

        tk.Button(btn_row, text="Save  200×200 WebP",
                  command=self._save,
                  bg="#2d6a4f", fg="#fff", activebackground="#40916c",
                  relief="flat", padx=14, pady=7,
                  font=("Segoe UI", 9, "bold")).pack(side="left")

    # ── Thumbnail panel ───────────────────────────────────────────────────────

    def _on_thumb_configure(self, event):
        self.thumb_canvas.configure(
            scrollregion=(0, 0, event.width, event.height))

    def _on_thumb_wheel(self, event):
        self.thumb_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _load_thumbnails(self):
        self._thumb_refs.clear()
        for w in self.thumb_inner.winfo_children():
            w.destroy()

        paths = sorted(IMAGES_DIR.glob("*.webp"))
        for i, path in enumerate(paths):
            self._add_thumb(path, *divmod(i, THUMB_COLS))

        self.root.update_idletasks()

    def _add_thumb(self, path: Path, row: int, col: int):
        # Load and fit thumbnail onto a black square
        try:
            img = Image.open(path).convert("RGB")
            img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
            square = Image.new("RGB", (THUMB_SIZE, THUMB_SIZE), BG_COLOR)
            ox = (THUMB_SIZE - img.width)  // 2
            oy = (THUMB_SIZE - img.height) // 2
            square.paste(img, (ox, oy))
            photo = ImageTk.PhotoImage(square)
            self._thumb_refs.append(photo)
        except Exception:
            photo = None

        cell = tk.Frame(self.thumb_inner, bg="#1a1a1a",
                         padx=3, pady=3, cursor="hand2")
        cell.grid(row=row, column=col, padx=2, pady=2, sticky="n")

        if photo:
            img_lbl = tk.Label(cell, image=photo, bg="#1a1a1a", bd=0)
            img_lbl.pack()

        short = path.stem if len(path.stem) <= 14 else path.stem[:13] + "…"
        tk.Label(cell, text=short, bg="#1a1a1a", fg="#777",
                 font=("Segoe UI", 7),
                 wraplength=THUMB_SIZE).pack()

        # Highlight on hover, open on click
        def _enter(_, f=cell):
            f.configure(bg="#2e2e2e")
            for w in f.winfo_children():
                try: w.configure(bg="#2e2e2e")
                except tk.TclError: pass

        def _leave(_, f=cell):
            f.configure(bg="#1a1a1a")
            for w in f.winfo_children():
                try: w.configure(bg="#1a1a1a")
                except tk.TclError: pass

        for widget in [cell] + list(cell.winfo_children()):
            widget.bind("<Button-1>",   lambda e, p=path: self._open(p))
            widget.bind("<MouseWheel>", self._on_thumb_wheel)
            widget.bind("<Enter>",      _enter)
            widget.bind("<Leave>",      _leave)

    # ── Editor ────────────────────────────────────────────────────────────────

    def _open(self, path: Path):
        try:
            self.source_image = Image.open(path).convert("RGB")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open:\n{e}")
            return
        self.current_path = path
        self.filename_var.set(path.name)
        self._reset()

    def _reset(self):
        if self.source_image is None:
            return
        w, h = self.source_image.size
        # Fit inside the display canvas, centered
        self.scale = min(CANVAS_SIZE / w, CANVAS_SIZE / h)
        sw = w * self.scale
        sh = h * self.scale
        self.img_x = (CANVAS_SIZE - sw) / 2
        self.img_y = (CANVAS_SIZE - sh) / 2
        self._render()

    def _render(self):
        if self.source_image is None:
            return
        self._canvas_photo = ImageTk.PhotoImage(
            self._build_frame(CANVAS_SIZE, self.img_x, self.img_y, self.scale))
        self.canvas.delete("all")
        self.canvas.create_image(0, 0, anchor="nw", image=self._canvas_photo)

    def _build_frame(self, size: int, img_x: float, img_y: float, scale: float) -> Image.Image:
        """Render source_image at (img_x, img_y, scale) onto a black square of `size`."""
        out = Image.new("RGB", (size, size), BG_COLOR)
        w, h   = self.source_image.size
        new_w  = max(1, int(w * scale))
        new_h  = max(1, int(h * scale))
        scaled = self.source_image.resize((new_w, new_h), Image.LANCZOS)
        px, py   = int(img_x), int(img_y)
        src_x    = max(0, -px)
        src_y    = max(0, -py)
        dst_x    = max(0, px)
        dst_y    = max(0, py)
        region_w = min(new_w - src_x, size - dst_x)
        region_h = min(new_h - src_y, size - dst_y)
        if region_w > 0 and region_h > 0:
            region = scaled.crop((src_x, src_y, src_x + region_w, src_y + region_h))
            out.paste(region, (dst_x, dst_y))
        return out

    # ── Interaction ───────────────────────────────────────────────────────────

    def _drag_start_cb(self, event):
        self._drag_start = (event.x, event.y)

    def _drag_cb(self, event):
        if self._drag_start is None or self.source_image is None:
            return
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        self.img_x += dx
        self.img_y += dy
        self._drag_start = (event.x, event.y)
        self._render()

    def _zoom_cb(self, event):
        if self.source_image is None:
            return
        factor = 1.1 if event.delta > 0 else (1 / 1.1)
        mx, my = event.x, event.y
        # Keep the image point under the cursor stationary
        self.img_x = mx - (mx - self.img_x) * factor
        self.img_y = my - (my - self.img_y) * factor
        self.scale *= factor
        self._render()

    # ── Save ──────────────────────────────────────────────────────────────────

    def _save(self):
        if self.source_image is None or self.current_path is None:
            messagebox.showwarning("Nothing to save", "Select an image first.")
            return

        # Scale canvas coords down to OUTPUT_SIZE space
        ratio     = OUTPUT_SIZE / CANVAS_SIZE
        save_x     = self.img_x * ratio
        save_y     = self.img_y * ratio
        save_scale = self.scale  * ratio
        out = self._build_frame(OUTPUT_SIZE, save_x, save_y, save_scale)

        try:
            out.save(self.current_path, "WebP", quality=WEBP_QUALITY, optimize=True)
        except Exception as e:
            messagebox.showerror("Save failed", str(e))
            return

        messagebox.showinfo("Saved", f"Saved {self.current_path.name}")
        self._load_thumbnails()   # refresh thumbnail strip


def main():
    root = tk.Tk()
    App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
