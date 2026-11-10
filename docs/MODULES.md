# Modules

Order matches `Configuration/main.yml`. "Gate" is the build/option restriction
declared in the file.

| # | Module | Gate | What it does |
|---|---|---|---|
| 1 | `adyo/start.yml` | — | Upgrade cleanup, mute toasts, setup markers (`HKLM\SOFTWARE\X-ADYO-OS`), tooling folder |
| 2 | `branding/copy-folders.yml` | — | Copies tooling, wallpapers, logo, report/undo scripts to `C:\Windows\X-ADYO-OS` |
| 3 | `ADYO RESTOREPOINT.ps1` | `rp-on` | Enables System Protection and creates a checkpoint |
| 4 | `ADYO BACKUP.ps1` | — | Exports services, AppX families, task states to `C:\Windows\X-ADYO-OS\Backups` |
| 5 | `debloat/appx-removals.yml` | per-build + options | Retired/consumer app removal, snapshot + deprovision |
| 6 | `debloat/onedrive.yml` | `remove-onedrive` | Uninstall OneDrive for all profiles, policy block, Explorer node removal |
| 7 | `debloat/edge.yml` | `opt-uninstall-edge` | Unlock + run Edge uninstaller, AppX sweep, updater off |
| 8 | `debloat/ai-components.yml` | `>=22000` + `remove-ai` | Copilot/Recall packages, Copilot policies, Recall feature off |
| 9 | `debloat/reinstall-blockers.yml` | per-build | Consumer-features policy, Store auto-download off, deprovisioned markers |
| 10 | `tasks/telemetry-tasks.yml` | per-build | Disables ~20 diagnostic scheduled tasks |
| 11 | `tasks/maintenance-tasks.yml` | per-build | Disables disk-footprint/WinSAT/cleanup churn |
| 12 | `privacy/telemetry-services.yml` | — | `DiagTrack`, `WerSvc`, `dmwappushservice` |
| 13 | `privacy/telemetry-policies.yml` | — | Diagnostic data, CEIP, WER, handwriting, advertising ID, DO |
| 14 | `privacy/settings-privacy.yml` | — | Location deny, activity feed, speech, feedback frequency |
| 15 | `privacy/cloud-content.yml` | per-build | CDM suggestions, spotlight, Start recommendations, sync-provider ads |
| 16 | `privacy/search-hardening.yml` | per-build | No web/Bing results, no cloud search, no highlights |
| 17 | `privacy/ai-features.yml` | `>=22000` | Recall snapshots off, Click to Do / Image Creator off |
| 18 | `privacy/app-telemetry.yml` | — | Edge, Office, NVIDIA, Visual Studio policy switches |
| 19 | `privacy/cross-device.yml` | — | Cloud clipboard, shared experiences, continue-on-device off |
| 20 | `adyo/services.yml` | per-build + options | Balanced service set (~25 services) |
| 21 | `services/extreme-services.yml` | `preset-extreme` | Xbox, touch, sensor, payment, AppReadiness off |
| 22 | `performance/power.yml` | options | Fast Startup off, hibernation and max-performance scheme |
| 23 | `performance/system.yml` | options + extreme | MMCSS, Games task, priority separation, NTFS, FTH, HAGS, memory |
| 24 | `performance/gaming.yml` | — | Game DVR off, Game Mode on |
| 25 | `performance/input.yml` | extreme extras | Mouse acceleration off, Sticky Keys shortcut off |
| 26 | `network/core.yml` | per-build | Network throttling off, LLMNR off, SMB hardening, HomeGroup/Wi-Fi Sense |
| 27 | `network/nic-config.yml` | — | NIC power saving off, delayed ACK/Nagle off per interface |
| 28 | `visual/context-menu.yml` | `>=22000` + `configure-lcm` | Classic right-click menu |
| 29 | `visual/taskbar.yml` | per-build | Widgets/chat off (11), News and interests off (10), search icon |
| 30 | `visual/explorer.yml` | options | Extensions, This PC, Quick Access tracking off, dark mode |
| 31 | `visual/extras.yml` | options + extreme | Transparency, recent-docs history off, reduced animations |
| 32 | `qol/updates.yml` | `wu-auto` / `wu-notify` | No surprise restarts, notify-only option, no early release opt-in |
| 33 | `qol/shortcuts.yml` | — | Long paths, Start/desktop shortcuts to the tooling folder |
| 34 | `qol/browsers.yml` | browser options | Chrome + Firefox (Chocolatey) / Brave (x64+Arm64) install |
| 35 | `branding/wallpaper.yml` | `configure-wallpaper` | X-ADYO OS wallpaper + lock screen for all profiles |
| 36 | `branding/oem-info.yml` | — | OEM information + Adyo logo in System Information |
| 37 | `security/mitigations.yml` | `opt-disable-mitigations` | Spectre/Meltdown overrides (opt-in) |
| 38 | `security/vbs.yml` | `opt-disable-vbs` | VBS / HVCI / hypervisor off (opt-in) |
| 39 | `adyo/finish.yml` | — | Notifications back, install report, reboot flag, Explorer restart |

## Helper scripts

| Script | Purpose |
|---|---|
| `BACKUP.ps1` | Pre-run state snapshots |
| `RESTOREPOINT.ps1` | System Restore checkpoint |
| `REPORT.ps1` | Self-contained HTML + TXT install report |
| `UNDO.ps1` | Service/task partial rollback |
| `APPLYHIVE.ps1` | Mirror HKCU tweaks into the Default hive |
| `EDGE-UNLOCK.ps1` | Edge uninstall chain |
| `CLEANUP.ps1` | Post-install cleanup helpers |
| `DEPROVISION.ps1` | Diff-based AppX deprovisioning |
| `ADYO-WALLPAPER.ps1` | Wallpaper + lock screen |

All scripts are version-stamped `1.0.0` and use the X-ADYO OS paths
(`C:\Windows\X-ADYO-OS`, `HKLM\SOFTWARE\X-ADYO-OS`).
