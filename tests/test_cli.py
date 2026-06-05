from __future__ import annotations

import io
import json
import unittest

from sophon_research import __version__
from sophon_research.cli import build_parser, run
from sophon_research.sophon import SophonRemoteError


class FakeClient:
    def api_index(self) -> dict[str, object]:
        return {
            "name": "Sophon public API",
            "docs": "https://sophon.at/about/api",
            "endpoints": {"evals": "https://sophon.at/api/v1/evals/{slug}"},
            "llms": {"index": "https://sophon.at/llms.txt"},
        }

    def search(self, query: str) -> dict[str, object]:
        return {
            "query": query,
            "results": {
                "eval": [
                    {
                        "slug": "swe-bench",
                        "title": "SWE-bench",
                        "score": 0.9,
                        "snippet": "software engineering benchmark",
                    }
                ],
                "paper": [
                    {
                        "slug": "paper-1",
                        "title": "Paper One",
                        "score": 0.5,
                        "snippet": "paper snippet",
                    }
                ],
            },
        }

    def get_entity(self, entity_type: str, slug: str) -> dict[str, object]:
        return {
            "slug": slug,
            "title": "SWE-bench",
            "shortDescription": "Real GitHub issues.",
            "canonicalUrl": "https://www.swebench.com",
        }

    def paper_text(self, slug: str) -> str:
        return f"text for {slug}"

    def llms(self, full: bool = False) -> str:
        return "# full" if full else "# index"


def fake_client_factory() -> FakeClient:
    return FakeClient()


class CliTests(unittest.TestCase):
    def test_help_exits_successfully(self) -> None:
        help_text = build_parser().format_help()

        self.assertIn("sophon-research", help_text)
        self.assertIn("Research AI evals", help_text)

    def test_version_command(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["version"],
            stdout=stdout,
            stderr=stderr,
            client_factory=fake_client_factory,
        )

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), f"sophon-research {__version__}")
        self.assertEqual(stderr.getvalue(), "")

    def test_doctor_prints_reachability(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["doctor"],
            stdout=stdout,
            stderr=stderr,
            client_factory=fake_client_factory,
        )

        self.assertEqual(code, 0)
        self.assertIn("ok Sophon API reachable", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_api_json_prints_stable_json(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["api", "--json"],
            stdout=stdout,
            stderr=stderr,
            client_factory=fake_client_factory,
        )

        self.assertEqual(code, 0)
        self.assertEqual(json.loads(stdout.getvalue())["name"], "Sophon public API")

    def test_search_type_filter_preserves_grouped_json(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["search", "swe-bench", "--type", "evals", "--limit", "1", "--json"],
            stdout=stdout,
            stderr=stderr,
            client_factory=fake_client_factory,
        )

        self.assertEqual(code, 0)
        data = json.loads(stdout.getvalue())
        self.assertEqual(sorted(data["results"]), ["eval"])
        self.assertEqual(data["results"]["eval"][0]["slug"], "swe-bench")

    def test_get_prints_entity_summary(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["get", "evals", "swe-bench"],
            stdout=stdout,
            stderr=stderr,
            client_factory=fake_client_factory,
        )

        self.assertEqual(code, 0)
        self.assertIn("SWE-bench", stdout.getvalue())
        self.assertIn("Slug: swe-bench", stdout.getvalue())

    def test_paper_requires_text_flag(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["paper", "paper-1"],
            stdout=stdout,
            stderr=stderr,
            client_factory=fake_client_factory,
        )

        self.assertEqual(code, 2)
        self.assertIn("requires --text", stderr.getvalue())

    def test_paper_text_json_is_bounded_record(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["paper", "paper-1", "--text", "--json"],
            stdout=stdout,
            stderr=stderr,
            client_factory=fake_client_factory,
        )

        self.assertEqual(code, 0)
        data = json.loads(stdout.getvalue())
        self.assertEqual(data["slug"], "paper-1")
        self.assertEqual(data["text"], "text for paper-1")

    def test_llms_full_prints_preview(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["llms", "--full"],
            stdout=stdout,
            stderr=stderr,
            client_factory=fake_client_factory,
        )

        self.assertEqual(code, 0)
        self.assertIn("llms-full.txt", stdout.getvalue())
        self.assertIn("# full", stdout.getvalue())

    def test_remote_errors_return_runtime_failure(self) -> None:
        def broken_client_factory() -> FakeClient:
            class BrokenClient(FakeClient):
                def api_index(self) -> dict[str, object]:
                    raise SophonRemoteError("network down")

            return BrokenClient()

        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(
            ["api"],
            stdout=stdout,
            stderr=stderr,
            client_factory=broken_client_factory,
        )

        self.assertEqual(code, 1)
        self.assertIn("network down", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
