# テスト仕様書

本プロジェクトの自動テスト（検証スクリプト）に関する仕様と実行方法を記述します。

## 1. テスト環境

- **実行場所**: `tests/` ディレクトリ配下のスクリプトを使用
- **依存関係**: プロジェクトの仮想環境 (`.venv`)

## 2. テスト一覧

### 2.1. 基本アクションの検証

#### 2.1.1. Input アクションの検証 (`tests/verify_input_action.py`)

- **目的**: `Input` アクションがテキストボックスに正しく入力できることを検証する。Win32 APIフォールバックによるフォーカス設定も確認する。
- **テスト内容**:
  1. メモ帳を起動。
  2. テキストエリアに `Input` アクションでテキストを入力。
  3. フォーカスが正しく設定されたかログで確認。
  4. 入力されたテキストが正しいか確認（GetPropertyで取得）。
- **期待される結果**:
  - フォーカスが正しく設定される（UI AutomationまたはWin32 API）。
  - テキストが正しく入力される。
  - "Input Action Verification: PASS" が出力される。

#### 2.1.2. Invoke アクションの検証 (`tests/verify_invoke_action.py`)

- **目的**: `Invoke` アクションがボタンを正しく実行できることを検証する。Win32 APIフォールバックによるフォーカス設定も確認する。
- **テスト内容**:
  1. 電卓を起動。
  2. 数字ボタンに `Invoke` アクションを実行。
  3. フォーカスが正しく設定されたかログで確認。
  4. ボタンが実行されたか確認（画面の変化を確認）。
- **期待される結果**:
  - フォーカスが正しく設定される（UI AutomationまたはWin32 API）。
  - ボタンが正しく実行される。
  - "Invoke Action Verification: PASS" が出力される。

#### 2.1.3. FocusElement アクションの検証 (`tests/verify_focus_action.py`)

- **目的**: `FocusElement` アクションが要素に正しくフォーカスを当てることを検証する。Win32 APIフォールバックも確認する。
- **テスト内容**:
  1. メモ帳を起動。
  2. テキストエリアに `FocusElement` アクションを実行。
  3. ログに "Focusing element" と "Focus successfully set" が含まれるか確認。
  4. `HasKeyboardFocus` プロパティが `True` になるか確認。
- **期待される結果**:
  - ログに期待されるメッセージが含まれる。
  - 要素にフォーカスが設定される。
  - "FocusElement Action Verification: PASS" が出力される。

#### 2.1.4. SendKeys アクションの検証 (`tests/verify_sendkeys_action.py`)

- **目的**: `SendKeys` アクションがグローバルなキー送信を正しく実行できることを検証する。
- **テスト内容**:
  1. メモ帳を起動。
  2. テキストエリアにフォーカスを当てる。
  3. `SendKeys` アクションで `{Ctrl}a` を送信（全選択）。
  4. `SendKeys` アクションで `{Delete}` を送信（削除）。
- **期待される結果**:
  - キーが正しく送信される。
  - フォーカス設定は行われない（SendKeysはグローバル）。
  - "SendKeys Action Verification: PASS" が出力される。

#### 2.1.5. Click アクションの検証 (`tests/verify_click_action.py`)

- **目的**: `Click` アクションが要素を正しくクリックできることを検証する。
- **テスト内容**:
  1. 電卓を起動。
  2. 数字ボタンに `Click` アクションを実行。
  3. ボタンがクリックされたか確認。
- **期待される結果**:
  - ボタンが正しくクリックされる。
  - "Click Action Verification: PASS" が出力される。

#### 2.1.6. Select アクションの検証 (`tests/verify_select_action.py`)

- **目的**: `Select` アクションがラジオボタンやリストアイテムを正しく選択できることを検証する。
- **テスト内容**:
  1. 設定アプリやダイアログを起動。
  2. ラジオボタンに `Select` アクションを実行。
  3. 選択状態が変更されたか確認。
- **期待される結果**:
  - 要素が正しく選択される。
  - フォーカス設定は不要（SelectionItemPattern）。
  - "Select Action Verification: PASS" が出力される。

#### 2.1.7. Force-run フラグの検証 (`tests/verify_force_run.py`)

- **目的**: `--force-run` フラグがフォーカス失敗時に正しく動作することを検証する。
- **テスト内容**:
  1. 存在しない要素に `Input` アクションを実行（通常実行）。
  2. フォーカス失敗でエラー停止することを確認。
  3. 同じアクションを `--force-run` で実行。
  4. 警告を出して続行することを確認。
- **期待される結果**:
  - 通常実行: "Could not set focus" でエラー停止（Exit code: 1）。
  - `--force-run`: 警告を出して続行（Exit code: 0）。
  - "Force-run Verification: PASS" が出力される。

### 2.2. ログ機能の検証 (`tests/verify_logging.py`)

- **目的**: `automator.py` が `--log-file` および `--log-level` オプションを正しく処理し、ログファイルを出力することを確認する。
- **テスト内容**:
  1.  ダミーの `actions.csv` を作成。
  2.  `automator.py` を `--log-file` 指定で実行。
  3.  生成されたログファイルを読み込み、特定のログメッセージ（"Loading actions", "Waiting" など）が含まれているか確認。
- **期待される結果**:
  - ログファイルが作成されること。
  - ログファイル内に期待されるメッセージが存在すること。
  - スクリプトが "Logging Verification: PASS" を出力して終了すること。

### 2.3. Dry-run モードの検証 (`tests/verify_dry_run.py`)

- **目的**: `automator.py` が `--dry-run` オプション指定時に、副作用のある操作（アプリ起動、クリック等）をスキップし、その旨をログ出力することを確認する。
- **テスト内容**:
  1.  メモ帳を起動するアクションを含むダミーの `actions.csv` を作成。
  2.  `automator.py` を `--dry-run` 指定で実行。
  3.  ログファイルを解析し、"[Dry-run] Would launch" などのメッセージが出力されているか確認。
- **期待される結果**:
  - 実際にアプリが起動しないこと（実行時間が極端に短いことで間接的に検証）。
  - ログに "[Dry-run]" プレフィックス付きのメッセージが記録されること。
  - スクリプトが "Dry-run Verification: PASS" を出力して終了すること。

### 2.4. スクリーンショット機能の検証 (`tests/verify_screenshot.py`)

- **目的**: アクション実行中にエラーが発生した場合、自動的にスクリーンショットが保存されることを確認する。
- **テスト内容**:
  1.  存在しないウィンドウを操作しようとする（必ず失敗する）ダミーの `actions.csv` を作成。
  2.  `automator.py` を実行。
  3.  `errors/` ディレクトリ内のファイル数をカウントし、実行後に増えているか確認。
- **期待される結果**:
  - `automator.py` がエラーで終了（またはエラーログを出力）すること。
  - `errors/` ディレクトリに新しい `.png` ファイルが生成されること。
  - スクリプトが "Screenshot Verification: PASS" を出力して終了すること。

### 2.5. 既存機能の検証

以下のスクリプトは、以前の実装フェーズで作成された機能検証用です。

#### 2.5.1. エイリアス機能の検証 (`tests/verify_alias_feature.py`)

- **目的**: Inspectorによるエイリアス定義ファイルの出力と、Automatorによるエイリアスの読み込み・解決を検証する。
- **テスト内容**:
  - **Inspector**: ダミーの記録データをセットし、`--output alias` モードでCSVが出力されるか確認。
  - **Automator**: ダミーのエイリアス定義とアクション定義を作成し、アクション実行時にエイリアスが正しいRPAパスに置換されるか確認。
- **期待される結果**:
  - Inspector: `inspector_YYYYMMDD_..._alias.csv` が生成され、正しいカラムを持つこと。
  - Automator: アクションの `Key` がエイリアス定義の内容に置き換わっていること。

#### 2.5.2. 階層化パスの検証 (`tests/verify_automator_chained_path.py`)

- **目的**: `Parent -> Child` 形式の階層化されたRPAパスを `automator.py` が正しく解析し、要素を特定できるか検証する。
- **テスト内容**:
  - メモ帳を起動。
  - `Window -> Pane -> Document` のような階層化パスを手動で構築。
  - `automator.find_element_by_path` を呼び出し、要素が見つかるか確認。
- **期待される結果**:
  - 指定した階層化パスで要素が正しく特定されること（Result: Found）。

#### 2.5.3. Inspector基本ロジックの検証 (`tests/verify_inspector.py`)

- **目的**: `inspector.py` が実際のアプリ（電卓）から適切なRPAパスを生成できるか検証する。
- **テスト内容**:
  - 電卓を起動。
  - ボタン「5」やメニューボタンを対象に `get_rpa_path` を実行。
- **期待される結果**:
  - 生成されたパスに `ClassName` や `foundIndex`、または `AutomationId` が適切に含まれていること。

#### 2.5.4. Inspectorモードの検証 (`tests/verify_inspector_modes.py`)

- **目的**: `modern` モードと `legacy` モードで生成されるパスの違いを検証する。
- **テスト内容**:
  - メモ帳を起動。
  - **Modern**: `Name` や `AutomationId` を優先したパスが生成されるか確認。
  - **Legacy**: `ClassName` と `foundIndex` を使用したパスが生成されるか確認。
- **期待される結果**:
  - 各モードのポリシーに従ったパスが生成されること。

#### 2.5.5. Inspector出力の検証 (`tests/verify_inspector_output.py`)

- **目的**: CSVファイル出力とクリップボード出力が正しく機能するか検証する。
- **テスト内容**:
  - ダミーデータをセットし、`output="csv"` と `output="clipboard"` を実行。
- **期待される結果**:
  - CSVファイルが生成されること。
  - クリップボードにCSV形式の文字列がコピーされること。

### 2.6. 追加機能の検証

#### 2.6.1. 日本語エイリアスの検証 (`tests/verify_japanese_alias.py`)

- **目的**: `AliasName` に日本語（マルチバイト文字）を使用しても正しく動作することを検証する。
- **テスト内容**:
  - 日本語のエイリアス名（例: "メモ帳テキストエリア"）を含むエイリアス定義ファイルを作成。
  - そのエイリアスを使用するアクション定義ファイルを作成。
  - Automatorで読み込み、正しくRPAパスに解決されるか確認。
- **期待される結果**:
  - 日本語エイリアスが文字化けせずに読み込まれ、対応するRPAパスに置換されること。

#### 2.6.2. 待機アクションの検証 (`tests/verify_wait_actions.py`)

- **目的**: `WaitUntilVisible`, `WaitUntilEnabled` アクションが正しく動作することを検証する。
- **テスト内容**:
  - メモ帳を起動。
  - `WaitUntilVisible` でテキストエリアが表示されるのを待つ。
  - `WaitUntilEnabled` でテキストエリアが有効になるのを待つ。
- **期待される結果**:
  - タイムアウトエラーにならずにアクションが完了し、"WaitUntil Actions Verification: PASS" が出力されること。

#### 2.6.3. 対話型Inspectorの検証 (`tests/verify_interactive_alias.py`)

- **目的**: Inspectorの対話型エイリアスモード (`interactive_alias`) のロジックを検証する。
- **テスト内容**:
  - `builtins.input` と `wait_for_click` をモック化。
  - エイリアス名入力 -> クリック -> 記録 のフローが正しく実行されるか確認。
- **期待される結果**:
  - 記録されたアイテム数が一致し、エイリアス名とパスが正しく保持されていること。

#### 2.6.4. 複数CSV取り込みの検証 (`tests/verify_multi_csv.py`)

- **目的**: 複数のアクションファイルとエイリアスファイルを正しく読み込み、マージして実行できることを検証する。
- **テスト内容**:
  - 3つのアクションファイル (`setup.csv`, `main.csv`, `teardown.csv`) を作成。
  - 2つのエイリアスファイル (`common.csv`, `override.csv`) を作成。
  - これらをまとめて指定して実行し、実行順序とエイリアス解決（オーバーライド含む）が正しいかログで確認する。
- **期待される結果**:
  - すべてのアクションが順序通り実行され、エイリアスが正しく解決され、"Multi CSV Verification: PASS" が出力されること。

#### 2.6.5. 制御構文の検証 (`tests/verify_control_flow.py`)

- **目的**: `If`, `Else`, `Loop`, `SetVariable` などの制御構文が正しく動作することを検証する。
- **テスト内容**:
  - 変数設定 (`SetVariable`) と参照。
  - 条件分岐 (`If` - `Else`) の真偽両パターン。
  - ループ処理 (`Loop`) の回数指定と条件指定。
  - ネストされたループと条件分岐。
- **期待される結果**:
  - ログに変数の値変化や分岐の実行結果が正しく記録され、"Control Flow Verification: PASS" が出力されること。

#### 2.6.6. 正規表現マッチングの検証 (`tests/verify_regex_match.py`)

- **目的**: `TargetApp` の `regex:` 接頭辞および `RPA_Path` 内の `RegexName` プロパティによる正規表現マッチングを検証する。
- **テスト内容**:
  - メモ帳を起動。
  - `TargetApp` に `regex:.*(メモ帳|Notepad).*` を指定してウィンドウを特定。
  - `Key` に `RegexName='.*(Editor|エディター).*'` を指定して要素を特定。
- **期待される結果**:
  - 正規表現を使用したウィンドウおよび要素の特定に成功し、"Regex Verification: PASS" が出力されること。

#### 2.6.7. Inspectorパス最適化の検証 (`tests/verify_inspector_path.py`)

- **目的**: Modernモードにおいて、`AutomationId` が存在する場合に短いパス（`Window -> Element`）が生成されることを検証する。
- **テスト内容**:
  - 電卓を起動。
  - "5"ボタンを特定。
  - `Inspector` をModernモードで初期化し、`get_rpa_path` を呼び出す。
- **期待される結果**:
  - 生成されたパスに `->` が含まれず、`AutomationId` が含まれていること（"Inspector Verification: PASS"）。

#### 2.6.8. 再帰検索フォールバックの検証 (`tests/verify_recursive_fallback.py`)

- **目的**: 要素が指定された階層で見つからない場合、再帰検索（全探索）にフォールバックして発見できることを検証する。
- **テスト内容**:
  - 電卓を起動。
  - 意図的に間違った階層（`searchDepth`）を指定して要素を検索し、失敗させる。
  - 自動的に再帰検索が実行され、要素が発見されるか確認する。
- **期待される結果**:
  - 階層指定での検索失敗後、再帰検索で要素が見つかり "PASS: Found recursively" が出力されること。

## 3. テスト実行方法

以下のコマンドですべての検証スクリプトを実行できます。

```bash
# 基本アクションの検証
python tests/verify_input_action.py
python tests/verify_invoke_action.py
python tests/verify_focus_action.py
python tests/verify_sendkeys_action.py
python tests/verify_click_action.py
python tests/verify_select_action.py
python tests/verify_force_run.py

# 新機能の検証
python tests/verify_logging.py
python tests/verify_dry_run.py
python tests/verify_screenshot.py
python tests/verify_japanese_alias.py
python tests/verify_wait_actions.py
python tests/verify_interactive_alias.py
python tests/verify_multi_csv.py
python tests/verify_control_flow.py
python tests/verify_regex_match.py
python tests/verify_inspector_path.py
python tests/verify_recursive_fallback.py

# 既存機能の検証
python tests/verify_alias_feature.py
python tests/verify_automator_chained_path.py
python tests/verify_inspector.py
python tests/verify_inspector_modes.py
python tests/verify_inspector_output.py
```

## 4. テスト結果レポート要件

テスト実行後は、以下の形式でレポートを作成すること。

### 4.1. レポート保存場所

`reports/test_results/` ディレクトリ配下に保存する。

### 4.2. レポートファイル

- `test_results_summary_YYYYMMDD_HHMM.md` - テスト結果サマリー（マークダウン形式、タイムスタンプ付き）
  - 例: `test_results_summary_20251206_0910.md`
- `<test_name>_output.txt` - 各テストの詳細出力

### 4.3. サマリーレポートの形式

以下の情報を含むこと:

1. **実行日時**
2. **テスト環境**（Python バージョン、OS、実行場所）
3. **テスト結果一覧表**
   - カラム: `| テスト対象 | テストファイル | 予期する結果 | 実行結果 | 判定 |`
   - 各テストについて、test_spec.md の期待結果と実際の実行結果を比較
   - 判定は ✅ PASS / ❌ FAIL / ⚠️ SKIP のいずれか
4. **詳細分析**
   - 各テストについて、test_spec.md との整合性を確認
   - 期待される動作と実際の動作を詳細に記述
   - 判定理由を明確に説明
5. **総合評価**
   - 実行したテスト数
   - 成功/失敗/スキップの件数と割合
6. **test_spec.md との齟齬**
   - 齟齬がある場合は詳細に記述
   - 齟齬がない場合は「齟齬なし」と明記
7. **実行しなかったテスト**
   - test_spec.md に記載されているが実行しなかったテストをリスト化
   - 理由を記述

### 4.4. レポート作成の注意事項

- 「合格した」だけの報告は不可
- 各テストについて、何を予期して実行結果がどうで、合否判定がどうなのか、すべて説明すること
- test_spec.md の内容と実際の実行結果を詳細に比較すること
- Exit code も含めて記録すること
