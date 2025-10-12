#!/usr/bin/env python3
"""
POS競合を解決するスクリプト

ongoing_memory_notes.md の方針に従い:
1. ongoing_memory_notes.md言及の10語: ADJ/VERBO行を削除、SUBST行を保持
2. SUBSTVERBO → SUBST パターン: SUBSTVERBO行を削除、SUBST行を保持
3. その他の競合: 個別判断が必要（このスクリプトでは保留）
"""

from pathlib import Path
from collections import defaultdict
from datetime import datetime


VORTARO_PATH = Path('literumilo/literumilo/data/vortaro.tsv')
ORIG_END = 10697


def load_dictionary():
    """辞書を読み込み"""
    lines = VORTARO_PATH.read_text(encoding='utf-8').splitlines()
    all_roots = defaultdict(list)

    for idx, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        parts = line.split('\t')
        root = parts[0]
        all_roots[root].append((idx, line, parts))

    return lines, all_roots


def resolve_mentioned_10_conflicts(dry_run=True):
    """ongoing_memory_notes.md言及の10語のPOS競合を解決"""
    lines, all_roots = load_dictionary()

    # 10語のリスト
    target_10 = ['apercept', 'areol', 'baktericid', 'barbitur', 'batu',
                 'bos', 'enkaŭstik', 'epigenez', 'epik', 'epirogenez']

    lines_to_delete = set()

    print("=== ongoing_memory_notes.md言及の10語の処理 ===\n")

    for root in target_10:
        if root not in all_roots:
            print(f"警告: {root} が辞書に見つかりません")
            continue

        occurrences = all_roots[root]
        if len(occurrences) != 2:
            print(f"警告: {root} の出現回数が2でありません（{len(occurrences)}回）")
            continue

        # ソート（行番号順）
        sorted_occ = sorted(occurrences, key=lambda x: x[0])
        first_idx, first_line, first_parts = sorted_occ[0]
        second_idx, second_line, second_parts = sorted_occ[1]

        first_pos = first_parts[1] if len(first_parts) > 1 else '?'
        second_pos = second_parts[1] if len(second_parts) > 1 else '?'

        # ADJ/VERBO + SUBST パターンを確認
        if first_pos in ['ADJ', 'VERBO'] and second_pos == 'SUBST':
            lines_to_delete.add(first_idx)
            print(f"{root}:")
            print(f"  削除: 行{first_idx} POS={first_pos}")
            print(f"  保持: 行{second_idx} POS={second_pos}")
        else:
            print(f"警告: {root} が想定パターンと異なります")
            print(f"  行{first_idx}: POS={first_pos}")
            print(f"  行{second_idx}: POS={second_pos}")

    print(f"\n削除対象: {len(lines_to_delete)}行\n")

    if dry_run:
        print("*** ドライランモード: 実際の削除は行いません ***")
        return lines_to_delete

    # バックアップと削除実行
    backup_and_delete(lines, lines_to_delete, "mentioned_10")
    return lines_to_delete


def resolve_substverbo_conflicts(dry_run=True):
    """SUBSTVERBO → SUBST パターンの競合を解決"""
    lines, all_roots = load_dictionary()
    lines_to_delete = set()

    print("=== SUBSTVERBO → SUBST パターンの処理 ===\n")

    for root, occurrences in sorted(all_roots.items()):
        if len(occurrences) <= 1:
            continue

        # SUBSTVERBO と SUBST の組み合わせを検索
        substverbo_indices = []
        subst_indices = []

        for idx, line, parts in occurrences:
            pos = parts[1] if len(parts) > 1 else '?'
            if pos == 'SUBSTVERBO':
                substverbo_indices.append((idx, line, parts))
            elif pos == 'SUBST':
                subst_indices.append((idx, line, parts))

        # SUBSTVERBOとSUBSTの両方がある場合、SUBSTVERBOを削除
        if substverbo_indices and subst_indices:
            print(f"{root}:")
            for idx, line, parts in substverbo_indices:
                lines_to_delete.add(idx)
                meaning = parts[2] if len(parts) > 2 else '?'
                block = "元" if idx <= ORIG_END else "追加"
                print(f"  削除: 行{idx:5d} ({block:2s}) POS=SUBSTVERBO Meaning={meaning}")

            for idx, line, parts in subst_indices:
                meaning = parts[2] if len(parts) > 2 else '?'
                block = "元" if idx <= ORIG_END else "追加"
                print(f"  保持: 行{idx:5d} ({block:2s}) POS=SUBST       Meaning={meaning}")

    print(f"\n削除対象: {len(lines_to_delete)}行\n")

    if dry_run:
        print("*** ドライランモード: 実際の削除は行いません ***")
        return lines_to_delete

    # バックアップと削除実行
    backup_and_delete(lines, lines_to_delete, "substverbo")
    return lines_to_delete


def backup_and_delete(lines, lines_to_delete, label):
    """バックアップを作成し、指定行を削除"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = VORTARO_PATH.parent / f"vortaro.tsv.bak.{timestamp}_{label}"
    backup_path.write_text(VORTARO_PATH.read_text(encoding='utf-8'), encoding='utf-8')
    print(f"バックアップ作成: {backup_path}")

    new_lines = []
    for idx, line in enumerate(lines, start=1):
        if idx not in lines_to_delete:
            new_lines.append(line)

    VORTARO_PATH.write_text('\n'.join(new_lines) + '\n', encoding='utf-8')
    print(f"\n削除完了: {len(lines_to_delete)}行を削除しました")
    print(f"新しい総行数: {len(new_lines)}")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='POS競合を解決')
    parser.add_argument('--execute', action='store_true',
                        help='実際に削除を実行（デフォルトはドライラン）')
    parser.add_argument('--mode', choices=['mentioned_10', 'substverbo', 'all'],
                        default='all',
                        help='処理モード: mentioned_10（10語のみ）, substverbo（SUBSTVERBO→SUBST）, all（両方）')

    args = parser.parse_args()

    if args.mode in ['mentioned_10', 'all']:
        mentioned_10_lines = resolve_mentioned_10_conflicts(dry_run=not args.execute)
        print()

    if args.mode in ['substverbo', 'all']:
        substverbo_lines = resolve_substverbo_conflicts(dry_run=not args.execute)
