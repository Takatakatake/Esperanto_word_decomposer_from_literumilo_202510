#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vortaro.tsv のフォーマット検証スクリプト

10697行目以降の追加エントリが正しいフォーマットになっているかチェック
"""

import sys
import os

def is_valid_transitivity(value):
    """transitiveco の有効な値かチェック"""
    return value in ['T', 'N', 'X']

def is_valid_senfinajxo(value):
    """senfinajxo の有効な値かチェック"""
    return value in ['SF', 'N']

def is_valid_kunfinajxo(value):
    """kunfinajxo の有効な値かチェック"""
    return value in ['KF', 'N']

def is_valid_limigo(value):
    """limigo の有効な値かチェック"""
    return value in ['NLM', 'LM', 'P', 'S', 'PRT', 'N']

def is_valid_rareco(value):
    """rareco の有効な値かチェック（0-4の整数）"""
    try:
        r = int(value)
        return 0 <= r <= 4
    except:
        return False

def is_valid_flago(value):
    """flago の有効な値かチェック"""
    return value in ['R', 'K', 'X']

def check_entry(line, line_num):
    """1行をチェック"""
    if not line.strip() or line.startswith('#'):
        return None

    fields = line.rstrip('\n').split('\t')

    if len(fields) < 9:
        return {
            'line': line_num,
            'morpheme': fields[0] if fields else '???',
            'error': f'列数不足（{len(fields)}列）'
        }

    morpheme, pos, meaning, col4, col5, col6, col7, col8, col9 = fields[:9]

    errors = []

    # 4列目（transitiveco）のチェック
    if not is_valid_transitivity(col4):
        errors.append(f'col4(transitiveco)="{col4}" は無効（T/N/X であるべき）')

    # 5列目（senfinajxo）のチェック
    if not is_valid_senfinajxo(col5):
        errors.append(f'col5(senfinajxo)="{col5}" は無効（SF/N であるべき）')

    # 6列目（kunfinajxo）のチェック
    if not is_valid_kunfinajxo(col6):
        errors.append(f'col6(kunfinajxo)="{col6}" は無効（KF/N であるべき）')

    # 7列目（limigo）のチェック
    if not is_valid_limigo(col7):
        errors.append(f'col7(limigo)="{col7}" は無効（NLM/LM/P/S/PRT/N であるべき）')

    # 8列目（rareco）のチェック
    if not is_valid_rareco(col8):
        errors.append(f'col8(rareco)="{col8}" は無効（0-4 の整数であるべき）')

    # 9列目（flago）のチェック
    if not is_valid_flago(col9):
        errors.append(f'col9(flago)="{col9}" は無効（R/K/X であるべき）')

    if errors:
        return {
            'line': line_num,
            'morpheme': morpheme,
            'pos': pos,
            'fields': fields[:9],
            'errors': errors
        }

    return None

def main():
    input_file = 'literumilo/literumilo/data/vortaro.tsv'

    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found", file=sys.stderr)
        sys.exit(1)

    print("10697行目以降のエントリをチェックしています...\n", file=sys.stderr)

    invalid_entries = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if line_num <= 10697:
                continue

            error_info = check_entry(line, line_num)
            if error_info:
                invalid_entries.append(error_info)

    if invalid_entries:
        print(f"❌ 不正なエントリが {len(invalid_entries)} 件見つかりました:\n", file=sys.stderr)

        for info in invalid_entries[:20]:  # 最初の20件を表示
            print(f"行 {info['line']}: {info['morpheme']} ({info.get('pos', '???')})", file=sys.stderr)
            if 'error' in info:
                print(f"  エラー: {info['error']}", file=sys.stderr)
            else:
                for err in info['errors']:
                    print(f"  - {err}", file=sys.stderr)
            print(f"  内容: {info.get('fields', [])}", file=sys.stderr)
            print(file=sys.stderr)

        if len(invalid_entries) > 20:
            print(f"... 他 {len(invalid_entries) - 20} 件", file=sys.stderr)

        # 全リストを出力
        print("\n全不正エントリリスト（TSV形式）:")
        print("line\tmorpheme\tpos\terror")
        for info in invalid_entries:
            morpheme = info['morpheme']
            pos = info.get('pos', '???')
            if 'error' in info:
                error_summary = info['error']
            else:
                error_summary = '; '.join(info['errors'])
            print(f"{info['line']}\t{morpheme}\t{pos}\t{error_summary}")

    else:
        print("✅ すべてのエントリが正しいフォーマットです！", file=sys.stderr)

    return len(invalid_entries)

if __name__ == '__main__':
    sys.exit(main())
