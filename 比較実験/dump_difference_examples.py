#!/usr/bin/env python3
"""
Dump detailed comparison data between literumilo (current) and literumilo_old.

Outputs three sections:
 1. Words that the old version marks invalid but the current version resolves.
 2. Words whose segmentation mismatches the gold standard in the old version.
 3. Any residual mismatches in the current version (should be few).

Results are written to 'comparison_differences.txt' alongside this script.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
PEJVO_PATH = ROOT / "PEJVO.txt"
NEW_PACKAGE_ROOT = ROOT / "literumilo"
OLD_PACKAGE_ROOT = ROOT / "literumilo_old"
OUTPUT_PATH = Path(__file__).resolve().parent / "comparison_differences.txt"

CARET_MAP: Dict[str, str] = {
    "c^": "ĉ",
    "g^": "ĝ",
    "h^": "ĥ",
    "j^": "ĵ",
    "s^": "ŝ",
    "u^": "ŭ",
    "C^": "Ĉ",
    "G^": "Ĝ",
    "H^": "Ĥ",
    "J^": "Ĵ",
    "S^": "Ŝ",
    "U^": "Ŭ",
}


def decode_entry(raw: str) -> Optional[Tuple[str, str]]:
    text = raw.strip()
    if not text:
        return None
    for src, dst in CARET_MAP.items():
        text = text.replace(src, dst)
    text = text.lower()
    if "/" not in text:
        return None
    if any(ch in text for ch in " -#!0123456789"):
        return None
    segments = [segment for segment in text.split("/") if segment]
    if len(segments) < 2:
        return None
    word = "".join(segments)
    if not word.isalpha():
        return None
    segmentation = ".".join(segments)
    return word, segmentation


def load_dataset(path: Path) -> List[Tuple[str, str]]:
    dataset: List[Tuple[str, str]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if ":" not in line:
                continue
            decoded = decode_entry(line.split(":", 1)[0])
            if decoded:
                dataset.append(decoded)
    return dataset


def cleanup_modules() -> None:
    to_delete = [name for name in sys.modules if name == "literumilo" or name.startswith("literumilo.")]
    for name in to_delete:
        del sys.modules[name]


def import_check_word(package_root: Path):
    cleanup_modules()
    sys.path.insert(0, str(package_root))
    try:
        module = importlib.import_module("literumilo.literumilo_check_word")
    finally:
        sys.path.pop(0)
    return module.check_word


def main() -> int:
    dataset = load_dataset(PEJVO_PATH)
    if not dataset:
        print("Failed to load dataset.")
        return 1

    check_new = import_check_word(NEW_PACKAGE_ROOT)
    check_old = import_check_word(OLD_PACKAGE_ROOT)

    old_invalid: List[Tuple[str, str, str]] = []
    old_mismatch: List[Tuple[str, str, str]] = []
    new_mismatch: List[Tuple[str, str, str]] = []

    for word, expected in dataset:
        new_res = check_new(word)
        old_res = check_old(word)

        new_valid = bool(getattr(new_res, "valid", False))
        old_valid = bool(getattr(old_res, "valid", False))

        new_word = getattr(new_res, "word", "")
        old_word = getattr(old_res, "word", "")

        if not old_valid and new_valid:
            old_invalid.append((word, expected, old_word))
        elif old_valid:
            if old_word.lower() != expected:
                old_mismatch.append((word, expected, old_word))

        if new_valid and new_word.lower() != expected:
            new_mismatch.append((word, expected, new_word))

    cleanup_modules()

    with OUTPUT_PATH.open("w", encoding="utf-8") as out:
        out.write("Words resolved by literumilo (current) but invalid in literumilo_old:\n")
        out.write("---------------------------------------------------------------------\n")
        for word, expected, old_output in old_invalid:
            out.write(f"{word}\texpected={expected}\told_output={old_output}\n")
        out.write(f"\nTotal: {len(old_invalid)}\n\n")

        out.write("Words with segmentation mismatch in literumilo_old:\n")
        out.write("-----------------------------------------------\n")
        for word, expected, old_output in old_mismatch:
            out.write(f"{word}\texpected={expected}\told_output={old_output}\n")
        out.write(f"\nTotal: {len(old_mismatch)}\n\n")

        out.write("Residual mismatches in literumilo (current):\n")
        out.write("-------------------------------------------\n")
        for word, expected, new_output in new_mismatch:
            out.write(f"{word}\texpected={expected}\tnew_output={new_output}\n")
        out.write(f"\nTotal: {len(new_mismatch)}\n")

    print(f"Wrote detailed differences to {OUTPUT_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
