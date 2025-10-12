#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lint data/vortaro.tsv for suspicious morphemes (final-vowel issues).

Heuristics:
  - For POS SUBST, morpheme SHOULD NOT end with 'o'.
  - For POS ADJ,   morpheme SHOULD NOT end with 'a'.
  - For POS ADVERBO, morpheme SHOULD NOT end with 'e'.
  - For POS VERBO, morpheme SHOULD NOT end with 'i'.

This is a heuristic; exceptions may exist (abbreviations etc.).
"""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VORTARO = ROOT / 'literumilo' / 'literumilo' / 'data' / 'vortaro.tsv'


def main() -> int:
    if not VORTARO.exists():
        print('Not found:', VORTARO)
        return 1

    suspicious = []
    with VORTARO.open(encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            if len(row) < 2:
                continue
            morph, pos = row[0], row[1].upper()
            end = morph[-1] if morph else ''
            if pos == 'SUBST' and end == 'o':
                suspicious.append((morph, pos))
            elif pos == 'ADJ' and end == 'a':
                suspicious.append((morph, pos))
            elif pos == 'ADVERBO' and end == 'e':
                suspicious.append((morph, pos))
            elif pos == 'VERBO' and end == 'i':
                suspicious.append((morph, pos))

    print('Suspicious morphemes ending with a grammatical vowel:')
    for m, p in suspicious[:200]:
        print(f'  {m}\t{p}')
    print(f'Total suspicious: {len(suspicious)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

