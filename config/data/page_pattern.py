r"""
# page_pattern.py

`export_config.py` / `import_config.py` が共通で使う、**HTML 内の探索パターン**の読み込み処理。

パターンは同じディレクトリの `page_pattern.json` に**完成した正規表現として**書く。
Python 側では正規表現を組み立てない（読み込んでコンパイルするだけ）。
扱う項目を増やしたいときは、`page_pattern.json` に 1 行足すだけでよい（Python は触らない）。

## `page_pattern.json` の形式

キー → 正規表現（文字列）のオブジェクト。

```json
{
    "tips" : "new\\s+TipsView\\s*\\( ... (?P<value>\\[[^\\]]*\\]) ... \\)",
    "property:og:title" : "<meta\\s+property\\s*=\\s*\"og:title\"\\s+content\\s*=\\s*\"(?P<value>[^\"]*)\"[^>]*>"
}
```

| 項目 | 内容 |
| --- | --- |
| キー | 設定ファイル（`config.json`）に書き出すキー名。`page` 以外なら自由（慣例: メタタグは `property:<名前>`） |
| 値 | 正規表現の文字列。**空文字は不可**（空のままにしたキーはエラーになる） |
| 順序 | 書いた順が、エクスポートの出力順になる |

JSON の文字列なので、正規表現の `\` は `\\`、`"` は `\"` と書く。

## 正規表現の条件

| 条件 | 内容 |
| --- | --- |
| 名前付きグループ `value` | 必須。置き換え対象の範囲を表す（`tips` は `[` `]` を含む。メタタグは引用符の内側） |
| フラグ | 指定できない（必要なら `(?s)` など、パターン先頭のインラインフラグを使う） |
| 不備がある場合 | `import page_pattern` の時点でメッセージを表示して終了コード `1` で終了する（正規表現として不正、`value` がない、空文字、など） |

## 値の型

| キー | `config.json` 上の型 | 変換 |
| --- | --- | --- |
| `tips` | `string[]` | `value` を `"..."` / `'...'` の列として分解する（`TIP_ITEM_PATTERN`） |
| それ以外 | `string` | HTML エスケープを外した文字列（`&amp;` ⇄ `&`） |

配列になるのは `tips` だけで、これは `PagePattern.TIPS_KEY` でコードに固定している。

## 定数

| 名前 | 説明 |
| --- | --- |
| `PATTERN_FILE` | パターンファイルのパス（`page_pattern.py` と同じディレクトリの `page_pattern.json`） |
| `PagePattern.SEARCH_PATTERN` | キー → コンパイル済み正規表現の辞書（`page_pattern.json` から読み込み、記述順） |
| `PagePattern.TIP_ITEM_PATTERN` | 配列内の文字列リテラル（`"..."` または `'...'`）にマッチする正規表現 |
| `PagePattern.TIPS_KEY` | 値が配列になるキー名（`"tips"`） |
| `PagePattern.LEGACY_KEYS` | 旧キー → 現行キーの対応表（旧 JSON の読み込み用） |

## 注意

- `//` や `<!--` の後ろにある呼び出しはコメントアウトとみなして無視する
- `page_pattern.json` にないキーは、エクスポートもインポートもできない（インポートでは未対応のキーとしてエラー）
"""

import html
import json
import re
from pathlib import Path


PATTERN_FILE = Path(__file__).resolve().parent / "page_pattern.json"


class PatternFileError(Exception):
    """`page_pattern.json` の内容に不備があるときに送出する。"""


def load_pattern_file(path: Path) -> dict[str, re.Pattern]:
    """
    `page_pattern.json` を読み込み、各正規表現をコンパイルして返す。

    ## 引数

    | 名前 | 型 | 説明 |
    | --- | --- | --- |
    | `path` | `Path` | パターンファイル |

    ## 戻り値

    | 型 | 説明 |
    | --- | --- |
    | `dict[str, re.Pattern]` | キー → コンパイル済み正規表現（記述順） |

    ## 例外

    | 型 | 条件 |
    | --- | --- |
    | `PatternFileError` | ファイルが読めない / JSON が不正 / 空のオブジェクト / 値が空文字または文字列でない / 正規表現として不正 / 名前付きグループ `value` がない |
    """
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise PatternFileError(f"{path} を読み込めません: {e}") from e

    if not isinstance(data, dict) or not data:
        raise PatternFileError("トップレベルは空でないオブジェクトである必要があります")

    patterns: dict[str, re.Pattern] = {}
    for key, source in data.items():
        if key == "page":
            raise PatternFileError("キー 'page' はページのパスに使われるため使えません")
        if not isinstance(source, str) or not source:
            raise PatternFileError(f"{key}: 正規表現は空でない文字列で書いてください")
        try:
            pattern = re.compile(source)
        except re.error as e:
            raise PatternFileError(f"{key}: 正規表現が不正です: {e}") from e
        if "value" not in pattern.groupindex:
            raise PatternFileError(f"{key}: 名前付きグループ (?P<value>...) がありません")
        patterns[key] = pattern

    return patterns


# 不備があれば、トレースバックではなくメッセージだけを表示して終了コード 1 で終了する
try:
    _SEARCH_PATTERN = load_pattern_file(PATTERN_FILE)
except PatternFileError as e:
    raise SystemExit(f"エラー: {PATTERN_FILE.name}: {e}")


class PagePattern:
    TIPS_KEY = "tips"

    SEARCH_PATTERN: dict[str, re.Pattern] = _SEARCH_PATTERN

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
        | `key` | `str` | `page_pattern.json` のキー |

        ## 戻り値

        | 型 | 条件 | 内容 |
        | --- | --- | --- |
        | `re.Pattern` | `SEARCH_PATTERN` にある | `page_pattern.json` に書かれた正規表現 |
        | `None` | ない | 未対応のキー |
        """
        return cls.SEARCH_PATTERN.get(key)


    @classmethod
    def is_list_key(cls, key: str) -> bool:
        """
        値が文字列の配列になるキーかを判定する。

        ## 戻り値

        | 型 | 値 | 意味 |
        | --- | --- | --- |
        | `bool` | `True` | 値は `list[str]`（`tips`） |
        | `bool` | `False` | 値は `str` |
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
        | `str` | それ以外 | HTML エスケープを外した文字列 |
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
        | `str` | それ以外 | `&` `<` `>` `"` をエスケープした文字列 |
        """
        if cls.is_list_key(key):
            return "[" + ", ".join(json.dumps(v, ensure_ascii=False) for v in value) + "]"
        return (
            value.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )
