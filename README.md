<p align="center">
  <img src="src/playbook/playbook.png" alt="X-ADYO OS" width="160">
</p>

<h1 align="center">X-ADYO OS</h1>

<p align="center">
  <strong>One AME Wizard playbook for Windows 10 <em>and</em> Windows 11 —</strong><br>
  every build from Windows 10 1809 to Windows 11 26H2.
</p>

<p align="center">
  <a href="https://github.com/adityagg13/X-ADYO-OS/releases/latest"><img src="https://img.shields.io/github/v/release/adityagg13/X-ADYO-OS?style=flat-square&color=2f6bff&label=release" alt="Release"></a>
  <a href="https://xadyoos.vercel.app"><img src="https://img.shields.io/badge/website-live-2f6bff?style=flat-square&logo=vercel&logoColor=white" alt="Website"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-2f6bff?style=flat-square" alt="GPL-3.0"></a>
  <a href="docs/COMPATIBILITY.md"><img src="https://img.shields.io/badge/Windows-10%20%7C%2011-2f6bff?style=flat-square&logo=windows&logoColor=white" alt="Windows 10 and 11"></a>
  <a href="docs/PRESETS.md"><img src="https://img.shields.io/badge/presets-Safe%20%7C%20Balanced%20%7C%20Extreme-2f6bff?style=flat-square" alt="Presets"></a>
  <img src="https://img.shields.io/badge/AME%20Wizard-playbook-2f6bff?style=flat-square" alt="AME Wizard playbook">
</p>

<p align="center">
  <a href="#-download">Download</a> ·
  <a href="#-quick-start">Quick start</a> ·
  <a href="#-why-one-playbook-for-both-operating-systems">Build coverage</a> ·
  <a href="#-presets">Presets</a> ·
  <a href="#-docs">Docs</a>
</p>

---

## 📦 Download

[**X-ADYO-OS-v1.0.0.apbx**](https://github.com/adityagg13/X-ADYO-OS/releases/latest) — the ready-to-use package.
Open it in AME Wizard via **Playbooks → Open**, or build it yourself from source with the
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

## 🚀 Quick start

1. Download the [latest `.apbx`](https://github.com/adityagg13/X-ADYO-OS/releases/latest) and open it in AME Wizard (**Playbooks → Open**).
2. Read [docs/INSTALL.md](docs/INSTALL.md) and [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md). Keep the laptop **plugged in** and Windows Update **fully up to date** before running.
3. Pick a preset — **Safe**, **Balanced** (default) or **Extreme** — keep the restore point on, and choose your browser (**Google Chrome**, **Brave** or **Firefox**).
4. Apply. After the reboot (only needed for the optional mitigation/VBS switches) open `C:\Windows\X-ADYO-OS\install-report.html` to see every change that was made.

The full pass takes about **12 minutes**. It needs an internet connection and no pending updates.

## 🧠 Why one playbook for both operating systems

X-ADYO OS keeps per-module `builds:` gates, so one package can serve:

- **Windows 10:** 1809 (17763), 1903 (18362), 1909 (18363), 2004–22H2 (19041–19045)
- **Windows 11:** 21H2 (22000), 22H2 (22621), 23H2 (22631), 24H2 (26100), 25H2 (26200),
  26H2 (26300), and the next servicing branch (28000)

Windows 11-only tweaks (Widgets, Copilot/Recall, taskbar alignment, legacy context
menu, HAGS, AI policies) carry `builds: ['>=22000']`. Windows 10-only tweaks
(News and interests, Cortana button, WalletService, dmwappushservice, HomeGroup,
Wi-Fi Sense) carry `builds: ['<22000']`. Everything shared is ungated.

## 🎚️ Presets

| Preset | What it does |
|---|---|
| **Safe** | Debloat, telemetry off, privacy policies. No service reductions beyond telemetry, no aggressive tuning. |
| **Balanced** (default) | Safe + conservative service set, scheduler/MMCSS tuning, network hardening, Explorer/taskbar polish. |
| **Extreme** | Balanced + Xbox/touch/sensor/payment services off, prefetch and paging-executive tweaks, animations reduced. |

Every preset writes the same restore point, the same backups and the same install
report. See [docs/PRESETS.md](docs/PRESETS.md) for the exact per-preset table.

## 🗂️ Structure

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

## 🔨 Build

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

## 🛟 Safety model

- **Restore point first** (unless you turn it off), then **full backups** of services,
  AppX families and scheduled tasks into `C:\Windows\X-ADYO-OS\Backups`.
- **Partial undo** restores service startup values and re-enables disabled tasks.
- **Full rollback** is the System Restore point named `X-ADYO OS v1.0.0`.
- Never-touch list (enforced by `scripts/validate-playbook.py`): Windows Update,
  Defender services, TrustedInstaller, AppXSvc/ClipSVC, Spooler, audio, WLAN, Store,
  winget, WebView2 and the shell AppX families.
- Removed apps can always be reinstalled from the Store; the report lists them.

## ✅ Verification status (honest)

- `scripts/validate-playbook.py` passes: XML schema, page limits, option names,
  include resolution, tag names, build-gate syntax, protected services/apps,
  executable references, orphan modules.
- The `.apbx` builds and its ZIP layout was verified (root `playbook.conf`,
  `Configuration/`, `Executables/`, `Images/`, 64 files, ~1.7 MB).
- **Not yet executed on a real Windows machine or VM.** This environment cannot run
  AME Wizard or a Windows build, so the YAML has been reviewed statically only.
  Test on a VM/snapshot first — especially the Edge removal, the Win10 1809–1909
  gates and the Extreme service set.

## 📚 Docs

| Doc | What's in it |
|---|---|
| [docs/INSTALL.md](docs/INSTALL.md) | Step-by-step run guide, from download to the post-install report |
| [docs/COMPATIBILITY.md](docs/COMPATIBILITY.md) | Supported builds, requirements and known caveats |
| [docs/PRESETS.md](docs/PRESETS.md) | The exact per-preset change table |
| [docs/MODULES.md](docs/MODULES.md) | Every module and what it touches |
| [docs/STOCK-VALUES.md](docs/STOCK-VALUES.md) | Every value the playbook can change, at stock |
| [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | Common failures and fixes |

## ⚖️ Credits and license

X-ADYO OS is released under GPL-3.0. See [LICENSE](LICENSE), [NOTICE](NOTICE) and
[CREDITS.md](CREDITS.md). The name, logo, wallpaper and lock screen were supplied by
the project owner.
