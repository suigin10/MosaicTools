# Mosaic Tools — Windows EXE Build Guide

Windows向けの単体EXEを作る手順です。

---

## Requirements / 必要なもの

| Tool | Version | Note |
|------|---------|------|
| Python | 3.9 or later | Enable "Add Python to PATH" during installation |
| pip | bundled with Python | used to install dependencies |

---

## Quick Start / クイックスタート

Place these files in the same folder:

```txt
MosaicTools/
├── mosaic.py
├── mosaic.spec
├── requirements.txt
└── build_windows.bat
```

Then double-click:

```txt
build_windows.bat
```

The executable will be created here:

```txt
dist\MosaicTools.exe
```

---

## Manual Build / 手動ビルド

```bat
pip install -r requirements.txt
pyinstaller mosaic.spec --clean
```

---

## Troubleshooting / トラブルシューティング

### `tkinterdnd2` is not found

```txt
ModuleNotFoundError: No module named 'tkinterdnd2'
```

Run:

```bat
pip install tkinterdnd2
```

### Antivirus false positive / ウイルス対策ソフトの誤検知

Executables created by PyInstaller may be falsely detected by antivirus software.

PyInstallerで作成したEXEは、ウイルス対策ソフトに誤検知されることがあります。

### Console window appears / コンソールが出る

Check that `console=False` is set in `mosaic.spec`.

`mosaic.spec` で `console=False` になっていることを確認してください。

### Use a custom icon / アイコンを設定したい

1. Prepare an `.ico` file.
2. Uncomment this line in `mosaic.spec`:

```python
# icon='mosaic.ico',
```

Change it to:

```python
icon='mosaic.ico',
```

Then build again.

---

## Build Output / ビルド出力

```txt
dist/
└── MosaicTools.exe
build/
```

For distribution, normally only `dist\MosaicTools.exe` is needed.
