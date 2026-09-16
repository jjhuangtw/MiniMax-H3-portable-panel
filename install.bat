@echo off
REM ============================================================================
REM  MiniMax H3 Portable Panel - installer
REM  Sets up the custom nodes and downloads the core models into an existing
REM  ComfyUI portable build. Run this from the folder that contains webui.py.
REM ============================================================================
setlocal
title MiniMax H3 Panel - Install
cd /d "%~dp0"

set "PY=python_embeded\python.exe"
if not exist "%PY%" (
    echo [X] Cannot find python_embeded\python.exe
    echo     Put this repo's files into your ComfyUI portable root, next to
    echo     python_embeded\ and ComfyUI\, then run install.bat again.
    echo     ComfyUI portable: https://github.com/comfyanonymous/ComfyUI/releases
    pause
    exit /b 1
)

echo.
echo [1/4] Python packages (gradio, websocket, zhconv)...
"%PY%" -m pip install --upgrade gradio requests websocket-client imageio-ffmpeg zhconv || goto :fail

echo.
echo [2/4] Custom nodes (pinned revisions)...
set "CN=ComfyUI\custom_nodes"
call :clone https://github.com/Songssx/ComfyUI-MiniMaxH3-TimelineDirector 53f7211e53385cfe80a9094bc31768f505e05a7c ComfyUI-MiniMaxH3-TimelineDirector
call :clone https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler d7c01b9011f2e8439493f6c02c29995a27df276f Comfyui_Minimax_h3_latent_Upscaler
call :clone https://github.com/NyckM/3d-Camera-control-H3-Minimax 846880de859959e801b2c506dc424bd5c8b5c6c4 3d-Camera-control-H3-Minimax
call :clone https://github.com/ethanfel/ComfyUI-MiniMax-H3-Edit 92ff5b926945e21d843fa618ba440ad2f96048e6 ComfyUI-MiniMax-H3-Edit
call :clone https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler main seedvr2_videoupscaler

echo.
echo [3/4] Core H3 models (Q4 diffusion + text encoder + VAEs + Turbo LoRAs)...
echo     This downloads ~35 GB and verifies every SHA-256.
"%PY%" -u download_q4_models.py || goto :fail
"%PY%" -u download_core_models.py || goto :fail

echo.
echo [4/4] Optional extras - run these yourself only if you want them:
echo     download_heretic_encoder.py   uncensored text encoder (panel default; falls back to standard)
echo     download_hd_models.py         HD two-pass latent upscaler
echo     download_seedvr2.py           SeedVR2 video upscaler (6.8 GB)
echo     download_krea2_style_loras.py official Krea2 style LoRAs (needs a Krea2 base model you provide)
echo.
echo [OK] Done. Start the panel with run_webui.bat
pause
exit /b 0

:clone
if exist "%CN%\%3\.git" (
    echo   - %3 already present, skipping
) else (
    git clone "%1" "%CN%\%3" && git -C "%CN%\%3" checkout %2
)
exit /b 0

:fail
echo.
echo [X] A step failed. Fix the error above and run install.bat again (it resumes).
pause
exit /b 1
