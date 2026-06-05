"""Read-only Sophon API client."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any, Callable, Protocol
from urllib import error, parse, request


DEFAULT_BASE_URL = "https://sophon.at"
DEFAULT_TIMEOUT_SECONDS = 15.0
READ_CHUNK_BYTES = 64 * 1024

ENTITY_TYPES = {
    "eval": "evals",
    "evals": "evals",
    "model": "models",
    "models": "models",
    "tool": "tools",
    "tools": "tools",
    "leaderboard": "leaderboards",
    "leaderboards": "leaderboards",
    "organization": "organizations",
    "organizations": "organizations",
    "person": "people",
    "people": "people",
    "capability": "capabilities",
    "capabilities": "capabilities",
    "paper": "papers",
    "papers": "papers",
}


class SophonError(RuntimeError):
    """Base class for Sophon client errors."""


class SophonUsageError(SophonError):
    """Raised for invalid local inputs before network calls."""


class SophonRemoteError(SophonError):
    """Raised when Sophon cannot be reached or returns an error."""


class SophonDecodeError(SophonError):
    """Raised when Sophon returns data with an unexpected shape."""


class ResponseLike(Protocol):
    def read(self, size: int = -1) -> bytes:
        """Read response bytes."""

    def __enter__(self) -> "ResponseLike":
        """Enter response context."""

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        """Exit response context."""


UrlOpen = Callable[..., ResponseLike]


@dataclass(frozen=True)
class SophonClient:
    """Small read-only client for Sophon's public API."""

    base_url: str | None = None
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS
    urlopen: UrlOpen = request.urlopen

    def __post_init__(self) -> None:
        base_url = self.base_url or os.environ.get("SOPHON_BASE") or DEFAULT_BASE_URL
        normalized = base_url.rstrip("/")
        if not normalized.startswith(("http://", "https://")):
            raise SophonUsageError(
                "Sophon base URL must start with http:// or https://"
            )
        object.__setattr__(self, "base_url", normalized)
        if self.timeout_seconds <= 0:
            raise SophonUsageError("timeout_seconds must be positive")

    def api_index(self) -> dict[str, Any]:
        """Return Sophon's API index JSON."""
        return self._get_json("/api/v1")

    def search(self, query: str) -> dict[str, Any]:
        """Search Sophon's catalog."""
        query = _require_non_empty(query, "query")
        return self._get_json("/api/v1/search", query={"q": query})

    def get_entity(self, entity_type: str, slug: str) -> dict[str, Any]:
        """Fetch an entity by type and slug."""
        canonical_type = canonical_entity_type(entity_type)
        slug = _require_non_empty(slug, "slug")
        return self._get_json(f"/api/v1/{canonical_type}/{_quote_segment(slug)}")

    def paper_text(self, slug: str, max_bytes: int | None = None) -> str:
        """Fetch paper text when Sophon exposes it."""
        slug = _require_non_empty(slug, "slug")
        return self._get_text(
            f"/api/v1/papers/{_quote_segment(slug)}/text",
            max_bytes=max_bytes,
        )

    def paper_pdf(self, slug: str, max_bytes: int | None = None) -> bytes:
        """Fetch paper PDF bytes when Sophon exposes them."""
        slug = _require_non_empty(slug, "slug")
        return self._get_bytes(
            f"/api/v1/papers/{_quote_segment(slug)}/pdf",
            max_bytes=max_bytes,
        )

    def llms(self, full: bool = False) -> str:
        """Fetch Sophon's agent-oriented LLM context text."""
        return self._get_text("/llms-full.txt" if full else "/llms.txt")

    def _get_json(
        self,
        path: str,
        query: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        text = self._get_text(path, query=query)
        try:
            decoded = json.loads(text)
        except json.JSONDecodeError as exc:
            raise SophonDecodeError("Sophon returned invalid JSON") from exc
        if not isinstance(decoded, dict):
            raise SophonDecodeError("Sophon returned JSON with an unexpected shape")
        return decoded

    def _get_text(
        self,
        path: str,
        query: dict[str, str] | None = None,
        max_bytes: int | None = None,
    ) -> str:
        raw = self._get_bytes(path, query=query, max_bytes=max_bytes)
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise SophonDecodeError("Sophon returned non-UTF-8 text") from exc

    def _get_bytes(
        self,
        path: str,
        query: dict[str, str] | None = None,
        max_bytes: int | None = None,
    ) -> bytes:
        max_bytes = _normalize_max_bytes(max_bytes)
        url = self._url(path, query=query)
        req = request.Request(
            url,
            headers={"User-Agent": "sophon-research/0.1.0"},
            method="GET",
        )
        try:
            with self.urlopen(req, timeout=self.timeout_seconds) as response:
                chunks: list[bytes] = []
                total = 0
                while True:
                    chunk = response.read(READ_CHUNK_BYTES)
                    if not chunk:
                        break
                    total += len(chunk)
                    if max_bytes is not None and total > max_bytes:
                        raise SophonRemoteError(
                            f"Sophon response exceeded {max_bytes} bytes"
                        )
                    chunks.append(chunk)
        except error.HTTPError as exc:
            detail = _http_error_detail(exc)
            raise SophonRemoteError(
                f"Sophon returned HTTP {exc.code}: {detail}"
            ) from exc
        except error.URLError as exc:
            raise SophonRemoteError(f"Sophon request failed: {exc.reason}") from exc
        except OSError as exc:
            raise SophonRemoteError(f"Sophon request failed: {exc}") from exc
        return b"".join(chunks)

    def _url(self, path: str, query: dict[str, str] | None = None) -> str:
        clean_path = path if path.startswith("/") else f"/{path}"
        url = f"{self.base_url}{clean_path}"
        if query:
            url = f"{url}?{parse.urlencode(query)}"
        return url


def canonical_entity_type(entity_type: str) -> str:
    """Return the canonical plural Sophon entity type."""
    normalized = _require_non_empty(entity_type, "entity_type").lower()
    canonical = ENTITY_TYPES.get(normalized)
    if canonical is None:
        allowed = ", ".join(sorted(set(ENTITY_TYPES.values())))
        raise SophonUsageError(
            f"unsupported entity type {entity_type!r}; expected one of: {allowed}"
        )
    return canonical


def _quote_segment(value: str) -> str:
    return parse.quote(value.strip(), safe="")


def _require_non_empty(value: str, field_name: str) -> str:
    normalized = str(value or "").strip()
    if not normalized:
        raise SophonUsageError(f"{field_name} must be non-empty")
    return normalized


def _normalize_max_bytes(max_bytes: int | None) -> int | None:
    if max_bytes is None:
        return None
    if max_bytes <= 0:
        raise SophonUsageError("max_bytes must be positive")
    return max_bytes


def _http_error_detail(exc: error.HTTPError) -> str:
    try:
        raw = exc.read(512).decode("utf-8", errors="replace").strip()
    except OSError:
        raw = ""
    if not raw:
        return exc.reason or "request failed"
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    if isinstance(decoded, dict):
        detail = decoded.get("error") or decoded.get("message") or decoded.get("detail")
        if detail:
            return str(detail)
    return raw
