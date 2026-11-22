import re, html, os, sys


class TlsSrc2HTML:
    """
    ## tls_source.html を、バージョン選択付きの Bootstrap 用 HTML に変換するクラス

    元の表は rowspan で1バージョンが複数の `<tr>` に分かれている。
    `createTableSearch` は `<tr>` 単位で絞り込むため、1バージョン = 1行に組み替える。
    (脆弱性・攻撃手法・対策は、1つのセルの中の入れ子の表にまとめる)

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `_fill` | テンプレートの ID のプレースホルダを置き換える |
    | `parse` | 元の HTML をバージョンごとのデータに変換する |
    | `row_html` | 1バージョン分の `<tr>` を作る |
    | `listbox` | 上部のバージョン選択(`<select>`)を作る |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `save_html` | HTML の断片を書き出す |
    | `save_css` | CSS を書き出す |
    | `save_js` | JavaScript を書き出す |
    | `save` | 上の3つをまとめて書き出す |
    | `save_preview` | 単体で開ける確認用ページを書き出す(任意) |

    """

    CSS = "tls.css"            # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "tls.js"              # 出力する JavaScript のファイル名(確認用ページも読み込む)
    LIB = "attack-script.js"   # 確認用ページが先に読み込む共有スクリプト(createTableSearch の定義)

    # ## ID(ここだけで管理する。テンプレートの `__APP_ID__` などが、この値に置き換わる)
    #
    # | 定数 | プレースホルダ | 使われる場所 | 説明 |
    # |---|---|---|---|
    # | `APP_ID` | `__APP_ID__` | HTML・CSS・JS | 全体を囲む要素の ID(CSS はこの ID 配下にだけ適用される) |
    # | `INPUT_ID` | `__INPUT_ID__` | HTML・JS | キーワード入力欄 |
    # | `COUNT_ID` | `__COUNT_ID__` | HTML・JS | 件数の表示 |
    # | `CLEAR_ID` | `__CLEAR_ID__` | HTML・JS | 絞り込み解除ボタン |
    # | `SELECT_ID` | `__SELECT_ID__` | HTML・JS | バージョン選択(`<select>`) |
    #
    # 同じページに他の表(apptest など)を貼っても重複しないよう、`tls-` を付けている。
    APP_ID = "tls-app"
    INPUT_ID = "tls-q"
    COUNT_ID = "tls-count"
    CLEAR_ID = "tls-clear"
    SELECT_ID = "tls-version-select"
    ALL_LABEL = "全て"          # 先頭の選択肢(全バージョンを表示する。既定)

    # 元の表の列数(1バージョンの先頭行のセル数と、2行目以降のセル数)
    HEAD_CELLS = 11
    SUB_CELLS = 3

    TAG = re.compile(r"<(/?)(table|tr|td|th)\b([^>]*)>", re.I)

    PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TLS バージョン別まとめ(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="__LIB__"></script>
<script src="__JS__"></script>
</body>
</html>
"""

    def __init__(
        self,
        src,
        out=None,
        template="template/template.html",
        css_template="template/template.css",
        js_template="template/template.js"
    ):
        """
        ## 初期化

        相対パスは、このスクリプトのあるフォルダを基準に解決する。

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `src` | `str` | (必須) | 入力 HTML(`<table>` の断片) |
        | `out` | `str` または `None` | `tls.html` | 出力 HTML(`src` と同じフォルダ) |
        | `template` | `str` | `"template/template.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template/template.css"` | CSS の元ファイル |
        | `js_template` | `str` | `"template/template.js"` | JavaScript の元ファイル |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        self.out = self._path(out) if out else os.path.join(os.path.dirname(self.src), "tls.html")
        self.template = self._read(template)
        self.css_text = self._read(css_template)
        self.js_text = self._read(js_template)
        out_dir = os.path.dirname(self.out)
        self.out_css = os.path.join(out_dir, self.CSS)
        self.out_js = os.path.join(out_dir, self.JS)
        self.rows = 0

    def _path(self, p):
        """
        ## 相対パスをスクリプト基準の絶対パスにする

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `p` | `str` | パス |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 絶対パス(絶対パスで渡されたらそのまま) |
        """
        return p if os.path.isabs(p) else os.path.join(self.here, p)

    def _read(self, p):
        """
        ## ファイルを UTF-8 で読み込む(改行コードは LF にそろえる)

        元の HTML は CRLF のため、`mermaid-source` の中身なども含めて LF に統一する。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `p` | `str` | パス(相対パスはスクリプト基準) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | ファイルの内容(改行は LF) |
        """
        with open(self._path(p), encoding="utf-8", newline="") as f:
            return f.read().replace("\r\n", "\n")

    def _fill(self, text):
        """
        ## テンプレートの ID のプレースホルダを、ID の定数に置き換える

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `text` | `str` | テンプレート(HTML・CSS・JS) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | `__APP_ID__` `__INPUT_ID__` `__COUNT_ID__` `__CLEAR_ID__` `__SELECT_ID__` を置換したもの |
        """
        for key, value in (
            ("__APP_ID__", self.APP_ID),
            ("__INPUT_ID__", self.INPUT_ID),
            ("__COUNT_ID__", self.COUNT_ID),
            ("__CLEAR_ID__", self.CLEAR_ID),
            ("__SELECT_ID__", self.SELECT_ID),
        ):
            text = text.replace(key, value)
        return text

    @staticmethod
    def _write(path, text):
        """
        ## ファイルを UTF-8 で書き出す(改行コードはそのまま)

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `path` | `str` | 出力先パス |
        | `text` | `str` | 書き出す内容 |
        """
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    def _split_rows(self, text):
        """
        ## トップレベルの表の行・セルに分解する

        入れ子の表(`<table>` の中の `<tr>` `<td>`)は分解せず、セルの中身として元のまま残す。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `text` | `str` | トップレベルの `<tbody>` の中身 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行リスト | `list[list[tuple[str, str]]]` | 行 → セル(開始タグの属性, 中身) |
        """
        rows, row, depth, cell = [], None, 0, None
        for m in self.TAG.finditer(text):
            close, name, attrs = m.group(1), m.group(2).lower(), m.group(3)
            if name == "table":
                depth += -1 if close else 1
            elif depth:
                continue                        # 入れ子の表の中は無視する
            elif name == "tr":
                if close:
                    rows.append(row)
                    row = None
                else:
                    row = []
            elif close:
                row.append((cell[0], text[cell[1]:m.start()]))
            else:
                cell = (attrs, m.end())
        return rows

    def parse(self):
        """
        ## 元の HTML をバージョンごとのデータにする

        先頭行(11セル)でバージョンが始まり、続く3セルの行は同じバージョンの脆弱性として扱う。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | バージョンのリスト | `list[dict]` | 下表のキーを持つ辞書 |

        | キー | 型 | 説明 |
        |---|---|---|
        | `name` | `str` | バージョン名(タグ名・選択肢の値にもなる) |
        | `cells` | `list[tuple[str, str]]` | 先頭行の11セル(開始タグの属性, 中身) |
        | `vulns` | `list[list[tuple[str, str]]]` | 脆弱性・攻撃手法・対策の3セルの行 |
        """
        text = self.src_text = self._read(self.src)
        start = text.index("<tbody>", text.index("</thead>")) + len("<tbody>")
        body = text[start:text.rindex("</tbody>")]
        groups = []
        for r in self._split_rows(body):
            if len(r) == self.HEAD_CELLS:
                name = html.unescape(re.sub(r"<[^>]+>", "", r[0][1])).strip()
                groups.append({"name": name, "cells": r, "vulns": [r[6:9]]})
            elif len(r) == self.SUB_CELLS:
                groups[-1]["vulns"].append(r)
            else:
                raise ValueError(f"想定外のセル数です: {len(r)}")
        return groups

    @staticmethod
    def _cell(tag, attrs, inner, indent):
        """
        ## セルを組み立てる(中身は元のまま変更しない)

        `mermaid-source` の図の記述などはインデントも含めて維持する必要があるため、中身は再整形しない。
        `rowspan` は1バージョン = 1行にしたため取り除く。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `tag` | `str` | `td` または `th` |
        | `attrs` | `str` | 開始タグの属性 |
        | `inner` | `str` | 元の中身 |
        | `indent` | `int` | 開始タグのインデント(空白の数) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<td>…</td>` |
        """
        a = re.sub(r'\s*rowspan="\d+"', "", attrs).strip()
        return f"{' ' * indent}<{tag}{(' ' + a) if a else ''}>{inner}</{tag}>"

    def row_html(self, g):
        """
        ## 1バージョン分の `<tr>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `g` | `dict` | `parse` が返す1バージョン分のデータ |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr data-tags="バージョン名">…</tr>` |

        | 列 | 元の列 | 出力 |
        |---|---|---|
        | 1 | バージョン | `<th class="name">`(左に固定) |
        | 2〜6 | 変更点〜利用状況 | そのまま |
        | 7 | 脆弱性・攻撃手法・対策 | 入れ子の表(3列)にまとめる |
        | 8〜9 | 規格・公開年 | そのまま |
        """
        esc, cell, c = html.escape, self._cell, g["cells"]
        sub_rows = "\n".join(
            "                            <tr>\n"
            + "\n".join(cell("td", a, i, 32) for a, i in v)
            + "\n                            </tr>"
            for v in g["vulns"]
        )
        sub = (
            '                <table class="table table-sm table-bordered mb-0 align-top sub-vuln">\n'
            '                    <thead class="table-light">\n'
            "                        <tr><th>脆弱性</th><th>攻撃手法</th><th>対策</th></tr>\n"
            "                    </thead>\n"
            "                    <tbody>\n"
            f"{sub_rows}\n"
            "                    </tbody>\n"
            "                </table>"
        )
        out = [
            f'        <tr data-tags="{esc(g["name"])}">',
            f'            <th scope="row" class="name">{esc(g["name"])}</th>',
            *(cell("td", a, i, 12) for a, i in c[1:6]),
            f'            <td class="p-0">\n{sub}\n            </td>',
            *(cell("td", a, i, 12) for a, i in c[9:11]),
            "        </tr>",
        ]
        return "\n".join(out)

    def listbox(self, title, names):
        """
        ## 上部のリストボックス(バージョンを1つだけ選ぶ)を作る

        先頭に「全て」(`value` が空)を置き、これを既定にする。
        `option` の `value` がタグ名で、`self.SELECT_ID` は `template.js` の `selectId` にも同じ値が入る(`_fill`)ので、絞り込みに使われる。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | ラベル |
        | `names` | `list[str]` | バージョン名(この順に並ぶ) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<select>` を含む `<div>` |
        """
        esc = html.escape
        opts = "\n".join(f'                <option value="{esc(n)}">{esc(n)}</option>' for n in names)
        return (
            f"""\
<div class="pt-3 d-flex flex-wrap gap-1 align-items-center mb-1">
            <label class="me-1" for="{self.SELECT_ID}">{title}</label>
            <select id="{self.SELECT_ID}" class="form-select form-select-sm w-auto mw-100">
                <option value="" selected>{self.ALL_LABEL}</option>
{opts}
            </select>
        </div>"""
        )

    def build(self):
        """
        ## HTML 全体を組み立てる

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | テンプレートの `__ROWS__` と `__FILTERS__` を置換したもの |

        行数は `self.rows` に入る。
        """
        groups = self.parse()
        self.rows = len(groups)
        names = [g["name"] for g in groups]
        if len(set(names)) != len(names):
            raise ValueError(f"バージョン名が重複しています: {names}")
        body = "\n".join(self.row_html(g) for g in groups)
        return (self._fill(self.template)
                .replace("__ROWS__", body)
                .replace("__FILTERS__", self.listbox("バージョン", names)))

    def save_html(self):
        """
        ## HTML の断片を `self.out` に書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        out = self.build()
        self._write(self.out, out)
        print(self.rows, "rows,", len(out), "bytes ->", self.out)
        return self.out

    def save_css(self):
        """
        ## CSS を `self.out_css` に書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        self._write(self.out_css, self._fill(self.css_text))
        print("css ->", self.out_css)
        return self.out_css

    def save_js(self):
        """
        ## JavaScript を `self.out_js` に書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        self._write(self.out_js, self._fill(self.js_text))
        print("js ->", self.out_js)
        return self.out_js

    def save(self):
        """
        ## HTML・CSS・JavaScript の3ファイルをまとめて書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パスのリスト | `list[str]` | HTML・CSS・JavaScript の順 |
        """
        return [self.save_html(), self.save_css(), self.save_js()]

    def save_preview(self):
        """
        ## 確認用ページ(Bootstrap CDN + CSS + 共有スクリプト + JS 込み)を書き出す

        貼り付け先のページがなくても、ブラウザで開くだけで動作を確認できる。
        `self.out` の拡張子の前に `-preview` を付けたファイルに書き出す。
        `mermaid-source` の図は、サイト側のスクリプトがないため文字のまま表示される。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        path = f"{os.path.splitext(self.out)[0]}-preview.html"
        page = (self.PREVIEW.replace("__CSS__", self.CSS).replace("__LIB__", self.LIB).replace("__JS__", self.JS)
                .replace("__FRAGMENT__", self.build()))
        self._write(path, page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = TlsSrc2HTML("tls_source.html")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
