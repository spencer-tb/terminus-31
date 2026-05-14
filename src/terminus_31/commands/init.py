"""Clone the manifest's repos and tools into ./tools/."""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path


def resolve_manifest_path(devnet: str, root: Path) -> Path:
    """Resolve a ``--devnet`` value to its manifest file path.

    Accepts the long form (``bal-devnet-7``) as-is, or the short form
    (``bal-7``) which is expanded to ``bal-devnet-7``.
    """
    if "-devnet-" not in devnet:
        parts = devnet.rsplit("-", 1)
        if len(parts) == 2 and parts[1].isdigit():
            devnet = f"{parts[0]}-devnet-{parts[1]}"
    return root / "manifests" / f"{devnet}.toml"


def load_manifest(path: Path) -> dict:
    with path.open("rb") as f:
        return tomllib.load(f)


def current_branch(workdir: Path) -> str | None:
    """Return the branch at ``workdir``, or None if detached / not a repo."""
    if not (workdir / ".git").exists():
        return None
    result = subprocess.run(
        ["git", "-C", str(workdir), "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return branch if branch != "HEAD" else None


def is_clean(workdir: Path) -> bool:
    """Return True if ``workdir`` has no uncommitted changes."""
    result = subprocess.run(
        ["git", "-C", str(workdir), "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and not result.stdout.strip()


def clone_or_update(url: str, ref: str, dest: Path) -> str:
    """Clone ``url@ref`` into ``dest``, or update if present. Return status."""
    if dest.exists():
        if current_branch(dest) == ref:
            return "skip"
        if not is_clean(dest):
            return "dirty"
        subprocess.run(
            ["git", "-C", str(dest), "fetch", "--quiet", "origin", ref],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(dest), "checkout", "--quiet", ref],
            check=True,
        )
        return "update"
    dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", "--quiet", "--branch", ref, url, str(dest)],
        check=True,
    )
    return "clone"


def run(devnet: str, root: Path) -> int:
    """Run ``terminus-31 init`` for the given devnet manifest."""
    manifest_path = resolve_manifest_path(devnet, root)
    if not manifest_path.exists():
        print(f"manifest not found: {manifest_path}", file=sys.stderr)
        return 1

    manifest = load_manifest(manifest_path)
    meta = manifest.get("devnet", {})
    name = meta.get("name", devnet)
    print(f"init: {name} (from {manifest_path.relative_to(root)})")

    failures: list[str] = []
    for category in ("repos", "tools"):
        entries = manifest.get(category, {})
        for entry_name, entry in entries.items():
            url = entry.get("url")
            ref = entry.get("ref")
            if not url or not ref:
                print(
                    f"  [skip] {category}.{entry_name}: missing url/ref",
                    file=sys.stderr,
                )
                continue
            dest = root / "tools" / entry_name
            try:
                status = clone_or_update(url, ref, dest)
                rel = dest.relative_to(root)
                print(
                    f"  [{status:>6}] {category}.{entry_name}@{ref} -> {rel}"
                )
                if status == "dirty":
                    print(
                        f"           working tree has uncommitted changes; "
                        f"not updating",
                        file=sys.stderr,
                    )
                    failures.append(f"{category}.{entry_name}")
            except subprocess.CalledProcessError as exc:
                failures.append(f"{category}.{entry_name}")
                print(
                    f"  [  fail] {category}.{entry_name}@{ref}: {exc}",
                    file=sys.stderr,
                )

    if failures:
        print(f"\nfailed: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0
