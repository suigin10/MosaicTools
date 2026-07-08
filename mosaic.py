# -*- coding: utf-8 -*-
# Mosaic Tools - Tkinter GUI Mosaic Tool (jpg/png/webp) with Live Preview
# 依存: Pillow, tkinterdnd2
import sys
from io import BytesIO
from pathlib import Path
from typing import List, Tuple, Optional

from PIL import Image, ImageOps, PngImagePlugin
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}


# -------------------------
# 画像処理ユーティリティ
# -------------------------
def ensure_mode(img: Image.Image) -> Image.Image:
    if img.mode in ("RGB", "RGBA"):
        return img
    if "A" in img.getbands():
        return img.convert("RGBA")
    return img.convert("RGB")


def mosaic_patch(img: Image.Image, box: Tuple[int, int, int, int], block: int) -> None:
    # 原寸用（保存時）
    x, y, w, h = box
    x2, y2 = x + w, y + h
    x, y = max(0, x), max(0, y)
    x2, y2 = min(img.width, x2), min(img.height, y2)
    if x >= x2 or y >= y2:
        return
    crop = img.crop((x, y, x2, y2))
    small_w = max(1, crop.width // max(1, block))
    small_h = max(1, crop.height // max(1, block))
    small = crop.resize((small_w, small_h), Image.NEAREST)
    big = small.resize(crop.size, Image.NEAREST)
    img.paste(big, (x, y))


def mosaic_patch_preview(
    img_preview: Image.Image,
    box_px: Tuple[int, int, int, int],
    block_preview: int,
) -> None:
    # プレビュー用（縮小後の画像に対して適用）
    x, y, w, h = box_px
    x2, y2 = x + w, y + h
    x, y = max(0, x), max(0, y)
    x2, y2 = min(img_preview.width, x2), min(img_preview.height, y2)
    if x >= x2 or y >= y2:
        return
    crop = img_preview.crop((x, y, x2, y2))
    small_w = max(1, crop.width // max(1, block_preview))
    small_h = max(1, crop.height // max(1, block_preview))
    small = crop.resize((small_w, small_h), Image.NEAREST)
    big = small.resize(crop.size, Image.NEAREST)
    img_preview.paste(big, (x, y))


# -------- PNGのテキスト系メタを丸ごと複製（tEXt/iTXt） --------
def build_pnginfo_with_text(src: Image.Image) -> Optional[PngImagePlugin.PngInfo]:
    """
    PNGのtEXt/iTXt系メタ（例: 'parameters', 'prompt' など）を可能な限り再生成する。
    - src.text（PillowのPngImagePluginが持つ辞書）を優先
    - 足りない場合は src.info の文字列値も拾う
    文字はUTF-8のiTXtで保存（日本語や長文でも安全）
    """
    pnginfo = PngImagePlugin.PngInfo()
    had_any = False

    # 1) .text（Pillowが抽出したテキストチャンク）
    text_map = getattr(src, "text", {}) or {}
    for k, v in text_map.items():
        try:
            pnginfo.add_itxt(k, v)
            had_any = True
        except Exception:
            pass

    # 2) .info にある文字列系キーも拾う（重複は避ける）
    existing = set(text_map.keys())
    for k, v in (getattr(src, "info", {}) or {}).items():
        if isinstance(v, str) and k not in existing:
            try:
                pnginfo.add_itxt(k, v)
                had_any = True
            except Exception:
                pass

    return pnginfo if had_any else None


# -------------------------
# 保存（JPEG/PNG/WebP）— メタデータ保持強化版
# -------------------------
def process_save(
    in_path: Path,
    regions: List[Tuple[int, int, int, int]],
    block: int,
    quality: int,
    webp_lossless: bool,
    suffix: str = "_mosaic",
) -> Path:
    with Image.open(in_path) as im0:
        # 向き補正 + モード整形
        im = ensure_mode(ImageOps.exif_transpose(im0))

        # モザイク適用（指定がなければ全体）
        if not regions:
            regions = [(0, 0, im.width, im.height)]
        for r in regions:
            mosaic_patch(im, r, block)

        # 出力パス
        out_path = in_path.with_name(in_path.stem + suffix + in_path.suffix)

        # メタデータ雛形
        save_kwargs = {}

        # EXIF（補正後から取り直す）— JPEG/PNG/WebP いずれも対応
        try:
            exif_bytes = im.getexif().tobytes()
            if exif_bytes:
                save_kwargs["exif"] = exif_bytes
        except Exception:
            pass

        # ICCプロファイル（共通）
        if "icc_profile" in im0.info:
            save_kwargs["icc_profile"] = im0.info["icc_profile"]

        ext = in_path.suffix.lower()

        # ---------- JPEG ----------
        if ext in (".jpg", ".jpeg"):
            im = im.convert("RGB")
            # subsampling='keep' は環境で失敗しやすいので数値に統一
            subsampling = im0.info.get("subsampling", 0) if getattr(im0, "format", "") == "JPEG" else 0
            save_kwargs.update(
                dict(
                    quality=int(quality),
                    subsampling=int(subsampling),
                    progressive=True,
                    optimize=True,
                )
            )
            im.save(out_path, format="JPEG", **save_kwargs)

        # ---------- PNG ----------
        elif ext == ".png":
            # tEXt/iTXt を丸ごと復元
            pnginfo = build_pnginfo_with_text(im0)
            if pnginfo:
                save_kwargs["pnginfo"] = pnginfo
            # PNGのeXIfチャンク（あれば）も書ける
            if "exif" in save_kwargs and not save_kwargs["exif"]:
                save_kwargs.pop("exif", None)
            save_kwargs["optimize"] = True
            im.save(out_path, format="PNG", **save_kwargs)

        # ---------- WebP ----------
        elif ext == ".webp":
            # WebPのXMP/EXIF/ICCを維持（ソースにあれば）
            # Pillowは 'exif' 'icc_profile' 'xmp' を受け付ける
            if "exif" in im0.info and im0.info["exif"]:
                save_kwargs["exif"] = im0.info["exif"]
            if "xmp" in im0.info and im0.info["xmp"]:
                save_kwargs["xmp"] = im0.info["xmp"]
            if "icc_profile" in im0.info and im0.info["icc_profile"]:
                save_kwargs["icc_profile"] = im0.info["icc_profile"]

            if webp_lossless:
                save_kwargs["lossless"] = True
            else:
                save_kwargs["quality"] = int(quality)
            im.save(out_path, format="WEBP", **save_kwargs)

        else:
            raise ValueError("未対応拡張子")

        return out_path


# -------------------------
# Tkinter GUI（ライブ反映付き）
# -------------------------
class MosaicGUI(TkinterDnD.Tk):
    def __init__(self, start_file: Optional[str] = None):
        super().__init__()
        self.title("Mosaic Tools")
        self.geometry("1120x780")

        # 画像と状態
        self.file: Optional[Path] = None
        self.im: Optional[Image.Image] = None        # 編集ベース（向き補正・モード整形）
        self.photo: Optional[tk.PhotoImage] = None
        self.regions: List[Tuple[int, int, int, int]] = []

        # 表示サイズとスケール
        self.canvas_w = 900
        self.canvas_h = 720
        self.scale = 1.0
        self.off_x = 0
        self.off_y = 0

        # ドラッグ中の仮矩形（Canvas座標で保持→都度画像座標へ変換）
        self.drag_start_canvas: Optional[Tuple[int, int]] = None
        self.drag_curr_canvas: Optional[Tuple[int, int]] = None

        self._build_ui()

        # ドラッグ&ドロップ登録
        self.drop_target_register(DND_FILES)
        self.dnd_bind("<<Drop>>", self.on_drop)

        # 起動時にファイルが渡されていたら即ロード
        if start_file:
            p = Path(start_file)
            if p.exists() and p.suffix.lower() in SUPPORTED_EXTS:
                self.load_image(p)

    def _build_ui(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=8, pady=8)

        # 左: Canvas
        left = ttk.Frame(container)
        left.pack(side="left", fill="both", expand=True)

        self.canvas = tk.Canvas(
            left,
            width=self.canvas_w,
            height=self.canvas_h,
            bg="#222222",
            highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # 右: コントロール
        right = ttk.Frame(container, width=300)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        # ファイル
        file_row = ttk.Frame(right)
        file_row.pack(fill="x", pady=(0, 6))
        ttk.Label(file_row, text="ファイル:").pack(side="left")
        self.var_path = tk.StringVar()
        ttk.Entry(file_row, textvariable=self.var_path).pack(
            side="left", fill="x", expand=True, padx=4
        )
        ttk.Button(file_row, text="開く", command=self.open_file).pack(side="left")

        # ブロックサイズ（ライブ反映）
        ttk.Label(right, text="ブロック(px)").pack(anchor="w")
        self.var_block = tk.IntVar(value=10)
        self.scale_block = ttk.Scale(
            right,
            from_=2,
            to=80,
            orient="horizontal",
            command=lambda v: self.on_block_changed(int(float(v))),
        )
        self.scale_block.set(10)
        self.scale_block.pack(fill="x")
        ttk.Label(right, textvariable=self.var_block).pack(anchor="e")

        # 品質（保存時のみ影響／UIに合わせて再描画）
        ttk.Label(right, text="品質 (JPEG/WebP)").pack(anchor="w", pady=(8, 0))
        self.var_quality = tk.IntVar(value=100)
        self.scale_q = ttk.Scale(
            right,
            from_=10,
            to=100,
            orient="horizontal",
            command=lambda v: self.on_quality_changed(int(float(v))),
        )
        self.scale_q.set(100)
        self.scale_q.pack(fill="x")
        ttk.Label(right, textvariable=self.var_quality).pack(anchor="e")

        # Lossless
        self.var_lossless = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            right,
            text="WebPを可逆 (lossless) で保存",
            variable=self.var_lossless,
        ).pack(anchor="w", pady=(8, 8))

        # サフィックス
        ttk.Label(right, text="出力サフィックス").pack(anchor="w")
        self.var_suffix = tk.StringVar(value="_mosaic")
        ttk.Entry(right, textvariable=self.var_suffix).pack(fill="x", pady=(0, 8))

        # 矩形一覧
        ttk.Label(right, text="矩形リスト (x,y,w,h)").pack(anchor="w")
        self.listbox = tk.Listbox(right, height=10, font=("Consolas", 10))
        self.listbox.pack(fill="both", expand=True)

        btns = ttk.Frame(right)
        btns.pack(fill="x", pady=6)
        ttk.Button(btns, text="最後を削除", command=self.pop_region).pack(
            side="left", expand=True, fill="x"
        )
        ttk.Button(btns, text="全消去", command=self.clear_regions).pack(
            side="left", expand=True, fill="x"
        )

        # 手入力追加
        manual_row = ttk.Frame(right)
        manual_row.pack(fill="x")
        ttk.Label(manual_row, text="追加 (x,y,w,h):").pack(side="left")
        self.var_manual = tk.StringVar()
        ttk.Entry(manual_row, textvariable=self.var_manual, width=18).pack(
            side="left", padx=4
        )
        ttk.Button(manual_row, text="追加", command=self.add_manual).pack(side="left")

        # 保存
        ttk.Button(right, text="この設定で保存", command=self.save_image).pack(
            fill="x", pady=(10, 0)
        )
        ttk.Label(
            right,
            text="保存先は同フォルダに *_mosaic を付与\n透過/EXIF/ICC/メタデータを可能な範囲で保持",
        ).pack(anchor="w", pady=(6, 0))

        # macOS ダークテーマ対策（任意）
        try:
            self.style = ttk.Style(self)
            if sys.platform == "darwin":
                self.style.theme_use("clam")
        except Exception:
            pass

    # ---------- ファイル操作 ----------
    def load_image(self, p: Path):
        if p.suffix.lower() not in SUPPORTED_EXTS:
            messagebox.showerror("エラー", "未対応拡張子です")
            return

        try:
            im0 = Image.open(p)
            self.im = ensure_mode(ImageOps.exif_transpose(im0))
            self.file = p
            self.var_path.set(str(p))
            self.regions.clear()
            self.listbox_delete_all()
            self.drag_start_canvas = None
            self.drag_curr_canvas = None
            self.redraw_preview()
        except Exception as e:
            messagebox.showerror("エラー", f"読み込み失敗：{e}")

    def open_file(self):
        file = filedialog.askopenfilename(
            title="画像を選択",
            filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.webp"), ("All", "*.*")],
        )
        if not file:
            return
        self.load_image(Path(file))

    def on_drop(self, event):
        data = event.data.strip()
        if not data:
            return

        try:
            paths = self.tk.splitlist(data)
        except Exception:
            paths = [data]

        if not paths:
            return

        p = Path(paths[0].strip("{}"))
        self.load_image(p)

    # ---------- スライダー即時反映 ----------
    def on_block_changed(self, v: int):
        self.var_block.set(v)
        self.redraw_preview()

    def on_quality_changed(self, v: int):
        self.var_quality.set(v)
        self.redraw_preview()

    # ---------- プレビュー描画（ライブ反映の要） ----------
    def redraw_preview(self):
        canvas = self.canvas
        canvas.delete("all")
        if not self.im:
            return

        w, h = self.im.width, self.im.height

        # 表示スケールと中央寄せ
        self.scale = min(self.canvas_w / w, self.canvas_h / h, 1.0)
        disp_w, disp_h = int(w * self.scale), int(h * self.scale)
        self.off_x = (self.canvas_w - disp_w) // 2
        self.off_y = (self.canvas_h - disp_h) // 2

        # 1) プレビュー元（縮小）を作成
        base_preview = self.im.resize((disp_w, disp_h), Image.NEAREST).convert("RGBA")
        preview = base_preview.copy()

        # 2) 確定矩形 + 仮矩形をプレビュー座標系に変換してモザイク適用
        block_orig = max(1, int(self.var_block.get()))
        block_preview = max(1, int(block_orig * self.scale))  # 原寸ブロック→プレビューブロック

        # 確定矩形
        for (x, y, rw, rh) in self.regions:
            bx = int(x * self.scale)
            by = int(y * self.scale)
            bw = max(1, int(rw * self.scale))
            bh = max(1, int(rh * self.scale))
            mosaic_patch_preview(preview, (bx, by, bw, bh), block_preview)

        # 仮矩形（ドラッグ中）
        temp_box_img = self.get_temp_rect_image_space()
        if temp_box_img:
            tx, ty, tw, th = temp_box_img
            bx = int(tx * self.scale)
            by = int(ty * self.scale)
            bw = max(1, int(tw * self.scale))
            bh = max(1, int(th * self.scale))
            mosaic_patch_preview(preview, (bx, by, bw, bh), block_preview)

        # 3) 画像描画
        data = BytesIO()
        preview.save(data, format="PNG")
        self.photo = tk.PhotoImage(data=data.getvalue())
        canvas.create_image(self.off_x, self.off_y, image=self.photo, anchor="nw")

        # 4) 枠線（見やすさ用）
        for (x, y, rw, rh) in self.regions:
            self._draw_rect_scaled(x, y, rw, rh, outline="#00FFD0")
        if temp_box_img:
            tx, ty, tw, th = temp_box_img
            self._draw_rect_scaled(tx, ty, tw, th, outline="#FFE066")

    def _draw_rect_scaled(self, x, y, w, h, outline="#00FFD0", width=2):
        x1 = self.off_x + int(x * self.scale)
        y1 = self.off_y + int(y * self.scale)
        x2 = self.off_x + int((x + w) * self.scale)
        y2 = self.off_y + int((y + h) * self.scale)
        self.canvas.create_rectangle(x1, y1, x2, y2, outline=outline, width=width)

    # 仮矩形（Canvas座標 → 画像座標ボックス）
    def get_temp_rect_image_space(self) -> Optional[Tuple[int, int, int, int]]:
        if not (self.drag_start_canvas and self.drag_curr_canvas and self.im):
            return None

        (sx, sy) = self.drag_start_canvas
        (ex, ey) = self.drag_curr_canvas

        p1 = self.canvas_to_image_xy(sx, sy)
        p2 = self.canvas_to_image_xy(ex, ey)
        if not (p1 and p2):
            return None

        x1, y1 = p1
        x2, y2 = p2
        x = min(x1, x2)
        y = min(y1, y2)
        w = max(1, abs(x2 - x1))
        h = max(1, abs(y2 - y1))
        return (x, y, w, h)

    def canvas_to_image_xy(self, cx: int, cy: int) -> Optional[Tuple[int, int]]:
        if not self.im:
            return None

        w, h = self.im.width, self.im.height
        disp_w, disp_h = int(w * self.scale), int(h * self.scale)

        if not (self.off_x <= cx <= self.off_x + disp_w and self.off_y <= cy <= self.off_y + disp_h):
            return None

        ix = int((cx - self.off_x) / self.scale)
        iy = int((cy - self.off_y) / self.scale)
        ix = max(0, min(ix, w))
        iy = max(0, min(iy, h))
        return ix, iy

    # ---------- マウス操作（ドラッグ中もライブ適用） ----------
    def on_mouse_down(self, e):
        self.drag_start_canvas = (e.x, e.y)
        self.drag_curr_canvas = (e.x, e.y)
        self.redraw_preview()

    def on_mouse_drag(self, e):
        if self.drag_start_canvas:
            self.drag_curr_canvas = (e.x, e.y)
            self.redraw_preview()

    def on_mouse_up(self, e):
        if not self.drag_start_canvas:
            return

        self.drag_curr_canvas = (e.x, e.y)
        temp = self.get_temp_rect_image_space()
        self.drag_start_canvas = None
        self.drag_curr_canvas = None

        if temp:
            self.regions.append(temp)
            self.listbox_insert(temp)

        self.redraw_preview()

    # ---------- 矩形リスト ----------
    def listbox_insert(self, box: Tuple[int, int, int, int]):
        x, y, w, h = box
        self.listbox.insert(tk.END, f"{x:4d},{y:4d},{w:4d},{h:4d}")

    def listbox_delete_all(self):
        self.listbox.delete(0, tk.END)

    def pop_region(self):
        if self.regions:
            self.regions.pop()
            self.listbox_delete_all()
            for b in self.regions:
                self.listbox_insert(b)
            self.redraw_preview()

    def clear_regions(self):
        if self.regions and messagebox.askyesno("確認", "矩形を全て消去しますか？"):
            self.regions.clear()
            self.listbox_delete_all()
            self.redraw_preview()

    def add_manual(self):
        s = getattr(self, "var_manual", tk.StringVar()).get().strip()
        try:
            x, y, w, h = map(int, s.split(","))
            if w <= 0 or h <= 0:
                raise ValueError
            self.regions.append((x, y, w, h))
            self.var_manual.set("")
            self.listbox_insert((x, y, w, h))
            self.redraw_preview()
        except Exception:
            messagebox.showerror(
                "エラー",
                "x,y,w,h を整数で指定してください（例: 100,120,300,250）",
            )

    # ---------- 保存（原寸適用） ----------
    def save_image(self):
        if not self.file:
            messagebox.showwarning("注意", "先に画像を開いてください")
            return

        try:
            out = process_save(
                self.file,
                regions=self.regions,
                block=max(1, int(self.var_block.get())),
                quality=max(10, min(100, int(self.var_quality.get()))),
                webp_lossless=bool(self.var_lossless.get()),
                suffix=self.var_suffix.get() or "_mosaic",
            )
            messagebox.showinfo("完了", f"保存しました：{out.name}")
        except Exception as e:
            messagebox.showerror("エラー", f"保存に失敗しました：{e}")


def main():
    # bat/ショートカット/ドラッグ&ドロップで渡された最初の引数を受ける
    start_file = sys.argv[1] if len(sys.argv) >= 2 else None
    app = MosaicGUI(start_file=start_file)
    app.mainloop()


if __name__ == "__main__":
    main()