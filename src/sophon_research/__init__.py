"""Sophon Research plugin package."""

__version__ = "0.1.1"

from .sophon import SophonClient, SophonError

__all__ = ["SophonClient", "SophonError", "__version__"]
