#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simulate importing a draft batch (vortaro.tsv rows) without touching
the on-disk dictionary. Reports how many previously invalid words
become valid when the draft entries are injected in-memory.

Usage:
  python 比較実験/simulate_draft_import.py path/to/batch.tsv [limit]
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INV_PLAIN = ROOT / "比較実験" / "invalid_plain_words.txt"

sys.path.insert(0, str(ROOT / 'literumilo'))
from literumilo import check_word  # type: ignore
from literumilo import literumilo_check_word  # type: ignore
from literumilo.literumilo_entry import EspDictEntry  # type: ignore


def load_batch(batch_path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    with batch_path.open(encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            # Expect 10 columns (9 + comment)
            if len(row) < 9:
                continue
            rows.append(row[:9])
    return rows


def inject_entries(rows: list[list[str]]) -> int:
    """Create EspDictEntry objects and merge into the in-memory dictionary."""
    counter = 0
    dct = literumilo_check_word.esperanto_dictionary
    for r in rows:
        try:
            entry = EspDictEntry(r)
        except Exception:
            continue
        key = entry.morpheme.lower().replace('.', '')
        dct[key] = entry
        counter += 1
    return counter


def load_invalid_words(limit: int | None = None) -> list[str]:
    words: list[str] = []
    with INV_PLAIN.open(encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        header = next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            display, lookup = row[0].strip(), row[1].strip()
            # keep lowercase single token
            if lookup != lookup.lower():
                continue
            if any(ch.isdigit() for ch in lookup):
                continue
            if '-' in lookup or "'" in lookup:
                continue
            words.append(lookup)
            if limit is not None and len(words) >= limit:
                break
    return words


def eval_words(words: list[str]) -> tuple[int, list[tuple[str, str]]]:
    ok = 0
    bad: list[tuple[str, str]] = []
    for w in words:
        r = check_word(w)
        if r.valid:
            ok += 1
        else:
            bad.append((w, r.word))
    return ok, bad


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: simulate_draft_import.py path/to/batch.tsv [limit]")
        return 2
    batch_path = Path(sys.argv[1]).resolve()
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    # Baseline
    words = load_invalid_words(limit)
    base_ok, base_bad = eval_words(words)
    print(f"Baseline valid: {base_ok}/{len(words)}")

    # Inject draft entries
    rows = load_batch(batch_path)
    added = inject_entries(rows)
    print(f"Injected {added} draft entries")

    # Re-evaluate
    new_ok, new_bad = eval_words(words)
    print(f"After injection valid: {new_ok}/{len(words)} (Δ{new_ok - base_ok})")

    return 0


if __name__ == '__main__':
    raise SystemExit(main())

