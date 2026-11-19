#!/usr/bin/env python3
"""
# page_pattern.py

`export_config.py` / `import_config.py` が共通で使う、**HTML 内の探索パターン定義**。

エクスポートとインポートで同じパターンを使うため、1 か所にまとめている。
扱う項目を増やしたいときは、`PagePattern.SEARCH_PATTERN` に 1 行足すだけでよい。

## 扱えるキー

| キー | 対象 | JSON 上の型 |
| --- | --- | --- |
| `tips` | `new TipsView(tipsModel, "tips", "tips", [...])` の `[...]` | `string[]` |
| `property:<名前>` | `<meta property="<名前>" content="...">` の `content` | `string` |

`property:` から始まるキーは、`SEARCH_PATTERN` に載っていなくても
`PagePattern.get_pattern` がその場でパターンを作る（インポートで使える）。
ただし**エクスポートの対象になるのは `SEARCH_PATTERN` のキーだけ**。

## 定数

| 名前 | 説明 |
| --- | --- |
| `TIPS_VIEW_PATTERN` | 4 番目の引数に配列を持つ `new TipsView(...)` にマッチする正規表現 |
| `PagePattern.SEARCH_PATTERN` | キー → 正規表現の辞書。正規表現には必ず名前付きグループ `value` を含める |
| `PagePattern.TIP_ITEM_PATTERN` | 配列内の文字列リテラル（`"..."` または `'...'`）にマッチする正規表現 |
| `PagePattern.TIPS_KEY` | チップ一覧のキー名（`"tips"`） |
| `PagePattern.PROPERTY_PREFIX` | メタタグのキーの接頭辞（`"property:"`） |
| `PagePattern.LEGACY_KEYS` | 旧キー → 現行キーの対応表（旧 JSON の読み込み用） |

## 注意

- `<meta>` は `property` 属性が **`content` 属性より前**にある書き方だけを対象とする
- `//` や `<!--` の後ろにある呼び出しはコメントアウトとみなして無視する
- メタタグの値は HTML エスケープを外した文字列として扱う（`&amp;` ⇄ `&`）
"""

import html
import json
import re


# `value` グループは、置き換え対象の範囲（`[` `]` や `"` の内側）を表す
TIPS_VIEW_PATTERN = re.compile(
    r"""new\s+TipsView\s*\(
        \s*\w+\s*,                          # model
        \s*(?:"[^"]*"|'[^']*')\s*,          # html
        \s*(?:"[^"]*"|'[^']*')\s*,          # id
        \s*(?P<value>\[[^\]]*\])            # dispElement（`[` `]` を含む）
        \s*\)""",
    re.VERBOSE,
)


def meta_pattern(prop: str) -> re.Pattern:
    """
    `<meta property="<prop>" content="...">` にマッチする正規表現を作る。

    ## 引数

    | 名前 | 型 | 説明 |
    | --- | --- | --- |
    | `prop` | `str` | `property` 属性の値（例: `"og:title"`） |

    ## 戻り値

    | 型 | 説明 |
    | --- | --- |
    | `re.Pattern` | `content` の中身を名前付きグループ `value` に持つ正規表現 |
    """
    return re.compile(
        rf"""<meta\s+property\s*=\s*"{re.escape(prop)}"\s+content\s*=\s*"(?P<value>[^"]*)"[^>]*>"""
    )


class PagePattern:
    TIPS_KEY = "tips"
    PROPERTY_PREFIX = "property:"

    SEARCH_PATTERN: dict[str, re.Pattern] = {
        "tips": TIPS_VIEW_PATTERN,
        "property:og:title": meta_pattern("og:title"),
        "property:og:url": meta_pattern("og:url"),
        "property:og:image": meta_pattern("og:image"),
        "property:og:type": meta_pattern("og:type"),
        "property:og:site_name": meta_pattern("og:site_name"),
        "property:og:description": meta_pattern("og:description"),
    }

    TIP_ITEM_PATTERN = re.compile(r"""\"([^\"]*)\"|'([^']*)'""")

    LEGACY_KEYS = {"tipList": "tips"}


    @classmethod
    def normalize_key(cls, key: str) -> str:
        """
        旧キーを現行キーに読み替える。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `key` | `str` | JSON に書かれていたキー |

        ## 戻り値

        | 型 | 説明 |
        | --- | --- |
        | `str` | `LEGACY_KEYS` にあれば現行キー、なければ `key` のまま |
        """
        return cls.LEGACY_KEYS.get(key, key)


    @classmethod
    def get_pattern(cls, key: str) -> re.Pattern | None:
        """
        キーに対応する正規表現を返す。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `key` | `str` | `"tips"` または `"property:<名前>"` |

        ## 戻り値

        | 型 | 条件 | 内容 |
        | --- | --- | --- |
        | `re.Pattern` | `SEARCH_PATTERN` にある | 登録済みの正規表現 |
        | `re.Pattern` | `property:` で始まり、名前が空でない | その場で作った正規表現 |
        | `None` | 上記以外 | 未対応のキー |
        """
        if key in cls.SEARCH_PATTERN:
            return cls.SEARCH_PATTERN[key]
        if key.startswith(cls.PROPERTY_PREFIX) and len(key) > len(cls.PROPERTY_PREFIX):
            return meta_pattern(key[len(cls.PROPERTY_PREFIX):])
        return None


    @classmethod
    def is_list_key(cls, key: str) -> bool:
        """
        値が文字列の配列になるキーかを判定する。

        ## 戻り値

        | 型 | 値 | 意味 |
        | --- | --- | --- |
        | `bool` | `True` | 値は `list[str]`（`tips`） |
        | `bool` | `False` | 値は `str`（`property:*`） |
        """
        return key == cls.TIPS_KEY


    @staticmethod
    def is_commented_out(text: str, start: int) -> bool:
        """
        マッチ位置が、同じ行の `//` または `<!--` より後ろにあるかを判定する。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `text` | `str` | HTML 全文 |
        | `start` | `int` | マッチの開始位置 |

        ## 戻り値

        | 型 | 値 | 意味 |
        | --- | --- | --- |
        | `bool` | `True` | コメントアウトされている |
        | `bool` | `False` | 有効なコード |
        """
        line_start = text.rfind("\n", 0, start) + 1
        prefix = text[line_start:start]
        return "//" in prefix or "<!--" in prefix


    @classmethod
    def find_matches(cls, text: str, key: str) -> list[re.Match]:
        """
        コメントアウトされていないマッチを、出現順に全て返す。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `text` | `str` | HTML 全文（改行コードは変換せず、そのまま渡すこと） |
        | `key` | `str` | 探すキー。未対応のキーは `ValueError` |

        ## 戻り値

        | 型 | 説明 |
        | --- | --- |
        | `list[re.Match]` | マッチのリスト。見つからなければ `[]` |
        """
        pattern = cls.get_pattern(key)
        if pattern is None:
            raise ValueError(f"未対応のキー: {key}")
        return [
            m for m in pattern.finditer(text)
            if not cls.is_commented_out(text, m.start())
        ]


    @classmethod
    def decode(cls, key: str, raw: str) -> list[str] | str:
        """
        HTML から取り出した文字列を、JSON に書く値へ変換する。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `key` | `str` | キー |
        | `raw` | `str` | マッチの `value` グループ |

        ## 戻り値

        | 型 | 条件 | 内容 |
        | --- | --- | --- |
        | `list[str]` | `tips` | チップ ID のリスト（記述順）。空配列なら `[]` |
        | `str` | `property:*` | HTML エスケープを外した文字列 |
        """
        if cls.is_list_key(key):
            return [
                double if double else single
                for double, single in cls.TIP_ITEM_PATTERN.findall(raw)
            ]
        return html.unescape(raw)


    @classmethod
    def encode(cls, key: str, value: list[str] | str) -> str:
        """
        JSON の値を、HTML に書き込む文字列へ変換する（`decode` の逆）。

        ## 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `key` | `str` | キー |
        | `value` | `list[str]` または `str` | JSON の値（型は `is_list_key` に従う） |

        ## 戻り値

        | 型 | 条件 | 内容 |
        | --- | --- | --- |
        | `str` | `tips` | `["a", "b"]` 形式の配列リテラル |
        | `str` | `property:*` | `&` `<` `>` `"` をエスケープした文字列 |
        """
        if cls.is_list_key(key):
            return "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in value) + "]"
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
