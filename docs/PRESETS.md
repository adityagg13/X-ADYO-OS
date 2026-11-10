# Presets

The preset is a wizard page. Selecting it writes `HKLM\SOFTWARE\X-ADYO-OS\SetupOptions\Preset`
and gates the actions that carry `option: 'preset-extreme'` or `option: '!preset-safe'`.

## Comparison

| Area | Safe | Balanced (default) | Extreme |
|---|---|---|---|
| AppX debloat (retired/consumer apps) | yes | yes | yes |
| Deprovision removed families | yes | yes | yes |
| Telemetry services (`DiagTrack`, `dmwappushservice`) | disabled | disabled | disabled |
| Telemetry / CEIP / WER / advertising policies | yes | yes | yes |
| Cloud content, suggestions, lock screen spotlight | yes | yes | yes |
| Windows Search web results + telemetry | off | off | off |
| Telemetry + maintenance scheduled tasks | disabled | disabled | disabled |
| OneDrive / Teams / optional app removals | per wizard | per wizard | per wizard |
| Conservative service set (Fax, RemoteRegistry, Maps, …) | — | yes | yes |
| `WSearch` / `PhoneSvc` / `TrkWks` on demand | — | yes | yes |
| MMCSS, game task priority, Win32PrioritySeparation | — | yes | yes |
| NTFS last-access off, FTH off | — | yes | yes |
| Network throttling, LLMNR, SMB hardening | — | yes | yes |
| NIC power saving off, delayed ACK off | — | yes | yes |
| Taskbar / Explorer / dark mode polish | per wizard | per wizard | per wizard |
| **Xbox service stack off** | — | — | yes |
| **Touch keyboard + sensor services off** | — | — | yes |
| **Payment / mobile hotspot services off** | — | — | yes |
| **AppReadiness, DsSvc, WerSvc off** | — | — | yes |
| **Prefetch off, paging executive resident** | — | — | yes |
| **Power throttling off, automatic maintenance off** | — | — | yes |
| **Sticky Keys shortcut off, animations reduced** | — | — | yes |
| **Widgets AppX removed (Win11)** | — | — | yes |

## Trade-offs you are accepting with Extreme

- Game Pass and some Xbox-integrated games stop working until the services are
  re-enabled (`sc config XblAuthManager start= demand`, same for `XblGameSave`,
  `XboxNetApiSvc`, `XboxGipSvc`).
- Touchscreen laptops lose the touch keyboard service.
- Auto-rotate and ambient-light adjustment stop on laptops.
- Prefetch off only makes sense on an SSD.
- Windows may keep more kernel memory resident (fine with 16 GB+).
- Higher idle power draw is *not* part of Extreme unless you also select
  "Maximum Performance power scheme".

## Anything can be changed afterwards

Every toggle is mirrored by a registry value or service start type that the install
report lists, and service changes are reversible with `Undo X-ADYO OS.cmd`.
