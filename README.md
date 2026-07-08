# Mosaic Tools

A small Windows-friendly GUI tool for applying mosaic/pixelation to JPG, PNG, and WebP images.

JPG / PNG / WebP 画像にモザイク処理をかけるための、シンプルなTkinter製GUIツールです。

---

## Features / 特徴

- Drag and drop image loading / 画像のドラッグ＆ドロップ読み込み
- Live preview while selecting a rectangle / 矩形選択中のライブプレビュー
- Multiple mosaic regions / 複数範囲のモザイク指定
- Manual region input: `x,y,w,h` / 座標の手入力追加
- JPG / PNG / WebP support / JPG・PNG・WebP対応
- Output suffix setting / 出力サフィックス指定
- Attempts to preserve EXIF / ICC / PNG text metadata / EXIF・ICC・PNGテキストメタデータを可能な範囲で保持

---

## Quick Start / すぐ使う

### Run from Python / Pythonから起動

Install dependencies:

```bat
pip install -r requirements.txt
```

Run:

```bat
python mosaic.py
```

Or double-click:

```txt
run_mosaic.bat
```

You can also drag and drop an image file onto `run_mosaic.bat`.

`run_mosaic.bat` に画像をドラッグ＆ドロップして起動することもできます。

---

## Build Windows EXE / Windows EXEを作る

Double-click:

```txt
build_windows.bat
```

Or run manually:

```bat
pip install -r requirements.txt
pyinstaller mosaic.spec --clean
```

After the build finishes, the executable will be created here:

```txt
dist\MosaicTools.exe
```

詳しい手順は `README_build.md` を見てください。

---

## How to Use / 使い方

1. Open or drag and drop an image.
2. Drag on the preview to select a mosaic area.
3. Adjust the block size slider.
4. Add more rectangles if needed.
5. Click the save button.

保存先は元画像と同じフォルダで、標準では `_mosaic` が付いたファイル名になります。

Example:

```txt
image.png
image_mosaic.png
```

---

## Supported Formats / 対応形式

| Format | Input | Output |
|--------|-------|--------|
| JPG / JPEG | Yes | Yes |
| PNG | Yes | Yes |
| WebP | Yes | Yes |

---

## Privacy Note / プライバシー注意

This tool tries to preserve image metadata such as EXIF, ICC profiles, PNG text chunks, and WebP XMP/EXIF when possible.

このツールは、可能な範囲でEXIF、ICCプロファイル、PNGのテキスト情報、WebPのXMP/EXIFなどを保持します。

If you need to remove private metadata such as GPS information, camera information, or AI generation prompts, remove metadata with another tool before publishing the image.

GPS情報、カメラ情報、生成AIのプロンプトなどを消したい場合は、公開前に別ツールでメタデータを削除してください。

---

## Requirements / 必要環境

- Python 3.9+
- Pillow
- tkinterdnd2
- PyInstaller, only for EXE build

---

## License

MIT License
