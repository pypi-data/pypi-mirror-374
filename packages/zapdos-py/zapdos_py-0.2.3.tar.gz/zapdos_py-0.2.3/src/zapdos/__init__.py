"""Zapdos - A CLI tool for indexing video files."""

from .video_indexer import index
from .client import Client

__all__ = ["index", "Client"]