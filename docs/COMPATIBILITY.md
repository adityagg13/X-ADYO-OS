# Compatibility

X-ADYO OS ships one package for Windows 10 and Windows 11. Support is expressed two
ways: `SupportedBuilds` in `playbook.conf` (which builds the wizard will offer) and
per-action `builds:` gates inside the YAML (which tweaks actually run).

## Build matrix

| OS | Release | Build | Listed in SupportedBuilds | Notes |
|---|---|---|---|---|
| Windows 10 | 1809 | 17763 | yes | EOL; tweaks are gated but least tested |
| Windows 10 | 1903 | 18362 | yes | EOL; least tested |
| Windows 10 | 1909 | 18363 | yes | EOL; least tested |
| Windows 10 | 2004 / 20H2 / 21H1 | 19041–19043 | yes | HAGS keys only exist from 2004+ |
| Windows 10 | 21H2 / 22H2 | 19044 / 19045 | yes | **recommended Windows 10 targets** |
| Windows 11 | 21H2 | 22000 | yes | Widgets/chat/Copilot pages vary by build |
| Windows 11 | 22H2 / 23H2 | 22621 / 22631 | yes | **recommended Windows 11 targets** |
| Windows 11 | 24H2 / 25H2 | 26100 / 26200 | yes | Recall keys exist from 24H2 |
| Windows 11 | 26H2 | 26300 | yes | same servicing branch as 24H2/25H2 |
| Windows 11 | next branch | 28000 | yes | forward-looking, tweaks are no-ops or gated |

Builds not listed are refused by the wizard. For testing on such a build use
`python scripts/build-playbook.py --no-gate`, which strips `SupportedBuilds` and
`Requirements` from the packaged copy only.

## What is gated

**Windows 11 only (`builds: ['>=22000']`)**

- AI components: Copilot packages, Recall policies, Click to Do, Image Creator
- Legacy context menu restore
- Taskbar: widgets (`TaskbarDa`), chat (`TaskbarMn`), alignment, Copilot button
- HAGS key (`HwSchMode`)
- Start menu recommendations, search highlights, Dev Home / Clipchamp / Photos removal
- Device Census scheduled tasks

**Windows 10 only (`builds: ['<22000']`)**

- `dmwappushservice`, `WalletService`
- News and interests feed, Cortana taskbar button
- Setting Sync scheduled tasks
- HomeGroup and Wi-Fi Sense policies
- Office Hub, OneConnect, Sticky Notes removal

Everything else is shared and uses keys that exist on both operating systems.

## Known limitations

1. **`!appx` and `!systemPackage` need the AME engine's helper binaries.** In a
   normal wizard install these are present. A bare CLI run without them will log
   failures for app removals — the playbook continues (all removals use
   `errorAction: Log`).
2. **Edge removal can break cumulative updates on some builds.** If an update fails
   afterwards, reinstall Edge, update, remove again (documented in `edge.yml`).
3. **Extreme disables the Xbox service stack**, which breaks Game Pass installs
   until re-enabled.
4. **`opt-disable-mitigations` and `opt-disable-vbs` need a reboot** and lower
   security. VBS off additionally stops WSL2, Hyper-V, Windows Sandbox and the
   Android subsystem from starting until `bcdedit /set hypervisorlaunchtype auto`
   is run.
5. **`opt-disable-sysmain` also disables memory compression** (both are governed by
   the same option because they share the same "plenty of RAM" precondition).
6. **Default browser is not forced.** Windows 10/11 protect the association; X-ADYO OS
   installs the chosen browser and lets Windows offer the choice.
7. **OEM logo** shows in System Information on both OS families, but Windows 11
   24H2+ moved some About surfaces to Settings and may not render the bitmap.
8. **No hardware test was performed** in the environment where this package was
   assembled. Run it on a VM snapshot first.
