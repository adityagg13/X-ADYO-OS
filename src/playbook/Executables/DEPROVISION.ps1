# DEPROVISION.ps1 - X-ADYO OS post-debloat deprovisioning
# X-ADYO OS v1.0.0 - GPL-3.0
#
# Design: snapshot the package families before debloat, then remove the provisioned
# copy of every family that disappeared in the diff.
#
# WHAT IT DOES
#   Configuration/tweaks/debloat/appx-removals.yml snapshots every package family
#   into %WinDir%\X-ADYO-OS\AppxPackagesOld.txt before removing anything. This script
#   diffs that snapshot against the live list and removes the *provisioned* package
#   for every family that disappeared, so a Windows feature update cannot put the
#   app back. It never touches packages that were already absent before the run.
#
# SAFETY
#   - Read-only diff; only Remove-AppxProvisionedPackage is called.
#   - Never removes the protected families listed in appx-removals.yml (they are
#     never removed by the playbook, so they never appear in the diff).
#   - Best effort: every failure is printed and the script still exits 0, because
#     a provisioning store that is busy must not halt the playbook.
#
# Runs as the elevated current user (provisioning cmdlets need admin, not TI).
# Exit codes: 0 = success or nothing to do (the engine only logs non-zero exits).

$ErrorActionPreference = 'Continue'

$windir  = [Environment]::GetFolderPath('Windows')
$listTxt = Join-Path $windir 'X-ADYO-OS\AppxPackagesOld.txt'

if (-not (Test-Path -LiteralPath $listTxt)) {
    Write-Output 'DEPROVISION: no pre-run appx snapshot found - skipping'
    exit 0
}

try {
    $before = Get-Content -LiteralPath $listTxt -ErrorAction Stop |
              Where-Object { $_ -and $_.Trim().Length -gt 0 } |
              ForEach-Object { $_.Trim() }
    $after  = (Get-AppxPackage -ErrorAction SilentlyContinue).PackageFamilyName
    $removed = @($before | Where-Object { $after -notcontains $_ })

    if ($removed.Count -eq 0) {
        Write-Output 'DEPROVISION: nothing was removed - skipping'
        exit 0
    }

    Write-Output "DEPROVISION: $($removed.Count) package families disappeared - removing provisioned copies"

    $provisioned = Get-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue
    $hits = @($provisioned | Where-Object { $removed -contains $_.PackageFamilyName })

    foreach ($pkg in $hits) {
        try {
            Remove-AppxProvisionedPackage -Online -PackageName $pkg.PackageName -ErrorAction Stop | Out-Null
            Write-Output "DEPROVISION: deprovisioned $($pkg.PackageFamilyName)"
        }
        catch {
            Write-Output "DEPROVISION: could not deprovision $($pkg.PackageFamilyName): $($_.Exception.Message)"
        }
    }

    # Record the families so the install report can list them.
    $report = Join-Path $windir 'X-ADYO-OS\deprovisioned.txt'
    $removed | Out-File -LiteralPath $report -Encoding UTF8
    Write-Output "DEPROVISION: wrote $report"
}
catch {
    Write-Output "DEPROVISION: non-fatal failure: $($_.Exception.Message)"
}

exit 0
