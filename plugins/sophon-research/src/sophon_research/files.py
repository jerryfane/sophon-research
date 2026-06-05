"""Safe local file writing for Sophon Research downloads."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path

from .sophon import SophonUsageError


@dataclass(frozen=True)
class WriteReceipt:
    path: Path
    bytes: int
    sha256: str


def resolve_output_path(output: str, slug: str, suffix: str) -> Path:
    """Resolve an output file path, treating existing directories as targets."""
    target = Path(output).expanduser()
    if target.exists() and target.is_dir():
        target = target / f"{safe_filename(slug)}{suffix}"
    if target.exists():
        raise SophonUsageError(f"refusing to overwrite existing file: {target}")
    parent = target.parent
    if not parent.exists():
        raise SophonUsageError(f"output directory does not exist: {parent}")
    if not parent.is_dir():
        raise SophonUsageError(f"output parent is not a directory: {parent}")
    return target


def write_private_file(path: Path, data: bytes) -> WriteReceipt:
    """Write bytes with private permissions and remove partial files on failure."""
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0)
    fd: int | None = None
    try:
        fd = os.open(path, flags, 0o600)
        view = memoryview(data)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise OSError("write returned no progress")
            view = view[written:]
        os.close(fd)
        fd = None
        return WriteReceipt(
            path=path,
            bytes=len(data),
            sha256=hashlib.sha256(data).hexdigest(),
        )
    except FileExistsError as exc:
        raise SophonUsageError(f"refusing to overwrite existing file: {path}") from exc
    except OSError:
        if fd is not None:
            try:
                os.close(fd)
            except OSError:
                pass
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def safe_filename(value: str) -> str:
    cleaned = []
    for character in value.strip():
        if character.isalnum() or character in ("-", "_", "."):
            cleaned.append(character)
        else:
            cleaned.append("-")
    name = "".join(cleaned).strip(".-")
    return name or "paper"
