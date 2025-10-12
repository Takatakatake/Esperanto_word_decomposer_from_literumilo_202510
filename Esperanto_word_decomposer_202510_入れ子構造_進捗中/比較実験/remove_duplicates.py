#!/usr/bin/env python3
"""
vortaro.tsv から重複語根を削除するスクリプト

重複のカテゴリ:
1. 完全重複（追加ブロック内）: 12語 → 後の出現を削除
2. POS競合: 57語 → 個別判断が必要（このスクリプトでは保留）
3. R/X/Kフラグ違い: 23語 → 個別判断が必要（このスクリプトでは保留）
4. その他の重複: 74語 → 個別判断が必要（このスクリプトでは保留）

このスクリプトは、カテゴリ1（完全重複）のみを自動削除します。
"""

from pathlib import Path
from collections import defaultdict
import sys
from datetime import datetime

VORTARO_PATH = Path('literumilo/literumilo/data/vortaro.tsv')
ORIG_END = 10697  # 元の辞書の最終行


def load_and_analyze_duplicates():
    """辞書を読み込み、重複を分析"""
    lines = VORTARO_PATH.read_text(encoding='utf-8').splitlines()

    all_roots = defaultdict(list)
    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        parts = line.split('\t')
        root = parts[0]
        all_roots[root].append((idx, line))

    duplicates = {root: occurrences for root, occurrences in all_roots.items()
                  if len(occurrences) > 1}

    return lines, all_roots, duplicates


def identify_complete_duplicates(duplicates):
    """完全重複（追加ブロック内）を特定"""
    complete_dups = []

    for root, occurrences in sorted(duplicates.items()):
        lines_content = [line for _, line in occurrences]
        line_numbers = [idx for idx, _ in occurrences]

        # 完全に同一かつ、すべて追加ブロック内
        if len(set(lines_content)) == 1 and all(idx > ORIG_END for idx in line_numbers):
            complete_dups.append((root, occurrences))

    return complete_dups


def remove_complete_duplicates(dry_run=True):
    """完全重複を削除（デフォルトはドライラン）"""
    lines, all_roots, duplicates = load_and_analyze_duplicates()
    complete_dups = identify_complete_duplicates(duplicates)

    print(f"=== 重複削除レポート ===")
    print(f"総行数: {len(lines)}")
    print(f"重複語根数: {len(duplicates)}")
    print(f"完全重複（追加ブロック内）: {len(complete_dups)}語\n")

    # 削除対象行を特定（最初の出現を残し、2回目以降を削除）
    lines_to_delete = set()

    for root, occurrences in complete_dups:
        sorted_occurrences = sorted(occurrences, key=lambda x: x[0])
        print(f"{root}: 保持=行{sorted_occurrences[0][0]}, 削除=", end="")

        for idx, line in sorted_occurrences[1:]:
            lines_to_delete.add(idx)
            print(f"行{idx}", end=" ")
        print()

    print(f"\n削除対象: {len(lines_to_delete)}行")
    print(f"削除後の総行数: {len(lines) - len(lines_to_delete)}")

    if dry_run:
        print("\n*** ドライランモード: 実際の削除は行いません ***")
        print("実際に削除するには --execute オプションを使用してください")
        return

    # バックアップ作成
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = VORTARO_PATH.parent / f"vortaro.tsv.bak.{timestamp}"
    backup_path.write_text(VORTARO_PATH.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"\nバックアップ作成: {backup_path}")

    # 削除実行
    new_lines = []
    for idx, line in enumerate(lines, start=1):
        if idx not in lines_to_delete:
            new_lines.append(line)

    VORTARO_PATH.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    print(f"\n削除完了: {len(lines_to_delete)}行を削除しました")
    print(f"新しい総行数: {len(new_lines)}")


def report_other_duplicates():
    """その他の重複を報告（削除は行わない）"""
    lines, all_roots, duplicates = load_and_analyze_duplicates()
    complete_dups = identify_complete_duplicates(duplicates)
    complete_dup_roots = {root for root, _ in complete_dups}

    # 完全重複以外の重複
    other_dups = {root: occ for root, occ in duplicates.items()
                  if root not in complete_dup_roots}

    print(f"\n=== その他の重複（手動判断が必要）===")
    print(f"合計: {len(other_dups)}語\n")

    # POS競合を特定
    pos_conflicts = []
    for root, occurrences in sorted(other_dups.items()):
        pos_list = []
        for _, line in occurrences:
            parts = line.split('\t')
            if len(parts) > 1:
                pos_list.append(parts[1])

        if len(set(pos_list)) > 1:
            pos_conflicts.append(root)

    print(f"POS競合がある重複: {len(pos_conflicts)}語")
    print("（例: 最初の10語）")
    for root in pos_conflicts[:10]:
        print(f"  {root}")
        for idx, line in other_dups[root]:
            parts = line.split('\t')
            pos = parts[1] if len(parts) > 1 else '?'
            print(f"    行{idx}: POS={pos}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='vortaro.tsvから重複を削除')
    parser.add_argument('--execute', action='store_true',
                        help='実際に削除を実行（デフォルトはドライラン）')
    parser.add_argument('--report-other', action='store_true',
                        help='その他の重複を報告')

    args = parser.parse_args()

    if args.report_other:
        report_other_duplicates()
    else:
        remove_complete_duplicates(dry_run=not args.execute)
