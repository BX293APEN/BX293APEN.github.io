#!/usr/bin/env python3
"""
# export_tips.py

`.html` 内の `new TipsView(tipsModel, "tips", "tips", [...])` を全て探し、
**ページごとのチップ一覧**を JSON ファイルに書き出す。

## 使い方

`config/tips/tiplist` で次のように実行する。

```
python export_tips.py
```

## 実行時の前提

| 項目 | 内容 |
| --- | --- |
| 実行ディレクトリ | `config/tips/tiplist`（どこから実行しても、スクリプトの場所を基準に解決する） |
| サイトのルート | スクリプトから `../../../`（`html/` と `model/` がある場所） |
| 探索ディレクトリ | ルート直下の `html` |
| 出力ファイル | スクリプトと同じディレクトリの `tips.json` |

## 出力形式

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
| `page` | `string` | ルートからの相対パス（区切りは `/`）。`index.html` が複数あるため、ファイル名だけでは一意にならない |
| `tipList` | `string[]` | `TipsView` の 4 番目の引数（`dispElement`）。HTML に書かれた順序のまま |

## 定数

| 名前 | 説明 |
| --- | --- |
| `TIPS_VIEW_PATTERN` | 4 番目の引数に配列を持つ `new TipsView(...)` にマッチする正規表現 |
| `TIP_ITEM_PATTERN` | 配列内の文字列リテラル（`"..."` または `'...'`）にマッチする正規表現 |

## 注意

- 4 番目の引数がない呼び出し（`html/tips/index.html` の `new TipsView(tipsModel, "index", "tipsList")`）は
  チップ一覧を持たないため**対象外**とし、警告を表示する
- `//` や `<!--` の後ろにある呼び出しはコメントアウトとみなして無視する
- 1 ファイルに複数の呼び出しがある場合は**最初の 1 つ**だけを使い、警告を表示する
"""

import json
import re
import sys
from pathlib import Path


class ExportTips:
    TIPS_VIEW_PATTERN = re.compile(
        r"""new\s+TipsView\s*\(
            \s*\w+\s*,                          # model
            \s*(?:"[^"]*"|'[^']*')\s*,          # html
            \s*(?:"[^"]*"|'[^']*')\s*,          # id
            \s*\[(?P<list>[^\]]*)\]             # dispElement
            \s*\)""",
        re.VERBOSE,
    )

    TIP_ITEM_PATTERN = re.compile(r"""\"([^\"]*)\"|'([^']*)'""")


    def __init__(self, root: str, html_dir: str = "html", output: str = "tips.json"):
        """
        出力先などの設定を保持する。相対パスはスクリプトの場所を基準に解決する。

        ## 引数

        | 名前 | 型 | 既定値 | 説明 |
        | --- | --- | --- | --- |
        | `root` | `str` | - | サイトのルートディレクトリ（例: `"../../../"`） |
        | `html_dir` | `str` | `"html"` | `root` からみた、HTML を探索するディレクトリ |
        | `output` | `str` | `"tips.json"` | 書き出す JSON ファイル |
        """
        base = Path(__file__).resolve().parent
        self.root = (base / root).resolve()
        self.html_dir = html_dir
        self.output = (base / output).resolve()


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


    def parse_tip_list(self, raw: str) -> list[str]:
        """
        配列リテラルの中身（`[` `]` の内側）からチップ ID を取り出す。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `raw` | `str` | 例: `"windowsTip", "linuxTip"` |

        ## 戻り値

        | 型 | 説明 |
        | --- | --- |
        | `list[str]` | チップ ID のリスト（記述順）。空配列なら `[]` |
        """
        return [
            double if double else single
            for double, single in self.TIP_ITEM_PATTERN.findall(raw)
        ]


    def collect_pages(self) -> tuple[list[dict], list[str]]:
        """
        `root/html_dir` 以下の全 `.html` を走査し、チップ一覧を集める。

        ## 引数

        なし（`__init__` で渡した設定を使う）。

        ## 戻り値

        `tuple[list[dict], list[str]]` の 2 要素タプル。

        | 位置 | 型 | 説明 |
        | --- | --- | --- |
        | 0 | `list[dict]` | `{"page": str, "tipList": list[str]}` のリスト（`page` の昇順） |
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

            matches = [
                m for m in self.TIPS_VIEW_PATTERN.finditer(text)
                if not self.is_commented_out(text, m.start())
            ]

            if not matches:
                if "new TipsView" in text:
                    warnings.append(f"{rel}: 配列の引数がない TipsView のみのため対象外")
                continue

            if len(matches) > 1:
                warnings.append(f"{rel}: TipsView が {len(matches)} 個あるため最初の 1 つのみ使用")

            pages.append({
                "page": rel,
                "tipList": self.parse_tip_list(matches[0].group("list")),
            })

        return pages, warnings


    def format_pages(self, pages: list[dict]) -> str:
        """
        ページ一覧を、依頼書式（`"page" : ...` / 1 行の `tipList`）の JSON 文字列に整形する。

        `json.dump(indent=4)` では `tipList` が 1 要素ごとに改行されて編集しづらいため、
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
            page = json.dumps(entry["page"], ensure_ascii=False)
            tips = ", ".join(json.dumps(tip, ensure_ascii=False) for tip in entry["tipList"])
            blocks.append(
                "    {\n"
                f'        "page" : {page},\n'
                f'        "tipList" : [{tips}]\n'
                "    }"
            )
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
    sys.exit(ExportTips("../../../").run())
