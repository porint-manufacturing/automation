# Automator App - 設計書

## 1. 概要

`inspector.py` で取得した UI 要素のキー（パス）を利用し、指定された操作手順（CSV）に従ってアプリケーションを自動操作する RPA ツールを作成します。

## 2. 要件

- **入力**: 操作手順が記述された CSV ファイル。
  - デフォルト: `actions.csv`（引数指定がない場合）
  - 引数指定: `python automator.py my_actions.csv`
- **実行**: CSV の行番号順に操作を実行。
- **待機**: 各操作の間に適切な待機時間を設ける（デフォルト設定 + CSV での指定も検討）。

## 3. CSV フォーマット

ヘッダーあり。以下のカラムを持つ。

| カラム名      | 説明                                                                   | 例                         |
| :------------ | :--------------------------------------------------------------------- | :------------------------- |
| **TargetApp** | 操作対象のウィンドウ名（トップレベル）。検索に使用。                   | `電卓`、`メモ帳`           |
| **Key**       | 操作対象のコントロールを特定するキー（`inspector.py` の `RPA_Path`）。 | `ButtonControl(Name='5')`  |
| **Action**    | 操作内容。                                                             | `Click`, `Input`, `Launch` |
| **Value**     | 入力値（`Input` の場合など）。                                         | `Hello World`, `calc.exe`  |

### 3.1. Action 一覧

- `Launch`: アプリを起動する（`Value` に実行ファイルパス）。`TargetApp` は無視または確認用。
- `Click`: 左クリック。
- `Input`: テキスト入力（`Value` の内容）。`{変数名}` で変数の値を参照可能。
- `Wait`: 指定秒数待機（`Value` に秒数）。
- `Focus`: ウィンドウまたは要素をフォーカス。
- `GetValue`: 要素の値（Name または ValuePattern）を取得し、変数に保存。`Value` カラムに変数名を指定。
- `SendKeys`: キー操作を送信（`{Ctrl}n` など）。
- `SetClipboard`: クリップボードに値を設定。
- `GetClipboard`: クリップボードから値を取得し、変数に保存。
- `Paste`: クリップボードの内容を貼り付け（`Ctrl+V` 送信）。
- `VerifyValue`: 要素の値が期待値（`Value`）と一致するか検証。
- `VerifyVariable`: 変数の値が期待値（`Value`）と一致するか検証。
- `Exit`: アプリケーション（ウィンドウ）を終了する。

## 4. 技術アーキテクチャ

### 4.1. モジュール構成

`automator.py`はオーケストレーション層として機能し、以下のモジュールに処理を委譲します：

#### コアモジュール (`src/automator/core/`)

- **ActionExecutor** (`action_executor.py`)
  - 全23種のアクション実行を担当
  - Launch, Click, Input, Wait, Focus, SendKeys, Select, Invoke
  - GetValue, SetVariable, GetClipboard, SetClipboard, Paste
  - VerifyValue, VerifyVariable, Screenshot
  - Exit, GetDateTime, GetProperty, GetRelative, FocusElement
  - Loop, EndLoop, If, EndIf
- **ElementFinder** (`element_finder.py`)
  - UI要素の検索と特定
  - RPAパス解析（階層パス対応）
  - エイリアス解決
  - 相対位置での要素検索

#### ユーティリティモジュール (`src/automator/utils/`)

- **FocusManager** (`focus.py`)
  - ウィンドウフォーカス管理
  - 最前面化処理

- **Screenshot** (`screenshot.py`)
  - エラー時のスクリーンショット撮影
  - `errors/` ディレクトリに保存

### 4.2. 設計原則

- **単一責任原則**: 各モジュールが明確な責任を持つ
- **関心の分離**: ロジックを層別に分離（オーケストレーション/実行/検索/ユーティリティ）
- **テスト容易性**: モジュール単位でテスト可能
- **保守性**: 変更影響範囲の限定

### 4.3. ライブラリ

- **`uiautomation`**: ウィンドウの検索、要素の特定、操作（Click, SetValue 等）に使用。
- **`csv`**: 標準ライブラリで読み込み。
- **`subprocess`**: アプリ起動用。

### 4.4. 変数管理

- `Automator` クラス内に辞書 `self.variables` を保持。
- `GetValue`, `GetClipboard` アクションで値を保存。
- `Input` アクションなどで `{変数名}` 形式の文字列を置換。

### 4.5. 要素特定ロジック (`Key` の解析)

`inspector.py` が出力する `RPA_Path` は `ControlTypeName(Property='Value') -> ...` という形式。
これを `ElementFinder` が解析し、ルート（`TargetApp` で指定されたウィンドウ）から順に `uiautomation` で要素を検索して特定する。

**検索戦略:**

1. `TargetApp` (Regex Name) でトップレベルウィンドウを検索・フォーカス。
2. `Key` 文字列を `->` で分割。
3. 各階層について、`ControlTypeName` とプロパティ（`Name`, `AutomationId`）をパースし、現在位置の子要素から検索。
4. 最終的な要素に対して `Action` を実行。

## 5. エラー処理

- **要素が見つからない場合**: 指定回数リトライした後、エラーログを出力して停止（または設定によりスキップ）。
- **操作失敗**: 例外をキャッチしてエラー表示。

## 6. ファイル構成

- `automator.py`: メインスクリプト（オーケストレーション）。
- `src/automator/`: Automatorモジュール群。
- `actions.csv`: デフォルトの操作定義ファイル。
