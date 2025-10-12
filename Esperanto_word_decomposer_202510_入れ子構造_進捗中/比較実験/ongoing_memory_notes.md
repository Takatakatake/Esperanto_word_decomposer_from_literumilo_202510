# Esperanto Morphology Project – Working Notes (Updated 2025-10-12)

このメモは、チャット履歴がない状態でも安全に作業を再開できるよう、現状をゼロベースで再点検した結果を記録しています。旧版 (`ongoing_memory_notes_original.md`) にあった重要な知見を再検証し、誤差・陳腐化の有無を確認した上で、正確な数値と現在のリスクを反映しました。

---

## 1. Core Principles & Conventions
- Unique decomposition: 1語形につき1つの語根列。アルゴリズム案と PEJVO 案が衝突した場合は、辞書レア度合計が小さい方（＝一般的な語）を採用し、同点時のみアルゴリズム案を優先する。
- Frequency guard: `literumilo_check_word.py` のスコアリングで語尾トークンを除外し、未知語には軽いペナルティ (+5) を課す。PEJVO 側のスコアが低い場合のみ置き換える。
- Dictionary hygiene: `vortaro.tsv` は常に9列（morpheme, POS, Meaning, transitiveco, senfinajxo, kunfinajxo, limigo, rareco, flago）。`senfinajxo` は N 固定（例外なし）、`flago` は R/K/X のみ。
- Rarity defaults: {Ｂ}=2, {Ｏ}=3、それ以外は 3 または 4。医・理・工など専門語は 4 を基準にし、頻出語のみ 2～3 に引き下げる。
- Meaning enum discipline: `literumilo_entry.Meaning` に存在しない値は追加しない（例: MILITO や INFORMADIKO は未定義）。意味が特定できない場合は N を使用する。
- Morphological endings: 形容詞エントリは必ず `with_end = KF` に設定し、複数・対格派生を保証する。動詞は `transitiveco` に T/N/X を必須設定。

---

## 2. Code & Tooling Overview
- `literumilo_check_word.py`: 辞書レア度を用いたタイブレーク／語尾除外／未知語ペナルティ。結果は `AnalysisResult` として大文字復元後に返す。
- `literumilo_suffix.py`: `check_end_ind()` が形容詞語根 (`fier.ind.aĵ.o` 等) を許容するよう拡張済み。`-ig`/`-iĝ` 連鎖も `iĝ` エントリ追加により解析可能。
- `literumilo_load.py`: 語根キーは最後に読み込まれた行で上書きされる。重複行がある場合、先行エントリの情報は失われるため、重複排除が最優先の保守項目。
- `literumilo_pejvo.py`: フォールバック時に名詞・形容詞・副詞の格変化、動詞の時制、能動/受動分詞、および `-ig` / `-iĝ` 派生を合成できるよう更新済み（辞書側で語根が未登録でも基本的な派生語を復元可能）。
- Support scripts (比較実験/):
  - `generate_draft_batch.py`, `auto_mark_ok_in_batch.py`, `simulate_draft_import.py`, `import_reviewed_batch.py`, `lint_vortaro_morphemes.py`
  - フォーマット修正系: `fix_vortaro_format.py`, `fix_vortaro_format_v2.py`, `fix_vortaro_format_v3.py`
  - 差分・集計補助: `compare_literumilo_versions.py`, `dump_difference_examples.py`

---

## 3. Dictionary Snapshot (2025-10-12 JST)
- `literumilo/literumilo/data/vortaro.tsv`: 11,721 行 / 11,542 ユニーク語根。オリジナル 10,697 行との差分は **1,024 行**（追加ブロック）。
- 全体の重複語根は **166**。うち 23 語は末尾ブロック内で完全に同一行が2回追加されており、以下が該当（例: `aren, argil, argument, ari, aristokrat, arkad, arkipelag, arkitekt, arkitektur, arkiv, armatur, arme, dekad, dekagram, dekalitr, dekametr, delft, demograf, denominaci, densometr, depresi, dermatit, dermatolog`）。残り 10 語は POS が異なる重複 (`apercept`, `areol`, `baktericid`, `barbitur`, `batu`, `bos`, `enkaŭstik`, `epigenez`, `epik`, `epirogenez`)。
- そのほかの重複 133 語は、元辞書に存在していた R/X の二重定義（例: `adiaux`, `alfabet`, `dum`, `kaj`, `se`）。この形式も `load_dictionary()` の仕様上は後行行で上書きされるため、残す場合は意図通りの順序を確認する。
- 追加ブロックに由来する重複は、既存語根を上書きし解析が変化するリスクが高い。重複除去後に `python -m unittest literumilo.tests.test_literumilo` を必ず実行する。
- PEJVO 辞書補助 (`literumilo/literumilo/literumilo_pejvo.py`) は `PEJVO.txt` を読み込むローダーであり、文書化済みの 5,463 語（`PIV2020_PEJVO候補_valid_words.txt`）を動的に取得する。これらをメイン辞書へ移す際は gloss を補完する。

---

## 4. PEJVO Integration Status
- 入力リスト: `比較実験/PEJVO_missing_in_vortaro.txt`（冒頭3行は説明、4行目以降に 2,730 行）。`^` → `x` 変換と Unicode アクセントの `x` 化、`#` コメント除去を行うと **2,509 個の一意語根**になる。
- 上記正規化後の語根のうち **924 個 (≈36.8%)** は既に `vortaro.tsv` に存在し、**1,585 個**が未登録。リストと辞書の差異は、同語根の表記揺れ（例: `ang^elus` ↔ `angxelus`）や重複エントリに起因する。
- `reviewed_import_PEJVO_batch_{1..19}.tsv` で `# OK` 承認済みの **227 語根**のうち、`vortaro.tsv` へ取り込まれているのは **225 語根**で、`abstinenc` と `akaj^u`（辞書側では `akajxu`）が未反映。
- `progress_log.csv` の集計は `added=13`, `drafted=2,187` と、実際の辞書状態と乖離している。`import_reviewed_batch.py` 実行時に更新されていないため、ログ整備が必要。

```
PEJVO batches (#OK rows = 227)
01 (20) abolici, aborigen, abstemi, abstinenc, acetat, acetil, acetilen, aceton, adenin, adenozin, adjudik, adonid, adsorb, aerofagi, aerometr, agapant, agnostikism, agreg, agresiv, akaj^u
02 (12) akvarel, albatros, alcion, alkaloid, alkohol, alpak, ambulanc, amen, ametist, amin, amnesti, amper
03 (14) ampermetr, amplitud, ampol, anafilaksi, anakronism, analfabet, ananas, anastigmat, anatom, anekdot, aneks, anemometr, aneroid, anestez
04 (12) ang^elus, angil, angstrom, anhidr, anilin, ankiloz, ankr, anod, anomali, anonim, anorak, ans
05 (12) anser, antagonism, anten, antidot, antifon, antimon, antipati, antipod, antiseps, antitez, antitoksin, antonim
06 (12) antracit, antropologi, antropolog, aort, apanag^, apart, apati, aperitiv, apetit, apik, apolog, apopleksi
07 (12) apostol, apostrof, apoteoz, apozici, april, aprob, apsid, arane, arbitr, arbut, ardez, are
08 (12) aren, argil, argument, ari, aristokrat, arkad, arkipelag, arkitekt, arkitektur, arkiv, armatur, arme
09 (12) argentin, ariergard, aristotel, arkiduk, artez, artiŝok, artritism, arĝent, asembl, asiri, aski, astigmatism
10 (12) astrakan, astronaŭtik, atik, atletik, atrepsi, avangard, averaĝ, avers, aviad, azi, aztek, azuki
11 (12) babel, badminton, baht, bakanal, bakteriologi, baktri, balkan, bandaĝ, bandoni, banĝ, barbarism, barjon
12 (12) basedov, baŭksit, bekerel, beletristik, bengal, benign, benzoat, bibliofili, bikonkav, bikonveks, bimetalism, bio
13 (12) biocenoz, biofizik, biogeografi, biomas, biosfer, biotop, birm, blenoragi, blog, blokhaŭs, bodi, bohemi
14 (12) boleto, bosni, boson, boston, braman, branĉ, brazil, brazilj, briofit, bromid, bronkit, brontosaŭr
15 (10) bubal, bud, bule, bulgar, buljon, buton, celsius, cement, cerber, ceter
16 (4) cezar, cifer, cipres, civit
17 (11) cukcukcikad, dac, damask, decibel, decigram, decilitr, decimetr, defauxlt, dehidraci, deism, deist
18 (12) dekad, dekagram, dekalitr, dekametr, delft, demograf, demoraliz, denominaci, densometr, depresi, dermatit, dermatolog
19 (12) dermatologi, dermatoz, detektor, detonaci, devon, devoni, dialektolog, dialektologi, diartr, dias, diaskop, diaterm
```

※ 上記リストは `reviewed_import_PEJVO_batch_*.tsv` を直接走査して得た語根列。`^` 記号を含むエントリは Unicode 正規化が未実施。

---

## 5. Lessons Learned from PEJVO Batches
- ADJ は `with_end=KF` 必須。`with_end=N` のままだと複数・対格が生成できず、Spot-check で失敗する（Batch 9 で再確認済み）。
- Meaning enum は `literumilo_entry.py` の列挙体に従う。軍事・経済は `N` を使用し、情報科学は `SCIENCO` を採用する（Batch 9 で出現した不正列挙値を修正）。
- VERBO エントリ形式: `[morpheme, VERBO, Meaning, T/N/X, N, KF, NLM, rarity, R]`。自動詞は `transitiveco=N` を設定し、派生形が正しく生成されることを Spot-check する（Batch 10 で初導入）。
- 多品詞カテゴリの同語根は `vortaro.tsv` では衝突するため、派生規則で扱える場合は単一 POS に集約する。どうしても必要な場合は別接頭辞/接尾辞として扱う。

---

## 6. Format Fix History & Remaining Issues
- 2025-10-12 16:56 JST (`fix_vortaro_format.py`): flago=P の 234 行を修正。Description を除去し、`transitiveco` と `senfinajxo` を正しい列に配置。`flago` を一括で R に統一。単体テスト 2件成功。
- 2025-10-12 17:11 JST (`fix_vortaro_format_v3.py`): 10697 行目以降の 225 行（globin～hidroksil + ADJ 4件）の列ずれを補正。`senfinajxo` を補完し、列数を 9 に統一。修正後の TSV は 0 件のフォーマットエラー。
- 現在の検証: `python3 - <<'PY'` で 9 列未満行は 0。`rg '\tP$'` でも flago=P は存在しない。
- 残存課題:
  - 追加ブロックの完全重複 23 行と POS 競合 10 行を削除／統合する。
  - Unicode 正規化（`^`, `x` 表記揺れ）を解決し、辞書キーを統一する。
  - `abstinenc` を辞書に追加し、`akaj^u` を `akajxu` へ正規化して差分を解消。
  - `progress_log.csv` の `status` を辞書実態に合わせて更新する（`added` 反映漏れ）。

---

## 7. Data Assets (比較実験/)
- `invalid_plain_words.txt` – 6,317 行（ヘッダ含む）。未解決の一般語バックログ。
- `invalid_proper_nouns.txt`, `invalid_leading_hyphen.txt`, `invalid_internal_hyphen.txt` – 固有名詞／接頭辞的語形／ハイフン含有語の除外候補。
- `draft_vortaro_additions.tsv` – 最初の 50 語のテンプレート。練習用。
- `batches/` – 全ドラフト・レビュー済み TSV。`reviewed_import_*` に `# OK` コメント付き行があり、合計 997 ユニーク語根が確認できる。
- `PIV2020_PEJVO候補_valid_words.txt` – 5,463 語（ヘッダ込み 5,464 行）の自動解析成功リスト。gloss 追加対象。
- `progress_log.csv` – `display, lookup, status, notes` を持つ作業ログ。現状 `added` は 13 のみ。

---

## 8. Repeatable Workflow (Post-Cleanup)
1. **前処理**: 重複語根の整理と `abstinenc` 追加を終えてから新規バッチへ進む。完了後に単体テスト (`PYTHONPATH=./literumilo python -m unittest literumilo.tests.test_literumilo`) を実行。
2. **語根選定**: `invalid_plain_words.txt` か `PEJVO_missing_in_vortaro.txt` から 150–200 語を抽出。必要に応じて頻度・分野でサブセット化。
3. **ドラフト生成**: `python 比較実験/generate_draft_batch.py 200`。生成先と `progress_log.csv` の更新を確認。
4. **自動マーキング (任意)**: `python 比較実験/auto_mark_ok_in_batch.py path/to/draft.tsv`。自動付与は厳格なので、人手検証が必要。
5. **手動レビュー**: 9 列値・Meaning enum・Rarity 等を精査し、承認行へ `# OK` を付与。必要に応じて `simulate_draft_import.py draft.tsv 1000` で効果を概算。
6. **インポート**: `python 比較実験/import_reviewed_batch.py reviewed.tsv`。`vortaro.tsv.bak.YYYYMMDD_HHMMSS` が生成されたことを確認し、`progress_log.csv` の `status` が `added` になるか再確認。
7. **検証**: 単体テスト＋手動 Spot-check (`from literumilo import check_word`)。複数形・対格・動詞活用・参加連鎖 (`-ig`, `-iĝ`) を含める。
8. **PEJVOリスト更新**: 取り込んだ語根を `PEJVO_missing_in_vortaro.txt` 側でマーキングし、重複防止。Unicode 正規化（x方式 → supersignoなど）も併記。

---

## 9. Edge Patterns & Conventions
- 複数形ヘッドワード (`-oj`, `-oj`) は単数語根に落とし込み、語尾で派生させる（例: `anuro` → `anur.oj`）。複合語風の語形が辞書キーになるのを避ける。
- 語尾母音で終わる語根（`apendikulari`, `antozo` など）は `lint_vortaro_morphemes.py` で警告が出るため、正当性を確認のうえ whitelist 管理。
- 接頭辞／接尾辞は `Synthesis` を `P` / `S` にし、`with_end` を N に設定。PEJVO 由来の語でも、辞書面で接頭辞扱いである場合はラベルを揃える。
- `-ind` / `-end` は形容詞語根＋`aĵ` を許容済み。`-ig` / `-iĝ` チェーンは `iĝ` ルート追加により解析される。

---

## 10. Metrics & Validation Signals
- `reviewed_import_*` に `# OK` が付いた行は **1,007 件**で、そのうちユニーク語根は **997**。カテゴリ別内訳: `PEJVO=227`, `chem=34`, `med=9`, `fix=5`, `mixed=732（ユニーク 722）`。
- 現行辞書への実導入は 1,024 行。`PEJVO` 225 語以外にも `mixed` 系が多数含まれており、重複除去前の状態では置換リスクが高い。
- 単体テスト実行コマンド:
  ```
  PYTHONPATH=./literumilo python -m unittest literumilo.tests.test_literumilo
  ```
- スポットチェック推奨パターン: 名詞複数・対格、形容詞 `aj/an`, 動詞 `-is/-as/-os/-us/-u`, 分詞 (`-ant`, `-int`, `-ont`, `-at`, `-it`, `-ot`), 連鎖 (`-ig`, `-iĝ`), 接頭辞 (`mal-`, `re-`, `ge-` など)。

---

## 11. Success Criteria & Rollback
- 追加後のウェブコーパス検証で `check_word()` の成功語が単調増加する。
- 単体テスト・Spot-check で回帰が発生しない。
- `vortaro.tsv` の 9 列フォーマットが維持され、`rg '\tP$'` レベルの簡易検証でゼロを確認。
- ロールバック手順: `literumilo/literumilo/data/vortaro.tsv.bak.*` を `vortaro.tsv` にリストア後、テストを再実行。必要に応じて対象バッチ TSV を修正し再インポート。

---

## 12. Outstanding To-Dos (Priority Order)
- 追加ブロックの重複削除と POS 競合解消。`literumilo_load.py` の上書き仕様により解析結果が不安定なため、最優先で処理する。
- `abstinenc` の辞書追加と `akaj^u → akajxu` 正規化。これで `reviewed_import_PEJVO_batch_*` の取り込み率を **225/227 → 227/227** へ引き上げられる。
- `progress_log.csv` のステータスを再同期し、今後の取り込みで `added` が正しく記録されるようにする。
- `reviewed_import_mixed_*` に含まれる重複語根（例: `apercept`, `baktericid`, `bos`）を整理。単一 POS に統合するか、辞書外で派生処理する。
- Unicode 表記揺れ（`^`, `x`, Unicode supersigno）を全ファイルで統一し、`rg`/`sort` ベースの比較が容易になるよう整備する。
- 重複解消後に単体テスト・Spot-check を再実行し、辞書上書きが起きていないことを確認する。

---

## Appendix – Useful Diagnostics
```bash
# 末尾ブロック（10697行目以降）の完全重複チェック
python3 - <<'PY'
from pathlib import Path
lines = Path('literumilo/literumilo/data/vortaro.tsv').read_text(encoding='utf-8').splitlines()
orig = 10697
seen = {}
dups = []
for idx, line in enumerate(lines[orig:], start=orig+1):
    if not line.strip():
        continue
    root = line.split('\t', 1)[0]
    if root in seen:
        dups.append((seen[root], idx, root))
    else:
        seen[root] = idx
for first, second, root in dups:
    print(f"{root}: first={first}, second={second}")
PY

# `PEJVO_missing_in_vortaro.txt` の正規化付き取り込み状況
python3 - <<'PY'
from pathlib import Path
ACCENT_TO_X = {'ĉ':'cx','ĝ':'gx','ĥ':'hx','ĵ':'jx','ŝ':'sx','ŭ':'ux',
               'Ĉ':'Cx','Ĝ':'Gx','Ĥ':'Hx','Ĵ':'Jx','Ŝ':'Sx','Ŭ':'Ux'}
def to_x(s: str) -> str:
    return ''.join(ACCENT_TO_X.get(ch, ch) for ch in s)
def load_pejvo_missing():
    roots = set()
    with Path('比較実験/PEJVO_missing_in_vortaro.txt').open(encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or line.startswith('PEJVO') or line.startswith('語根'):
                continue
            raw = line.split('\t')[0].split('#')[0].strip()
            roots.add(to_x(raw.replace('^', 'x')))
    return roots
def load_dictionary_roots():
    roots = set()
    with Path('literumilo/literumilo/data/vortaro.tsv').open(encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            root = line.split('\t', 1)[0]
            roots.add(to_x(root))
    return roots
missing = load_pejvo_missing()
present = load_dictionary_roots()
covered = len([root for root in missing if root in present])
print(f"covered (unique) {covered} / {len(missing)}; remaining {len(missing)-covered}")
PY

# reviewed_import_* のカテゴリ別集計
python3 - <<'PY'
from pathlib import Path
from collections import defaultdict
cats = defaultdict(set)
for path in Path('比較実験/batches').glob('reviewed_import_*.tsv'):
    cat = path.name.split('_')[2]
    with path.open(encoding='utf-8') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t')
            if len(parts) < 10 or '# OK' not in parts[9]:
                continue
            cats[cat].add(parts[0])
for cat in sorted(cats):
    print(f"{cat}: {len(cats[cat])} unique roots")
print(f"total unique: {len(set().union(*cats.values()))}")
PY
```

このドキュメントは常に最新の事実と残タスクを反映させること。新しい知見が得られた場合は、根拠となるコマンドやファイルとともに追記する。
