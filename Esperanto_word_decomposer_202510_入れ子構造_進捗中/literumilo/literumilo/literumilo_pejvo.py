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
from typing import Dict, List, Optional, Tuple

from .literumilo_utils import caret_to_accent
from .literumilo_entry import POS
from .literumilo_ending import get_ending

_PEJVO_CACHE: Optional[Dict[str, str]] = None

CANONICAL_SUFFIXES = {
    POS.Substantive: "o",
    POS.Adjective: "a",
    POS.Adverb: "e",
    POS.Verb: "i",
}

PARTICIPLE_SUFFIXES = ("ant", "int", "ont", "at", "it", "ot")


def _split_segmentation(segmentation: str) -> List[str]:
    """Split a dotted segmentation string into components."""
    if not segmentation:
        return []
    return [token for token in segmentation.split(".") if token]


def _join_tokens(tokens: List[str]) -> str:
    return ".".join(token for token in tokens if token)


def _remove_suffix_token(tokens: List[str], suffix: str) -> Optional[List[str]]:
    """Remove the expected canonical suffix token (o/a/e/i) if present."""
    if not suffix:
        return tokens[:]
    if tokens and tokens[-1] == suffix:
        return tokens[:-1]
    return None


def _extract_derivational_suffixes(stem: str) -> Tuple[str, List[str], bool]:
    """
    Extract participle / ig / iĝ suffixes from the stem.
    Returns the remaining base, the suffix tokens (in order),
    and a flag indicating whether the resulting base should be
    treated as a verb root.
    """
    suffix_tokens: List[str] = []
    derives_from_verb = False

    # Detect participles (only one can apply at the very end).
    for part in PARTICIPLE_SUFFIXES:
        if stem.endswith(part):
            stem = stem[: -len(part)]
            suffix_tokens.insert(0, part)
            derives_from_verb = True
            break

    # Detect ig / iĝ chains (they precede participles if any).
    while True:
        if stem.endswith("ig"):
            stem = stem[:-2]
            suffix_tokens.insert(0, "ig")
            derives_from_verb = True
            continue
        if stem.endswith("iĝ"):
            stem = stem[:-2]
            suffix_tokens.insert(0, "iĝ")
            derives_from_verb = True
            continue
        break

    return stem, suffix_tokens, derives_from_verb


def _lookup_canonical_tokens(
    pejvo_map: Dict[str, str], base: str, canonical_pos: POS
) -> Optional[List[str]]:
    """
    Try to obtain the canonical segmentation for a base by consulting the PEJVO map.
    We try both the bare base and the base + canonical suffix.
    """
    candidates: List[str] = []
    canonical_suffix = CANONICAL_SUFFIXES.get(canonical_pos)
    if base:
        candidates.append(base)
        if canonical_suffix:
            candidates.append(base + canonical_suffix)

    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        segmentation = pejvo_map.get(candidate)
        if not segmentation:
            continue
        tokens = _split_segmentation(segmentation)
        if canonical_suffix:
            stripped = _remove_suffix_token(tokens, canonical_suffix)
            if stripped is None:
                continue
            return stripped
        return tokens  # no suffix to strip
    return None


def _lookup_variations(pejvo_map: Dict[str, str], word: str) -> Optional[str]:
    """
    Attempt to derive a PEJVO segmentation for inflected forms such as plural nouns,
    verb conjugations, participles, and ig/iĝ derivatives.
    """
    ending = get_ending(word)
    if not ending:
        return None

    base = word[: -ending.length]
    if not base:
        return None

    suffix_tokens: List[str] = []
    canonical_pos = ending.part_of_speech

    # Extract participles and ig/iĝ. These imply verb derivation.
    stem, derived_tokens, derived_is_verb = _extract_derivational_suffixes(base)
    suffix_tokens.extend(derived_tokens)
    if derived_is_verb:
        canonical_pos = POS.Verb
    elif canonical_pos not in CANONICAL_SUFFIXES:
        # Only handle the standard parts of speech (noun/adj/adv/verb)
        return None

    canonical_tokens = _lookup_canonical_tokens(pejvo_map, stem, canonical_pos)
    if canonical_tokens is None:
        return None

    final_tokens = canonical_tokens + suffix_tokens + [ending.ending]
    return _join_tokens(final_tokens)


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
    word_lower = word.lower()
    pejvo_map = load_pejvo_decompositions()
    direct = pejvo_map.get(word_lower)
    if direct:
        return direct
    return _lookup_variations(pejvo_map, word_lower)


def _clear_cache():
    """Reset the in-memory cache (primarily for testing)."""
    global _PEJVO_CACHE
    _PEJVO_CACHE = None
