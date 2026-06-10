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
from .files import WriteReceipt, resolve_output_path, write_private_file
from .sophon import (
    SophonClient,
    SophonDecodeError,
    SophonRemoteError,
    SophonUsageError,
)


DEFAULT_DOWNLOAD_LIMIT_BYTES = 25 * 1024 * 1024
LICENSE_NOTE = (
    "Sophon returns paper text/PDF only when licensing permits redistribution."
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
    except OSError as exc:
        print(f"sophon-research: local file error: {exc}", file=stderr)
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
    search.add_argument(
        "--limit",
        "--per",
        type=int,
        default=10,
        dest="limit",
        help="results per group (1..30)",
    )
    search.add_argument(
        "--sort",
        choices=("relevance", "title", "recent", "-relevance", "-title", "-recent"),
        help="order within each result group; prefix - to reverse",
    )
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
    paper.add_argument("--pdf", action="store_true", help="fetch paper PDF")
    paper.add_argument("--output", help="output file or existing directory")
    paper.add_argument(
        "--max-bytes",
        type=int,
        default=DEFAULT_DOWNLOAD_LIMIT_BYTES,
        help="maximum response size for text or PDF downloads",
    )
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
    result_type = SEARCH_RESULT_KEYS[args.result_type] if args.result_type else None
    data = client_factory().search(
        args.query,
        result_type=result_type,
        per=args.limit,
        sort=args.sort,
    )
    if args.result_type:
        group = result_type
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
    if args.text and args.pdf:
        raise SophonUsageError("paper accepts only one of --text or --pdf")
    if not args.text and not args.pdf:
        raise SophonUsageError(f"paper requires --text or --pdf. {LICENSE_NOTE}")
    if args.pdf and not args.output:
        raise SophonUsageError("paper --pdf requires --output")

    client = client_factory()
    if args.pdf:
        output_path = resolve_output_path(args.output, args.slug, ".pdf")
        data = client.paper_pdf(args.slug, max_bytes=args.max_bytes)
        receipt = write_private_file(
            output_path,
            data,
        )
        _print_receipt(
            receipt,
            slug=args.slug,
            kind="pdf",
            json_output=args.json_output,
            stdout=stdout,
        )
        return 0

    output_path = None
    if args.output:
        output_path = resolve_output_path(args.output, args.slug, ".txt")

    text = client.paper_text(args.slug, max_bytes=args.max_bytes)
    if args.output:
        receipt = write_private_file(
            output_path,
            text.encode("utf-8"),
        )
        _print_receipt(
            receipt,
            slug=args.slug,
            kind="text",
            json_output=args.json_output,
            stdout=stdout,
        )
    elif args.json_output:
        print(
            json_text({"slug": args.slug, "note": LICENSE_NOTE, **bounded_text(text)}),
            end="",
            file=stdout,
        )
    else:
        print(
            format_text_preview(f"Paper text: {args.slug}", text) + LICENSE_NOTE + "\n",
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


def _print_receipt(
    receipt: WriteReceipt,
    *,
    slug: str,
    kind: str,
    json_output: bool,
    stdout: TextIO,
) -> None:
    record = {
        "slug": slug,
        "kind": kind,
        "path": str(receipt.path),
        "bytes": receipt.bytes,
        "sha256": receipt.sha256,
        "note": LICENSE_NOTE,
    }
    if json_output:
        print(json_text(record), end="", file=stdout)
    else:
        print(
            "\n".join(
                [
                    f"Wrote {kind}: {receipt.path}",
                    f"Bytes: {receipt.bytes}",
                    f"SHA-256: {receipt.sha256}",
                    LICENSE_NOTE,
                ]
            ),
            file=stdout,
        )


if __name__ == "__main__":
    raise SystemExit(main())
