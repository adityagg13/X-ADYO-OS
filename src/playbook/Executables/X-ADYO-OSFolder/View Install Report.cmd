@echo off
title X-ADYO OS - Install Report
if not exist "%SystemRoot%\X-ADYO-OS\install-report.html" (
    echo No report found yet. Run the X-ADYO OS playbook first.
    pause
    exit /b 1
)
start "" "%SystemRoot%\X-ADYO-OS\install-report.html"
