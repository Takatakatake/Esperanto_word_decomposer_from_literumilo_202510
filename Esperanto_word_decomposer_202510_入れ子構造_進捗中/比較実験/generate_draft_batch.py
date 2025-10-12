#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate a draft batch of dictionary additions (vortaro.tsv rows) from
`比較実験/invalid_plain_words.txt`, skipping entries already present in
`比較実験/progress_log.csv`.

Outputs:
  - 比較実験/batches/draft_vortaro_additions_YYYYMMDD_HHMM.tsv
  - Appends rows to 比較実験/progress_log.csv with status=drafted

This script only provides a heuristic draft for POS/transitivity, etc.
Human review is required before importing into data/vortaro.tsv.
"""
from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INV_PLAIN = ROOT / "比較実験" / "invalid_plain_words.txt"
PROGRESS = ROOT / "比較実験" / "progress_log.csv"
BATCH_DIR = ROOT / "比較実験" / "batches"


def read_progress() -> set[str]:
    done: set[str] = set()
    if not PROGRESS.exists():
        return done
    with PROGRESS.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = (row.get("status") or "").strip().lower()
            if status in {"drafted", "added", "skipped"}:
                done.add(row.get("lookup", ""))
    return done


def ensure_progress_header():
    if not PROGRESS.exists():
        with PROGRESS.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["display", "lookup", "status", "notes"]) 
            writer.writeheader()


def guess_pos_and_trans(word: str) -> tuple[str, str]:
    # Very conservative heuristic
    if word.endswith("i"):
        return "VERBO", "X"
    if word.endswith("o"):
        return "SUBST", "N"
    if word.endswith("a"):
        return "ADJ", "N"
    if word.endswith("e"):
        return "ADVERBO", "N"
    return "SUBST", "N"


def guess_morpheme(word: str) -> str:
    # Remove the final vowel if it matches a canonical ending
    if word and word[-1] in "oiaeu":
        return word[:-1]
    return word


def main(limit: int = 200) -> int:
    ensure_progress_header()
    already = read_progress()
    candidates: list[tuple[str, str]] = []

    with INV_PLAIN.open(encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            display, lookup = row[0].strip(), row[1].strip()
            if not lookup or lookup in already:
                continue
            # keep only lowercase single-token entries here
            if lookup != lookup.lower():
                continue
            if any(ch.isdigit() for ch in lookup):
                continue
            candidates.append((display, lookup))
            if len(candidates) >= limit:
                break

    if not candidates:
        print("No new candidates to draft.")
        return 0

    BATCH_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M")
    batch_path = BATCH_DIR / f"draft_vortaro_additions_{ts}.tsv"

    with batch_path.open("w", encoding="utf-8", newline="") as out:
        out.write("# morpheme\tPOS\tMEANING\tTRANS\tWITHOUT_END\tWITH_END\tSYNTH\tRARITY\tFLAG\t# SOURCE\n")
        for display, lookup in candidates:
            pos, trans = guess_pos_and_trans(lookup)
            morph = guess_morpheme(lookup)
            meaning = "N"
            without_end = "N"
            with_end = "KF"
            synth = "NLM"
            rarity = "3"
            flag = "R"
            out.write(f"{morph}\t{pos}\t{meaning}\t{trans}\t{without_end}\t{with_end}\t{synth}\t{rarity}\t{flag}\t# PIV:{display}\n")

    # append to progress
    with PROGRESS.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["display", "lookup", "status", "notes"]) 
        for display, lookup in candidates:
            writer.writerow({"display": display, "lookup": lookup, "status": "drafted", "notes": batch_path.name})

    print("Draft written:", batch_path)
    print("Drafted entries:", len(candidates))
    return 0


if __name__ == "__main__":
    n = 200
    if len(sys.argv) > 1:
        try:
            n = int(sys.argv[1])
        except Exception:
            pass
    raise SystemExit(main(n))

