#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-mark rows as '# OK' in a draft batch when high-confidence checks pass.

Heuristic policy:
  - Reconstruct a headword from morpheme+POS (o/a/e/i) and check `check_word`.
  - For SUBST: also require plural 'oj', acc 'on', and plural acc 'ojn' to be valid.
  - For ADJ: also require 'aj', 'an', 'ajn' to be valid.
  - For ADVERBO: base 'e' must be valid (acc 'en' is optional; do not require).
  - For VERBO: base 'i' must be valid and at least one finite form ('as' or 'is' or 'os' or 'us' or 'u') must be valid.

Edits the batch TSV in-place by appending ' # OK' to the final comment field.
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'literumilo'))
from literumilo import check_word  # type: ignore


def headword(morph: str, pos: str) -> str:
    pos = pos.upper()
    if pos == 'SUBST':
        return morph + 'o'
    if pos == 'ADJ':
        return morph + 'a'
    if pos == 'ADVERBO':
        return morph + 'e'
    if pos == 'VERBO':
        return morph + 'i'
    return morph


def is_valid(word: str) -> bool:
    r = check_word(word)
    return bool(r.valid)


def ok_for_row(morph: str, pos: str) -> bool:
    posu = pos.upper()
    base = headword(morph, posu)
    if not is_valid(base):
        return False
    if posu == 'SUBST':
        return all(is_valid(morph + sfx) for sfx in ['o', 'oj', 'on', 'ojn'])
    if posu == 'ADJ':
        return all(is_valid(morph + sfx) for sfx in ['a', 'aj', 'an', 'ajn'])
    if posu == 'ADVERBO':
        # base 'e' required; 'en' optional → do not require to avoid false negatives
        return True
    if posu == 'VERBO':
        # require base 'i' and at least one finite form
        return any(is_valid(morph + sfx) for sfx in ['as', 'is', 'os', 'us', 'u'])
    return True


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: auto_mark_ok_in_batch.py path/to/batch.tsv')
        return 2
    batch_path = Path(sys.argv[1]).resolve()
    rows = []
    with batch_path.open(encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            rows.append(row)

    if not rows:
        print('Empty batch file')
        return 1

    header = rows[0]
    changed = 0
    for i in range(1, len(rows)):
        row = rows[i]
        if not row or row[0].startswith('#'):
            continue
        if len(row) < 9:
            continue
        morph = row[0].strip()
        pos = row[1].strip()
        comment = row[9] if len(row) > 9 else ''
        if '# OK' in comment or '# ok' in comment.lower():
            continue
        try:
            if ok_for_row(morph, pos):
                if len(row) > 9:
                    row[9] = (comment + ' # OK').strip()
                else:
                    row.append('# OK')
                changed += 1
        except Exception:
            pass

    with batch_path.open('w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        for row in rows:
            writer.writerow(row)

    print(f'Marked {changed} rows as # OK in {batch_path.name}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

