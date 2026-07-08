@echo off
setlocal
REM Mosaic Tools launcher

REM Move to this script directory
pushd "%~dp0"

REM Launch with Python. Drag-and-drop image paths are passed through.
python "%~dp0mosaic.py" %*

popd
endlocal
