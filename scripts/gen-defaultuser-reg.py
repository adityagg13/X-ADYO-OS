#!/usr/bin/env python3
"""Generate Executables/default-user.reg from the playbook's HKCU tweak actions.

APPLYHIVE.ps1 imports this file into HKU\\AME_UserHive_Default (the Default profile
hive loaded by main.yml), so a brand-new Windows account starts with the same
per-user privacy, Explorer and input settings as the account that ran the playbook.

Scans src/playbook/Configuration/tweaks/**/*.yml for declarative HKCU actions:

    !registryValue: {path: 'HKCU\\...\\Key', value: 'Name', data: '1', type: REG_DWORD}
    !registryValue: {path: 'HKCU\\...', value: 'Name', operation: delete}
    !registryKey:   {path: 'HKCU\\...\\Key'}
    !registryKey:   {path: 'HKCU\\...\\Key', operation: delete}

Both inline `{...}` and block-style YAML are supported, using the same line
scanner as scripts/validate-playbook.py (no PyYAML dependency, and the engine's
custom `!tag:` syntax is preserved).

Honest limitation: the output is a SUPERSET across presets and
wizard options, because the selections are only known at run time. That is safe
for privacy/visual defaults; a profile created before install is untouched.

Usage:
    python scripts/gen-defaultuser-reg.py           # write the file
    python scripts/gen-defaultuser-reg.py --check   # exit 1 if stale/missing
"""

from __future__ import annotations

import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TWEAKS = os.path.join(ROOT, "src", "playbook", "Configuration", "tweaks")
OUT = os.path.join(ROOT, "src", "playbook", "Executables", "default-user.reg")
DEFAULT_HIVE = r"HKEY_USERS\AME_UserHive_Default"

ACTION_RE = re.compile(r"^\s*-\s*!(?P<tag>registryValue|registryKey)\s*:\s*(?P<rest>.*)$")


def parse_inline(body: str) -> dict[str, str]:
    body = body.strip()
    if not (body.startswith("{") and body.endswith("}")):
        return {}
    inner = body[1:-1]
    parts, token, depth = [], "", 0
    for ch in inner:
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(token)
            token = ""
        else:
            token += ch
    if token.strip():
        parts.append(token)
    out = {}
    for part in parts:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        out[key.strip()] = value.strip().strip("'\"")
    return out


def parse_block(lines: list[str], start: int) -> tuple[dict[str, str], int]:
    """Read the indented key: value lines that follow a block-style action."""
    attrs: dict[str, str] = {}
    base_indent = len(lines[start]) - len(lines[start].lstrip())
    idx = start + 1
    while idx < len(lines):
        line = lines[idx]
        if not line.strip():
            idx += 1
            continue
        indent = len(line) - len(line.lstrip())
        if indent <= base_indent and line.lstrip().startswith("-"):
            break
        if indent <= base_indent and re.match(r"^[A-Za-z]", line.lstrip()):
            break
        stripped = line.strip()
        if ":" in stripped and not stripped.startswith(("#", "-")):
            key, value = stripped.split(":", 1)
            attrs[key.strip()] = value.strip().strip("'\"")
        idx += 1
    return attrs, idx


def esc_str(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def collect() -> tuple[list[str], list[str]]:
    values: list[str] = []   # ordered .reg lines under a key
    problems: list[str] = []
    seen: set[tuple[str, str]] = set()

    files = sorted(glob.glob(os.path.join(TWEAKS, "**", "*.yml"), recursive=True))
    for path in files:
        with open(path, encoding="utf-8-sig") as fh:
            lines = fh.read().splitlines()

        idx = 0
        while idx < len(lines):
            match = ACTION_RE.match(lines[idx])
            if not match:
                idx += 1
                continue
            tag = match.group("tag")
            rest = match.group("rest").strip()
            if rest.startswith("{"):
                attrs = parse_inline(rest)
                idx += 1
            else:
                attrs, idx = parse_block(lines, idx)

            reg_path = attrs.get("path", "")
            if not reg_path.upper().startswith("HKCU\\"):
                continue

            hive_path = DEFAULT_HIVE + reg_path[len("HKCU"):]
            operation = attrs.get("operation", "add")

            if tag == "registryKey":
                if operation == "delete":
                    values.append(f"[-{hive_path}]")
                else:
                    values.append(f"[{hive_path}]")
                values.append("")
                continue

            name = attrs.get("value", "")
            if name == "":
                problems.append(f"{os.path.basename(path)}: empty value name (default value) skipped")
                continue
            key = (hive_path, name)
            if key in seen:
                continue
            seen.add(key)

            if operation == "delete":
                values.append(f"[{hive_path}]")
                values.append(f'"{esc_str(name)}"=-')
                values.append("")
                continue

            vtype = attrs.get("type", "REG_SZ").upper()
            data = attrs.get("data", "")
            if vtype == "REG_DWORD":
                try:
                    number = int(data, 0) & 0xFFFFFFFF
                except ValueError:
                    problems.append(f"{os.path.basename(path)}: non-numeric REG_DWORD '{data}' for {name}")
                    continue
                rendered = f"dword:{number:08x}"
            elif vtype == "REG_QWORD":
                rendered = f"hex(b):{int(data, 0):016x}"
            elif vtype in {"REG_EXPAND_SZ"}:
                rendered = f'hex(2):{",".join(f"{b:02x}" for b in (data + chr(0)).encode("utf-16-le"))}'
            elif vtype == "REG_BINARY":
                rendered = f"hex:{data.lower()}"
            elif vtype == "REG_MULTI_SZ":
                parts = data.split("\\0") if data else []
                raw = "".join(part + "\0" for part in parts) + "\0"
                rendered = f'hex(7):{",".join(f"{b:02x}" for b in raw.encode("utf-16-le"))}'
            else:
                rendered = f'"{esc_str(data)}"'

            values.append(f"[{hive_path}]")
            values.append(f'"{esc_str(name)}"={rendered}')
            values.append("")

    # collapse duplicate key headers, preserving order
    out: list[str] = []
    last_header = None
    for line in values:
        if line.startswith("[") and line.endswith("]") and not line.startswith("[-"):
            if line == last_header:
                continue
            last_header = line
        elif line == "":
            continue
        out.append(line)
    return out, problems


def build_text() -> tuple[str, list[str]]:
    body, problems = collect()
    header = [
        "Windows Registry Editor Version 5.00",
        "",
        "; X-ADYO OS - generated by scripts/gen-defaultuser-reg.py - do not edit by hand.",
        "; Imported into HKU\\AME_UserHive_Default by Executables/APPLYHIVE.ps1.",
        "; Mirrors every declarative HKCU tweak (superset across presets/options).",
        "",
    ]
    return "\r\n".join(header + body + [""]), problems


def main(argv: list[str]) -> int:
    text, problems = build_text()
    for problem in problems:
        print(f"WARN  {problem}")

    check = "--check" in argv
    existing = ""
    if os.path.isfile(OUT):
        with open(OUT, "rb") as fh:
            raw = fh.read()
        for encoding in ("utf-16", "utf-8-sig"):
            try:
                existing = raw.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

    if check:
        if existing.replace("\r\n", "\n") != text.replace("\r\n", "\n"):
            print("STALE: Executables/default-user.reg does not match the YAML modules")
            return 1
        print("OK: default-user.reg is up to date")
        return 0

    # Registry Editor expects UTF-16LE for "Windows Registry Editor Version 5.00".
    with open(OUT, "wb") as fh:
        fh.write(b"\xff\xfe" + text.replace("\r\n", "\n").replace("\n", "\r\n").encode("utf-16-le"))
    keys = sum(1 for line in text.splitlines() if line.startswith("[") and not line.startswith("[-"))
    print(f"wrote {os.path.relpath(OUT, ROOT)} ({keys} key sections, {len(text.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
