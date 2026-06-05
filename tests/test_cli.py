from __future__ import annotations

import io
import unittest

from sophon_research import __version__
from sophon_research.cli import build_parser, run


class CliTests(unittest.TestCase):
    def test_help_exits_successfully(self) -> None:
        help_text = build_parser().format_help()

        self.assertIn("sophon-research", help_text)
        self.assertIn("Research AI evals", help_text)

    def test_version_command(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()

        code = run(["version"], stdout=stdout, stderr=stderr)

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), f"sophon-research {__version__}")
        self.assertEqual(stderr.getvalue(), "")


if __name__ == "__main__":
    unittest.main()
