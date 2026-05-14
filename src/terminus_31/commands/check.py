"""Probe PATH for binaries declared in the manifest and print install hints."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

from terminus_31.commands.init import (
    load_manifest,
    resolve_manifest_path,
)


def get_version(path: str) -> str | None:
    """Try common version flags; return the first line of output if found."""
    for flag in ("--version", "version", "-V"):
        try:
            result = subprocess.run(
                [path, flag],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (subprocess.SubprocessError, OSError):
            continue
        if result.returncode != 0:
            continue
        output = (result.stdout or result.stderr).strip()
        if output and "unknown" not in output.lower():
            return output.splitlines()[0]
    return None


def _iter_binary_entries(manifest: dict):
    """Yield (category, name, entry) for every manifest entry with a `binary`."""
    for category in ("repos", "clients", "tools"):
        for name, entry in manifest.get(category, {}).items():
            if entry.get("binary"):
                yield category, name, entry


def run(devnet: str, root: Path) -> int:
    """Run ``terminus-31 check`` for the given devnet manifest."""
    manifest_path = resolve_manifest_path(devnet, root)
    if not manifest_path.exists():
        print(f"manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    manifest = load_manifest(manifest_path)
    print(f"check: {manifest.get('devnet', {}).get('name', devnet)} binaries")

    missing: list[tuple[str, str, dict]] = []
    for category, name, entry in _iter_binary_entries(manifest):
        binary = entry["binary"]
        path = shutil.which(binary)
        if path:
            version = get_version(path) or "(installed)"
            print(f"  ok    {binary:24} {version}")
        else:
            missing.append((category, name, entry))
            print(f"  miss  {binary:24} not on PATH ({category}.{name})")

    if missing:
        print("\ninstall hints:")
        for category, name, entry in missing:
            hint = entry.get("install_hint", "(no install hint in manifest)")
            print(f"\n  {entry['binary']}  ({category}.{name})")
            for line in hint.splitlines():
                print(f"      {line}")
        return 1
    print("\nall manifest binaries available")
    return 0
