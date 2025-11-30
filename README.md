# Windows UI Automation Tool

Python製のWindows UI自動化ツールキットです。`uiautomation` ライブラリをベースに、アクション定義ファイル（CSV）による自動化実行 (`automator.py`) と、UI要素の解析・パス生成ツール (`inspector.py`) を提供します。

## 特徴

- **Automator (`automator.py`)**:
  - CSVファイルに記述されたアクション（クリック、入力、待機など）を順次実行。
  - RPAパスによる柔軟な要素特定（階層化パス、正規表現サポート）。
  - エイリアス機能によるアクション定義の簡略化。
  - 変数の使用と検証機能。
- **Inspector (`inspector.py`)**:
  - マウスオーバーとクリックでUI要素を解析し、RPAパスを自動生成。
  - **Modernモード**: AutomationIdを優先するモダンアプリ向け。
  - **Legacyモード**: ClassNameを優先するレガシーアプリ向け。
  - **Chained Path**: 親子関係を利用した高速で堅牢なパス生成。
  - CSV出力、クリップボードコピー、エイリアス定義テンプレート生成に対応。

## 必要要件

- Windows OS
- Python 3.x
- `uiautomation`
- `keyboard`

## インストール

```bash
# リポジトリのクローン
git clone <repository-url>
cd automation

# 仮想環境の作成と有効化（推奨）
python -m venv .venv
.venv\Scripts\activate

# 依存ライブラリのインストール
pip install -r requirements.txt
```

## 使い方

### 1. UI要素の調査 (Inspector)

操作したいアプリケーションのUI要素を特定し、RPAパスを取得します。

```bash
# 基本的な使用法（クリップボードにコピー）
python inspector.py

# レガシーアプリ向けモード
python inspector.py --mode legacy

# エイリアス定義用のCSVテンプレートを作成
python inspector.py --output alias
```

- 要素をクリックすると、その要素のRPAパスが生成されます。
- `ESC` キーで終了します。

### 2. アクションの定義

`actions.csv` などのCSVファイルを作成し、自動化の手順を記述します。

| TargetApp | Key                          | Action | Value |
| :-------- | :--------------------------- | :----- | :---- |
| 電卓      | ButtonControl(Name='5')      | Click  |       |
| 電卓      | ButtonControl(Name='プラス') | Click  |       |
| 電卓      | ButtonControl(Name='3')      | Click  |       |
| 電卓      | ButtonControl(Name='等号')   | Click  |       |

### 3. 自動化の実行 (Automator)

作成したアクション定義ファイルを指定して実行します。

```bash
# アクションファイルの実行
python automator.py actions.csv

# エイリアスファイルを使用して実行
python automator.py actions.csv --aliases aliases.csv
```

## ディレクトリ構成

- `automator.py`: 自動化実行のメインスクリプト
- `inspector.py`: UI解析ツール
- `docs/`: ドキュメント
- `tests/`: テストスクリプト
- `debug/`: デバッグ用スクリプト

## ライセンス

[MIT License](LICENSE)
