#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vortaro.tsv の包括的なフォーマット修正スクリプト v2

問題: 10697行目以降の追加エントリで、4列目（transitiveco）に
      description（単語形）が残っており、全体が1列右にずれている。

正しい形式:
  morpheme	POS	Meaning	transitiveco	senfinajxo	kunfinajxo	limigo	rareco	flago

現在の誤った形式:
  morpheme	POS	Meaning	description	transitiveco	senfinajxo	kunfinajxo	limigo	rareco

修正内容:
1. 4列目が T/N/X でない場合（description の場合）
   → 4列目を削除し、残りを左にシフト
2. 列が8列になった場合、9列目に R を追加
"""

import sys
import os
from datetime import datetime

def is_valid_transitivity(value):
    """transitiveco の有効な値かチェック"""
    return value in ['T', 'N', 'X']

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

    morpheme = fields[0]
    pos = fields[1]
    meaning = fields[2]
    col4 = fields[3]
    rest = fields[4:]
    comment_parts = fields[9:] if len(fields) > 9 else []

    modified = False

    # 4列目が有効な transitivity かチェック
    if not is_valid_transitivity(col4):
        # 4列目は description → 削除
        print(f"Line {line_num}: {morpheme} ({pos}) - Removing description '{col4}' from col4", file=sys.stderr)

        # 残りの列を1つ左にシフト
        # 元: morpheme POS Meaning description col5 col6 col7 col8 col9 [comment...]
        # 新: morpheme POS Meaning col5 col6 col7 col8 col9 flago [comment...]

        if len(rest) >= 5:
            # rest[0] = 元のcol5（transitiveco候補）
            # rest[1] = 元のcol6（senfinajxo候補）
            # rest[2] = 元のcol7（kunfinajxo候補）
            # rest[3] = 元のcol8（limigo候補）
            # rest[4] = 元のcol9（rareco候補）
            # rest[5] 以降 = コメント

            new_trans = rest[0] if is_valid_transitivity(rest[0]) else 'N'
            new_senfinajxo = rest[1] if rest[1] in ['SF', 'N'] else 'N'
            new_kunfinajxo = rest[2] if rest[2] in ['KF', 'N'] else 'KF'
            new_limigo = rest[3]
            new_rareco = rest[4]

            # flago を決定
            if len(rest) >= 6:
                new_flago = rest[5] if rest[5] in ['R', 'K', 'X'] else 'R'
                comment_parts = rest[6:]
            else:
                new_flago = 'R'
                comment_parts = []

            new_fields = [morpheme, pos, meaning, new_trans, new_senfinajxo,
                          new_kunfinajxo, new_limigo, new_rareco, new_flago]

            print(f"  → Shifted columns left, transitiveco={new_trans}, senfinajxo={new_senfinajxo}, kunfinajxo={new_kunfinajxo}, flago={new_flago}", file=sys.stderr)

            modified = True
        else:
            # 列が足りない → そのまま
            return line, False

    else:
        # 4列目は既に有効 → 変更不要
        new_fields = fields[:9]
        comment_parts = fields[9:]

    if modified:
        result = '\t'.join(new_fields)
        if comment_parts:
            result += '\t' + '\t'.join(comment_parts)
        return result + '\n', True
    else:
        return line, False

def main():
    input_file = 'literumilo/literumilo/data/vortaro.tsv'
    output_file = 'literumilo/literumilo/data/vortaro_fixed_v2.tsv'
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
