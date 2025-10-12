#!/usr/bin/env python3
"""
POS競合の詳細分析スクリプト

ongoing_memory_notes.mdで言及された10語を含む、
全てのPOS競合を分析し、解決方針を提案する
"""

from pathlib import Path
from collections import defaultdict


VORTARO_PATH = Path('literumilo/literumilo/data/vortaro.tsv')
ORIG_END = 10697


def analyze_pos_conflicts():
    """POS競合の詳細分析"""
    lines = VORTARO_PATH.read_text(encoding='utf-8').splitlines()

    all_roots = defaultdict(list)
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        parts = line.split('\t')
        root = parts[0]
        all_roots[root].append((idx, line))

    # POS競合を特定
    pos_conflicts = []

    for root, occurrences in sorted(all_roots.items()):
        if len(occurrences) <= 1:
            continue

        pos_list = []
        for _, line in occurrences:
            parts = line.split('\t')
            if len(parts) > 1:
                pos_list.append(parts[1])

        if len(set(pos_list)) > 1:
            pos_conflicts.append((root, occurrences))

    print(f"=== POS競合の詳細分析 ===")
    print(f"POS競合がある語根: {len(pos_conflicts)}語\n")

    # ongoing_memory_notes.md言及の10語
    target_10 = ['apercept', 'areol', 'baktericid', 'barbitur', 'batu',
                 'bos', 'enkaŭstik', 'epigenez', 'epik', 'epirogenez']

    # カテゴリ分類
    original_block_conflicts = []  # 元ブロック内の競合
    added_block_conflicts = []     # 追加ブロックが関与
    mentioned_10_conflicts = []    # 言及された10語

    for root, occurrences in pos_conflicts:
        line_numbers = [idx for idx, _ in occurrences]

        if root in target_10:
            mentioned_10_conflicts.append((root, occurrences))
        elif all(idx <= ORIG_END for idx in line_numbers):
            original_block_conflicts.append((root, occurrences))
        else:
            added_block_conflicts.append((root, occurrences))

    print(f"カテゴリ分類:")
    print(f"  - 元ブロック内の競合: {len(original_block_conflicts)}語")
    print(f"  - 追加ブロックが関与: {len(added_block_conflicts)}語")
    print(f"  - ongoing_memory_notes.md言及の10語: {len(mentioned_10_conflicts)}語\n")

    # 言及された10語を詳細表示
    print("=== ongoing_memory_notes.md言及の10語 ===\n")
    for root, occurrences in mentioned_10_conflicts:
        print(f"{root}:")
        for idx, line in occurrences:
            parts = line.split('\t')
            pos = parts[1] if len(parts) > 1 else '?'
            meaning = parts[2] if len(parts) > 2 else '?'
            trans = parts[3] if len(parts) > 3 else '?'
            rareco = parts[7] if len(parts) > 7 else '?'
            flago = parts[8] if len(parts) > 8 else '?'
            block = "元" if idx <= ORIG_END else "追加"

            print(f"  行{idx:5d} ({block:2s}): POS={pos:15s} Meaning={meaning:12s} "
                  f"Trans={trans:3s} Rareco={rareco} Flago={flago}")
        print()

    # 追加ブロックが関与する競合（ongoing_memory_notes.mdの言及10語を除く）
    print(f"\n=== 追加ブロックが関与するPOS競合（言及10語を除く）===")
    print(f"合計: {len(added_block_conflicts)}語\n")

    # パターン分析
    pattern_counts = defaultdict(int)
    for root, occurrences in added_block_conflicts:
        pos_list = [line.split('\t')[1] for _, line in occurrences if len(line.split('\t')) > 1]
        pattern = ' vs '.join(sorted(set(pos_list)))
        pattern_counts[pattern] += 1

    print("POS競合パターン（頻度順）:")
    for pattern, count in sorted(pattern_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {pattern}: {count}語")

    print("\n（最初の10語の詳細）")
    for root, occurrences in added_block_conflicts[:10]:
        print(f"\n{root}:")
        for idx, line in occurrences:
            parts = line.split('\t')
            pos = parts[1] if len(parts) > 1 else '?'
            meaning = parts[2] if len(parts) > 2 else '?'
            block = "元" if idx <= ORIG_END else "追加"
            print(f"  行{idx:5d} ({block:2s}): POS={pos:15s} Meaning={meaning}")


def suggest_resolution_strategy():
    """解決方針の提案"""
    print("\n" + "="*60)
    print("=== POS競合の解決方針 ===\n")

    print("【方針1: SUBSTVERBO → SUBST の統一】")
    print("  多くの競合は追加ブロックで SUBSTVERBO → SUBST に変更されている")
    print("  → 追加ブロックの SUBST を優先し、元の SUBSTVERBO を削除\n")

    print("【方針2: ADJ/SUBST 競合】")
    print("  ongoing_memory_notes.mdの10語に多いパターン")
    print("  → 形態素解析の派生規則で対応できる場合は単一POSに統合")
    print("  → 必要な場合は両方を残す（辞書の仕様上、後行が有効）\n")

    print("【方針3: 元ブロック内の競合】")
    print("  R/X フラグの二重定義（`adiaux`, `alfabet`, `dum`, `kaj`, `se`）")
    print("  → 意図的な設計の可能性があるため慎重に判断\n")

    print("【推奨手順】")
    print("  1. ongoing_memory_notes.md言及の10語を個別検証")
    print("  2. SUBSTVERBO → SUBST パターンを一括処理")
    print("  3. その他は個別判断")
    print("="*60)


if __name__ == '__main__':
    analyze_pos_conflicts()
    suggest_resolution_strategy()
