@echo off
setlocal

REM Mosaic Tools Windows EXE build script
pushd "%~dp0"

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m PyInstaller mosaic.spec --clean

if errorlevel 1 (
    echo.
    echo Build failed.
    pause
    popd
    exit /b 1
)

echo.
echo Build complete: dist\MosaicTools.exe
pause

popd
endlocal
