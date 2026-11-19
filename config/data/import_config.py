#!/usr/bin/env python3
"""
# import_config.py

`export_config.py` が書き出した JSON を読み込み、各 `.html` の該当箇所**だけ**を上書きする。

| キー | 書き換える場所 |
| --- | --- |
| `tips` | `new TipsView(tipsModel, "tips", "tips", [...])` の `[...]` |
| `property:og:title` など | `<meta property="og:title" content="...">` の `content` |

探すキーとパターンは `page_pattern.py` の `PagePattern` で定義している。

## 使い方

`config/data` で次のように実行する。

```
python import_config.py
```

変更内容だけを確認したい場合は、末尾の `ImportTips("../../", dry_run=True)` に切り替える。

## 実行時の前提

| 項目 | 内容 |
| --- | --- |
| 実行ディレクトリ | `config/data`（どこから実行しても、スクリプトの場所を基準に解決する） |
| サイトのルート | スクリプトから `../../`。JSON の `page` はここからの相対パス |
| 入力ファイル | スクリプトと同じディレクトリの `tips.json` |
| モデル | ルートからの `model/tips/tips.js`（チップ ID の存在確認用。ファイルがなければ確認を省略） |
| 共通モジュール | スクリプトと同じディレクトリの `page_pattern.py` |

## 入力形式

```json
[
    {
        "page" : "html/tips/appbuild.html",
        "tips" : ["cTip", "securityTip", "serverTip"],
        "property:og:title" : "アプリ作成メモ"
    }
]
```

| キー | 型 | 説明 |
| --- | --- | --- |
| `page` | `string` | ルートからの相対パス（区切りは `/`）。必須 |
| `tips` | `string[]` | 新しいチップ ID のリスト。空配列も可。旧キー `tipList` も読める |
| `property:*` | `string` | `<meta property="*">` の新しい `content`。HTML エスケープは不要（書き込み時に行う） |

**JSON に書かれていないキーは、HTML を変更しない。**

## 動作

| 項目 | 内容 |
| --- | --- |
| 書き換え範囲 | 該当する `[...]` や `content` の中身のみ。他の部分は 1 バイトも変更しない |
| 値が同じ場合 | そのキーは書き換えない（空白や引用符の書き方も元のまま残る） |
| HTML にタグがない場合 | **そのキーはインポートしない**（警告のみ。ファイルは書き換える） |
| 改行コード | 元ファイルのまま保持（CRLF のファイルは CRLF のまま） |
| 文字コード | UTF-8（BOM なし）で読み書き |
| 変更がない場合 | ファイルを書き込まない |
| エラーがある場合 | **1 ファイルも書き換えず**に終了コード `1` で終了（全件検証してから書き込む） |
| 未知のチップ ID | 警告のみ（モデルの `tipsData` に存在しない ID）。書き換えは行う |

## エラーと警告

| 種類 | 内容 |
| --- | --- |
| エラー | JSON が読めない / 配列でない / `page` がない・重複 / 未対応のキー / 値の型が違う |
| エラー | `page` がルートの外を指す / ファイルがない |
| 警告 | HTML にそのキーのタグがない（スキップ） |
| 警告 | 同じキーが 1 ファイルに複数ある（最初の 1 つのみ書き換え） |
| 警告 | 未知のチップ ID |

## 定数

| 名前 | 説明 |
| --- | --- |
| `MODEL_KEY_PATTERN` | モデルの `tipsData` から、チップ ID（キー）を取り出す正規表現 |

## 注意

- 表示順は `TipsView` 側が `model.tipsIndex`（キーの昇順）で決めるため、`tips` の**並び順は表示に影響しない**
- `//` や `<!--` の後ろにある呼び出しはコメントアウトとみなして無視する
"""

import json
import re
import sys
from pathlib import Path

from page_pattern import PagePattern


class ImportTips:
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
        | `root` | `str` | - | サイトのルートディレクトリ（例: `"../../"`） |
        | `json_path` | `str` | `"tips.json"` | 読み込む JSON ファイル |
        | `model` | `str` | `"model/tips/tips.js"` | `root` からみた、チップ ID 確認用のモデル |
        | `dry_run` | `bool` | `False` | `True` ならファイルを書き換えず、変更内容だけ表示する |
        """
        base = Path(__file__).resolve().parent
        self.root = (base / root).resolve()
        self.json_path = (base / json_path).resolve()
        self.model_path = self.root / model
        self.dry_run = dry_run


    def validate_entries(self, data: object) -> tuple[list[dict], list[str]]:
        """
        JSON のトップレベル構造を検証し、旧キーを読み替えた形に整える。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `data` | `object` | `json.load` の結果 |

        ## 戻り値

        `tuple[list[dict], list[str]]` の 2 要素タプル。

        | 位置 | 型 | 説明 |
        | --- | --- | --- |
        | 0 | `list[dict]` | `{"page": str, "values": {キー: 値}}` のリスト。`values` のキーは旧キーを現行キーに読み替え済み |
        | 1 | `list[str]` | エラーメッセージ。問題がなければ空リスト |

        ## 検証内容

        | 内容 | 条件 |
        | --- | --- |
        | トップレベル | 配列であること |
        | 各要素 | オブジェクトで、`page`（空でない文字列）を持つこと |
        | `page` | 重複しないこと |
        | その他のキー | `PagePattern` が対応するキーであること（`tips`、`property:*`） |
        | `tips` | 文字列の配列であること |
        | `property:*` | 文字列であること |
        | 別名 | `tips` と `tipList` を同時に書かないこと |
        """
        if not isinstance(data, list):
            return [], ["JSON のトップレベルは配列である必要があります"]

        entries: list[dict] = []
        errors: list[str] = []
        seen: set[str] = set()

        for i, entry in enumerate(data):
            label = f"[{i}]"
            if not isinstance(entry, dict):
                errors.append(f"{label}: オブジェクトではありません")
                continue

            page = entry.get("page")
            if not isinstance(page, str) or not page:
                errors.append(f"{label}: page が文字列ではありません")
                continue
            label = f"[{i}] {page}"

            if page in seen:
                errors.append(f"{label}: page が重複しています")
            seen.add(page)

            values: dict = {}
            for raw_key, value in entry.items():
                if raw_key == "page":
                    continue

                key = PagePattern.normalize_key(raw_key)
                if PagePattern.get_pattern(key) is None:
                    errors.append(f"{label}: 未対応のキー '{raw_key}'")
                    continue
                if key in values:
                    errors.append(f"{label}: {key} が重複しています（旧キーとの併記を含む）")
                    continue

                if PagePattern.is_list_key(key):
                    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
                        errors.append(f"{label}: {raw_key} が文字列の配列ではありません")
                        continue
                elif not isinstance(value, str):
                    errors.append(f"{label}: {raw_key} が文字列ではありません")
                    continue

                values[key] = value

            entries.append({"page": page, "values": values})

        return entries, errors


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


    def replace_value(self, text: str, key: str, value: list[str] | str) -> tuple[str, int] | None:
        """
        `key` に対応する箇所の中身を `value` で置き換える。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `text` | `str` | HTML 全文（改行コードは変換せず、そのまま渡すこと） |
        | `key` | `str` | `"tips"` または `"property:<名前>"` |
        | `value` | `list[str]` または `str` | 新しい値 |

        ## 戻り値

        | 型 | 条件 | 内容 |
        | --- | --- | --- |
        | `tuple[str, int]` | 該当箇所が見つかった | `(置換後の全文, 見つかった個数)`。値が同じなら全文は変わらない |
        | `None` | 該当箇所が見つからない | - |
        """
        matches = PagePattern.find_matches(text, key)
        if not matches:
            return None

        # 値が同じなら触らない（HTML エスケープや空白の書き方の違いで差分を出さない）
        match = matches[0]
        if PagePattern.decode(key, match.group("value")) == value:
            return text, len(matches)

        start, end = match.span("value")
        return text[:start] + PagePattern.encode(key, value) + text[end:], len(matches)


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

        entries, errors = self.validate_entries(data)
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

        for entry in entries:
            page: str = entry["page"]
            values: dict = entry["values"]
            path = (self.root / page).resolve()

            if not path.is_relative_to(self.root):
                errors.append(f"{page}: ルートの外を指しています")
                continue
            if not path.is_file():
                errors.append(f"{page}: ファイルがありません")
                continue

            # `read_text` は CRLF を LF に変換してしまうため、バイト列から復号する
            original = path.read_bytes().decode("utf-8")
            updated = original

            for key, value in values.items():
                if key == PagePattern.TIPS_KEY and known_ids is not None:
                    for tip in value:
                        if tip not in known_ids:
                            print(f"警告: {page}: 未知のチップ ID '{tip}'", file=sys.stderr)

                result = self.replace_value(updated, key, value)
                if result is None:
                    print(f"警告: {page}: {key} のタグがないためスキップします", file=sys.stderr)
                    continue

                updated, count = result
                if count > 1:
                    print(f"警告: {page}: {key} が {count} 個あるため最初の 1 つのみ書き換えます", file=sys.stderr)

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
    sys.exit(ImportTips("../../").run())
