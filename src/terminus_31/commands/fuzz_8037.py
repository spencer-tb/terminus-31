"""Run the EIP-8037 differential fuzz campaign via goevmlab generic-fuzzer."""

from __future__ import annotations

import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from terminus_31.commands.init import load_manifest, resolve_manifest_path


DEFAULT_ENGINES = [
    "eip8037",
    "eip8037_sstore_restoration",
    "eip8037_deep_calls",
    "eip8037_create_sd_same_tx",
]


# Map manifest binary name -> goevmlab generic-fuzzer flag.
_BINARY_TO_FLAG = {
    "ethereum-spec-evm": "--eels",
    "revme": "--revme",
    "nethtest": "--nethermind",
    "evmstate": "--nimbus",
}


def find_generic_fuzzer(root: Path) -> Path:
    """Locate (and build if missing) the goevmlab generic-fuzzer binary."""
    src_dir = root / "tools" / "goevmlab" / "cmd" / "generic-fuzzer"
    binary = src_dir / "generic-fuzzer"
    if not src_dir.is_dir():
        raise RuntimeError(
            "goevmlab not found under tools/goevmlab. Run "
            "`terminus-31 init --devnet ...` first."
        )
    if not binary.is_file():
        print(f"building generic-fuzzer in {src_dir}", file=sys.stderr)
        subprocess.run(["go", "build", "."], cwd=src_dir, check=True)
    return binary


def collect_vm_paths(manifest: dict) -> dict[str, str]:
    """Return a {binary-name: PATH-resolved-path} for each manifest VM."""
    paths: dict[str, str] = {}
    for category in ("repos", "clients"):
        for name, entry in manifest.get(category, {}).items():
            binary = entry.get("binary")
            if not binary:
                continue
            resolved = shutil.which(binary)
            if resolved:
                paths[binary] = resolved
            else:
                print(
                    f"warning: '{binary}' ({category}.{name}) not on PATH "
                    f"— skipping",
                    file=sys.stderr,
                )
    return paths


def build_fuzzer_args(
    fuzzer: Path,
    vm_paths: dict[str, str],
    engines: list[str],
    outdir: Path,
    parallel: int,
) -> list[str]:
    args: list[str] = [str(fuzzer)]
    for binary, path in vm_paths.items():
        flag = _BINARY_TO_FLAG.get(binary)
        if flag is None:
            print(
                f"warning: no goevmlab flag mapped for '{binary}' — "
                f"binary will not participate",
                file=sys.stderr,
            )
            continue
        args.extend([flag, path])
    for engine in engines:
        args.extend(["--engine", engine])
    args.extend(
        [
            "--fork", "Amsterdam",
            "--outdir", str(outdir),
            "--parallel", str(parallel),
            "--cleanupFiles=true",
        ]
    )
    return args


def run(
    devnet: str,
    hours: float | None,
    engines: list[str] | None,
    parallel: int,
    root: Path,
) -> int:
    """Drive the EIP-8037 differential fuzz campaign."""
    manifest_path = resolve_manifest_path(devnet, root)
    if not manifest_path.exists():
        print(f"manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    manifest = load_manifest(manifest_path)
    devnet_name = manifest.get("devnet", {}).get("name", devnet)

    fuzzer = find_generic_fuzzer(root)
    vm_paths = collect_vm_paths(manifest)
    if len(vm_paths) < 2:
        print(
            f"need at least 2 VMs for differential fuzzing, found "
            f"{len(vm_paths)}: {list(vm_paths.keys())}",
            file=sys.stderr,
        )
        return 1

    chosen_engines = engines or DEFAULT_ENGINES

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    outdir = root / "out" / f"fuzz-8037-{timestamp}"
    outdir.mkdir(parents=True, exist_ok=True)

    args = build_fuzzer_args(
        fuzzer, vm_paths, chosen_engines, outdir, parallel
    )

    print(f"fuzz-8037: {devnet_name}")
    print(f"  out:      {outdir.relative_to(root)}")
    print(f"  vms:      {', '.join(vm_paths)}")
    print(f"  engines:  {', '.join(chosen_engines)}")
    print(f"  parallel: {parallel}")
    if hours is not None:
        print(f"  duration: {hours}h")
    print(f"  cmd:      {' '.join(args)}")
    print()

    if hours is not None:
        seconds = int(hours * 3600)
        args = ["timeout", str(seconds)] + args

    return subprocess.run(args).returncode
