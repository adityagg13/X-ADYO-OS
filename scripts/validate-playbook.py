#!/usr/bin/env python3
"""X-ADYO OS playbook validator.

Checks the playbook against the AME Wizard engine (v0.8.4) rules that can be
verified statically, so a broken package is caught before it reaches a machine:

  1. playbook.conf: required elements, SupportedBuilds present, FeaturePages limits
     (max 4 options, <=2 with both TopLine and BottomLine, <=3 with either),
     unique option names, DefaultOption exists, OOBE has exactly 3 bullet points
     with the three distinct icons when SupportsISO is true.
  2. Configuration: every !task include resolves, every tag is one the engine
     registers, every option:/options: name exists in playbook.conf.
  3. builds: expressions use only the supported comparators.
  4. Never-touch services are not disabled/deleted and protected AppX families
     are never removed.
  5. ExeDir references point at files that ship in Executables/.
  6. Every YAML file is reachable from main.yml (no orphan modules).

Exit code 0 = no errors (warnings allowed), 1 = errors found.

No third-party dependencies: the engine's YAML uses custom tags (!task:, ...),
so files are scanned line by line instead of parsed.
"""

from __future__ import annotations

import fnmatch
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAYBOOK = os.path.join(ROOT, "src", "playbook")
CONF = os.path.join(PLAYBOOK, "playbook.conf")
CONFIG = os.path.join(PLAYBOOK, "Configuration")
EXECUTABLES = os.path.join(PLAYBOOK, "Executables")

VALID_TAGS = {
    "file", "service", "run", "powerShell", "cmd", "scheduledTask",
    "registryKey", "registryValue", "appx", "systemPackage", "taskKill",
    "software", "download", "writeStatus", "status", "task",
}

# Engine protects these outright; the playbook must never disable or delete them.
NEVER_TOUCH_SERVICES = {
    "wuauserv", "trustedinstaller", "usosvc", "dosvc", "spooler", "audiosrv",
    "winmgmt", "schedule", "profsvc", "usermgr", "staterepository",
    "installservice", "appxsvc", "clipsvc", "securityhealthservice",
    "mdcoreSvc".lower(), "wlansvc", "netman", "netprofm", "nlasvc", "cdpsvc",
    "cdpusersvc", "waasmedicsvc", "bits", "cryptsvc", "msiserver",
}

# AppX families that must never be removed (Store, winget, frameworks, shell).
PROTECTED_APPX = [
    "Microsoft.WindowsStore*",
    "Microsoft.DesktopAppInstaller*",
    "Microsoft.Web.WebView2*",
    "Microsoft.VCLibs*",
    "Microsoft.NET.Native*",
    "Microsoft.UI.Xaml*",
    "Microsoft.WindowsAppRuntime*",
    "Microsoft.XboxIdentityProvider*",
    "Microsoft.Xbox.TCUI*",
    "MicrosoftWindows.Client.CBS*",
    "*StartMenuExperienceHost*",
    "*ShellExperienceHost*",
    "*Windows.Search*",
    "Microsoft.Windows.FileExplorer*",
    "Microsoft.Windows.SecHealthUI*",
    "Microsoft.SecHealthUI*",
]

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# ----------------------------------------------------------------- playbook.conf
def check_conf() -> set[str]:
    if not os.path.isfile(CONF):
        err("playbook.conf missing")
        return set()

    try:
        tree = ET.parse(CONF)
    except ET.ParseError as exc:
        err(f"playbook.conf is not valid XML: {exc}")
        return set()

    root = tree.getroot()
    if root.tag != "Playbook":
        err(f"playbook.conf root element is <{root.tag}>, expected <Playbook>")

    required = ["Name", "Username", "Title", "ShortDescription", "Description",
                "Details", "Version", "UniqueId"]
    for tag in required:
        el = root.find(tag)
        if el is None or not (el.text or "").strip():
            err(f"playbook.conf: <{tag}> is missing or empty")

    builds = [b.text.strip() for b in root.findall("./SupportedBuilds/string") if b.text]
    if not builds:
        err("playbook.conf: <SupportedBuilds> is empty - the wizard will not offer the playbook")
    win10 = [b for b in builds if b.isdigit() and int(b) < 22000]
    win11 = [b for b in builds if b.isdigit() and int(b) >= 22000]
    if not win10:
        err("playbook.conf: no Windows 10 builds listed")
    if not win11:
        err("playbook.conf: no Windows 11 builds listed")

    uid = (root.findtext("UniqueId") or "").strip()
    if uid and not re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}", uid):
        err(f"playbook.conf: UniqueId '{uid}' is not a UUIDv4")

    version = (root.findtext("Version") or "").strip()
    if version and not re.fullmatch(r"\d+(\.\d+){0,2}(\s.*)?", version):
        err(f"playbook.conf: Version '{version}' has an invalid format")

    # SupportsISO requires exactly three bullet points with distinct valid icons.
    if (root.findtext("SupportsISO") or "").strip().lower() == "true":
        bullets = root.findall("./OOBE/BulletPoints/BulletPoint")
        icons = [b.get("Icon") for b in bullets]
        if len(bullets) != 3:
            err(f"playbook.conf: SupportsISO requires exactly 3 BulletPoints, found {len(bullets)}")
        if len(set(icons)) != len(icons):
            err("playbook.conf: OOBE BulletPoint icons must be distinct")
        for b in bullets:
            if b.get("Icon") not in {"Rocket", "Privacy", "Lock"}:
                err(f"playbook.conf: invalid BulletPoint icon '{b.get('Icon')}'")

    # FeaturePages
    options: set[str] = set()
    pages = root.findall("./FeaturePages/*")
    for page in pages:
        page_type = page.tag
        if page_type not in {"CheckboxPage", "RadioPage", "RadioImagePage"}:
            err(f"playbook.conf: unsupported page type <{page_type}>")
            continue
        opts = list(page.findall("./Options/*"))
        has_top = page.find("TopLine") is not None
        has_bottom = page.find("BottomLine") is not None
        limit = 2 if (has_top and has_bottom) else (3 if (has_top or has_bottom) else 4)
        if len(opts) > limit:
            err(f"playbook.conf: <{page_type}> has {len(opts)} options, engine limit is {limit} "
                f"(TopLine={has_top}, BottomLine={has_bottom})")

        names = []
        for opt in opts:
            name = (opt.findtext("Name") or "").strip()
            if not name:
                if opt.get("None") != "true":
                    err(f"playbook.conf: <{page_type}> option without <Name>")
                continue
            names.append(name)
            if name in options:
                err(f"playbook.conf: duplicate option name '{name}'")
            options.add(name)

        if page_type == "RadioPage":
            default = page.get("DefaultOption")
            if not default:
                err(f"playbook.conf: <RadioPage> missing DefaultOption")
            elif default not in names:
                err(f"playbook.conf: <RadioPage> DefaultOption '{default}' is not one of its options")
        if page_type == "RadioImagePage":
            default = page.get("DefaultOption")
            if default and default not in names:
                err(f"playbook.conf: <RadioImagePage> DefaultOption '{default}' is not one of its options")
            for opt in opts:
                if opt.get("None") == "true":
                    continue
                fn = (opt.findtext("FileName") or "").strip()
                icon = os.path.join(PLAYBOOK, "Images", fn + ".png")
                if not fn:
                    err("playbook.conf: RadioImageOption without FileName")
                elif not os.path.isfile(icon):
                    err(f"playbook.conf: Images/{fn}.png missing for a RadioImageOption")

    # Software packages must reference existing icons
    for pkg in root.findall("./Software/Package"):
        option = pkg.get("Option") or ""
        name = (pkg.findtext("Name") or "").strip()
        icon = (pkg.findtext("Icon") or "").strip()
        for field, value in (("Name", name), ("Title", pkg.findtext("Title")),
                             ("Description", pkg.findtext("Description")), ("Icon", icon)):
            if not (value or "").strip():
                err(f"playbook.conf: Software package '{name or option}' missing {field}")
        if icon and not os.path.isfile(os.path.join(PLAYBOOK, "Images", icon)):
            err(f"playbook.conf: Software icon Images/{icon} missing")
        if option and option not in options:
            err(f"playbook.conf: Software package option '{option}' is not offered on any page")

    print(f"  builds      : {len(builds)} ({len(win10)} Windows 10, {len(win11)} Windows 11)")
    print(f"  pages       : {len(pages)}")
    print(f"  options     : {len(options)}")
    return options


# ------------------------------------------------------------------- YAML scan
TAG_RE = re.compile(r"!(?P<tag>[A-Za-z]+)\s*:")
TASK_PATH_RE = re.compile(r"!task\s*:\s*\{\s*path\s*:\s*['\"]?([^'\",}]+)")
OPTION_RE = re.compile(r"\boption\s*:\s*['\"]?(!?[A-Za-z0-9_\-&]+)")
OPTIONS_LIST_RE = re.compile(r"\boptions\s*:\s*\[([^\]]*)\]")
BUILDS_RE = re.compile(r"\bbuilds\s*:\s*\[([^\]]*)\]")
EXEDIR_RE = re.compile(r"\bexeDir\s*:\s*true", re.I)
NAMED_ACTION_RE = re.compile(r"^\s*-\s*!(?P<tag>[A-Za-z]+)\s*:\s*(?P<rest>.*)$")


def norm(path: str) -> str:
    return path.replace("\\", "/")


def yaml_files() -> list[str]:
    out = []
    for base, _dirs, files in os.walk(CONFIG):
        for f in files:
            if f.endswith((".yml", ".yaml")):
                out.append(os.path.join(base, f))
    return sorted(out)


def parse_inline_map(rest: str) -> dict[str, str]:
    body = rest.strip()
    if not (body.startswith("{") and body.endswith("}")):
        return {}
    inner = body[1:-1]
    result: dict[str, str] = {}
    depth = 0
    token = ""
    parts: list[str] = []
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
    for part in parts:
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        result[key.strip()] = value.strip().strip("'\"")
    return result


def check_yaml(options: set[str]) -> None:
    files = yaml_files()
    if not files:
        err("Configuration/ has no YAML files")
        return

    included: set[str] = set()
    downloaded: set[str] = set()
    for path in files:
        with open(path, encoding="utf-8-sig") as fh:
            for m in re.finditer(r"!download\s*:\s*\{[^}]*destination\s*:\s*['\"]?([^'\",}]+)", fh.read()):
                downloaded.add(norm(m.group(1).strip()))
        # block style destination:
        with open(path, encoding="utf-8-sig") as fh:
            for m in re.finditer(r"destination\s*:\s*['\"]?([^'\",\n}]+)", fh.read()):
                downloaded.add(norm(m.group(1).strip()))

    covered_win10 = 0
    covered_win11 = 0
    both = 0
    tags_used: set[str] = set()

    for path in files:
        rel = norm(os.path.relpath(path, CONFIG))
        with open(path, encoding="utf-8-sig") as fh:
            lines = fh.read().splitlines()

        text = "\n".join(lines)
        if not re.search(r"^\s*title\s*:", text, re.M):
            warn(f"{rel}: no 'title:' key")
        if not re.search(r"^\s*actions\s*:", text, re.M):
            err(f"{rel}: no 'actions:' list")

        # build-gate classification for the compatibility summary
        gates = BUILDS_RE.findall(text)
        lower = [g for g in gates if any(tok.strip().startswith(("<", "!>")) for tok in g.split(","))]
        upper = [g for g in gates if any(tok.strip().startswith((">", "!<")) for tok in g.split(","))]
        if any("<22000" in g for g in gates) and not any(">=22000" in g for g in gates):
            covered_win10 += 1
        elif any(">=22000" in g for g in gates) and not any("<22000" in g for g in gates):
            covered_win11 += 1
        else:
            both += 1
        _ = (lower, upper)

        for idx, line in enumerate(lines, 1):
            for m in TAG_RE.finditer(line):
                tag = m.group("tag")
                tags_used.add(tag)
                if tag not in VALID_TAGS:
                    err(f"{rel}:{idx}: unknown engine tag '!{tag}:' (engine v0.8.4 registers 15 tags)")

            for m in TASK_PATH_RE.finditer(line):
                target = norm(m.group(1).strip())
                full = os.path.join(CONFIG, target)
                if not os.path.isfile(full):
                    err(f"{rel}:{idx}: !task include not found: {target}")
                else:
                    included.add(target)

            for m in OPTION_RE.finditer(line):
                name = m.group(1).lstrip("!").split("&")[0]
                if name and name not in options:
                    err(f"{rel}:{idx}: option '{m.group(1)}' is not defined in playbook.conf")
            for m in OPTIONS_LIST_RE.finditer(line):
                for raw in m.group(1).split(","):
                    name = raw.strip().strip("'\"").lstrip("!")
                    if name and name not in options and not name.startswith("preset-"):
                        warn(f"{rel}:{idx}: options entry '{name}' is not defined in playbook.conf")

            for m in BUILDS_RE.finditer(line):
                for raw in m.group(1).split(","):
                    token = raw.strip().strip("'\"")
                    if token and not re.fullmatch(r"!?[<>]=?\d{5}(\.\d+)?|\d{5}", token):
                        err(f"{rel}:{idx}: invalid builds token '{token}'")

        # action-level checks (inline and block style)
        for idx, line in enumerate(lines):
            m = NAMED_ACTION_RE.match(line)
            if not m:
                continue
            tag = m.group("tag")
            rest = m.group("rest")
            attrs = parse_inline_map(rest) if rest.strip().startswith("{") else {}
            if not attrs:
                # block style: gather following lines until the next list item
                block = []
                base_indent = len(line) - len(line.lstrip())
                for nxt in lines[idx + 1:]:
                    if not nxt.strip():
                        continue
                    indent = len(nxt) - len(nxt.lstrip())
                    if nxt.lstrip().startswith("- ") and indent <= base_indent:
                        break
                    if indent <= base_indent and not nxt.lstrip().startswith(("name", "operation", "startup")):
                        if indent <= base_indent:
                            break
                    block.append(nxt.strip())
                attrs = dict(parse_inline_map("{" + ", ".join(block) + "}"))
                if not attrs:
                    for entry in block:
                        if ":" in entry:
                            k, v = entry.split(":", 1)
                            attrs[k.strip()] = v.strip().strip("'\"")

            lineno = idx + 1
            if tag == "service":
                name = attrs.get("name", "").lower()
                startup = attrs.get("startup", "")
                operation = attrs.get("operation", "change")
                if name in NEVER_TOUCH_SERVICES and (startup == "4" or operation == "delete"):
                    err(f"{rel}:{lineno}: never-touch service '{name}' cannot be disabled or deleted")
            if tag == "appx":
                name = attrs.get("name", "")
                for pattern in PROTECTED_APPX:
                    if fnmatch.fnmatch(name.lower(), pattern.lower()):
                        err(f"{rel}:{lineno}: protected AppX family '{name}' cannot be removed")
            if tag in {"powerShell", "cmd", "run"} and (
                    attrs.get("exeDir", "").lower() == "true" or EXEDIR_RE.search("\n".join(lines[idx:idx + 6]))):
                payload = attrs.get("command") or attrs.get("exe") or ""
                payload = payload.strip().strip("'\"")
                if payload.startswith(".\\"):
                    payload = payload[2:]
                if payload and not payload.startswith(("http", "start ", "reg ", "powercfg", "bcdedit", "sc ")):
                    script = payload.split()[0] if payload.split() else ""
                    if script and re.search(r"\.(ps1|cmd|bat|exe|reg)$", script, re.I):
                        if norm(script) in downloaded:
                            continue  # produced at run time by !download
                        if not os.path.isfile(os.path.join(EXECUTABLES, norm(script))):
                            err(f"{rel}:{lineno}: executable '{script}' not found in Executables/")

    # reachability from main.yml
    main = os.path.join(CONFIG, "main.yml")
    reachable: set[str] = set()
    queue = ["main.yml"]
    while queue:
        current = queue.pop()
        if current in reachable:
            continue
        reachable.add(current)
        full = os.path.join(CONFIG, current)
        if not os.path.isfile(full):
            continue
        with open(full, encoding="utf-8-sig") as fh:
            for m in TASK_PATH_RE.finditer(fh.read()):
                queue.append(norm(m.group(1).strip()))

    for path in files:
        rel = norm(os.path.relpath(path, CONFIG))
        if rel not in reachable:
            err(f"{rel}: not reachable from main.yml")

    print(f"  yaml files  : {len(files)} ({both} both OS, {covered_win10} Win10-gated, {covered_win11} Win11-gated)")
    print(f"  tags used   : {', '.join(sorted(tags_used))}")


def main() -> int:
    print("X-ADYO OS playbook validation")
    print("-" * 60)
    options = check_conf()
    check_yaml(options)
    print("-" * 60)

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    if errors:
        print(f"\nFAILED: {len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"OK: no errors, {len(warnings)} warning(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
