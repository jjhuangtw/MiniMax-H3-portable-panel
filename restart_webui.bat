@echo off
title MiniMax H3 - Restart Portable
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0restart_portable.ps1"
if errorlevel 1 pause
