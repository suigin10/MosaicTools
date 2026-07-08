# Mosaic Tools

A small Windows-friendly GUI tool for applying mosaic/pixelation to JPG, PNG, and WebP images.

JPG / PNG / WebP 画像にモザイク処理をかけるための、シンプルな Tkinter 製 GUI ツールです。

---

## Features / 特徴

- Drag and drop image loading / 画像のドラッグ＆ドロップ読み込み
- Current filename display / 現在開いているファイル名の表示
- Live preview while selecting a rectangle / 矩形選択中のライブプレビュー
- Multiple mosaic regions / 複数範囲のモザイク指定
- Manual region input: `x,y,w,h` / 座標の手入力追加
- JPG / PNG / WebP support / JPG・PNG・WebP 対応
- JPEG / WebP quality setting / JPEG・WebP の品質設定
- Optional WebP lossless output / WebP の可逆保存オプション
- Optional metadata preservation / メタデータ保持のオン・オフ切り替え
- Output suffix setting / 出力サフィックス指定

---

## Quick Start / すぐ使う

### Run from Python / Python から起動

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

## Build Windows EXE / Windows EXE を作る

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
4. Adjust save options if needed.
5. Add more rectangles if needed.
6. Click the save button.

保存先は元画像と同じフォルダで、標準では `_mosaic` が付いたファイル名になります。

Example:

```txt
image.png
image_mosaic.png
```

---

## Save Options / 保存オプション

### Quality / 品質

`品質（JPEG / WebP の非可逆保存）` controls the output quality for JPEG and lossy WebP.

`品質（JPEG / WebP の非可逆保存）` は、JPEG と非可逆 WebP の保存品質を調整します。

Default value: `100`

初期値は `100` です。

### WebP Lossless / WebP 可逆保存

`WebPを可逆保存する（劣化なし・容量大きめ）` saves WebP images in lossless mode. When enabled, the quality slider is disabled because lossy quality is not used.

`WebPを可逆保存する（劣化なし・容量大きめ）` をオンにすると、WebP を可逆保存します。オンの間は非可逆品質を使わないため、品質スライダーは無効になります。

### Metadata / メタデータ

`メタデータを保持する（EXIF / 生成AIプロンプト等）` preserves metadata when possible.

`メタデータを保持する（EXIF / 生成AIプロンプト等）` をオンにすると、可能な範囲でメタデータを保持します。

This may include EXIF, ICC profiles, PNG text chunks such as AI generation parameters, and WebP XMP/EXIF.

保持対象には、EXIF、ICC プロファイル、生成AI画像の `parameters` などを含む PNG テキスト情報、WebP の XMP/EXIF などが含まれる場合があります。

If you want to remove private metadata before sharing an image, turn this option off.

画像を公開する前に個人情報やプロンプト情報を消したい場合は、このオプションをオフにしてください。

---

## Supported Formats / 対応形式

| Format | Input | Output | Notes |
|--------|-------|--------|-------|
| JPG / JPEG | Yes | Yes | Quality setting is available |
| PNG | Yes | Yes | Quality setting is not used |
| WebP | Yes | Yes | Lossy quality or lossless output is available |

---

## Privacy Note / プライバシー注意

This tool can preserve image metadata such as EXIF, ICC profiles, PNG text chunks, and WebP XMP/EXIF when possible. Metadata preservation is enabled by default.

このツールは、可能な範囲で EXIF、ICC プロファイル、PNG のテキスト情報、WebP の XMP/EXIF などを保持できます。メタデータ保持は初期状態でオンです。

If you need to remove private metadata such as GPS information, camera information, or AI generation prompts, turn off metadata preservation before saving.

GPS 情報、カメラ情報、生成AIのプロンプトなどを消したい場合は、保存前にメタデータ保持をオフにしてください。

---

## Requirements / 必要環境

- Python 3.9+
- Pillow
- tkinterdnd2
- PyInstaller, only for EXE build

---

## License

MIT License
