#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vortaro.tsv の包括的なフォーマット修正スクリプト

問題: 10697行目以降の追加エントリの多くで、4列目（transitiveco）に
      description（単語形）が残っている。

修正内容:
1. 4列目が T/N/X でない場合 → 4列目を削除し、5列目以降を左にシフト
2. 5列目が SF/N でない場合 → N に修正
3. 6列目が KF/N でない場合 → KF に修正
4. 修正後、4列目を適切な transitiveco 値に設定
   - SUBST/ADJ → N
   - VERBO → 元の5列目が T/N/X なら維持、そうでなければ N
"""

import sys
import os
from datetime import datetime

def is_valid_transitivity(value):
    """transitiveco の有効な値かチェック"""
    return value in ['T', 'N', 'X']

def is_valid_senfinajxo(value):
    """senfinajxo の有効な値かチェック"""
    return value in ['SF', 'N']

def is_valid_kunfinajxo(value):
    """kunfinajxo の有効な値かチェック"""
    return value in ['KF', 'N']

def fix_entry(line, line_num, original_line_count):
    """1行を修正する"""
    if not line.strip() or line.startswith('#'):
        return line, False

    # 10697行目以前は修正しない
    if line_num <= original_line_count:
        return line, False

    fields = line.rstrip('\n').split('\t')

    # 9列未満なら問題あり（ただし修正せずそのまま）
    if len(fields) < 9:
        return line, False

    morpheme, pos, meaning, col4, col5, col6, col7, col8, col9 = fields[:9]
    comment = '\t'.join(fields[9:]) if len(fields) > 9 else ''

    modified = False

    # パターン1: 4列目が無効な transitivity
    if not is_valid_transitivity(col4):
        # 4列目は description → 削除して左にシフト
        print(f"Line {line_num}: {morpheme} ({pos}) - Removing description '{col4}' from col4", file=sys.stderr)

        # 5列目が有効な transitivity かチェック
        if is_valid_transitivity(col5):
            # 5列目が transitivity → それを4列目に
            new_trans = col5
            # 残りを左にシフト
            new_fields = [morpheme, pos, meaning, new_trans, col6, col7, col8, col9, col9]
            print(f"  → Moved transitivity '{new_trans}' from col5 to col4", file=sys.stderr)
        else:
            # 5列目も無効 → 4列目を N に設定
            if pos == 'VERBO':
                new_trans = 'N'  # VERBO のデフォルト
            else:
                new_trans = 'N'  # SUBST/ADJ のデフォルト
            # 5列目以降を左にシフト
            new_fields = [morpheme, pos, meaning, new_trans, col5, col6, col7, col8, col9]
            print(f"  → Set col4(transitiveco) to '{new_trans}'", file=sys.stderr)

        modified = True
    else:
        # 4列目は既に有効
        new_fields = [morpheme, pos, meaning, col4, col5, col6, col7, col8, col9]

    # パターン2: 5列目が無効な senfinajxo
    if not is_valid_senfinajxo(new_fields[4]):
        print(f"Line {line_num}: {morpheme} ({pos}) - Fixing col5(senfinajxo) '{new_fields[4]}' → 'N'", file=sys.stderr)
        new_fields[4] = 'N'
        modified = True

    # パターン3: 6列目が無効な kunfinajxo
    if not is_valid_kunfinajxo(new_fields[5]):
        print(f"Line {line_num}: {morpheme} ({pos}) - Fixing col6(kunfinajxo) '{new_fields[5]}' → 'KF'", file=sys.stderr)
        new_fields[5] = 'KF'
        modified = True

    if modified:
        if comment:
            return '\t'.join(new_fields) + '\t' + comment + '\n', True
        else:
            return '\t'.join(new_fields) + '\n', True
    else:
        return line, False

def main():
    input_file = 'literumilo/literumilo/data/vortaro.tsv'
    output_file = 'literumilo/literumilo/data/vortaro_fixed_comprehensive.tsv'
    ORIGINAL_LINE_COUNT = 10697  # 元のvortaro.tsvの行数

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found", file=sys.stderr)
        sys.exit(1)

    fixed_count = 0
    total_lines = 0

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        for line_num, line in enumerate(infile, 1):
            total_lines += 1
            fixed_line, was_fixed = fix_entry(line, line_num, ORIGINAL_LINE_COUNT)
            outfile.write(fixed_line)

            if was_fixed:
                fixed_count += 1

    print(f"\n修正完了: {total_lines} 行中 {fixed_count} 行を修正しました", file=sys.stderr)
    print(f"出力ファイル: {output_file}", file=sys.stderr)

if __name__ == '__main__':
    main()
