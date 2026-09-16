@echo off
title MiniMax H3 WebUI - Portable (RTX 4090)
cd /d "%~dp0"

echo =================================================================
echo   MiniMax H3 Portable WebUI (RTX 4090)
echo =================================================================
echo.
echo [1/2] Starting or opening the existing local WebUI...
echo [2/2] Browser address: http://127.0.0.1:7860
echo.

set PYTHONIOENCODING=utf-8
.\python_embeded\python.exe webui.py
if errorlevel 1 pause
