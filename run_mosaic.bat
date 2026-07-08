@echo off
setlocal
REM Mosaic Tools launcher (fallback for environments without pythonw.exe)

REM 実行フォルダへ移動
pushd "%~dp0"

REM python.exe で起動（ドラッグ＆ドロップ対応）
python "%~dp0mosaic.py" %*

popd
endlocal