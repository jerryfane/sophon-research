"""Command-line interface for Sophon Research."""

from __future__ import annotations

import argparse
import sys
from typing import Callable, TextIO

from . import __version__
from .formatting import (
    bounded_text,
    format_api_index,
    format_entity,
    format_search_results,
    format_text_preview,
    json_text,
    limit_search_results,
)
from .sophon import (
    SophonClient,
    SophonDecodeError,
    SophonRemoteError,
    SophonUsageError,
)


SEARCH_RESULT_KEYS = {
    "eval": "eval",
    "evals": "eval",
    "model": "model",
    "models": "model",
    "tool": "tool",
    "tools": "tool",
    "leaderboard": "leaderboard",
    "leaderboards": "leaderboard",
    "organization": "organization",
    "organizations": "organization",
    "person": "person",
    "people": "person",
    "capability": "capability",
    "capabilities": "capability",
    "paper": "paper",
    "papers": "paper",
}

ClientFactory = Callable[[], SophonClient]


def main(argv: list[str] | None = None) -> int:
    return run(argv, stdout=sys.stdout, stderr=sys.stderr)


def run(
    argv: list[str] | None = None,
    *,
    stdout: TextIO,
    stderr: TextIO,
    client_factory: ClientFactory = SophonClient,
) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        return args.func(args, stdout=stdout, client_factory=client_factory)
    except SophonUsageError as exc:
        print(f"sophon-research: {exc}", file=stderr)
        return 2
    except (SophonRemoteError, SophonDecodeError) as exc:
        print(f"sophon-research: {exc}", file=stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sophon-research",
        description="Research AI evals, models, tools, and papers using Sophon.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"sophon-research {__version__}",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    doctor = subcommands.add_parser("doctor", help="check Sophon API reachability")
    doctor.add_argument("--json", action="store_true", dest="json_output")
    doctor.set_defaults(func=cmd_doctor)

    api = subcommands.add_parser("api", help="show Sophon API index")
    api.add_argument("--json", action="store_true", dest="json_output")
    api.set_defaults(func=cmd_api)

    search = subcommands.add_parser("search", help="search Sophon's catalog")
    search.add_argument("query", help="search query")
    search.add_argument(
        "--type",
        choices=sorted(SEARCH_RESULT_KEYS),
        dest="result_type",
    )
    search.add_argument("--limit", type=int, default=10, help="results per group")
    search.add_argument("--json", action="store_true", dest="json_output")
    search.set_defaults(func=cmd_search)

    get = subcommands.add_parser("get", help="fetch a Sophon entity")
    get.add_argument("entity_type", help="entity type, such as evals or papers")
    get.add_argument("slug", help="Sophon entity slug")
    get.add_argument("--json", action="store_true", dest="json_output")
    get.set_defaults(func=cmd_get)

    paper = subcommands.add_parser("paper", help="fetch Sophon paper text")
    paper.add_argument("slug", help="Sophon paper slug")
    paper.add_argument("--text", action="store_true", help="fetch paper text")
    paper.add_argument("--json", action="store_true", dest="json_output")
    paper.set_defaults(func=cmd_paper)

    llms = subcommands.add_parser("llms", help="fetch Sophon's LLM context text")
    llms.add_argument("--full", action="store_true", help="fetch llms-full.txt")
    llms.add_argument("--json", action="store_true", dest="json_output")
    llms.set_defaults(func=cmd_llms)

    version = subcommands.add_parser("version", help="show Sophon Research version")
    version.set_defaults(func=cmd_version)
    return parser


def cmd_doctor(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    client_factory: ClientFactory,
) -> int:
    api = client_factory().api_index()
    result = {
        "ok": True,
        "name": api.get("name"),
        "docs": api.get("docs"),
    }
    if args.json_output:
        print(json_text(result), end="", file=stdout)
    else:
        print(f"ok Sophon API reachable: {result['name']}", file=stdout)
    return 0


def cmd_api(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    client_factory: ClientFactory,
) -> int:
    data = client_factory().api_index()
    if args.json_output:
        print(json_text(data), end="", file=stdout)
    else:
        print(format_api_index(data), end="", file=stdout)
    return 0


def cmd_search(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    client_factory: ClientFactory,
) -> int:
    data = client_factory().search(args.query)
    if args.result_type:
        group = SEARCH_RESULT_KEYS[args.result_type]
        results = data.get("results")
        values = results.get(group, []) if isinstance(results, dict) else []
        data = {**data, "results": {group: values}}
    data = limit_search_results(data, args.limit)
    if args.json_output:
        print(json_text(data), end="", file=stdout)
    else:
        print(format_search_results(data), end="", file=stdout)
    return 0


def cmd_get(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    client_factory: ClientFactory,
) -> int:
    data = client_factory().get_entity(args.entity_type, args.slug)
    if args.json_output:
        print(json_text(data), end="", file=stdout)
    else:
        print(format_entity(data), end="", file=stdout)
    return 0


def cmd_paper(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    client_factory: ClientFactory,
) -> int:
    if not args.text:
        raise SophonUsageError("paper requires --text until download support is added")
    text = client_factory().paper_text(args.slug)
    if args.json_output:
        print(
            json_text({"slug": args.slug, **bounded_text(text)}),
            end="",
            file=stdout,
        )
    else:
        print(
            format_text_preview(f"Paper text: {args.slug}", text),
            end="",
            file=stdout,
        )
    return 0


def cmd_llms(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    client_factory: ClientFactory,
) -> int:
    text = client_factory().llms(full=args.full)
    label = "llms-full.txt" if args.full else "llms.txt"
    if args.json_output:
        print(json_text({"source": label, **bounded_text(text)}), end="", file=stdout)
    else:
        print(format_text_preview(label, text), end="", file=stdout)
    return 0


def cmd_version(
    args: argparse.Namespace,
    *,
    stdout: TextIO,
    client_factory: ClientFactory,
) -> int:
    print(f"sophon-research {__version__}", file=stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
