#!/usr/bin/env python3
"""Build an X-ADYO OS .apbx.

The AME Wizard reads an .apbx that is a password-protected ZIP (password `malte`)
whose ROOT contains playbook.conf, Configuration/ and Executables/. This script
produces exactly that layout:

    dist/X-ADYO-OS-v<version>.apbx
        playbook.conf
        playbook.png
        Images/...
        Configuration/...
        Executables/...

Usage:
    python scripts/build-playbook.py                  # normal build
    python scripts/build-playbook.py --no-gate        # test build: no SupportedBuilds/Requirements
    python scripts/build-playbook.py --no-password    # plain zip (debug only, wizard rejects it)
    python scripts/build-playbook.py --out NAME.apbx

Encryption: AME Wizard refuses any archive that is not a ZIP encrypted with the
password `malte` (that is exactly what 7-Zip writes with `-tzip -p`). The ZipCrypto
cipher is implemented here in pure Python, so the build needs no external archiver
and works on a machine with no 7-Zip installed. Every entry is encrypted and the
build self-verifies by decrypting the archive back with `malte`.
"""

from __future__ import annotations

import argparse
import binascii
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import time
import zipfile
import zlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src", "playbook")
DIST = os.path.join(ROOT, "dist")
PASSWORD = "malte"
SKIP_NAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}


def read_version() -> str:
    conf = os.path.join(SRC, "playbook.conf")
    with open(conf, encoding="utf-8-sig") as fh:
        match = re.search(r"<Version>\s*([^<]+?)\s*</Version>", fh.read())
    return match.group(1) if match else "0.0.0"


def strip_gate(conf_path: str) -> None:
    """Remove SupportedBuilds and Requirements so any build can load the playbook."""
    with open(conf_path, encoding="utf-8-sig") as fh:
        text = fh.read()
    text = re.sub(r"\s*<SupportedBuilds>.*?</SupportedBuilds>", "", text, flags=re.S)
    text = re.sub(r"\s*<Requirements>.*?</Requirements>", "", text, flags=re.S)
    with open(conf_path, "w", encoding="utf-8") as fh:
        fh.write(text)


def collect_files(base: str) -> list[tuple[str, str]]:
    out = []
    for root, _dirs, files in os.walk(base):
        for name in files:
            if name in SKIP_NAMES or name.endswith(".apbx"):
                continue
            full = os.path.join(root, name)
            rel = os.path.relpath(full, base).replace(os.sep, "/")
            out.append((full, rel))
    return sorted(out, key=lambda item: item[1])


def regenerate_default_hive() -> None:
    """Keep Executables/default-user.reg in sync with the HKCU tweak modules."""
    generator = os.path.join(ROOT, "scripts", "gen-defaultuser-reg.py")
    if not os.path.isfile(generator):
        return
    result = subprocess.run([sys.executable, generator], capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"gen-defaultuser-reg.py failed:\n{result.stdout}\n{result.stderr}")
    print(f"  default hive: {result.stdout.strip()}")


def _build_crc_table() -> list[int]:
    table = []
    for index in range(256):
        value = index
        for _ in range(8):
            value = (value >> 1) ^ 0xEDB88320 if value & 1 else value >> 1
        table.append(value)
    return table


CRC_TABLE = _build_crc_table()


def _crc32_byte(crc: int, byte: int) -> int:
    return ((crc >> 8) ^ CRC_TABLE[(crc ^ byte) & 0xFF]) & 0xFFFFFFFF


class _ZipCrypto:
    """PKZIP 2.0 stream cipher (the scheme 7-Zip uses with -tzip -p)."""

    def __init__(self, password: bytes) -> None:
        self.k0, self.k1, self.k2 = 0x12345678, 0x23456789, 0x34567890
        for byte in password:
            self._update(byte)

    def _update(self, byte: int) -> None:
        self.k0 = _crc32_byte(self.k0, byte)
        self.k1 = ((self.k1 + (self.k0 & 0xFF)) * 134775813 + 1) & 0xFFFFFFFF
        self.k2 = _crc32_byte(self.k2, self.k1 >> 24)

    def _stream_byte(self) -> int:
        temp = (self.k2 | 2) & 0xFFFF
        return ((temp * (temp ^ 1)) >> 8) & 0xFF

    def encrypt(self, data: bytes) -> bytes:
        out = bytearray(len(data))
        for i, byte in enumerate(data):
            out[i] = byte ^ self._stream_byte()
            self._update(byte)
        return bytes(out)


def _dos_datetime(ts: float) -> tuple[int, int]:
    t = time.localtime(ts)
    year = max(1980, t.tm_year)
    dos_date = ((year - 1980) << 9) | (t.tm_mon << 5) | t.tm_mday
    dos_time = (t.tm_hour << 11) | (t.tm_min << 5) | (t.tm_sec // 2)
    return dos_time, dos_date


def write_zipcrypto(out_path: str, stage: str, files: list[tuple[str, str]], password: str) -> None:
    """Write a ZIP with every entry encrypted using ZipCrypto (password `malte`)."""
    dos_time, dos_date = _dos_datetime(time.time())
    central = bytearray()
    written = 0
    with open(out_path, "wb") as fh:
        for full, rel in files:
            with open(full, "rb") as src:
                raw = src.read()
            crc = binascii.crc32(raw) & 0xFFFFFFFF
            compressor = zlib.compressobj(6, zlib.DEFLATED, -15)
            packed = compressor.compress(raw) + compressor.flush()
            method = 8
            if len(packed) >= len(raw):
                packed, method = raw, 0

            cipher = _ZipCrypto(password.encode("utf-8"))
            header = bytearray(os.urandom(11))
            header.append((crc >> 24) & 0xFF)          # check byte for flag bit 0
            payload = cipher.encrypt(bytes(header) + packed)

            name = rel.encode("utf-8")
            offset = written
            local = struct.pack(
                "<IHHHHHIIIHH", 0x04034B50, 20, 0x0001, method, dos_time, dos_date,
                crc, len(payload), len(raw), len(name), 0,
            ) + name
            fh.write(local)
            fh.write(payload)
            written += len(local) + len(payload)

            central += struct.pack(
                "<IHHHHHHIIIHHHHHII", 0x02014B50, 20, 20, 0x0001, method, dos_time,
                dos_date, crc, len(payload), len(raw), len(name), 0, 0, 0, 0, 0, offset,
            ) + name

        central_offset = written
        fh.write(central)
        fh.write(struct.pack(
            "<IHHHHIIH", 0x06054B50, 0, 0, len(files), len(files),
            len(central), central_offset, 0,
        ))


def verify_archive(out_path: str, password: str | None) -> None:
    """Fail the build when the archive the wizard sees is not readable."""
    key = password.encode("utf-8") if password else None
    with zipfile.ZipFile(out_path) as zf:
        names = zf.namelist()
        if "playbook.conf" not in names:
            sys.exit("playbook.conf is not at the archive root")
        if password and not all(info.flag_bits & 0x0001 for info in zf.infolist()):
            sys.exit("some entries are not encrypted - AME Wizard will reject the playbook")
        data = zf.read("playbook.conf", pwd=key)
        if b"<Playbook" not in data:
            sys.exit("playbook.conf inside the archive is not valid XML")
        # every entry must decrypt with the same password and match its CRC
        for info in zf.infolist():
            payload = zf.read(info, pwd=key)
            if (binascii.crc32(payload) & 0xFFFFFFFF) != info.CRC:
                sys.exit(f"CRC mismatch after decryption: {info.filename}")


def build(out_name: str, password: bool, no_gate: bool) -> str:
    if not os.path.isfile(os.path.join(SRC, "playbook.conf")):
        sys.exit("src/playbook/playbook.conf not found - run from the repository root")

    regenerate_default_hive()
    version = read_version()
    os.makedirs(DIST, exist_ok=True)
    out_path = os.path.join(DIST, out_name or f"X-ADYO-OS-v{version}.apbx")

    with tempfile.TemporaryDirectory() as tmp:
        stage = os.path.join(tmp, "playbook")
        shutil.copytree(SRC, stage)
        if no_gate:
            strip_gate(os.path.join(stage, "playbook.conf"))
            print("  mode        : TEST BUILD (SupportedBuilds + Requirements stripped)")

        files = collect_files(stage)

        if password:
            # AME Wizard refuses anything that is not a ZIP encrypted with `malte`.
            # ZipCrypto (the format 7-Zip writes by default) is produced here in
            # pure Python so the build needs no external archiver.
            write_zipcrypto(out_path, stage, files, PASSWORD)
            print(f"  archive     : ZIP, ZipCrypto encrypted (password `{PASSWORD}`)")
        else:
            with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
                for full, rel in files:
                    zf.write(full, arcname=rel)
            print("  archive     : plain uncompressed-password ZIP (debug only)")

    verify_archive(out_path, PASSWORD if password else None)

    size = os.path.getsize(out_path)
    print(f"  version     : {version}")
    print(f"  files       : {len(files)}")
    print(f"  output      : {out_path} ({size / 1024 / 1024:.1f} MB)")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the X-ADYO OS .apbx")
    parser.add_argument("--out", help="output file name inside dist/")
    parser.add_argument("--no-password", action="store_true", help="write a plain ZIP")
    parser.add_argument("--no-gate", action="store_true", help="strip SupportedBuilds + Requirements (testing only)")
    args = parser.parse_args()

    print("X-ADYO OS build")
    print("-" * 60)
    build(args.out or "", password=not args.no_password, no_gate=args.no_gate)
    print("-" * 60)
    print("Open the .apbx with AME Wizard (Playbooks -> Open).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
