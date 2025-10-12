#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import a reviewed batch (TSV rows for vortaro.tsv) into the on-disk dictionary.

Safety features:
  - Only imports lines whose trailing comment contains "# OK" (case-insensitive).
  - Creates a timestamped backup of data/vortaro.tsv before appending.
  - Updates 比較実験/progress_log.csv (status=added) for imported entries.

Usage:
  python 比較実験/import_reviewed_batch.py path/to/batch.tsv
"""
from __future__ import annotations

import csv
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_VORTARO = ROOT / 'literumilo' / 'literumilo' / 'data' / 'vortaro.tsv'
PROGRESS = ROOT / '比較実験' / 'progress_log.csv'


def ensure_progress() -> None:
    if not PROGRESS.exists():
        with PROGRESS.open('w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['display','lookup','status','notes'])
            writer.writeheader()


def load_progress() -> dict[str, dict[str,str]]:
    rows: dict[str, dict[str,str]] = {}
    if not PROGRESS.exists():
        return rows
    with PROGRESS.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            key = (r.get('lookup') or '').strip()
            if key:
                rows[key] = r
    return rows


def save_progress(progress: dict[str, dict[str,str]]) -> None:
    with PROGRESS.open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['display','lookup','status','notes'])
        writer.writeheader()
        for r in progress.values():
            writer.writerow(r)


def parse_batch(batch_path: Path) -> list[list[str]]:
    rows: list[list[str]] = []
    with batch_path.open(encoding='utf-8') as f:
        reader = csv.reader(f, delimiter='\t')
        for row in reader:
            if not row or row[0].startswith('#'):
                continue
            # Accept rows with 9 or more columns; the 10th is a free-form comment.
            if len(row) < 9:
                continue
            comment = (row[9] if len(row) > 9 else '').lower()
            if '# ok' not in comment:
                continue
            rows.append(row[:9])
    return rows


def main() -> int:
    if len(sys.argv) < 2:
        print('Usage: import_reviewed_batch.py path/to/batch.tsv')
        return 2
    batch_path = Path(sys.argv[1]).resolve()
    if not DATA_VORTARO.exists():
        print('Missing dictionary file:', DATA_VORTARO)
        return 1

    ensure_progress()
    progress = load_progress()
    rows = parse_batch(batch_path)
    if not rows:
        print('No rows with "# OK" found; aborting (nothing to import).')
        return 0

    # Backup
    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup = DATA_VORTARO.with_name(DATA_VORTARO.name + f'.bak.{ts}')
    shutil.copy2(DATA_VORTARO, backup)
    print('Backup written:', backup)

    # Append
    with DATA_VORTARO.open('a', encoding='utf-8') as out:
        for r in rows:
            out.write('\t'.join(r) + '\n')

    # Update progress (mark drafted entries as added if present)
    updated = 0
    for r in rows:
        morph = r[0]
        # Try to find by lookup/morpheme match
        for key, rec in list(progress.items()):
            if rec.get('lookup') == morph or rec.get('display') == morph:
                rec['status'] = 'added'
                rec['notes'] = f'imported:{batch_path.name}'
                updated += 1
    save_progress(progress)

    print(f'Imported entries: {len(rows)}; progress updated: {updated}')
    print('Done.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
