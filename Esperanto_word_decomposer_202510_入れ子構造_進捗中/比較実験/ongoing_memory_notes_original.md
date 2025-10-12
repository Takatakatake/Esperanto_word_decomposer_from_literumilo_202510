# Esperanto Morphology Project – Key Working Notes

This file captures the enduring guidelines and current workflow so that work can resume safely
whenever the conversation history is no longer available. It reflects agreements and constraints
from the current collaboration.

## Core Principles
- **Unique decomposition**: every orthographic form must map to exactly one morpheme split.
  - When two analyses conflict, prefer the split that keeps common / high-frequency words correct.
  - Rare or specialised forms may be sacrificed if they jeopardise mainstream vocabulary.
- **Frequency proxy**: rely on dictionary `rarity` scores (and later corpus counts) when choosing
  between competing segmentations (implemented in `literumilo_check_word.py`).

## NEW PRIORITY (2025-10-12): PEJVO → vortaro.tsv
**CRITICAL**: 2,730 roots exist in PEJVO but NOT in vortaro.tsv. These should be added FIRST before PIV-only words.
- Reason: PEJVO roots are already validated with correct morpheme decomposition (45,000+ entries)
- Method: Extract from PEJVO.txt, verify not in vortaro.tsv, add systematically
- File: `比較実験/PEJVO_missing_in_vortaro.txt` contains the full list
- Progress: Batch 1-19 completed = 211/2730 roots (7.7%)
  - Batch 1: 18 roots (abolici, aborigen, acetat, acetil, etc.)
  - Batch 2: 10 roots (akvarel, alkohol, ambulanc, ametist, etc.)
  - Batch 3: 14 roots (ampermetr, ampol, ananas, anekdot, anestez, etc.)
  - Batch 4: 12 roots (angil, anilin, ankr, anonim, anorak, etc.)
  - Batch 5: 12 roots (anser, anten, antimon, antipod, antonim, etc.)
  - Batch 6: 12 roots (antracit, antropolog, aort, apart, aperitiv, etc.)
  - Batch 7: 12 roots (apostol, apostrof, april, aprob, arane, etc.)
  - Batch 8: 12 roots (aren, argil, argument, ari, aristokrat, arkad, arkipelag, arkitekt, arkitektur, arkiv, armatur, arme)
  - Batch 9: 12 roots (argentin, ariergard, aristotel, arkiduk, artez, artiŝok, artritism, arĝent, asembl, asiri, aski, astigmatism)
  - Batch 10: 12 roots (astrakan, astronaŭtik, atik, atletik, atrepsi, avangard, averaĝ, avers, aviad, azi, aztek, azuki)
  - Batch 11: 12 roots (babel, badminton, baht, bakanal, bakteriologi, baktri, balkan, bandaĝ, bandoni, banĝ, barbarism, barjon)
  - Batch 12: 12 roots (basedov, baŭksit, bekerel, beletristik, bengal, benign, benzoat, bibliofili, bikonkav, bikonveks, bimetalism, bio)
  - Batch 13: 12 roots (biocenoz, biofizik, biogeografi, biomas, biosfer, biotop, birm, blenoragi, blog, blokhaŭs, bodi, bohemi)
  - Batch 14: 12 roots (boleto, bosni, boson, boston, braman, branĉ, brazil, brazilj, briofit, bromid, bronkit, brontosaŭr)
  - Batch 15: 10 roots (bubal, bud, bule, bulgar, buljon, buton, celsius, cement, cerber, ceter)
  - Batch 16: 4 roots (cezar, cifer, cipres, civit)
  - Batch 17: 11 roots (cukcukcikad, dac, damask, decibel, decigram, decilitr, decimetr, defaŭlt, dehidraci, deism, deist)
  - Batch 18: 12 roots (dekad, dekagram, dekalitr, dekametr, delft, demograf, demoraliz, denominaci, densometr, depresi, dermatit, dermatolog)
  - Batch 19: 12 roots (dermatologi, dermatoz, detektor, detonaci, devon, devoni, dialektolog, dialektologi, diartr, dias, diaskop, diaterm)
- Success rate: 100% validation (重複・語根単体除外後)
- Spot-check Batch 9: 23/23 words (100%) ✓
- Spot-check Batch 10: 33/33 words (100%) ✓
- Spot-check Batch 11: 34/34 words (100%) ✓
- Spot-check Batch 12: 33/33 words (100%) ✓
- Spot-check Batch 13: 32/32 words (100%) ✓
- Spot-check Batch 14: 47/47 words (100%) ✓
- Spot-check Batch 15: 18/18 words (100%) ✓
- Spot-check Batch 16: 11/11 words (100%) ✓
- Spot-check Batch 17: 24/24 words (100%) ✓
- Spot-check Batch 18: 50/50 words (100%) ✓
- Spot-check Batch 19: 48/48 words (100%) ✓
- Rarity guidelines established:
  - 基本語({Ｂ}) → RARITY=2 (元々20.6%)
  - 一般語({Ｏ}) → RARITY=3 (元々38.1%、最多)
  - マーカー無 → RARITY=3 or 4 (専門用語は4)
- Lessons learned (Batch 9):
  - ADJ entries MUST have WITH_END=KF (not N) to support plural/accusative forms
  - Valid Meaning enum values: Check literumilo_entry.py before using (e.g., no MILITO, EKONOMIO, INFORMADIKO)
  - Use SCIENCO for information science terms, N for military/economic terms without specific category
  - Batch 9 TSV file corrected and re-imported successfully after initial Meaning enum errors
- Lessons learned (Batch 10):
  - VERBO entries format: morpheme, VERBO, Meaning, TRANS(T/N/X), N, KF, NLM, rarity, P
  - Successfully added first VERBO (aviad) in PEJVO batches with TRANS=N (intransitive)
  - ADJ entries (atik, azi) both correctly set WITH_END=KF and validated at 100%
  - Diverse POS mix (8 SUBST, 2 ADJ, 1 VERBO, 1 noun) all validated successfully
- Lessons learned (Batch 11):
  - Diverse meaning categories successfully mapped: RELIGIO, SPORTO, MONERO, SCIENCO, GEOGRAFIO, MUZIKILO, GRAMATIKO
  - ADJ entry (baktri) correctly set WITH_END=KF and validated at 100%
  - All 12 roots span wide domain coverage (religion, sports, currency, science, geography, music, grammar, physics)
  - 100% success rate maintained across all word forms (nominative, accusative, plural)
- Lessons learned (Batch 12):
  - Scientific terminology focus: MALSANO, MINERALO, MEZURUNUO, KEMIAJXO successfully mapped
  - Four ADJ entries (bengal, benign, bikonkav, bikonveks) all correctly set WITH_END=KF
  - Prefix-like root (bio) functions correctly in compound words (biodiverseco, biofuelo, biogaso)
  - Medical, chemical, optical, and economic terminology all validated at 100%
- Lessons learned (Batch 13):
  - Environmental science cluster: biocenoz, biomas, biosfer, biotop all using N (no specific enum)
  - Two ADJ entries (birm, bohemi) both correctly set WITH_END=KF and validated at 100%
  - Mixed domain coverage: environmental science, biology, medicine, religion, information technology
  - 13 consecutive batches with 100% success rate maintained 🔥
- Lessons learned (Batch 14):
  - Successfully mapped specialized categories: FUNGO (boleto), MUZIKO (boston), PLANTO (briofit)
  - Three ADJ entries (branĉ, brazil, brazilj) all correctly set WITH_END=KF and validated at 100%
  - PIV2020-sourced roots (branĉ, brontosaŭr) integrate seamlessly with PEJVO workflow
  - Diverse domain coverage: mycology, physics, music, religion, geography, botany, chemistry, medicine, paleontology
  - 14 consecutive batches with 100% success rate maintained 🔥
- Lessons learned (Batch 15):
  - Four ADJ entries (bule, bulgar, celsius, ceter) all correctly set WITH_END=KF and validated at 100%
  - Basic vocabulary focus: bud, buton, cement, ceter all assigned RARITY=2 per PEJVO {Ｂ} markers
  - Mixed domain coverage: zoology, mathematics, ethnic, food, clothing, science, mythology
  - 15 consecutive batches with 100% success rate maintained 🔥
- Lessons learned (Batch 16):
  - Smaller batch (4 roots) focusing on high-frequency roots: cezar, cifer, cipres, civit
  - Two basic vocabulary items (cifer, civit) assigned RARITY=2 per PEJVO {Ｂ} markers
  - All word forms validated including complex derivatives (ciferecigi, civitaneco)
  - 16 consecutive batches with 100% success rate maintained 🔥
- Lessons learned (Batch 17):
  - 11 roots: cukcukcikad, dac, damask, decibel, decigram, decilitr, decimetr, defaŭlt, dehidraci, deism, deist
  - Measurement units cluster: decibel, decigram, decilitr, decimetr (all RARITY=3 as general terms)
  - Successfully mapped ANIMALO (cukcukcikad), MALSANO (dehidraci), SXTOFO (damask), MEZURUNUO (units)
  - Mixed rarity: 5×RARITY=3 (units+technical), 3×RARITY=4 (specialized: cukcukcikad, dac, deism, deist)
  - 17 consecutive batches with 100% success rate maintained 🔥
- Lessons learned (Batch 18):
  - **CRITICAL VERBO format fix**: VERBO entries must NOT have description column in 4th position
  - Correct VERBO format: morpheme, VERBO, Meaning, TRANS(T/N/X), N, KF, NLM, rarity, P
  - Initially wrote: `demoraliz VERBO N demoralizi T N KF...` (wrong - included description)
  - Corrected to: `demoraliz VERBO N T N KF...` (right - TRANS value directly in 4th column)
  - Measurement units cluster: dekagram, dekalitr, dekametr (all MEZURUNUO, RARITY=3)
  - Successfully mapped PROFESIO (demograf, dermatolog), MEZURILO (densometr), MALSANO (dermatit)
  - Medical terminology cluster: dermatit, dermatolog (dermatology field)
  - Mixed domain coverage: time units, measurement, ceramics, demographics, economics, medicine
  - 18 consecutive batches with 100% success rate maintained 🔥

## **CRITICAL FORMAT FIX (2025-10-12)**: vortaro.tsv 仕様違反の修正

### 問題の発覚:
Batch 1-18 で追加した全234エントリが、vortaro.tsv の仕様に違反していることが判明。

### 問題の内容:
**誤ったフォーマット（Batch 1-17で使用）:**
- SUBST: `morpheme	SUBST	Meaning	description	N	KF	NLM	rarity	P`
- ADJ: `morpheme	ADJ	Meaning	description	N	KF	NLM	rarity	P`
- VERBO: `morpheme	VERBO	Meaning	description	T/N/X	KF	NLM	rarity	P`

**正しいフォーマット:**
- SUBST: `morpheme	SUBST	Meaning	N	N	KF	NLM	rarity	R`
- ADJ: `morpheme	ADJ	Meaning	N	N	KF	NLM	rarity	R`
- VERBO: `morpheme	VERBO	Meaning	T/N/X	N	KF	NLM	rarity	R`

### 具体的な問題点:
1. **4列目（transitiveco）**: 本来「T/N/X」であるべきところに description（例: argentino, abolicii）が入っていた
2. **9列目（flago）**: 本来「R/K/X」であるべきところに独自の「P」が入っていた
3. 元のvortaro.tsv（1-10697行目）は正しいフォーマット（flago=R/K/X）

### 修正作業（2025-10-12 16:56）:
- 修正スクリプト作成: `比較実験/fix_vortaro_format.py`
- バックアップ作成: `vortaro.tsv.bak.before_format_fix_20251012_165603`
- 修正内容:
  1. SUBST/ADJ（226個）: 4列目の description を削除
  2. VERBO（6個）: 4列目の description を削除、5列目の TRANS を4列目に移動
  3. VERBO（2個: aviad, demoraliz）: flago のみ P→R
  4. すべて（234個）: flago を P→R に変更

### 修正結果:
- ✅ 修正エントリ数: 234個
- ✅ ユニットテスト: 2/2 passed (100%)
- ✅ Batch 9 スポットチェック: 24/24 words (100%)
- ✅ Batch 18 スポットチェック: 50/50 words (100%)
- ✅ VERBO スポットチェック: 18/18 words (100%)
- ✅ flago=P のエントリ: 0個（完全に除去）

### 今後の教訓:
- **絶対に守るべきフォーマット**: 元のvortaro.tsv（1-10697行目）のフォーマットを厳密に遵守
- **4列目は transitiveco のみ**: description は vortaro.tsv に含めない
- **5列目 senfinajxo は必須**: 欠かしてはいけない（常に N）
- **flago は R/K/X のみ**: 独自フラグ（P等）は使用しない
- **今後のバッチ追加**: 以下の正しいフォーマットでTSVを作成すること

## **COMPREHENSIVE FORMAT FIX #2 (2025-10-12 17:11)**: 全追加エントリの再修正

### 再発覚した問題:
第1回の修正（16:56）では flago=P のエントリ（234個）のみを修正したが、
**別の生成AIの指摘により、さらに221個の不正なエントリが発見された。**

これらは10697行目以降に追加されたエントリで、以下の問題があった：
1. **4列目に description が残っている**（globino, glukagono等）
2. **senfinajxo列（col5）が完全に欠けている**

### 不正エントリの範囲:
- 11255行目～11475行目: 221個のエントリ（globin～hidroksil）
- 11664,11665,11668,11671行目: 4個のADJエントリ（bule, bulgar, celsius, ceter）
- **合計: 225個の不正エントリ**

### 問題の構造:

**誤った形式（senfinajxo列が欠けている）:**
```
morpheme POS Meaning description transitiveco kunfinajxo limigo rareco flago
globin   SUBST KEMIAJXO globino    N            KF         NLM    4      R
```

**正しい形式:**
```
morpheme POS Meaning transitiveco senfinajxo kunfinajxo limigo rareco flago
globin   SUBST KEMIAJXO N          N          KF         NLM    4      R
```

### 修正作業（2025-10-12 17:11）:
- 修正スクリプト作成: `比較実験/fix_vortaro_format_v3.py`
- バックアップ作成: `vortaro.tsv.bak.before_comprehensive_fix_20251012_171115`
- 修正内容:
  1. 4列目が T/N/X でない場合 → description として削除
  2. fields[4]（元の transitiveco）→ col4に移動
  3. senfinajxo 列として N を col5 に挿入
  4. fields[5-8]（元の kunfinajxo, limigo, rareco, flago）→ col6-9に維持
  5. ADJで col5=KF の場合 → col5 を N に修正（senfinajxo補完）

### 修正結果:
- ✅ 修正エントリ数: 225個
- ✅ ユニットテスト: 2/2 passed (100%)
- ✅ Batch 9 スポットチェック: 3/3 words (100%)
- ✅ Batch 14 スポットチェック: 3/3 words (100%)
- ✅ Batch 18 スポットチェック: 3/3 words (100%)
- ✅ 修正対象エントリ: 3/3 words (100%)（globino, glukagono, hadeano）
- ✅ フォーマット検証: **0 errors**（完全に修正）

### 根本原因:
- 第1回の修正では flago=P のエントリのみを対象としたため、
  **既に flago=R だった別バッチのエントリ（221個）を見逃していた**
- これらのエントリは Batch 1-18 とは別に追加されたもの（おそらく自動生成）
- senfinajxo 列が完全に欠けていたため、全体が1列左にずれていた

### **正しいTSVフォーマット（今後必ず使用）:**

```tsv
# SUBST エントリ（名詞）
morpheme	SUBST	Meaning	N	N	KF	NLM	rarity	R	# コメント

# 例:
argentin	SUBST	LANDO	N	N	KF	NLM	3	R	# OK 地理: アルゼンチン [PEJVO一般語]
```

```tsv
# ADJ エントリ（形容詞）
morpheme	ADJ	Meaning	N	N	KF	NLM	rarity	R	# コメント

# 例:
agresiv	ADJ	N	N	N	KF	NLM	2	R	# OK 形容詞: 攻撃的な [PEJVO基本語]
```

```tsv
# VERBO エントリ（動詞）
morpheme	VERBO	Meaning	T/N/X	N	KF	NLM	rarity	R	# コメント

# 例（他動詞）:
demoraliz	VERBO	N	T	N	KF	NLM	4	R	# OK 動詞: 士気をくじく [PEJVO専門語]

# 例（自動詞）:
aviad	VERBO	N	N	N	KF	NLM	3	R	# OK 動詞: 飛行する [PEJVO一般語]

# 例（両用）:
abolici	VERBO	N	X	N	KF	NLM	2	R	# OK 動詞: 廃止する [PEJVO基本語]
```

**列の説明:**
1. morpheme: 語根（例: argentin, agresiv, demoraliz）
2. POS: 品詞（SUBST, ADJ, VERBO, etc.）
3. Meaning: 意味カテゴリ（LANDO, MALSANO, N, etc.）
4. transitiveco: 他動性（SUBST/ADJ: N固定、VERBO: T/N/X）⚠️ **descriptionを入れない！**
5. senfinajxo: 語尾なし（N固定）
6. kunfinajxo: 語尾あり（KF固定）
7. limigo: 制限（NLM or LM）
8. rareco: 頻度（2-4）
9. flago: フラグ（R固定）⚠️ **Pは使わない！**

## Current Code State
- `literumilo_suffix.py`: `-ind` / `-end` now accept adjectival bases (e.g., *fierindaĵo* →
  `fier.ind.aĵ.o`).
- `literumilo_check_word.py`: tie-breaker prefers lower rarity sum when PEJVO and algorithm outputs
  differ; falls back to algorithm if equal.
- PEJVO tail section `# --- PIV2020 automatically added entries ---` holds 5,463 auto-generated
  words (from `PIV2020_PEJVO追加候補.txt`).

## Data Artifacts (under `比較実験/`)
- `invalid_proper_nouns.txt` – capitalised names from the PIV≠PEJVO difference.
- `invalid_leading_hyphen.txt` – affix-like entries (prefixes/suffixes) starting with `-`.
- `invalid_internal_hyphen.txt` – multiword or compound forms containing hyphens.
- `invalid_plain_words.txt` – 6,316 ordinary words still unresolved (main backlog).
- `draft_vortaro_additions.tsv` – first 50 plain words with auto-generated TSV rows for
  `vortaro.tsv` (requires human review before import).
- `PIV2020_PEJVO候補_valid_words.txt` – 5,463 words already analysed successfully; they are
  appended to PEJVO but still lack rich glosses.
- `PIV2020_PEJVO候補_invalid.txt` – full list (7,494) of unresolved words for tracking.

## Recommended Workflow (repeatable without chat memory)
1. **Track progress externally**: create `比較実験/progress_log.csv` where each row stores word,
   status (`todo / drafted / added / skipped`), and optional notes.
2. **Process in small batches** (≈150–200 words per round):
   - Take next chunk from `invalid_plain_words.txt`.
   - Draft tentative `vortaro.tsv` entries (copy template from
     `draft_vortaro_additions.tsv`).
   - Cross-check meaning/POS with PIV or other references.
   - Append to `vortaro.tsv` in sub-batches of 10–20 words; run tests
     (`PYTHONPATH=./literumilo python -m unittest literumilo.tests.test_literumilo`).
   - Update `progress_log.csv`.
3. **Run targeted rule updates** for words that still fail despite dictionary entries
   (log them separately, then adjust `literumilo_suffix.py` or related modules).
4. **Solidify PEJVO entries**: after dictionary additions are approved, move corresponding
   PIV entries from auto-generated list into PEJVO’s main body with full glosses.

## Additional Notes
- Maintain conservative changes: each addition should be justified (gloss source, POS, etc.).
- Keep raw PIV data untouched (`PIV2020_structured.txt`, `PIV2020.html`), use derived files for work.
- Future enhancement: integrate corpus frequency (e.g., `wiki_esperanto.txt`) into the tie-break
  scoring to refine segmentation prioritisation.

---

# Handover (Detailed) — How to Resume Safely From Scratch

This section is a self-contained “start here” guide. Even if chat memory is lost,
following these steps will reproduce the current approach and let you continue
expanding coverage safely and consistently.

## 0. Goal and Non‑Negotiables
- Improve literumilo’s Esperanto morphology accuracy by:
  - Integrating PEJVO’s analysed forms as a fallback (for exact headwords),
  - Systematically adding missing roots to `vortaro.tsv` so that plural/accusative,
    verb tenses, and participles derive automatically from the core dictionary.
- Preserve unique decomposition. When algorithm and PEJVO disagree, prefer the
  analysis with lower dictionary rarity sum; if equal, prefer algorithmic split.
- Never regress frequent/common words for rare/edge cases.

## 1. Code State and Local Modifications
- `literumilo_suffix.py`
  - `check_end_ind()` extended to allow adjectival bases (e.g., `fier.ind.aĵ.o`).
- `literumilo_check_word.py`
  - Adds scoring tie‑break between algorithm and PEJVO using dictionary rarity.
  - Endings set used to avoid penalising grammatical endings in scoring.
- `data/vortaro.tsv`
  - Added `iĝ` root (VERBO, with‑ending=KF, synthesis=S) to support -iĝi chains.
- Safety scripts (under `比較実験/`):
  - `generate_draft_batch.py` — make next draft batch of TSV rows (200 by default).
  - `simulate_draft_import.py` — inject a draft batch in memory and report Δvalid.
  - `auto_mark_ok_in_batch.py` — mark rows `# OK` when high‑confidence checks pass.
  - `import_reviewed_batch.py` — append only `# OK` rows to `data/vortaro.tsv`, with
    timestamped backup and progress log update.
  - `lint_vortaro_morphemes.py` — flag suspicious morphemes ending in grammatical vowels.

## 2. Dictionary Row Semantics (vortaro.tsv)
Each row has 9 columns (TSV):
1. morpheme (lowercase, supersigned letters allowed; no final POS vowel)
2. POS (`SUBST`, `VERBO`, `ADJ`, `ADVERBO`, `SUFIKSO`, `PREFIKSO`, `PARTICIPO`, …)
3. meaning (enum such as `KEMIAJXO`, `MINERALO`, `MEZURILO`, `MALSANO`, `MEDIKAMENTO`,
   `ELEMENTO`, `ANIMALO`, `INSEKTO`, `SCIENCO`, `LINGVO`, `ANATOMIO`, `GRAMATIKO`, `NUKSO`,
   `PLANTO`, `VETURILO`, `LOKO`, `ALGO`… or `N` if unknown)
4. transitivity (`T`/`N`/`X`; `VERBO` only; otherwise `N`)
5. without‑ending (`SF` or `N`)
6. with‑ending (`KF` or `N`)
7. synthesis (`NLM` recommended for normal roots; `S` suffix; `P` prefix; `PRT` participles; `LM` limited)
8. rarity (`0` very common … `4` rare). We currently set added scientific terms to `4`.
9. flag (`R` normal; `K` comp‑only; `X` exclude)

Conservative defaults used so far for `SUBST` roots:
`TRANS=N`, `WITHOUT_END=N`, `WITH_END=KF`, `SYNTH=NLM`, `RARITY=4`, `FLAG=R`.

## 3. Endings and Derived Forms
- Noun: `o`, `oj`, `on`, `ojn`
- Adjective: `a`, `aj`, `an`, `ajn`
- Adverb: `e` (+ optional `en`)
- Verb: base `i`; finite forms `as/is/os/us/u`; participles `ant/int/ont/at/it/ot`
  (these combine with `a/aj/an/ajn` etc.); causatives `ig`, inchoatives `iĝ`.
  These work automatically if the root exists in `vortaro.tsv` and suffix rules allow.

## 4. Reproducible Workflow

### 4.1 Generate next draft (200 words)
```
python 比較実験/generate_draft_batch.py 200
```
Output: `比較実験/batches/draft_vortaro_additions_YYYYMMDD_HHMM.tsv`
- `比較実験/progress_log.csv` updated with `status=drafted`.

### 4.2 (Optional) Auto‑mark easy wins as `# OK`
```
python 比較実験/auto_mark_ok_in_batch.py 比較実験/batches/draft_vortaro_additions_….tsv
```
- Very strict heuristics; manual review still recommended.

### 4.3 Estimate impact without editing dictionary
```
python 比較実験/simulate_draft_import.py 比較実験/batches/draft_vortaro_additions_….tsv 1000
```
Reports baseline and after‑injection valid counts, helping prioritise review.

### 4.4 Human review of 9 columns
- Edit TSV rows; ensure column semantics are correct; append `# OK` to the last column for rows approved to import.
- Keep `meaning` within the enum used by `literumilo_entry.Meaning`.

### 4.5 Import reviewed rows (safe)
```
python 比較実験/import_reviewed_batch.py 比較実験/batches/reviewed_import_….tsv
```
- Creates `data/vortaro.tsv.bak.YYYYMMDD_HHMMSS` before appending.
- Updates `progress_log.csv` with `status=added` where possible.

### 4.6 Regression tests and spot checks
```
PYTHONPATH=./literumilo python -m unittest literumilo.tests.test_literumilo
```
- Also manually `from literumilo import check_word` on representative words including plural/accusative and participle chains.

## 5. PEJVO and Algorithm Tie‑Break
- PEJVO is used as a fallback when algorithmic decomposition fails for that exact headword.
- If both produce different results, the implementation scores each by summing rarity of constituent morphemes (ignoring endings) and selects the lower sum. Ties prefer the algorithm.
- This operationalises the “common words first; unique decomposition” principle.

## 6. Known Edge Patterns and How We Handle Them
- Plural headwords (`-oj`) in PIV/PEJVO: add a singular root and let plural derive (`anuro` → `anur.oj`).
- Roots whose final letter happens to be a grammatical vowel: valid cases exist (e.g., `antozo`, `apendikulari`). Use `lint_vortaro_morphemes.py` to flag and then whitelist legitimate cases.
- -ind/-end + -aĵ: handled by allowing adjectival bases for `-ind/-end`.
- -ig / -iĝ: both supported (`ig` existed; `iĝ` was added). Chains like `far.iĝ.int.a` parse.

## 7. What To Do When You Resume
1) Run a draft: `python 比較実験/generate_draft_batch.py 200`.
2) (Optional) Auto‑mark: `python 比較実験/auto_mark_ok_in_batch.py …`.
3) Estimate: `python 比較実験/simulate_draft_import.py … 1000`.
4) Review 15–20 rows, set 9 columns correctly, append `# OK`.
5) Import: `python 比較実験/import_reviewed_batch.py …`.
6) Test: `PYTHONPATH=./literumilo python -m unittest …` and a few `check_word()` spot checks.
7) Commit or archive results as needed; update `progress_log.csv`.

### 7.1 Current Progress Snapshot (as of 849 imported roots) 🚀🎯🏆🔥✨
- Imported batches (all rarity=4, conservative settings):
  - reviewed_import_chem_1.tsv (12)
  - reviewed_import_chem_2.tsv (8)
  - reviewed_import_chem_med_3.tsv (14)
  - reviewed_import_med_4.tsv (9)
  - reviewed_import_mixed_5.tsv (12)
  - reviewed_import_mixed_6.tsv (22)
  - reviewed_import_fix_plurals.tsv (3)
  - reviewed_import_fix_roots.tsv (2)
  - reviewed_import_mixed_7.tsv (25): plants, minerals, chemistry, anatomy
  - reviewed_import_mixed_8.tsv (36): medicine, animals, chemistry, elements, algae
  - reviewed_import_mixed_9.tsv (61): fungi, animals, plants, insects, medical terms
  - reviewed_import_mixed_10.tsv (78): cell biology, chemistry, medical, dendrology
  - reviewed_import_mixed_11.tsv (83): medical, plants, minerals, music theory, grammar
  - reviewed_import_mixed_12.tsv (87): emulsification, endocrinology, epistemology, epigenetics
  - reviewed_import_mixed_13.tsv (22): psychology, chemistry, biology (fuels, algae, insects)
  - reviewed_import_mixed_13b.tsv (11): music, mathematics, chemistry, biology, paleontology
  - reviewed_import_mixed_13c.tsv (16): plants, chemistry, materials, animals, ships, religion
  - reviewed_import_mixed_13d.tsv (27): ships, animals, plants, chemistry, medical, geology
  - reviewed_import_mixed_13e.tsv (29): geology, medical, chemistry, biology, literature
  - reviewed_import_mixed_13f.tsv (38): biochemistry, anatomy, chemistry, mineralogy, fish, plants, tools, medicine
  - reviewed_import_mixed_13g.tsv (24): religion, geology, plants, anatomy, medicine, paleontology, science, physics, animals, insects
  - reviewed_import_mixed_13h.tsv (24): plants, cooking, architecture, chemistry, science, animals, mathematics
  - reviewed_import_mixed_13i.tsv (24): plants, ethnology, animals, geology, cooking, history, birds, mineralogy, medicine, physics, tools, religion
  - reviewed_import_mixed_13j.tsv (23): ethnology, linguistics, animals, textiles, history, medicine, economy, botany, tools
  - reviewed_import_mixed_13k.tsv (23): religion, philosophy, chemistry, mathematics, plants, astronomy, printing, medicine, animals
  - reviewed_import_mixed_13l.tsv (20): chemistry, medicine, biology, animals (henikoz prefix removed post-import)
  - reviewed_import_mixed_13m.tsv (25): geology, ethnology, philosophy, plants, animals, paleontology, literature, tools, chemistry, biology, cooking, history (draft 2 lines 155-180)
  - reviewed_import_mixed_13n.tsv (20) ← NEW: fungi, tools, plants, chemistry, science, animals (draft 2 lines 180-202, **DRAFT 2 COMPLETE**)
- Total imported roots so far: **849** (+398 in current session: 22+11+16+27+29+38+24+24+24+23+23+20+25+20) 🏆🎯🔥⭐⭐⭐✨✨✨
- vortaro.tsv total lines: 11,498 (was 10,804 → +694 lines)
- Representative words confirmed valid: `amfipodoj`, `anemometrio`, `anizokorio`, `antraceno`, `ambulanĉo`, `alĝebro`, `amenoreo`, `anur.o/oj`, `apiolo`, `aplito`, `arginino`, `areolo`, `arek.o`, `baktericido`, `balanito`, `barumo`, `barbituro`, `batometrio`, `bazidio`, `bostriko`, `bradikardio`, `bromelio`, `bronkoskopo`, `bufono`, `bulimio`, `bungaro`, `bursito`, `cisteino`, `citologio`, `citokromo`, `citozino`, `dekubito`, `dengo`, `dendrokronologio`, `densometrio`, `dismenoreo`, `dispneo`, `divertikulo`, `dipterokarpo`, `dolomito`, `dodekafonio`, `durio`, `efedrino`, `encefalalgio`, `encefalino`, `endorfino`, `endoskopio`, `endokrinologio`, `epinefrino`, `epistemologio`, `ergonomio`, `georgiko`, `geosfer.o`, `geriatrio`, `globin.o`, `gluk.o`, `gluon.o`, `goetit.o`, `gomb.o`, `goniometrio`, `gordiulo`, `gospel.o`, `graben.o`, `granulom.o`, `graptolit.o`, `gravimetr io`, `graviton.o`, `gregarin.o`, `grindeli.o`, `grundologi.o`, `guanin.o`, `guĝ.i`, `gvanak.o`, `haliaet.o`, `halit.o`, `halofito`, `hamiltoniano`, `handspeko` など。
- Batch 7 impact: Δ+184 valid words (75→259 out of 1000 test sample)
- Batch 8 impact: Δ+183 valid words (100→283 out of 1000 test sample)
- Batch 9 impact: Δ+181 valid words (140→321 out of 1000 test sample)
- Batch 10 impact: Δ+0 (words not in test sample, but still valuable additions)
- Batch 11 impact: Δ+4 valid words (203→207 out of 1000 test sample)
- Batch 12 impact: Δ+2 valid words (203→205 out of 1000 test sample)
- Spot-check success rates: Batch 8: 94.4% (17/18), Batch 9-13n: **100%** ⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐⭐ (21/21, 24/24, 23/23, 24/24, 12/12, 11/11, 16/16, 23/23, 29/29, 38/38, 27/27, 26/26, 24/24, 24/24, 23/23, 23/23, 27/27, 21/21)
- Cumulative baseline improvement: 75→205+ valid words (+173%+ improvement across all batches!)
- **18 consecutive batches with 100% success rate** 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥✨✨✨
- Next targets: continue with batches prioritising specialized terminology. Keep rarity at 4 unless a word is clearly common.
- Fixed issues: corrected plural/adjectival forms (fukoficoj→fukofic, fulgoromorfoj→fulgoromorf, gadoformaj→gadoform, galinoformaj→galinoform, gaviformaj→gaviform, gavioformaj→gavioform, gefireoj→gefire, gimnotedoj→gimnoted, gnetopsidoj→gnetopsid, gobiusedoj→gobiused, gobiusoidoj→gobiusoid, gordiuloj→gordiul, graptolitoj→graptolit, gregarinoj→gregarin, griledoj→griled, grosulariacoj→grosulariac, gutiferoj→gutifer, hapaledoj→hapaled, hemiĥorduloj→hemiĥordul, hesperornitoformaj→hesperornitoform, heteropteroj→heteropter, hidroidoj→hidroid); fixed root form (gombo→gomb); fixed POS (granitoida ADJ→granitoid SUBST); removed prefix-only entries (heks, heksa, henikoz - already registered as TEHXPREFIKSO)
- Key insight: Scientific classification names often appear only in plural/adj forms in PIV; convert to singular root (e.g., "gadoformaj" → "gadoform", "hidroidoj" → "hidroid"). Entry format: morpheme column (column 1) should contain ROOT only, not full word. Collective nouns ending in -oj should be registered as singular roots. Chemical prefixes (heks-, henikoz-) are TEHXPREFIKSO and should not be imported as standalone SUBST

## 8. Success Criteria
- Δvalid improves on web corpus and invalid backlog shrinks steadily.
- No regressions in unit tests and representative frequent words.
- New roots use consistent meanings, conservative synthesis, and rarity=4 unless clearly common.

## 9. Rollback
- If anything looks off after import, restore the latest `vortaro.tsv.bak.*` and rerun tests.

## 10. Open To‑Dos (Backlog)
- Continue adding high‑confidence roots from: chemistry → medical → minerals → metrology → linguistics.
- Consider integrating corpus frequency into tie‑break scoring (in addition to rarity).
- Expand whitelist in linting when legitimate vowel‑final roots are confirmed.
