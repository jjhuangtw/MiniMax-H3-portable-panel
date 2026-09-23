@echo off
REM ============================================================================
REM  MiniMax H3 Portable Panel - optional model downloads (double-click, pick a number)
REM  Every download resumes if interrupted and verifies SHA-256. Run it again any time.
REM ============================================================================
setlocal enabledelayedexpansion
title MiniMax H3 Panel - Optional downloads
cd /d "%~dp0"

set "PY=python_embeded\python.exe"
if not exist "%PY%" (
    echo [X] Cannot find python_embeded\python.exe - run this from the panel folder.
    pause
    exit /b 1
)

:menu
echo.
echo =================================================================
echo   Optional downloads - pick what you want
echo =================================================================
echo   1. Image tab   - Krea2 image model + encoder + VAE   (~19 GB)
echo   2. Image tab   - Krea2 official style LoRAs (9)      (~4 GB)
echo   3. Edit tab    - Qwen-Image-2.1 image editing        (~17 GB)
echo   4. Upscale tab - SeedVR2 video upscaler              (~7 GB)
echo   5. HD two-pass latent upscaler (24 GB cards only)    (~0.7 GB)
echo   6. Heretic uncensored text encoder                   (~16 GB)
echo   7. AI prompt writer for the "AI prompt" buttons      (~5 GB, included in 1)
echo   A. Recommended set: 1 + 4
echo   Q. Quit  (or just press Enter)
echo.
set "PICK="
set /p PICK="Your choice: "
REM Empty input also quits, so a closed or piped stdin never loops the menu forever.
if not defined PICK exit /b 0
if /i "!PICK!"=="Q" exit /b 0
if /i "!PICK!"=="A" (
    call :run download_krea2_official.py
    call :run download_seedvr2.py
    goto :menu
)
if "!PICK!"=="1" call :run download_krea2_official.py
if "!PICK!"=="2" call :run download_krea2_style_loras.py
if "!PICK!"=="3" call :run download_qwen_image_models.py
if "!PICK!"=="4" call :run download_seedvr2.py
if "!PICK!"=="5" call :run download_hd_models.py
if "!PICK!"=="6" call :run download_heretic_encoder.py
if "!PICK!"=="7" call :run download_prompt_llm.py
goto :menu

:run
echo.
echo --- %~1 ---
"%PY%" -u %~1
if errorlevel 1 (
    echo [X] %~1 failed. Check your connection and pick it again - it resumes.
) else (
    echo [OK] %~1 done. Restart the panel ^(restart_webui.bat^) so it sees the new models.
)
exit /b 0
