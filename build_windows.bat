@echo off
setlocal

REM Mosaic Tools Windows EXE build script
REM Double-click this file to install dependencies and build the EXE.

pushd "%~dp0"

echo === Installing requirements ===
python -m pip install --upgrade pip
if errorlevel 1 goto :error

python -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo === Building MosaicTools.exe ===
python -m PyInstaller mosaic.spec --clean
if errorlevel 1 goto :error

echo.
echo Build completed:
echo dist\MosaicTools.exe
echo.
pause
popd
endlocal
exit /b 0

:error
echo.
echo Build failed.
echo.
pause
popd
endlocal
exit /b 1
