#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vortaro.tsv の包括的なフォーマット修正スクリプト v3

問題: 10697行目以降の追加エントリで、以下の問題がある:
  1. 4列目に description が入っている
  2. senfinajxo 列が欠けている

元の誤った形式（9列）:
  morpheme	POS	Meaning	description	kunfinajxo	limigo	rareco	flago

正しい形式（9列）:
  morpheme	POS	Meaning	transitiveco	senfinajxo	kunfinajxo	limigo	rareco	flago

修正内容:
  1. 4列目が T/N/X でない → description として削除
  2. senfinajxo 列を N として挿入
  3. 残りの列を正しい位置に配置
"""

import sys
import os

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

    # 4列目が有効な transitivity かチェック
    if not is_valid_transitivity(col4):
        # 4列目は description → 削除して再構成
        # 元: morpheme POS Meaning description kunfinajxo limigo rareco flago [...]
        # 新: morpheme POS Meaning transitiveco senfinajxo kunfinajxo limigo rareco flago

        if len(fields) < 8:
            # 列が足りない
            return line, False

        # 元の列構造:
        # fields[3] = description（削除対象）
        # fields[4] = transitiveco（→ col4に移動）
        # fields[5] = kunfinajxo（→ col6に維持）
        # fields[6] = limigo（→ col7に維持）
        # fields[7] = rareco（→ col8に維持）
        # fields[8] = flago（→ col9に維持）

        # transitiveco を決定（fields[4]から取得、無効ならデフォルト）
        if is_valid_transitivity(fields[4]):
            new_trans = fields[4]
        elif pos == 'VERBO':
            new_trans = 'N'  # VERBOのデフォルト
        else:
            new_trans = 'N'  # SUBST/ADJのデフォルト

        new_senfinajxo = 'N'  # senfinajxoは常にN（欠けている列を補完）
        new_kunfinajxo = fields[5] if fields[5] in ['KF', 'N'] else 'KF'
        new_limigo = fields[6] if fields[6] in ['NLM', 'LM', 'P', 'S', 'PRT', 'N'] else 'NLM'
        new_rareco = fields[7]
        new_flago = fields[8] if fields[8] in ['R', 'K', 'X'] else 'R'

        comment_parts = fields[9:] if len(fields) > 9 else []

        new_fields = [morpheme, pos, meaning, new_trans, new_senfinajxo,
                      new_kunfinajxo, new_limigo, new_rareco, new_flago]

        print(f"Line {line_num}: {morpheme} ({pos}) - Removed description '{col4}'", file=sys.stderr)
        print(f"  → Fixed format: trans={new_trans}, senf={new_senfinajxo}, kunf={new_kunfinajxo}, lim={new_limigo}, rar={new_rareco}, flag={new_flago}", file=sys.stderr)

        result = '\t'.join(new_fields)
        if comment_parts:
            result += '\t' + '\t'.join(comment_parts)
        return result + '\n', True

    else:
        # 4列目は既に有効 → 変更不要
        # ただし、ADJで col5=KF の問題がある場合は修正
        if pos == 'ADJ' and len(fields) >= 6 and fields[4] == 'KF':
            # ADJでcol5がKFの場合、senfinajxoが欠けている
            # 元: morpheme ADJ Meaning N KF KF NLM rareco flago
            # 新: morpheme ADJ Meaning N N  KF NLM rareco flago
            # col5 の KF を N に置き換え
            new_fields = fields[:9]
            new_fields[4] = 'N'  # senfinajxo を N に
            comment_parts = fields[9:] if len(fields) > 9 else []
            print(f"Line {line_num}: {morpheme} (ADJ) - Fixed senfinajxo: changed col5 from KF to N", file=sys.stderr)
            result = '\t'.join(new_fields)
            if comment_parts:
                result += '\t' + '\t'.join(comment_parts)
            return result + '\n', True

        return line, False

def main():
    input_file = 'literumilo/literumilo/data/vortaro.tsv'
    output_file = 'literumilo/literumilo/data/vortaro_fixed_v3.tsv'
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
