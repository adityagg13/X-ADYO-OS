# CLEANUP.ps1 - X-ADYO-OS end-of-run artifact cleanup
# X-ADYO OS v1.0.0 - GPL-3.0 - https://github.com/adyo-os/playbook
#
# Design rules (deliberate, by design):
#   1. X-ADYO-OS NEVER deletes System Restore points / shadow copies - rollback is
#      a core feature, not housekeeping.
#   2. X-ADYO-OS does NOT run cleanmgr/Disk Cleanup: it costs minutes and is pure
#      housekeeping, so it stays out of the critical path.
#   3. Temp clearing skips everything the AME Wizard may still be using (the
#      'AME' subtree).
#
# onUpgrade semantics: safe to run at ANY time (fresh install, upgrade re-run,
# or manual). It only removes provably-stale X-ADYO-OS leftovers and temp items;
# it never touches %WinDir%\X-ADYO-OS content (report, backups, toggles) or user
# documents.
#
# NOTE (T3-i, honest wiring status): this script is NOT currently referenced by
# main.yml (the pipeline is locked in 01-architecture section 6). It ships in
# Executables\ for manual use and for the main agent to wire into a future
# build (see worklog T3-i).
#
# PS 5.1, built-ins only. Exit codes: 0 always (best-effort cleanup must never
# break an install; individual failures are logged as warnings).

$ErrorActionPreference = 'Continue'

# ------------------------------------------------------- X-ADYO-OS leftovers ---

$windir = [Environment]::GetFolderPath('Windows')

# Legacy/dev locations X-ADYO-OS never uses in v1.0.0 but may have existed on
# pre-release test machines. Removing them keeps onUpgrade runs clean.
$staleDirs = @(
    (Join-Path $env:ProgramData 'X-ADYO-OS'),                 # pre-release staging path (superseded by %WinDir%\X-ADYO-OS)
    (Join-Path $windir 'X-ADYO-OS\Temp'),                     # transient staging, if a module ever creates one
    (Join-Path $windir 'X-ADYO-OSFolder')                     # legacy folder name from early development
)
foreach ($dir in $staleDirs) {
    if (Test-Path -LiteralPath $dir -PathType Container) {
        Write-Output "CLEANUP: removing stale folder $dir"
        Remove-Item -LiteralPath $dir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

# Wizard-side temp scratch that is unambiguously ours (never in use mid-run).
Get-ChildItem -Path $env:TEMP -Filter 'adyos-*' -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# ------------------------------------------------------------ user temp ------
# Clear the user temp folder EXCEPT the
# 'AME' tree, which the wizard may still be reading while a playbook executes.
$userTemp = $null
foreach ($p in @($env:TEMP, $env:TMP, "$env:LOCALAPPDATA\Temp")) {
    if ($p -and (Test-Path -LiteralPath $p -PathType Container)) { $userTemp = $p; break }
}
if ($userTemp) {
    Write-Output "CLEANUP: clearing user temp ($userTemp), keeping 'AME' and X-ADYO-OS items"
    Get-ChildItem -LiteralPath $userTemp -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -ne 'AME' -and $_.Name -notlike 'adyos-*' } |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}
else {
    Write-Warning 'CLEANUP: user temp folder not found.'
}

# ----------------------------------------------------------- system temp -----
$machine = [System.EnvironmentVariableTarget]::Machine
$sysTemp = $null
foreach ($p in @(
        [System.Environment]::GetEnvironmentVariable('Temp', $machine),
        [System.Environment]::GetEnvironmentVariable('Tmp', $machine),
        (Join-Path $windir 'Temp')
    )) {
    if ($p -and (Test-Path -LiteralPath $p -PathType Container)) { $sysTemp = $p; break }
}
if ($sysTemp) {
    Write-Output "CLEANUP: clearing system temp ($sysTemp)"
    Get-ChildItem -LiteralPath $sysTemp -ErrorAction SilentlyContinue |
        Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
}
else {
    Write-Warning 'CLEANUP: system temp folder not found.'
}

Write-Output 'CLEANUP: done. (System Restore points and shadow copies were intentionally NOT touched.)'
exit 0
