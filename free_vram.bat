@echo off
title MiniMax H3 - Free VRAM
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0comfy_control.ps1" -Action free
pause
