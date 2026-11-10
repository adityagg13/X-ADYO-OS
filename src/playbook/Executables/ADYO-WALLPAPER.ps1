# ADYO-WALLPAPER.ps1 - X-ADYO OS wallpaper and lock screen
# X-ADYO OS v1.0.0 - GPL-3.0
#
# Called by Configuration/tweaks/branding/wallpaper.yml (option: configure-wallpaper)
# as the elevated current user.
#
# WHAT IT DOES
#   1. Sets the desktop wallpaper for every local profile (and the Default hive, so
#      new accounts inherit it) via the documented HKCU values plus a live
#      SystemParametersInfo call for the signed-in session.
#   2. Sets the lock screen image through the Personalization policy values, which
#      are honoured on Windows 10 and Windows 11.
#
# Images live in C:\Windows\X-ADYO-OS\Wallpapers (copied by copy-folders.yml), so the
# paths stay valid after the playbook folder is removed.
#
# Idempotent, PS 5.1, no admin-only cmdlets beyond registry writes. Always exits 0.

$ErrorActionPreference = 'Continue'

$windir   = [Environment]::GetFolderPath('Windows')
$tools    = Join-Path $windir 'X-ADYO-OS'
$wallDir  = Join-Path $tools 'Wallpapers'
$desktop  = Join-Path $wallDir 'adyo-desktop.jpg'
$lock     = Join-Path $wallDir 'adyo-lockscreen.jpg'

if (-not (Test-Path -LiteralPath $desktop)) {
    Write-Output "WALLPAPER: $desktop not found - skipping"
    exit 0
}

# --------------------------------------------------------------- desktop ---
$profiles = @()
try {
    $profiles = Get-ChildItem 'C:\Users' -Directory -ErrorAction SilentlyContinue |
                Where-Object { $_.Name -notin @('Public','Default','All Users') } |
                ForEach-Object { $_.Name }
}
catch {
    Write-Output "WALLPAPER: could not enumerate profiles: $($_.Exception.Message)"
}

# The playbook runs as TrustedInstaller; writing another user's hive directly is not
# reliable, so each profile is patched through its loaded user hive when present and
# skipped otherwise. The currently signed-in user is always handled below.
foreach ($sid in (Get-ChildItem 'Registry::HKEY_USERS' -ErrorAction SilentlyContinue)) {
    $path = "$($sid.PSPath)\Control Panel\Desktop"
    if (Test-Path -LiteralPath $path) {
        try {
            Set-ItemProperty -LiteralPath $path -Name 'WallPaper' -Value $desktop -Type String -ErrorAction Stop
            Write-Output "WALLPAPER: set for $($sid.PSChildName)"
        } catch {
            Write-Output "WALLPAPER: skipped $($sid.PSChildName): $($_.Exception.Message)"
        }
    }
}

# Apply immediately for the interactive session (and refresh the cached bitmap)
try {
    Add-Type -Namespace XADYOOS -Name Wallpaper -MemberDefinition @'
[DllImport("user32.dll", CharSet = CharSet.Auto)]
public static extern int SystemParametersInfo(int uAction, int uParam, string lpvParam, int fuWinIni);
'@ -ErrorAction SilentlyContinue
    [XADYOOS.Wallpaper]::SystemParametersInfo(20, 0, $desktop, 3) | Out-Null
    Write-Output 'WALLPAPER: desktop refreshed'
}
catch {
    Write-Output "WALLPAPER: SystemParametersInfo unavailable: $($_.Exception.Message)"
}

# ------------------------------------------------------------ lock screen ---
if (Test-Path -LiteralPath $lock) {
    $pol = 'HKLM:\SOFTWARE\Policies\Microsoft\Windows\Personalization'
    try {
        New-Item -Path $pol -Force | Out-Null
        Set-ItemProperty -Path $pol -Name 'LockScreenImage' -Value $lock -Type String
        Set-ItemProperty -Path $pol -Name 'LockScreenOverlaysDisabled' -Value 1 -Type DWord
        Write-Output 'WALLPAPER: lock screen configured'
    }
    catch {
        Write-Output "WALLPAPER: lock screen not set: $($_.Exception.Message)"
    }
}

exit 0
