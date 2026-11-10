@echo off
title X-ADYO OS - Partial Undo
powershell -NoProfile -Command "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { Start-Process -FilePath '%~f0' -Verb RunAs; exit }"
echo This restores service startup values and re-enables the scheduled tasks
echo X-ADYO OS disabled. Registry tweaks and removed apps are NOT restored here -
echo use System Restore (rstrui.exe) for a full rollback.
echo.
pause
powershell -NoProfile -ExecutionPolicy Bypass -File "%SystemRoot%\X-ADYO-OS\UNDO.ps1"
echo.
pause
