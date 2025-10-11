#! -*- coding: utf-8
# literumilo_pejvo.py
#
# Helper utilities to load morpheme decompositions from the PEJVO dictionary.
# These decompositions provide a high quality fallback for literumilo when the
# built-in dictionary cannot analyse a word (or returns a less precise split).
#
# The loader is intentionally tolerant: if the PEJVO source file is missing,
# an empty map is returned and literumilo keeps its current behaviour.
#
# Author: OpenAI Codex assistant (2025)
#

import os
from typing import Dict, Optional, Tuple

from .literumilo_utils import caret_to_accent

_PEJVO_CACHE: Optional[Dict[str, str]] = None


def _default_pejvo_path() -> Optional[str]:
    """Return the default location of PEJVO.txt.
    The location can be overridden with the environment variable PEJVO_PATH.
    """
    env_path = os.environ.get("PEJVO_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    candidate = os.path.join(base_dir, "PEJVO.txt")
    if os.path.exists(candidate):
        return candidate

    return None


def _normalise_entry(entry: str) -> Optional[Tuple[str, str]]:
    """Normalise a raw PEJVO entry (left-hand side before the colon).
    Returns a tuple (word, segmentation) in lower case when the entry contains a
    valid decomposition; otherwise returns None.
    """
    cleaned = caret_to_accent(entry).strip().lower()
    if "/" not in cleaned:
        return None

    segments = [segment for segment in cleaned.split("/") if segment]
    if len(segments) < 2:
        return None

    word = "".join(segments)
    if not word.isalpha():
        return None

    segmentation = ".".join(segments)
    return word, segmentation


def load_pejvo_decompositions(pejvo_path: Optional[str] = None) -> Dict[str, str]:
    """Load PEJVO decompositions into a dictionary {word: segmentation}.
    The result is cached so the file is parsed at most once per process.
    """
    global _PEJVO_CACHE
    if _PEJVO_CACHE is not None:
        return _PEJVO_CACHE

    path = pejvo_path or _default_pejvo_path()
    data: Dict[str, str] = {}

    if not path:
        _PEJVO_CACHE = data
        return data

    try:
        with open(path, encoding="utf-8") as handle:
            for line in handle:
                if ":" not in line:
                    continue
                entry = line.split(":", 1)[0]
                normalised = _normalise_entry(entry)
                if not normalised:
                    continue
                word, segmentation = normalised
                data.setdefault(word, segmentation)
    except OSError:
        data = {}

    _PEJVO_CACHE = data
    return data


def lookup_pejvo(word: str) -> Optional[str]:
    """Return the PEJVO segmentation for the given word, if available."""
    if not word:
        return None
    return load_pejvo_decompositions().get(word)


def _clear_cache():
    """Reset the in-memory cache (primarily for testing)."""
    global _PEJVO_CACHE
    _PEJVO_CACHE = None
