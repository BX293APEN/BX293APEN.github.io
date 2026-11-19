#!/usr/bin/env python3
"""
# export_config.py

`.html` 内の次の項目を全て探し、**ページごとの設定**を JSON ファイルに書き出す。

| キー | 探す場所 |
| --- | --- |
| `tips` | `new TipsView(tipsModel, "tips", "tips", [...])` の `[...]` |
| `property:og:title` など | `<meta property="og:title" content="...">` の `content` |

探すキーとパターンは `page_pattern.py` の `PagePattern.SEARCH_PATTERN` で定義している。
項目を増やすときは、そちらに 1 行足す。

## 使い方

`config/data` で次のように実行する。

```
python export_config.py
```

## 実行時の前提

| 項目 | 内容 |
| --- | --- |
| 実行ディレクトリ | `config/data`（どこから実行しても、スクリプトの場所を基準に解決する） |
| サイトのルート | スクリプトから `../../`（`html/` と `model/` がある場所） |
| 探索ディレクトリ | ルート直下の `html` |
| 出力ファイル | スクリプトと同じディレクトリの `tips.json` |
| 共通モジュール | スクリプトと同じディレクトリの `page_pattern.py` |

## 出力形式

```json
[
    {
        "page" : "html/tips/appbuild.html",
        "tips" : ["cTip", "securityTip", "serverTip"],
        "property:og:title" : "アプリ作成メモ",
        "property:og:url" : "https://bx293apen.github.io/html/tips/appbuild.html"
    }
]
```

| キー | 型 | 説明 |
| --- | --- | --- |
| `page` | `string` | ルートからの相対パス（区切りは `/`）。`index.html` が複数あるため、ファイル名だけでは一意にならない |
| `tips` | `string[]` | `TipsView` の 4 番目の引数（`dispElement`）。HTML に書かれた順序のまま |
| `property:*` | `string` | `<meta property="*">` の `content`。HTML エスケープは外した文字列 |

## 注意

- **HTML にないタグのキーは出力しない**（`tips` のないページは `tips` を書かない）
- 1 つもキーが見つからないページは出力しない
- 4 番目の引数がない `TipsView` 呼び出し（`html/tips/index.html` の `new TipsView(tipsModel, "index", "tipsList")`）は
  `tips` を持たないものとして扱い、警告を表示する
- `//` や `<!--` の後ろにある呼び出しはコメントアウトとみなして無視する
- 同じキーが 1 ファイルに複数ある場合は**最初の 1 つ**だけを使い、警告を表示する
"""

import json
import sys
from pathlib import Path

from page_pattern import PagePattern


class ExportTips:
    def __init__(self, root: str, html_dir: str = "html", output: str = "tips.json"):
        """
        出力先などの設定を保持する。相対パスはスクリプトの場所を基準に解決する。

        ## 引数

        | 名前 | 型 | 既定値 | 説明 |
        | --- | --- | --- | --- |
        | `root` | `str` | - | サイトのルートディレクトリ（例: `"../../"`） |
        | `html_dir` | `str` | `"html"` | `root` からみた、HTML を探索するディレクトリ |
        | `output` | `str` | `"tips.json"` | 書き出す JSON ファイル |
        """
        base = Path(__file__).resolve().parent
        self.root = (base / root).resolve()
        self.html_dir = html_dir
        self.output = (base / output).resolve()


    def collect_pages(self) -> tuple[list[dict], list[str]]:
        """
        `root/html_dir` 以下の全 `.html` を走査し、`SEARCH_PATTERN` の各キーの値を集める。

        ## 引数

        なし（`__init__` で渡した設定を使う）。

        ## 戻り値

        `tuple[list[dict], list[str]]` の 2 要素タプル。

        | 位置 | 型 | 説明 |
        | --- | --- | --- |
        | 0 | `list[dict]` | `{"page": str, <キー>: <値>, ...}` のリスト（`page` の昇順）。見つかったキーだけを持つ |
        | 1 | `list[str]` | 警告メッセージのリスト |
        """
        pages: list[dict] = []
        warnings: list[str] = []

        for path in sorted((self.root / self.html_dir).rglob("*.html")):
            rel = path.relative_to(self.root).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                warnings.append(f"{rel}: UTF-8 として読めないためスキップ")
                continue

            entry: dict = {"page": rel}

            for key in PagePattern.SEARCH_PATTERN:
                matches = PagePattern.find_matches(text, key)

                if not matches:
                    if key == PagePattern.TIPS_KEY and "new TipsView" in text:
                        warnings.append(f"{rel}: 配列の引数がない TipsView のみのため tips は対象外")
                    continue

                if len(matches) > 1:
                    warnings.append(f"{rel}: {key} が {len(matches)} 個あるため最初の 1 つのみ使用")

                entry[key] = PagePattern.decode(key, matches[0].group("value"))

            if len(entry) > 1:
                pages.append(entry)

        return pages, warnings


    def format_pages(self, pages: list[dict]) -> str:
        """
        ページ一覧を、依頼書式（`"key" : value`、配列は 1 行）の JSON 文字列に整形する。

        `json.dump(indent=4)` では配列が 1 要素ごとに改行されて編集しづらいため、
        配列だけを 1 行にまとめる。出力は標準の JSON としてそのまま読み込める。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `pages` | `list[dict]` | `collect_pages` の戻り値の 0 番目 |

        ## 戻り値

        | 型 | 説明 |
        | --- | --- |
        | `str` | 末尾に改行を含む JSON 文字列。`pages` が空なら `[]` |
        """
        if not pages:
            return "[]\n"

        blocks = []
        for entry in pages:
            lines = []
            for key, value in entry.items():
                name = json.dumps(key, ensure_ascii=False)
                if isinstance(value, list):
                    body = "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in value) + "]"
                else:
                    body = json.dumps(value, ensure_ascii=False)
                lines.append(f"        {name} : {body}")
            blocks.append("    {\n" + ",\n".join(lines) + "\n    }")
        return "[\n" + ",\n".join(blocks) + "\n]\n"


    def run(self) -> int:
        """
        走査して JSON を書き出す。

        ## 戻り値

        | 値 | 意味 |
        | --- | --- |
        | `0` | 成功 |
        | `1` | 探索ディレクトリがない |
        """
        if not (self.root / self.html_dir).is_dir():
            print(f"エラー: {self.root / self.html_dir} がありません", file=sys.stderr)
            return 1

        pages, warnings = self.collect_pages()

        for message in warnings:
            print(f"警告: {message}", file=sys.stderr)

        with self.output.open("w", encoding="utf-8", newline="\n") as f:
            f.write(self.format_pages(pages))

        print(f"{len(pages)} ページ分を {self.output} に書き出しました")
        return 0


if __name__ == "__main__":
    sys.exit(ExportTips("../../").run())
