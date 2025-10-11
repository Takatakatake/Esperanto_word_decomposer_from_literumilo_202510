#!/usr/bin/env python3
"""
Identify words that appear in PIV2020_structured.txt (headwords and derived forms)
but are absent from PEJVO.txt.

The script mirrors the normalisation pipeline used during manual exploration:
  * convert caret notation (c^, g^, …) to Unicode supersigned letters,
  * strip emphasis markers (_…_), slashes, hyphens, apostrophes, and footnote digits,
  * NFC-normalise the result and lowercase it,
  * treat only single-token words (optionally hyphenated) from PIV as candidates,
  * write a report listing the difference set preserving original orthography.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parent.parent
PIV_PATH = ROOT / "PIV2020_structured.txt"
PEJVO_PATH = ROOT / "PEJVO.txt"
OUTPUT_PATH = ROOT / "PIV2020にあってPEJVOになかった単語"

CARETS: Dict[str, str] = {
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
VALID_CHARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzĈĉĜĝĤĥĴĵŜŝŬŭ")
BOLD_PATTERN = re.compile(r"\*\*(.+?)\*\*")


def caret_to_accent(text: str) -> str:
    for src, dst in CARETS.items():
        text = text.replace(src, dst)
    return text


def canonicalize(text: str) -> str:
    return unicodedata.normalize("NFC", caret_to_accent(text))


def strip_markup(word: str) -> str:
    word = word.strip()
    if word.startswith("_") and word.endswith("_") and len(word) > 2:
        word = word[1:-1]
    return word


def strip_digits(word: str) -> str:
    """Remove meaningless footnote markers and digits from display strings."""
    return re.sub(r"[\d^]", "", word)


def clean_display(word: str) -> str:
    """Produce a user-facing representation without digits or trailing slashes."""
    word = strip_digits(word)
    return word.replace("/", "")


def normalise(entry: str) -> str:
    entry = canonicalize(entry)
    entry = strip_markup(entry)
    entry = strip_digits(entry)
    entry = entry.replace("/", "")
    entry = entry.replace("-", "").replace("'", "")
    cleaned = [ch for ch in entry if ch in VALID_CHARS]
    return "".join(cleaned).lower()


def is_single_token(word: str) -> bool:
    if not word:
        return False
    parts = word.split()
    if len(parts) == 1:
        pass
    elif len(parts) == 2 and "-" in word:
        pass
    else:
        return False

    allowed = VALID_CHARS.union({"-", "'"})
    return all(ch in allowed for ch in word)


def collect_piv_forms() -> Dict[str, str]:
    piv_forms = {}
    with PIV_PATH.open(encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line.startswith("### "):
                original = canonicalize(line[4:].strip())
                word = clean_display(original)
                if word and is_single_token(word):
                    norm = normalise(original)
                    if norm:
                        piv_forms.setdefault(norm, word)
            elif "Derived form:" in line:
                for candidate in BOLD_PATTERN.findall(line):
                    original = canonicalize(candidate.strip())
                    word = clean_display(original)
                    if word and is_single_token(word):
                        norm = normalise(original)
                        if norm:
                            piv_forms.setdefault(norm, word)
    return piv_forms


def collect_pejvo_forms() -> Dict[str, str]:
    pejvo_forms = {}
    with PEJVO_PATH.open(encoding="utf-8") as handle:
        for raw_line in handle:
            if ":" not in raw_line:
                continue
            original = canonicalize(raw_line.split(":", 1)[0])
            display = clean_display(original)
            if not is_single_token(display):
                continue
            norm = normalise(original)
            if norm:
                pejvo_forms.setdefault(norm, display)
    return pejvo_forms


def main() -> None:
    if not PIV_PATH.exists() or not PEJVO_PATH.exists():
        raise SystemExit("Required source files not found.")

    piv_map = collect_piv_forms()
    pejvo_map = collect_pejvo_forms()

    only_in_piv = {norm: word for norm, word in piv_map.items() if norm not in pejvo_map}

    lines = [
        "PIV2020 にあって PEJVO にない単語一覧 (見出し語 + 派生語, 空白語除外)",
        f"PIV2020_structured.txt (単語数・正規化後ユニーク): {len(piv_map):,}",
        f"PEJVO.txt (単語数・正規化後ユニーク): {len(pejvo_map):,}",
        f"差集合 (PIVのみ): {len(only_in_piv):,}",
        "判定ルール: 見出し語 + Derived form を対象。空白を含まない語、およびハイフンのみを含む二語構成は許可。"
        " /・-・アポストロフィ等を除去し小文字化して比較。",
        "ユニコード字上符の正規化には NFC を使用。",
        "以下のリストは原表記を保持しています。\n",
    ]

    for word in sorted(only_in_piv.values(), key=lambda w: w.lower()):
        lines.append(word)

    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
