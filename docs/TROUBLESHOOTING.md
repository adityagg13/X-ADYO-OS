# Troubleshooting

## The wizard refuses to open the playbook

- **"Error while attempting to load Playbook: Playbook must be encrypted using
  'malte' as the password"** → the `.apbx` is a plain ZIP. Rebuild with
  `python scripts/build-playbook.py` (default output is ZipCrypto-encrypted with
  `malte`). Verify with `python -c "import zipfile;z=zipfile.ZipFile('dist/X-ADYO-OS-v1.0.0.apbx');z.read('playbook.conf',pwd=b'malte')"`.
  Do **not** password-protect it with AES (WinRAR `-ma4`, 7-Zip `-mem=AES256`); the
  wizard only reads ZipCrypto. Standalone 7-Zip `a -tzip -pmalte` is correct.
- "Playbook Name is too long" / invalid characters → do not rename `Name`,
  `Username` or `Title` in `playbook.conf`.
- The package must have `playbook.conf` at the **root** of the archive, not inside a
  folder. Rebuild with `python scripts/build-playbook.py`.
- Unsupported build → update Windows, or build a test copy with `--no-gate`.

## Deployment halts or reports errors

Open `C:\Windows\X-ADYO-OS\install-report.html` and the wizard's log
(`%ProgramData%\AME\Logs\<run>\Output.txt`).

| Symptom | Likely cause | Fix |
|---|---|---|
| Halt at start | `NoPendingUpdates`, on battery, no internet | Install updates, plug in, go online, re-run |
| Many "app not found" logs | `!appx` needs AME helper binaries (CLI-only runs) | Use the wizard, not a bare CLI |
| Edge removal fails | UCPD / Edge updater still running | Run `C:\Windows\X-ADYO-OS\...\EDGE-UNLOCK.ps1` elevated after a reboot, or `winget install Microsoft.Edge` to reset |
| Edge removal → update loop | Known Edge/update interaction | Reinstall Edge, install updates, remove again |
| Low storage error | Backups + restore point need a few hundred MB | Free space and re-run |
| Services show "not found" | Service renamed/removed on that build | Harmless; all service actions log instead of halting |

## Windows Update fails after install

X-ADYO OS never disables Windows Update. If an update fails:

1. `winget install Microsoft.Edge` (if you removed Edge), install updates, remove again.
2. Re-enable VBS if you disabled it: `bcdedit /set hypervisorlaunchtype auto`.
3. Restore services with `Undo X-ADYO OS.cmd`, retry the update.

## Game Pass / Xbox games stopped working

You selected the Extreme preset. Re-enable the stack:

```
sc config XblAuthManager start= demand
sc config XblGameSave start= demand
sc config XboxNetApiSvc start= demand
sc config XboxGipSvc start= demand
```

## Touch keyboard / rotation stopped

Extreme disables `TabletInputService`, `SensorService` and `SensorDataService`:

```
sc config TabletInputService start= demand
sc config SensorService start= demand
sc config SensorDataService start= demand
```

## WSL2 / Hyper-V / Sandbox stopped starting

You disabled Core Isolation/VBS (`opt-disable-vbs`). Undo:

```
bcdedit /set hypervisorlaunchtype auto
reg add HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard /v EnableVirtualizationBasedSecurity /t REG_DWORD /d 1 /f
```

Reboot afterwards.

## Wallpaper did not change

- The wallpaper option must be selected, and `C:\Windows\X-ADYO-OS\Wallpapers\adyo-desktop.jpg`
  must exist (copied by the module).
- Some corporate/managed images override the lock screen by policy; desktop wallpaper
  still applies.
- Run `C:\Windows\X-ADYO-OS\ADYO-WALLPAPER.ps1` manually (elevated) if needed.

## Report is missing

`REPORT.ps1` writes to `C:\Windows\X-ADYO-OS`. If the tooling folder was deleted, the
report is gone; re-running the playbook regenerates it.

## Full rollback

`rstrui.exe` → select the restore point named **X-ADYO OS v1.0.0**. That restores the
complete registry state at once. Removed Store apps are not restored by System
Restore — reinstall them from the Store.
