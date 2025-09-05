"""Marvelpy - A fully-typed Python client for the Marvel Comics API.

This package provides a comprehensive, async-first client for interacting with
the Marvel Comics API, featuring full type safety and modern Python practices.
"""

from ._version import __version__
from .hello import hello_world

__all__ = ["__version__", "hello_world"]
