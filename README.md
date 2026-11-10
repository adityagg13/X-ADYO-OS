# X-ADYO OS

<p align="center">
  <img src="src/playbook/playbook.png" alt="X-ADYO OS" width="220">
</p>

**One AME Wizard playbook for Windows 10 *and* Windows 11 — every build from Windows 10 1809 to Windows 11 26H2.**

## Download

[**X-ADYO-OS-v1.0.0.apbx**](https://github.com/adityagg13/X-ADYO-OS/releases/latest) — the ready-to-use package.
Open it in AME Wizard via **Playbooks → Open**. Build it yourself from source with the
commands in [Build](#build).

X-ADYO OS is one build-aware configuration for every Windows 10 and Windows 11 release:

| Area | What it covers |
|---|---|
| **Windows 10** | Every build from 1809 to 22H2, plus Windows 10-only modules (News and interests, Cortana button, HomeGroup, Wi-Fi Sense) |
| **Windows 11** | Every build from 21H2 to 26H2, plus Windows 11-only modules (Widgets, Copilot/Recall, legacy context menu, HAGS) |
| **Presets** | Safe, Balanced (default) and Extreme |
| **Rollback** | System Restore point, full service/AppX/task backups, partial undo script, stock-values inventory |
| **Report** | Self-contained HTML + TXT install report listing every real before/after change |

> Every tweak is gated per build, so the same package behaves correctly on a fresh
> Windows 10 1809 install and on Windows 11 26H2. `docs/MODULES.md` lists every module
> and what it changes.

---

## Why one playbook for both operating systems

X-ADYO OS keeps per-module `builds:` gates, so one package can serve:

- **Windows 10:** 1809 (17763), 1903 (18362), 1909 (18363), 2004–22H2 (19041–19045)
- **Windows 11:** 21H2 (22000), 22H2 (22621), 23H2 (22631), 24H2 (26100), 25H2 (26200),
  26H2 (26300), and the next servicing branch (28000)

Windows 11-only tweaks (Widgets, Copilot/Recall, taskbar alignment, legacy context
menu, HAGS, AI policies) carry `builds: ['>=22000']`. Windows 10-only tweaks
(News and interests, Cortana button, WalletService, dmwappushservice, HomeGroup,
Wi-Fi Sense) carry `builds: ['<22000']`. Everything shared is ungated.

---

## Presets

| Preset | What it does |
|---|---|
| **Safe** | Debloat, telemetry off, privacy policies. No service reductions beyond telemetry, no aggressive tuning. |
| **Balanced** (default) | Safe + conservative service set, scheduler/MMCSS tuning, network hardening, Explorer/taskbar polish. |
| **Extreme** | Balanced + Xbox/touch/sensor/payment services off, prefetch and paging-executive tweaks, animations reduced. |

Every preset writes the same restore point, the same backups and the same install
report. See [docs/PRESETS.md](docs/PRESETS.md) for the exact per-preset table.

---

## Structure

```
src/playbook/
├── playbook.conf                  # metadata, build gates, wizard pages, presets
├── playbook.png                   # 256px icon (X-ADYO OS logo)
├── Images/                        # browser icons + Adyo badge
├── Configuration/
│   ├── main.yml                   # module order
│   ├── adyo/                      # start, services (balanced), finish
│   └── tweaks/
│       ├── debloat/               # appx, OneDrive, Edge, AI components, blockers
│       ├── privacy/               # telemetry, cloud content, search, AI data
│       ├── services/              # extreme-only service set
│       ├── performance/           # power, system, gaming, input
│       ├── network/               # core stack, per-adapter tuning
│       ├── visual/                # context menu, taskbar, Explorer, extras
│       ├── tasks/                 # telemetry + maintenance scheduled tasks
│       ├── security/              # opt-in mitigations / VBS
│       ├── qol/                   # updates, shortcuts, browser install
│       └── branding/              # tooling folder, wallpaper, OEM info
└── Executables/                   # PowerShell tooling + wallpapers + logo
```

---

## Build

```bash
python scripts/validate-playbook.py     # schema + safety checks, must print OK
python scripts/build-playbook.py        # -> dist/X-ADYO-OS-v1.0.0.apbx
```

- `--no-gate` strips `SupportedBuilds`/`Requirements` for testing on an unsupported build.
- `--no-password` writes a plain ZIP. Debug only — **AME Wizard rejects it.**
- The default output is a ZIP where every entry is encrypted with the password
  `malte` (ZipCrypto, the format 7-Zip produces with `-tzip -p`), written by a
  built-in pure-Python encoder, so no 7-Zip/WinRAR is needed. Anything else makes
  the wizard show *"Playbook must be encrypted using 'malte' as the password"*.
- The build self-verifies: it decrypts the finished archive with `malte`, checks
  every CRC and confirms `playbook.conf` sits at the archive root.

The archive root contains `playbook.conf` directly — no wrapping folder. Open it in
AME Wizard via **Playbooks → Open**.

---

## Install

1. Read [docs/INSTALL.md](docs/INSTALL.md) and [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md).
2. Disable Defender's real-time toggles when the wizard asks (the playbook does not
   remove Defender, but the engine needs the toggles off to write system state).
3. Pick a preset, keep the restore point on, choose your browser
   (**Google Chrome**, **Brave** or **Firefox**), apply.
4. After the reboot (only needed for the optional mitigation/VBS switches) open
   `C:\Windows\X-ADYO-OS\install-report.html`.

## Safety model

- **Restore point first** (unless you turn it off), then **full backups** of services,
  AppX families and scheduled tasks into `C:\Windows\X-ADYO-OS\Backups`.
- **Partial undo** restores service startup values and re-enables disabled tasks.
- **Full rollback** is the System Restore point named `X-ADYO OS v1.0.0`.
- Never-touch list (enforced by `scripts/validate-playbook.py`): Windows Update,
  Defender services, TrustedInstaller, AppXSvc/ClipSVC, Spooler, audio, WLAN, Store,
  winget, WebView2 and the shell AppX families.
- Removed apps can always be reinstalled from the Store; the report lists them.

---

## Verification status (honest)

- `scripts/validate-playbook.py` passes: XML schema, page limits, option names,
  include resolution, tag names, build-gate syntax, protected services/apps,
  executable references, orphan modules.
- The `.apbx` builds and its ZIP layout was verified (root `playbook.conf`,
  `Configuration/`, `Executables/`, `Images/`, 64 files, ~1.7 MB).
- **Not yet executed on a real Windows machine or VM.** This environment cannot run
  AME Wizard or a Windows build, so the YAML has been reviewed statically only.
  Test on a VM/snapshot first — especially the Edge removal, the Win10 1809–1909
  gates and the Extreme service set.

---

## Credits and license

X-ADYO OS is released under GPL-3.0. See [LICENSE](LICENSE), [NOTICE](NOTICE) and
[CREDITS.md](CREDITS.md). The name, logo, wallpaper and lock screen were supplied by
the project owner.
