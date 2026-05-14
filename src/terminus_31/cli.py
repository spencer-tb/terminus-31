"""terminus-31 CLI entry point."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from terminus_31 import __version__
from terminus_31.commands import check as check_cmd
from terminus_31.commands import fuzz_8037 as fuzz_8037_cmd
from terminus_31.commands import init as init_cmd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="terminus-31",
        description=(
            "Agent-first operational workspace for Ethereum execution "
            "layer testing."
        ),
    )
    parser.add_argument("--version", action="version", version=__version__)
    sub = parser.add_subparsers(dest="command")

    init_parser = sub.add_parser(
        "init",
        help="Clone the manifest's repos and tools into ./tools/.",
    )
    init_parser.add_argument(
        "--devnet",
        required=True,
        help=(
            "Devnet identifier matching a file under manifests/, e.g. "
            "'bal-7' or 'bal-devnet-7'."
        ),
    )

    check_parser = sub.add_parser(
        "check",
        help="Probe PATH for manifest binaries; print install hints if missing.",
    )
    check_parser.add_argument(
        "--devnet",
        required=True,
        help="Devnet identifier (same form as `init`).",
    )

    fuzz_parser = sub.add_parser(
        "fuzz-8037",
        help="Run the EIP-8037 differential fuzz campaign.",
    )
    fuzz_parser.add_argument(
        "--devnet",
        required=True,
        help="Devnet identifier (same form as `init`).",
    )
    fuzz_parser.add_argument(
        "--hours",
        type=float,
        default=None,
        help="Run duration in hours. If omitted, runs until interrupted.",
    )
    fuzz_parser.add_argument(
        "--engine",
        action="append",
        dest="engines",
        default=None,
        help=(
            "goevmlab engine to use. Repeat to use multiple. Defaults "
            "to the four eip8037* engines."
        ),
    )
    fuzz_parser.add_argument(
        "--parallel",
        type=int,
        default=4,
        help="Parallel goroutines in goevmlab generic-fuzzer (default 4).",
    )

    sub.add_parser(
        "help",
        help="Show help for every subcommand (top-level + init/check/fuzz-8037).",
    )
    return parser


def _print_all_help(parser: argparse.ArgumentParser) -> None:
    """Print help for the top-level parser and every subcommand."""
    parser.print_help()
    print()
    for action in parser._actions:
        if not isinstance(action, argparse._SubParsersAction):
            continue
        for name, sub_parser in action.choices.items():
            if name == "help":
                continue
            print(f"--- {name} ---\n")
            sub_parser.print_help()
            print()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "init":
        return init_cmd.run(args.devnet, Path.cwd())
    if args.command == "check":
        return check_cmd.run(args.devnet, Path.cwd())
    if args.command == "fuzz-8037":
        return fuzz_8037_cmd.run(
            devnet=args.devnet,
            hours=args.hours,
            engines=args.engines,
            parallel=args.parallel,
            root=Path.cwd(),
        )
    if args.command == "help":
        _print_all_help(parser)
        return 0
    print(
        f"command {args.command!r} not yet implemented",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
