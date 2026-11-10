@echo off
title X-ADYO OS - Create Restore Point
powershell -NoProfile -Command "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { Start-Process -FilePath '%~f0' -Verb RunAs; exit }"
powershell -NoProfile -ExecutionPolicy Bypass -File "%SystemRoot%\X-ADYO-OS\RESTOREPOINT.ps1"
echo.
pause
