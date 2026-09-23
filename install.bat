@echo off
REM ============================================================================
REM  MiniMax H3 Portable Panel - installer (no git required)
REM  Run this from the ComfyUI portable root - the folder that contains
REM  python_embeded\ and ComfyUI\ - after copying this repo's files in.
REM ============================================================================
setlocal enabledelayedexpansion
title MiniMax H3 Panel - Install
cd /d "%~dp0"

set "PY=python_embeded\python.exe"
if not exist "%PY%" (
    echo [X] Cannot find python_embeded\python.exe here.
    echo.
    echo     Copy this repo's files into your ComfyUI portable folder - the one
    echo     that already contains  python_embeded\  and  ComfyUI\  - then
    echo     double-click install.bat again.
    echo     Get ComfyUI portable: https://github.com/comfyanonymous/ComfyUI/releases
    echo.
    pause
    exit /b 1
)

echo.
echo [1/5] Panel Python packages (gradio, websocket, zhconv)...
"%PY%" -m pip install --upgrade "gradio==6.26.0" requests websocket-client imageio-ffmpeg zhconv || goto :fail

echo.
echo [2/5] Aligning ComfyUI's own dependencies to your ComfyUI version...
echo       (fixes the v0.36 "MallocGraph has no attribute rogue_count" crash)
if exist "ComfyUI\requirements.txt" (
    "%PY%" -m pip install -r ComfyUI\requirements.txt || goto :fail
) else (
    echo   - ComfyUI\requirements.txt not found, skipping
)

echo.
echo [3/5] Custom nodes + their Python packages (pinned versions, zips - no git needed)...
"%PY%" -u download_nodes.py || goto :fail

echo.
echo [4/5] Core H3 models (Q4 diffusion + text encoder + VAEs + Turbo LoRAs)...
echo       This downloads ~38 GB and verifies every SHA-256. It resumes if interrupted.
"%PY%" -u download_q4_models.py || goto :fail
"%PY%" -u download_core_models.py || goto :fail
"%PY%" -u download_int8_vae.py || goto :fail
"%PY%" -u download_prompt_guides.py || goto :fail

echo.
echo [5/5] Optional extras (image generation, image editing, video upscaling...):
echo       double-click  download_extras.bat  any time and pick a number.
echo.
echo       Long videos: the panel uses TimelineDirector out of the box. The newer
echo       Smite79 engine must be installed by hand (its licence does not allow
echo       installers to fetch it): https://github.com/Smite79/MiniMax-H3-LongVideos
echo.
echo [OK] Done. Start the panel by double-clicking  run_webui.bat
echo.
set /p LAUNCH="Start the panel now? [Y/N] "
if /i "!LAUNCH!"=="Y" start "" "%~dp0run_webui.bat"
exit /b 0

:fail
echo.
echo [X] A step failed. Fix the error above and run install.bat again (it resumes).
pause
exit /b 1
