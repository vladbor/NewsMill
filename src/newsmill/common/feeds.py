"""Loading and validating the newsfeeds.yaml configuration file."""

from __future__ import annotations

import logging
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


def load_newsfeeds(path: str) -> dict[str, str]:
    """Load RSS feed definitions from a YAML file.

    The expected format is a top-level ``newsfeeds`` key containing a list of
    dictionaries, each with a single ``"Agency Name": "RSS URL"`` pair.

    Args:
        path: Path to the newsfeeds.yaml file.

    Returns:
        A mapping of agency name to RSS feed URL.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is missing, malformed, or does not match the
            expected structure.
    """
    file_path = Path(path)
    if not file_path.is_file():
        logger.error("Newsfeeds file not found: %s", path)
        raise FileNotFoundError(f"Newsfeeds file not found: {path}")

    with file_path.open(encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, dict) or "newsfeeds" not in data:
        logger.error("Newsfeeds file %s is missing the 'newsfeeds' key", path)
        raise ValueError(f"Newsfeeds file {path} is missing the 'newsfeeds' key")

    feeds_list = data["newsfeeds"]
    if not isinstance(feeds_list, list):
        logger.error("'newsfeeds' in %s must be a list", path)
        raise ValueError(f"'newsfeeds' in {path} must be a list")

    feeds: dict[str, str] = {}
    for entry in feeds_list:
        if not isinstance(entry, dict) or len(entry) != 1:
            logger.error("Invalid newsfeed entry in %s: %r", path, entry)
            raise ValueError(f"Invalid newsfeed entry in {path}: {entry!r}")
        agency, url = next(iter(entry.items()))
        if not isinstance(agency, str) or not isinstance(url, str):
            logger.error("Invalid newsfeed pair in %s: %r", path, entry)
            raise ValueError(f"Invalid newsfeed pair in {path}: {entry!r}")
        feeds[agency] = url

    return feeds
