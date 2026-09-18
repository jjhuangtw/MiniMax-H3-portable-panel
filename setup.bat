@echo off
REM ============================================================================
REM  MiniMax H3 Portable Panel - ONE-CLICK setup (no git, no 7-Zip needed)
REM  Put this single file in an empty folder on a drive with ~200 GB free and
REM  double-click it. It downloads ComfyUI portable + the panel + core models
REM  and launches the WebUI. Resumable: if a download drops, run it again.
REM ============================================================================
setlocal enabledelayedexpansion
title MiniMax H3 - One-click setup
cd /d "%~dp0"

where curl >nul 2>nul || goto :notools
where tar  >nul 2>nul || goto :notools

set "PORT=ComfyUI_windows_portable"
set "COMFY_7Z=https://github.com/comfyanonymous/ComfyUI/releases/download/v0.36.0/ComfyUI_windows_portable_nvidia.7z"
set "PANEL_ZIP=https://github.com/jjhuangtw/MiniMax-H3-portable-panel/archive/refs/heads/main.zip"

echo.
echo ============================================================
echo   MiniMax H3 - one-click setup
echo   This downloads about 40 GB total and can take a while.
echo ============================================================
echo.

REM --- 1. 7zr.exe (extracts the .7z; ~0.6 MB) ------------------------------
if not exist 7zr.exe (
    echo [1/5] Downloading 7zr.exe ...
    curl -L --fail -o 7zr.exe "https://www.7-zip.org/a/7zr.exe" || goto :dlfail
)

REM --- 2 + 3. ComfyUI portable (~2 GB) ------------------------------------
if exist "%PORT%\python_embeded\python.exe" (
    echo [2/5] ComfyUI portable already present, skipping download.
) else (
    if not exist ComfyUI_portable.7z (
        echo [2/5] Downloading ComfyUI portable ^(~2 GB^) ...
        curl -L --fail -o ComfyUI_portable.7z "%COMFY_7Z%" || goto :dlfail
    )
    echo [3/5] Extracting ComfyUI portable ^(this takes a minute^) ...
    REM Don't treat a 7zr warning exit as fatal; judge success by the extracted python.exe below.
    7zr.exe x -y ComfyUI_portable.7z >nul
)
if not exist "%PORT%\python_embeded\python.exe" (
    echo [X] ComfyUI portable did not extract as expected. Delete ComfyUI_portable.7z and re-run.
    pause & exit /b 1
)
if exist ComfyUI_portable.7z del /q ComfyUI_portable.7z

REM --- 4. the panel, copied into the portable folder ---------------------
echo [4/5] Downloading the MiniMax H3 panel ...
curl -L --fail -o panel.zip "%PANEL_ZIP%" || goto :dlfail
if exist panel_tmp rmdir /s /q panel_tmp
mkdir panel_tmp
tar -xf panel.zip -C panel_tmp || goto :extractfail
for /d %%D in ("panel_tmp\*") do xcopy /e /y /i /q "%%D\*" "%PORT%\" >nul
rmdir /s /q panel_tmp
del /q panel.zip

REM --- 5. install packages + custom nodes + core models ------------------
echo [5/5] Installing packages, custom nodes and core H3 models ...
echo       ^(~35 GB of models with SHA-256 checks; this is the long part.^)
echo.
cd /d "%~dp0%PORT%"
call "%~dp0%PORT%\install.bat"
exit /b 0

:notools
echo [X] This needs the built-in curl and tar (Windows 10 1803+ or Windows 11).
echo     Please update Windows, then run setup.bat again.
pause & exit /b 1

:dlfail
echo.
echo [X] A download failed. Check your internet connection and run setup.bat again (it resumes).
pause & exit /b 1

:extractfail
echo.
echo [X] Extraction failed. Delete the partial file and run setup.bat again.
pause & exit /b 1
