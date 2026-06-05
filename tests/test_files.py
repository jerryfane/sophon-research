from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sophon_research.files import (
    resolve_output_path,
    safe_filename,
    write_private_file,
)
from sophon_research.sophon import SophonUsageError


class FileTests(unittest.TestCase):
    def test_resolve_output_path_uses_directory_and_safe_slug(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = resolve_output_path(directory, "paper/name", ".pdf")

            self.assertEqual(path, Path(directory) / "paper-name.pdf")

    def test_write_private_file_sets_private_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.txt"

            receipt = write_private_file(path, b"paper")

            self.assertEqual(receipt.bytes, 5)
            self.assertEqual(path.read_bytes(), b"paper")
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_write_private_file_requests_binary_mode_when_available(self) -> None:
        path = Path("paper.pdf")

        with (
            patch("sophon_research.files.os.O_BINARY", 0x8000, create=True),
            patch("sophon_research.files.os.open", return_value=123) as open_mock,
            patch("sophon_research.files.os.write", return_value=4),
            patch("sophon_research.files.os.close"),
        ):
            receipt = write_private_file(path, b"data")

        flags = open_mock.call_args.args[1]
        self.assertTrue(flags & 0x8000)
        self.assertEqual(receipt.bytes, 4)

    def test_write_private_file_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.txt"
            path.write_text("existing")

            with self.assertRaisesRegex(SophonUsageError, "overwrite"):
                write_private_file(path, b"new")

            self.assertEqual(path.read_text(), "existing")

    def test_write_private_file_removes_partial_file_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.txt"

            def fail_write(fd: int, data: bytes) -> int:
                raise OSError("disk full")

            with patch("os.write", side_effect=fail_write):
                with self.assertRaisesRegex(OSError, "disk full"):
                    write_private_file(path, b"paper")

            self.assertFalse(path.exists())

    def test_write_private_file_removes_partial_file_when_close_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.txt"
            real_close = os.close

            def fail_close(fd: int) -> None:
                real_close(fd)
                raise OSError("close failed")

            with patch("os.close", side_effect=fail_close):
                with self.assertRaisesRegex(OSError, "close failed"):
                    write_private_file(path, b"paper")

            self.assertFalse(path.exists())

    def test_safe_filename_has_fallback(self) -> None:
        self.assertEqual(safe_filename(" / "), "paper")


if __name__ == "__main__":
    unittest.main()
