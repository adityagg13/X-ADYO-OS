# Install

## Requirements

- Windows 10 1809+ or Windows 11 21H2+ (x64 or Arm64)
- AME Wizard (latest release)
- Internet connection (browser install, Chocolatey packages)
- AC power (the playbook refuses to run on battery)
- No pending Windows updates
- A fresh System Restore point **or** a VM snapshot

## Before you start

1. **Back up your data.** The playbook does not touch personal files, but restore
   points are not a data backup.
2. **Uninstall third-party antivirus.** The AME engine requires no AV besides
   Defender; the wizard's prepare step will block otherwise.
3. **Disable Defender's four toggles** when the wizard asks: real-time protection,
   cloud-delivered protection, automatic sample submission, tamper protection.
   X-ADYO OS does **not** remove Defender and does not need it permanently disabled.
4. **Run all pending updates.** `NoPendingUpdates` is a hard requirement.
5. **Note your product key / MSA state** if this machine is your daily driver.

## Steps

1. Open AME Wizard → **Playbooks → Open** → pick `dist/X-ADYO-OS-v1.0.0.apbx`.
2. The wizard shows the X-ADYO OS pages:
   - Preset: Safe / Balanced / Extreme
   - Restore point: keep **on**
   - Updates: automatic or notify-only
   - Components: Edge, OneDrive, Teams, AI removal
   - Inbox apps: Xbox, Photos, Phone Link, Dev Home
   - Advanced: mitigations, VBS, max-performance power scheme
   - Extras: hibernation, SysMain, search indexing, HAGS
   - Appearance: wallpaper, dark mode, legacy context menu, transparency
   - Browser: Chrome / Brave / Firefox (one is always installed)
3. Start the deployment. Roughly 8–15 minutes depending on the app removals and
   browser download.
4. Explorer restarts at the end so the visual changes appear.
5. Reboot if `C:\Windows\X-ADYO-OS\reboot-required.txt` exists (only with the opt-in
   mitigation/VBS switches).

## After install

- Open `C:\Windows\X-ADYO-OS\install-report.html` — every module, service, app and
  policy change, with undo notes.
- Pre-change snapshots are in `C:\Windows\X-ADYO-OS\Backups`.
- `Undo X-ADYO OS.cmd` restores service startup values and re-enables disabled tasks.
- `rstrui.exe` → `X-ADYO OS v1.0.0` restores the full registry state.

## Unsupported builds

If the wizard refuses your build, either update Windows or build a test copy:

```bash
python scripts/build-playbook.py --no-gate --out X-ADYO-OS-test.apbx
```

That copy has no `SupportedBuilds`/`Requirements`; it will load anywhere but gives
no compatibility guarantee.

## ISO mode

`SupportsISO` is true, so the wizard can also inject X-ADYO OS into a Windows ISO.
`!appx`, `!cmd`, `!powerShell` and `!software` behave differently in ISO mode (some
are rejected by the engine), so ISO injection applies the registry, service and
policy modules only — the app removals run after first boot when the OOBE stage
executes the playbook. Verify your ISO in a VM before deploying it.
