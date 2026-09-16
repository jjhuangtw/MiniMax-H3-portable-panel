@echo off
title MiniMax H3 - Cancel Generation
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0comfy_control.ps1" -Action cancel
pause
