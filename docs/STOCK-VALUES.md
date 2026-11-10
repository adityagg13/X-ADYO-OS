# Stock values (revert inventory)

X-ADYO OS is reversible in three layers:

1. **System Restore point** (`X-ADYO OS v1.0.0`) — full registry rollback.
2. **`C:\Windows\X-ADYO-OS\Backups`** — the machine's own pre-run export
   (`services-before.reg`, `appx-before.txt`, `tasks-before.csv`, `meta.json`).
3. **`Undo X-ADYO OS.cmd`** — restores service `Start` values and re-enables disabled tasks.

This page documents the *stock* Windows values so you can restore any single change
by hand. Service codes: `2` = Automatic, `3` = Manual, `4` = Disabled.

> Prefer the machine's own backup over this table: Microsoft moves service defaults
> between builds, and this table reflects the most common Windows 10 22H2 / Windows 11
> 24H2–26H2 defaults.

## Services

| Service | X-ADYO OS sets | Stock (Windows) | Notes |
|---|---|---|---|
| `DiagTrack` | 4 | 2 | Telemetry pipeline |
| `WerSvc` | 3 (4 on Extreme) | 3 | Windows Error Reporting |
| `dmwappushservice` | 4 | 3 | Device metadata |
| `Fax` | 4 | 3 | Fax only |
| `RemoteRegistry` | 4 | 4 | Already disabled by default on Home |
| `RetailDemo` | 4 | 3 | Retail demo mode |
| `WMPNetworkSvc` | 4 | 3 | Media sharing |
| `SNMPTRAP` | 4 | 3 | SNMP traps |
| `WpcMonSvc` | 4 | 3 | Parental controls |
| `diagnosticshub.standardcollector.service` | 4 | 3 | Diagnostic Hub |
| `Browser` | 4 | 3 | Computer Browser (SMBv1 era) |
| `RemoteAccess` | 4 | 4 | Routing and Remote Access |
| `lfsvc` | 4 | 3 | Geolocation |
| `MapsBroker` | 4 | 2 | Offline maps |
| `WalletService` (Win10) | 4 | 3 | Wallet |
| `WSearch` | 3 (4 with option) | 2 | Windows Search |
| `PhoneSvc` | 3 | 3 | Phone service |
| `stisvc` | 3 | 3 | Scanners/cameras |
| `SSDPSRV`, `upnphost`, `FDResPub` | 3 | 3 / 3 / 3 | Network discovery |
| `lmhosts` | 3 | 3 | NetBIOS helper |
| `TrkWks` | 3 | 2 | Link tracking |
| `SharedAccess` | 3 | 3 | Internet Connection Sharing |
| `SstpSvc` | 3 | 3 | SSTP VPN |
| `ALG` | 3 | 3 | Application Layer Gateway |
| `PcaSvc` | 3 | 2 | Program Compatibility Assistant |
| `WdiServiceHost`, `WdiSystemHost` | 3 | 3 | Diagnostics |
| `SysMain` | 4 with option | 2 | Superfetch |
| `XblAuthManager`, `XblGameSave`, `XboxNetApiSvc`, `XboxGipSvc` | 4 on Extreme | 3 | Xbox stack |
| `TabletInputService` | 4 on Extreme | 3 | Touch keyboard |
| `SensorService`, `SensorDataService` | 4 on Extreme | 3 | Sensors |
| `SEMgrSvc`, `icssvc` | 4 on Extreme | 3 | Payments / hotspot |
| `AppReadiness`, `DsSvc` | 4 on Extreme | 3 | UWP readiness / data sharing |
| `DoSvc` | 3 on Extreme | 2 | Delivery Optimization |
| `PrintNotify` | 3 on Extreme | 3 | Print notifications |

## Registry (selected)

| What | Path | X-ADYO OS | Stock |
|---|---|---|---|
| Diagnostic data | `HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection\AllowTelemetry` | 0 | 1–3 |
| Advertising ID | `HKCU\...\AdvertisingInfo\Enabled` | 0 | 1 |
| Activity feed | `HKLM\SOFTWARE\Policies\Microsoft\Windows\System\EnableActivityFeed` | 0 | 1 |
| Fast Startup | `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power\HiberbootEnabled` | 0 | 1 |
| SystemResponsiveness | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile` | 10 | 20 |
| Win32PrioritySeparation | `HKLM\SYSTEM\CurrentControlSet\Control\PriorityControl` | 26 | 2 |
| NetworkThrottlingIndex | `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile` | 4294967295 | 10 |
| File extensions | `HKCU\...\Explorer\Advanced\HideFileExt` | 0 | 1 |
| Classic context menu | `HKCU\Software\Classes\CLSID\{86ca1aa0-…}\InprocServer32` | added | absent |
| Mouse acceleration | `HKCU\Control Panel\Mouse\MouseSpeed` | 0 | 1 |
| Mitigations (opt-in) | `HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\FeatureSettingsOverride` | 3 | 0 |
| VBS (opt-in) | `HKLM\SYSTEM\CurrentControlSet\Control\DeviceGuard\EnableVirtualizationBasedSecurity` | 0 | 1 |

## Power

| Change | Undo |
|---|---|
| Max performance scheme active | `powercfg /setactive SCHEME_BALANCED` |
| Hibernation off | `powercfg /hibernate on` |
| Fast Startup off | set `HiberbootEnabled` to `1` |
| VBS hypervisor off | `bcdedit /set hypervisorlaunchtype auto` |
