#!/usr/bin/env python3
"""
# import_tips.py

`export_tips.py` が書き出した JSON を読み込み、各 `.html` の
`new TipsView(tipsModel, "tips", "tips", [...])` の**配列部分だけ**を上書きする。

## 使い方

`config/tips/tiplist` で次のように実行する。

```
python import_tips.py
```

変更内容だけを確認したい場合は、末尾の `ImportTips("../../../", dry_run=True)` に切り替える。

## 実行時の前提

| 項目 | 内容 |
| --- | --- |
| 実行ディレクトリ | `config/tips/tiplist`（どこから実行しても、スクリプトの場所を基準に解決する） |
| サイトのルート | スクリプトから `../../../`。JSON の `page` はここからの相対パス |
| 入力ファイル | スクリプトと同じディレクトリの `tips.json` |
| モデル | ルートからの `model/tips/tips.js`（チップ ID の存在確認用。ファイルがなければ確認を省略） |

## 入力形式

```json
[
    {
        "page" : "html/tips/linux.html",
        "tipList" : ["windowsTip", "dockerTip", "serverTip"]
    }
]
```

| キー | 型 | 説明 |
| --- | --- | --- |
| `page` | `string` | ルートからの相対パス（区切りは `/`） |
| `tipList` | `string[]` | 新しいチップ ID のリスト。空配列も可 |

## 動作

| 項目 | 内容 |
| --- | --- |
| 書き換え範囲 | `TipsView` 呼び出しの `[...]` のみ。他の部分は 1 バイトも変更しない |
| 改行コード | 元ファイルのまま保持（CRLF のファイルは CRLF のまま） |
| 文字コード | UTF-8（BOM なし）で読み書き |
| 変更がない場合 | ファイルを書き込まない |
| エラーがある場合 | **1 ファイルも書き換えず**に終了コード `1` で終了（全件検証してから書き込む） |
| 未知のチップ ID | 警告のみ（`--model` のキーに存在しない ID）。書き換えは行う |

## 定数

| 名前 | 説明 |
| --- | --- |
| `TIPS_VIEW_PATTERN` | 4 番目の引数に配列を持つ `new TipsView(...)` にマッチする正規表現 |
| `MODEL_KEY_PATTERN` | モデルの `tipsData` から、チップ ID（キー）を取り出す正規表現 |

## 注意

- 表示順は `TipsView` 側が `model.tipsIndex`（キーの昇順）で決めるため、`tipList` の**並び順は表示に影響しない**
- `//` や `<!--` の後ろにある呼び出しはコメントアウトとみなして無視する
- 1 ファイルに複数の呼び出しがある場合は**最初の 1 つ**だけを書き換える
"""

import json
import re
import sys
from pathlib import Path


class ImportTips:
    TIPS_VIEW_PATTERN = re.compile(
        r"""new\s+TipsView\s*\(
            \s*\w+\s*,                          # model
            \s*(?:"[^"]*"|'[^']*')\s*,          # html
            \s*(?:"[^"]*"|'[^']*')\s*,          # id
            \s*\[(?P<list>[^\]]*)\]             # dispElement
            \s*\)""",
        re.VERBOSE,
    )

    MODEL_KEY_PATTERN = re.compile(r"""^\s*\"(?P<id>[A-Za-z0-9_]+)\"\s*:\s*\{""", re.MULTILINE)


    def __init__(
        self,
        root: str,
        json_path: str = "tips.json",
        model: str = "model/tips/tips.js",
        dry_run: bool = False,
    ):
        """
        読み込む JSON などの設定を保持する。`root` と `json_path` の相対パスはスクリプトの場所を基準に解決する。

        ## 引数

        | 名前 | 型 | 既定値 | 説明 |
        | --- | --- | --- | --- |
        | `root` | `str` | - | サイトのルートディレクトリ（例: `"../../../"`） |
        | `json_path` | `str` | `"tips.json"` | 読み込む JSON ファイル |
        | `model` | `str` | `"model/tips/tips.js"` | `root` からみた、チップ ID 確認用のモデル |
        | `dry_run` | `bool` | `False` | `True` ならファイルを書き換えず、変更内容だけ表示する |
        """
        base = Path(__file__).resolve().parent
        self.root = (base / root).resolve()
        self.json_path = (base / json_path).resolve()
        self.model_path = self.root / model
        self.dry_run = dry_run


    def is_commented_out(self, text: str, start: int) -> bool:
        """
        マッチ位置が、同じ行の `//` または `<!--` より後ろにあるかを判定する。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `text` | `str` | HTML 全文 |
        | `start` | `int` | `new TipsView` の開始位置 |

        ## 戻り値

        | 型 | 値 | 意味 |
        | --- | --- | --- |
        | `bool` | `True` | コメントアウトされている |
        | `bool` | `False` | 有効なコード |
        """
        line_start = text.rfind("\n", 0, start) + 1
        prefix = text[line_start:start]
        return "//" in prefix or "<!--" in prefix


    def validate_entries(self, data: object) -> list[str]:
        """
        JSON のトップレベル構造を検証する。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `data` | `object` | `json.load` の結果 |

        ## 戻り値

        | 型 | 説明 |
        | --- | --- |
        | `list[str]` | エラーメッセージ。問題がなければ空リスト |

        ## 検証内容

        | 内容 | 条件 |
        | --- | --- |
        | トップレベル | 配列であること |
        | 各要素 | `page`（文字列）と `tipList`（文字列の配列）を持つこと |
        | `page` | 重複しないこと |
        """
        if not isinstance(data, list):
            return ["JSON のトップレベルは配列である必要があります"]

        errors: list[str] = []
        seen: set[str] = set()

        for i, entry in enumerate(data):
            label = f"[{i}]"
            if not isinstance(entry, dict):
                errors.append(f"{label}: オブジェクトではありません")
                continue

            page = entry.get("page")
            tip_list = entry.get("tipList")

            if not isinstance(page, str) or not page:
                errors.append(f"{label}: page が文字列ではありません")
                continue
            label = f"[{i}] {page}"

            if page in seen:
                errors.append(f"{label}: page が重複しています")
            seen.add(page)

            if not isinstance(tip_list, list) or not all(isinstance(t, str) for t in tip_list):
                errors.append(f"{label}: tipList が文字列の配列ではありません")

        return errors


    def load_known_ids(self) -> set[str] | None:
        """
        モデルファイルからチップ ID の一覧を取り出す。

        ## 引数

        なし（`__init__` で渡した `model` を使う）。

        ## 戻り値

        | 型 | 条件 |
        | --- | --- |
        | `set[str]` | チップ ID の集合 |
        | `None` | ファイルが存在しない（確認を省略する） |
        """
        if not self.model_path.is_file():
            return None
        text = self.model_path.read_text(encoding="utf-8")
        return {m.group("id") for m in self.MODEL_KEY_PATTERN.finditer(text)}


    def replace_tip_list(self, text: str, tip_list: list[str]) -> tuple[str, int] | None:
        """
        `TipsView` 呼び出しの配列部分を `tip_list` で置き換える。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `text` | `str` | HTML 全文（改行コードは変換せず、そのまま渡すこと） |
        | `tip_list` | `list[str]` | 新しいチップ ID |

        ## 戻り値

        | 型 | 条件 | 内容 |
        | --- | --- | --- |
        | `tuple[str, int]` | 呼び出しが見つかった | `(置換後の全文, 見つかった呼び出しの数)` |
        | `None` | 呼び出しが見つからない | - |
        """
        matches = [
            m for m in self.TIPS_VIEW_PATTERN.finditer(text)
            if not self.is_commented_out(text, m.start())
        ]
        if not matches:
            return None

        new_array = "[" + ", ".join(json.dumps(tip, ensure_ascii=False) for tip in tip_list) + "]"

        # `list` グループは `[` `]` の内側なので、前後 1 文字ずつ広げて括弧ごと置き換える
        start, end = matches[0].span("list")
        return text[:start - 1] + new_array + text[end + 1:], len(matches)


    def run(self) -> int:
        """
        JSON を読み込み、検証してから各 HTML を書き換える。

        ## 戻り値

        | 値 | 意味 |
        | --- | --- |
        | `0` | 成功（`dry_run` の場合は更新予定の表示まで） |
        | `1` | 入力 JSON の不備、または 1 件でもエラーがあった（どのファイルも書き換えない） |
        """
        try:
            with open(self.json_path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as e:
            print(f"エラー: {self.json_path} を読み込めません: {e}", file=sys.stderr)
            return 1

        errors = self.validate_entries(data)
        if errors:
            for message in errors:
                print(f"エラー: {message}", file=sys.stderr)
            return 1

        known_ids = self.load_known_ids()
        if known_ids is None:
            print(f"注意: {self.model_path} がないため、チップ ID の存在確認を省略します", file=sys.stderr)

        # 1. 全件を検証しながら、書き込み内容をメモリ上に作る
        pending: list[tuple[Path, str, str]] = []  # (パス, 表示名, 新しい全文)
        unchanged = 0

        for entry in data:
            page: str = entry["page"]
            tip_list: list[str] = entry["tipList"]
            path = (self.root / page).resolve()

            if not path.is_relative_to(self.root):
                errors.append(f"{page}: ルートの外を指しています")
                continue
            if not path.is_file():
                errors.append(f"{page}: ファイルがありません")
                continue

            if known_ids is not None:
                for tip in tip_list:
                    if tip not in known_ids:
                        print(f"警告: {page}: 未知のチップ ID '{tip}'", file=sys.stderr)

            # `read_text` は CRLF を LF に変換してしまうため、バイト列から復号する
            original = path.read_bytes().decode("utf-8")
            result = self.replace_tip_list(original, tip_list)
            if result is None:
                errors.append(f"{page}: 有効な new TipsView(..., [...]) が見つかりません")
                continue

            updated, count = result
            if count > 1:
                print(f"警告: {page}: TipsView が {count} 個あるため最初の 1 つのみ書き換えます", file=sys.stderr)

            if updated == original:
                unchanged += 1
            else:
                pending.append((path, page, updated))

        if errors:
            for message in errors:
                print(f"エラー: {message}", file=sys.stderr)
            print("エラーがあるため、どのファイルも書き換えていません", file=sys.stderr)
            return 1

        # 2. エラーがなければ書き込む
        for path, page, updated in pending:
            if self.dry_run:
                print(f"[dry-run] 更新予定: {page}")
            else:
                path.write_bytes(updated.encode("utf-8"))
                print(f"更新: {page}")

        verb = "更新予定" if self.dry_run else "更新"
        print(f"{verb} {len(pending)} 件 / 変更なし {unchanged} 件")
        return 0


if __name__ == "__main__":
    sys.exit(ImportTips("../../../").run())
