from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch
from urllib import error

from sophon_research.sophon import (
    SophonClient,
    SophonDecodeError,
    SophonRemoteError,
    SophonUsageError,
    canonical_entity_type,
    canonical_search_sort,
    canonical_search_type,
)


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload
        self.position = 0

    def read(self, size: int = -1) -> bytes:
        if size is None or size < 0:
            size = len(self.payload) - self.position
        start = self.position
        end = min(len(self.payload), start + size)
        self.position = end
        return self.payload[start:end]

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


class FakeTransport:
    def __init__(self, payload: bytes = b"{}"):
        self.payload = payload
        self.urls: list[str] = []
        self.timeouts: list[float] = []

    def __call__(self, req: object, timeout: float) -> FakeResponse:
        self.urls.append(req.full_url)
        self.timeouts.append(timeout)
        return FakeResponse(self.payload)


class SophonClientTests(unittest.TestCase):
    def test_api_index_reads_json_object(self) -> None:
        transport = FakeTransport(json.dumps({"name": "Sophon public API"}).encode())
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        result = client.api_index()

        self.assertEqual(result["name"], "Sophon public API")
        self.assertEqual(transport.urls, ["https://example.test/api/v1"])

    def test_base_url_can_come_from_environment(self) -> None:
        transport = FakeTransport(b'{"ok":true}')
        with patch.dict("os.environ", {"SOPHON_BASE": "https://alt.example/"}):
            client = SophonClient(urlopen=transport)

        client.api_index()

        self.assertEqual(transport.urls, ["https://alt.example/api/v1"])

    def test_search_url_encodes_query(self) -> None:
        transport = FakeTransport(b'{"query":"swe bench","results":{}}')
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        client.search("swe bench")

        self.assertEqual(
            transport.urls,
            ["https://example.test/api/v1/search?q=swe+bench"],
        )

    def test_search_url_encodes_optional_params(self) -> None:
        transport = FakeTransport(b'{"query":"swe bench","results":{}}')
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        client.search("swe bench", result_type="evals", per=2, sort="-recent")

        self.assertEqual(
            transport.urls,
            ["https://example.test/api/v1/search?q=swe+bench&type=eval&per=2&sort=-recent"],
        )

    def test_invalid_search_params_fail_before_network(self) -> None:
        transport = FakeTransport()
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        with self.assertRaises(SophonUsageError):
            client.search("swe bench", result_type="widgets")
        with self.assertRaises(SophonUsageError):
            client.search("swe bench", per=31)
        with self.assertRaises(SophonUsageError):
            client.search("swe bench", sort="hot")

        self.assertEqual(transport.urls, [])

    def test_entity_type_validation_happens_before_network(self) -> None:
        transport = FakeTransport()
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        with self.assertRaises(SophonUsageError):
            client.get_entity("widgets", "x")

        self.assertEqual(transport.urls, [])

    def test_get_entity_quotes_slug(self) -> None:
        transport = FakeTransport(b'{"slug":"a/b"}')
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        client.get_entity("eval", "a/b")

        self.assertEqual(transport.urls, ["https://example.test/api/v1/evals/a%2Fb"])

    def test_paper_text_reads_plain_text(self) -> None:
        transport = FakeTransport(b"paper text")
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        text = client.paper_text("paper-slug")

        self.assertEqual(text, "paper text")
        self.assertEqual(
            transport.urls,
            ["https://example.test/api/v1/papers/paper-slug/text"],
        )

    def test_paper_pdf_reads_bytes(self) -> None:
        transport = FakeTransport(b"%PDF-1.7")
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        data = client.paper_pdf("paper-slug")

        self.assertEqual(data, b"%PDF-1.7")
        self.assertEqual(
            transport.urls,
            ["https://example.test/api/v1/papers/paper-slug/pdf"],
        )

    def test_paper_download_stops_at_size_limit(self) -> None:
        transport = FakeTransport(b"abcdef")
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        with self.assertRaisesRegex(SophonRemoteError, "exceeded 4 bytes"):
            client.paper_pdf("paper-slug", max_bytes=4)

    def test_llms_full_uses_full_endpoint(self) -> None:
        transport = FakeTransport(b"# Sophon")
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        self.assertEqual(client.llms(full=True), "# Sophon")
        self.assertEqual(transport.urls, ["https://example.test/llms-full.txt"])

    def test_invalid_json_shape_fails(self) -> None:
        transport = FakeTransport(b"[]")
        client = SophonClient(base_url="https://example.test", urlopen=transport)

        with self.assertRaises(SophonDecodeError):
            client.api_index()

    def test_http_error_is_readable(self) -> None:
        def fail(req: object, timeout: float) -> FakeResponse:
            raise error.HTTPError(
                url=req.full_url,
                code=404,
                msg="Not Found",
                hdrs={},
                fp=io.BytesIO(b'{"error":"missing"}'),
            )

        client = SophonClient(base_url="https://example.test", urlopen=fail)

        with self.assertRaisesRegex(SophonRemoteError, "HTTP 404: missing"):
            client.api_index()

    def test_canonical_entity_aliases(self) -> None:
        self.assertEqual(canonical_entity_type("paper"), "papers")
        self.assertEqual(canonical_entity_type("people"), "people")

    def test_canonical_search_aliases(self) -> None:
        self.assertEqual(canonical_search_type("evals"), "eval")
        self.assertEqual(canonical_search_type("people"), "person")
        self.assertEqual(canonical_search_sort("-recent"), "-recent")


if __name__ == "__main__":
    unittest.main()
