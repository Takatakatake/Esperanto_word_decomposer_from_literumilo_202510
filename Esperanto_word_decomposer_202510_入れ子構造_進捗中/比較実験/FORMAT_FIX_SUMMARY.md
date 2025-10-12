# vortaro.tsv フォーマット修正サマリー

**日時**: 2025-10-12 16:56

## 問題の発覚

Batch 1-18 で追加した全234エントリが、vortaro.tsv の正式な仕様に違反していることが判明。

### 誤ったフォーマット:
```tsv
# SUBST/ADJ
morpheme	POS	Meaning	description	N	KF	NLM	rarity	P

# VERBO
morpheme	VERBO	Meaning	description	T/N/X	KF	NLM	rarity	P
```

### 正しいフォーマット:
```tsv
# SUBST/ADJ
morpheme	POS	Meaning	N	N	KF	NLM	rarity	R

# VERBO
morpheme	VERBO	Meaning	T/N/X	N	KF	NLM	rarity	R
```

## 問題の詳細

1. **4列目（transitiveco）**: 本来「T/N/X」であるべきところに description（単語形）が入っていた
   - 例: `argentin	SUBST	LANDO	argentino	N	KF...` ← `argentino` が4列目に
   - 例: `abolici	VERBO	N	abolicii	X	KF...` ← `abolicii` が4列目に

2. **9列目（flago）**: 本来「R/K/X」であるべきところに独自の「P」が入っていた

3. **影響範囲**: Batch 1-18 の全234エントリ
   - SUBST: 202個
   - ADJ: 24個
   - VERBO: 8個

## 修正作業

### 使用ツール:
- 修正スクリプト: `比較実験/fix_vortaro_format.py`

### バックアップ:
- `literumilo/literumilo/data/vortaro.tsv.bak.before_format_fix_20251012_165603`

### 修正内容:

#### パターン1: SUBST/ADJ（226個）
```
修正前: morpheme	SUBST	Meaning	description	N	KF	NLM	rarity	P
修正後: morpheme	SUBST	Meaning	N	N	KF	NLM	rarity	R
```
→ 4列目の description を削除、9列目を P→R

#### パターン2: VERBO（description あり、6個）
```
修正前: morpheme	VERBO	Meaning	description	T/N/X	KF	NLM	rarity	P
修正後: morpheme	VERBO	Meaning	T/N/X	N	KF	NLM	rarity	R
```
→ 4列目の description を削除、5列目の TRANS を4列目に移動、9列目を P→R

#### パターン3: VERBO（既に正しい、2個: aviad, demoraliz）
```
修正前: morpheme	VERBO	Meaning	T/N	N	KF	NLM	rarity	P
修正後: morpheme	VERBO	Meaning	T/N	N	KF	NLM	rarity	R
```
→ 9列目のみ P→R

## 修正結果

### 統計:
- **修正エントリ数**: 234個
- **flago=P のエントリ**: 0個（完全に除去）
- **flago 分布（修正後）**:
  - R: 10,870個
  - K: 686個
  - X: 151個

### 検証結果:
- ✅ ユニットテスト: 2/2 passed (100%)
- ✅ Batch 9 スポットチェック: 24/24 words (100%)
- ✅ Batch 18 スポットチェック: 50/50 words (100%)
- ✅ VERBO スポットチェック: 18/18 words (100%)

## 今後の対策

### 絶対に守るべきフォーマット:

```tsv
# SUBST（名詞）
morpheme	SUBST	Meaning	N	N	KF	NLM	rarity	R	# コメント

# ADJ（形容詞）
morpheme	ADJ	Meaning	N	N	KF	NLM	rarity	R	# コメント

# VERBO（動詞）
morpheme	VERBO	Meaning	T/N/X	N	KF	NLM	rarity	R	# コメント
```

### 重要な注意点:
1. ⚠️ **4列目は transitiveco のみ** - description を入れない
2. ⚠️ **9列目は R/K/X のみ** - 独自フラグ（P等）を使わない
3. ⚠️ **元のvortaro.tsv（1-10697行目）のフォーマットを厳密に遵守**

### 参考資料:
- 詳細は `比較実験/ongoing_memory_notes.md` の「CRITICAL FORMAT FIX」セクションを参照
