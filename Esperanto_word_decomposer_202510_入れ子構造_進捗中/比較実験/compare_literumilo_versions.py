#!/usr/bin/env python3
"""
Compare the Esperanto morpheme analyser outputs of the current literumilo
package and the archived literumilo_old package using PEJVO.txt as gold data.

The script reports, for each implementation:
  * how many entries are recognised as valid words;
  * how many analysed segmentations match the gold morpheme split;
  * example disagreements to aid diagnosis.

It assumes the following workspace layout (paths are resolved relative to
this file):

  Esperanto_word_decomposer_.../
    ├── PEJVO.txt
    ├── literumilo/        (improved version)
    └── literumilo_old/    (archived reference version)
"""

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
PEJVO_PATH = ROOT / "PEJVO.txt"
NEW_PACKAGE_ROOT = ROOT / "literumilo"
OLD_PACKAGE_ROOT = ROOT / "literumilo_old"

# caret notation → accented letter map (PEJVO uses ^ for supersigned letters).
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


@dataclass
class EvaluationResult:
    name: str
    total: int
    invalid: int
    mismatch: int
    invalid_examples: List[Tuple[str, str, str]]
    mismatch_examples: List[Tuple[str, str, str]]

    @property
    def valid_count(self) -> int:
        return self.total - self.invalid

    @property
    def exact_match(self) -> int:
        return self.total - self.invalid - self.mismatch

    @property
    def valid_ratio(self) -> float:
        return self.valid_count / self.total if self.total else 0.0

    @property
    def exact_ratio(self) -> float:
        return self.exact_match / self.total if self.total else 0.0


def decode_entry(raw: str) -> Optional[Tuple[str, str]]:
    """Convert a PEJVO entry headword into (word, segmentation)."""
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


def load_gold_dataset(path: Path) -> List[Tuple[str, str]]:
    dataset: List[Tuple[str, str]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if ":" not in line:
                continue
            head = line.split(":", 1)[0]
            decoded = decode_entry(head)
            if decoded:
                dataset.append(decoded)
    return dataset


def cleanup_modules() -> None:
    """Remove literumilo modules from sys.modules to avoid cross-contamination."""
    to_delete = [name for name in sys.modules if name == "literumilo" or name.startswith("literumilo.")]
    for name in to_delete:
        del sys.modules[name]


def import_check_word(package_root: Path):
    """Import literumilo.literumilo_check_word from the specified package root."""
    sys.path.insert(0, str(package_root))
    try:
        module = importlib.import_module("literumilo.literumilo_check_word")
    finally:
        sys.path.pop(0)
    return module.check_word


def evaluate(name: str, package_root: Path, dataset: Sequence[Tuple[str, str]]) -> EvaluationResult:
    check_word = import_check_word(package_root)
    invalid = 0
    mismatch = 0
    invalid_examples: List[Tuple[str, str, str]] = []
    mismatch_examples: List[Tuple[str, str, str]] = []

    for word, expected in dataset:
        try:
            result = check_word(word)
        except Exception as exc:  # pragma: no cover - protective guard
            invalid += 1
            if len(invalid_examples) < 10:
                invalid_examples.append((word, expected, f"EXCEPTION: {exc!r}"))
            continue

        analyzed = getattr(result, "word", "") or ""
        valid_flag = bool(getattr(result, "valid", False))

        if not valid_flag:
            invalid += 1
            if len(invalid_examples) < 10:
                invalid_examples.append((word, expected, analyzed))
            continue

        normalized = analyzed.lower()
        if normalized != expected:
            mismatch += 1
            if len(mismatch_examples) < 10:
                mismatch_examples.append((word, expected, analyzed))

    cleanup_modules()
    return EvaluationResult(
        name=name,
        total=len(dataset),
        invalid=invalid,
        mismatch=mismatch,
        invalid_examples=invalid_examples,
        mismatch_examples=mismatch_examples,
    )


def format_examples(title: str, rows: Iterable[Tuple[str, str, str]]) -> str:
    lines = [title]
    for word, expected, observed in rows:
        lines.append(f"  - {word}: expected {expected} | observed {observed}")
    if len(lines) == 1:
        lines.append("  (none)")
    return "\n".join(lines)


def main() -> int:
    if not PEJVO_PATH.exists():
        print(f"PEJVO dataset not found at {PEJVO_PATH}")
        return 1

    dataset = load_gold_dataset(PEJVO_PATH)
    if not dataset:
        print("No valid entries extracted from PEJVO.txt; aborting.")
        return 1

    results: List[EvaluationResult] = []
    for name, root in (
        ("literumilo (current)", NEW_PACKAGE_ROOT),
        ("literumilo_old", OLD_PACKAGE_ROOT),
    ):
        if not root.exists():
            print(f"Package root missing: {root}")
            return 1
        results.append(evaluate(name, root, dataset))

    print("Esperanto morpheme analyser comparison")
    print("=====================================\n")
    print(f"Gold dataset: {len(dataset)} entries extracted from {PEJVO_PATH.name}\n")

    for res in results:
        print(f"{res.name}")
        print(f"  Valid analyses : {res.valid_count}/{res.total} ({res.valid_ratio:.2%})")
        print(f"  Exact matches  : {res.exact_match}/{res.total} ({res.exact_ratio:.2%})")
        print(f"  Invalid count  : {res.invalid}")
        print(f"  Mismatch count : {res.mismatch}\n")

    if len(results) == 2:
        newer, older = results
        delta_valid = newer.valid_count - older.valid_count
        delta_exact = newer.exact_match - older.exact_match
        print("Improvements (current - old)")
        print("-----------------------------")
        print(f"  Valid analyses : {delta_valid:+d}")
        print(f"  Exact matches  : {delta_exact:+d}\n")

        if newer.invalid_examples:
            print(format_examples(f"{newer.name} invalid examples:", newer.invalid_examples))
            print()
        if newer.mismatch_examples:
            print(format_examples(f"{newer.name} mismatch examples:", newer.mismatch_examples))
            print()

        if older.invalid_examples:
            print(format_examples(f"{older.name} invalid examples:", older.invalid_examples))
            print()
        if older.mismatch_examples:
            print(format_examples(f"{older.name} mismatch examples:", older.mismatch_examples))
            print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
