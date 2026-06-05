"""Output formatting helpers for Sophon Research."""

from __future__ import annotations

import json
from typing import Any


DEFAULT_TEXT_LIMIT = 4000


def json_text(data: Any) -> str:
    """Return stable pretty JSON text."""
    return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def bounded_text(text: str, limit: int = DEFAULT_TEXT_LIMIT) -> dict[str, Any]:
    """Return a bounded preview record for potentially large text."""
    if limit < 0:
        limit = 0
    truncated = len(text) > limit
    return {
        "text": text[:limit],
        "chars": len(text),
        "truncated": truncated,
    }


def format_api_index(data: dict[str, Any]) -> str:
    lines = [str(data.get("name") or "Sophon public API")]
    description = data.get("description")
    if description:
        lines.append(str(description))
    docs = data.get("docs")
    if docs:
        lines.append(f"Docs: {docs}")
    endpoints = data.get("endpoints")
    if isinstance(endpoints, dict) and endpoints:
        lines.append("Endpoints: " + ", ".join(sorted(endpoints)))
    llms = data.get("llms")
    if isinstance(llms, dict) and llms:
        lines.append("LLM context: " + ", ".join(sorted(llms)))
    return "\n".join(lines) + "\n"


def limit_search_results(data: dict[str, Any], limit: int) -> dict[str, Any]:
    """Return a copy of search results with each result group bounded."""
    if limit < 0:
        limit = 0
    results = data.get("results")
    if not isinstance(results, dict):
        return dict(data)
    limited = dict(data)
    limited["results"] = {
        str(group): values[:limit] if isinstance(values, list) else values
        for group, values in results.items()
    }
    return limited


def format_search_results(data: dict[str, Any]) -> str:
    query = data.get("query")
    lines = [f"Search: {query}" if query else "Search results"]
    results = data.get("results")
    if not isinstance(results, dict) or not results:
        lines.append("No results.")
        return "\n".join(lines) + "\n"

    for group in sorted(results):
        values = results[group]
        if not isinstance(values, list) or not values:
            continue
        lines.append(f"\n{group}:")
        for item in values:
            if not isinstance(item, dict):
                continue
            slug = item.get("slug") or "-"
            title = item.get("title") or slug
            score = item.get("score")
            suffix = f" score={score}" if score is not None else ""
            lines.append(f"- {title} ({slug}){suffix}")
            snippet = item.get("snippet")
            if snippet:
                lines.append(f"  {str(snippet)[:240]}")
    return "\n".join(lines) + "\n"


def format_entity(data: dict[str, Any]) -> str:
    title = data.get("title") or data.get("name") or data.get("slug") or "Sophon entity"
    lines = [str(title)]
    slug = data.get("slug")
    if slug:
        lines.append(f"Slug: {slug}")
    for key in ("shortDescription", "description", "domain", "format", "license"):
        value = data.get(key)
        if value:
            lines.append(f"{key}: {value}")
    url = data.get("canonicalUrl") or data.get("url")
    if url:
        lines.append(f"URL: {url}")
    return "\n".join(lines) + "\n"


def format_text_preview(label: str, text: str, limit: int = DEFAULT_TEXT_LIMIT) -> str:
    preview = bounded_text(text, limit=limit)
    suffix = "\n[truncated]\n" if preview["truncated"] else "\n"
    return f"{label}\n\n{preview['text']}{suffix}"
