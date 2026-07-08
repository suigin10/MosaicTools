# -*- mode: python ; coding: utf-8 -*-
# mosaic.spec — PyInstaller spec for mosaic.py
# Usage: pyinstaller mosaic.spec

import sys
from pathlib import Path

block_cipher = None

# tkinterdnd2 のデータファイルを自動検索して同梱する
import tkinterdnd2
dnd2_dir = Path(tkinterdnd2.__file__).parent
datas = [(str(dnd2_dir), 'tkinterdnd2')]

a = Analysis(
    ['mosaic.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'tkinterdnd2',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MosaicTools',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # ← GUIアプリなのでコンソール非表示
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='mosaic.ico',    # アイコンを使う場合はコメントを外してicoファイルを用意
)
