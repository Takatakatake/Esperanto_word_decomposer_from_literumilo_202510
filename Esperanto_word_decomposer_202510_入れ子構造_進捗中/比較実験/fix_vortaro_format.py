#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vortaro.tsv のフォーマット修正スクリプト

問題: Batch 1-18 で追加したエントリ（flago=P）が、
      4列目に description を含んでおり、仕様違反となっている。

修正内容:
1. SUBST/ADJ で4列目にdescriptionがあるもの → 4列目を削除
2. VERBO で4列目にdescriptionがあるもの → 4列目を削除、5列目を4列目に移動
3. すべての flago=P を flago=R に変更
"""

import sys
import os
from datetime import datetime

def is_valid_transitivity(value):
    """transitiveco の有効な値かチェック"""
    return value in ['T', 'N', 'X']

def fix_entry(line, line_num):
    """1行を修正する"""
    if not line.strip() or line.startswith('#'):
        return line

    fields = line.rstrip('\n').split('\t')

    # 9列でない、または flago != P なら変更不要
    if len(fields) != 9 or fields[8] != 'P':
        return line

    morpheme, pos, meaning, col4, col5, col6, col7, col8, flago = fields

    # パターン判定
    if pos in ['SUBST', 'ADJ']:
        # パターン1: SUBST/ADJ で4列目にdescriptionがある
        # 現在: morpheme	POS	Meaning	description	N	KF	NLM	rarity	P
        # 修正: morpheme	POS	Meaning	N	N	KF	NLM	rarity	R
        if not is_valid_transitivity(col4):
            # 4列目はdescription → 削除
            new_fields = [morpheme, pos, meaning, 'N', col5, col6, col7, col8, 'R']
            print(f"Line {line_num}: {pos} - Removed description '{col4}'", file=sys.stderr)
            return '\t'.join(new_fields) + '\n'
        else:
            # 4列目が既に正しい → flago のみ変更
            new_fields = fields[:]
            new_fields[8] = 'R'
            print(f"Line {line_num}: {pos} - Only changed flago P→R", file=sys.stderr)
            return '\t'.join(new_fields) + '\n'

    elif pos == 'VERBO':
        # パターン2/3: VERBO
        if not is_valid_transitivity(col4):
            # パターン2: 4列目にdescriptionがある
            # 現在: morpheme	VERBO	Meaning	description	T/N/X	KF	NLM	rarity	P
            # 修正: morpheme	VERBO	Meaning	T/N/X	N	KF	NLM	rarity	R
            if is_valid_transitivity(col5):
                new_fields = [morpheme, pos, meaning, col5, 'N', col6, col7, col8, 'R']
                print(f"Line {line_num}: VERBO - Removed description '{col4}', moved transitivity '{col5}'", file=sys.stderr)
                return '\t'.join(new_fields) + '\n'
            else:
                print(f"Line {line_num}: VERBO - WARNING: col4='{col4}', col5='{col5}' - unexpected pattern", file=sys.stderr)
                # とりあえず flago のみ変更
                new_fields = fields[:]
                new_fields[8] = 'R'
                return '\t'.join(new_fields) + '\n'
        else:
            # パターン3: 4列目が既に正しい transitivity
            # 現在: morpheme	VERBO	Meaning	T/N	N	KF	NLM	rarity	P
            # 修正: morpheme	VERBO	Meaning	T/N	N	KF	NLM	rarity	R
            new_fields = fields[:]
            new_fields[8] = 'R'
            print(f"Line {line_num}: VERBO - Only changed flago P→R (transitivity '{col4}' already correct)", file=sys.stderr)
            return '\t'.join(new_fields) + '\n'

    else:
        # その他のPOS → flago のみ変更
        new_fields = fields[:]
        new_fields[8] = 'R'
        print(f"Line {line_num}: {pos} - Only changed flago P→R", file=sys.stderr)
        return '\t'.join(new_fields) + '\n'

def main():
    input_file = 'literumilo/literumilo/data/vortaro.tsv'
    output_file = 'literumilo/literumilo/data/vortaro_fixed.tsv'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found", file=sys.stderr)
        sys.exit(1)

    fixed_count = 0

    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:

        for line_num, line in enumerate(infile, 1):
            fixed_line = fix_entry(line, line_num)
            outfile.write(fixed_line)

            if fixed_line != line:
                fixed_count += 1

    print(f"\n修正完了: {fixed_count} 行を修正しました", file=sys.stderr)
    print(f"出力ファイル: {output_file}", file=sys.stderr)

if __name__ == '__main__':
    main()
