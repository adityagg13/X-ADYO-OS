@echo off
title X-ADYO OS - Reinstall Microsoft Edge
powershell -NoProfile -Command "if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { Start-Process -FilePath '%~f0' -Verb RunAs; exit }"
winget install Microsoft.Edge --source winget --accept-package-agreements --accept-source-agreements
echo.
pause
