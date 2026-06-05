"""Command-line interface for Sophon Research."""

from __future__ import annotations

import argparse
import sys
from typing import TextIO

from . import __version__


def main(argv: list[str] | None = None) -> int:
    return run(argv, stdout=sys.stdout, stderr=sys.stderr)


def run(
    argv: list[str] | None = None,
    *,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "version":
        print(f"sophon-research {__version__}", file=stdout)
        return 0
    parser.print_help(stdout)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sophon-research",
        description="Research AI evals, models, tools, and papers using Sophon.",
    )
    parser.add_argument("--version", action="version", version=f"sophon-research {__version__}")
    subcommands = parser.add_subparsers(dest="command")
    subcommands.add_parser("version", help="show Sophon Research version")
    return parser
