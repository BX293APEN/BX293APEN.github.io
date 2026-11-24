import re, html, os, sys


class CryptMd2HTML:
    """
    ## 整形済みの `crypt_normalized.md` を、タグ絞り込み付きの Bootstrap 用 HTML に変換するクラス

    `normalize.py` が作る md(全セクション同じ8列の Markdown 表)を読み、1項目 = 1行の `<tr>` にする。
    プルダウンは使わず、行に付けたタグ(`data-tags`)と、タグのボタン(`data-tag`)だけで絞り込む。

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `_fill` | テンプレートの ID のプレースホルダを置き換える |
    | `parse` | md をセクション・行に変換する |
    | `tags_of` | 1行のタグ(分野・分類・CRYPTREC種別・量子耐性)を決める |
    | `_qr_tag` | 量子耐性のタグを決める(`tags_of` から呼ぶ) |
    | `_qr_split` | 量子耐性列の補足を、CRYPTREC種別用(PQCリスト関連)と備考用に分ける(`row_html` から呼ぶ) |
    | `row_html` | 1項目分の `<tr>` を作る |
    | `filters` | 上部のタグのボタン群を作る |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `save_html` / `save_css` / `save_js` / `save` | 各ファイルを書き出す |
    | `save_preview` | 単体で開ける確認用ページを書き出す(任意) |
    """

    CSS = "crypt.css"            # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "crypt.js"              # 出力する JavaScript のファイル名(確認用ページも読み込む)
    LIB = "preview-lib.js"       # 確認用ページが先に読み込むスクリプト(本番の共有スクリプトの `createTableSearch` と同じもの。本番では配布しない)

    # ## ID(ここだけで管理する。テンプレートの `__APP_ID__` などが、この値に置き換わる)
    #
    # | 定数 | プレースホルダ | 使われる場所 | 説明 |
    # |---|---|---|---|
    # | `APP_ID` | `__APP_ID__` | HTML・CSS・JS | 全体を囲む要素の ID(CSS はこの ID 配下にだけ適用される) |
    # | `INPUT_ID` | `__INPUT_ID__` | HTML・JS | キーワード入力欄 |
    # | `COUNT_ID` | `__COUNT_ID__` | HTML・JS | 件数の表示 |
    # | `CLEAR_ID` | `__CLEAR_ID__` | HTML・JS | 絞り込み解除ボタン |
    APP_ID = "crypt-app"
    INPUT_ID = "crypt-q"
    COUNT_ID = "crypt-count"
    CLEAR_ID = "crypt-clear"

    # `data-tags` の区切り文字(タグ名には使わない)。共有スクリプト(`createTableSearch`)が `|` で分割する
    TAG_SEP = "|"

    # ## CRYPTREC種別のタグ(先頭一致で判定。上から順に調べる)
    #
    # | 先頭の文字 | タグ |
    # |---|---|
    # | `電子政府推奨暗号` | `電子政府推奨暗号` |
    # | `推奨候補暗号` | `推奨候補暗号` |
    # | `運用監視暗号` | `運用監視暗号` |
    # | `リスト外` `CRYPTREC` `対象外` | `リスト外・対象外` |
    # | `-` | `未掲載` |
    CRYPTREC = (
        ("電子政府推奨暗号", "電子政府推奨暗号"),
        ("推奨候補暗号", "推奨候補暗号"),
        ("運用監視暗号", "運用監視暗号"),
        ("リスト外", "リスト外・対象外"),
        ("CRYPTREC", "リスト外・対象外"),
        ("対象外", "リスト外・対象外"),
        ("-", "未掲載"),
    )

    # ## 量子耐性のタグ(「量子耐性」列の先頭の記号で判定する)
    #
    # 判定は上から順に行い、最初に当てはまったものにする。
    #
    # | 順 | タグ | 条件 |
    # |---|---|---|
    # | 1 | `量子耐性○(量子暗号)` | 記号が `○` で、名称・分類に `QR_QUANTUM_WORDS` のどれかを含む(計算量でなく物理法則・情報理論に基づく方式) |
    # | 2 | `量子耐性○(PQC)` | 記号が `○`(上に当てはまらないもの) |
    # | 3 | `量子耐性△` | 記号が `△` |
    # | 4 | `量子耐性×` | 記号が `✖`(タグの表記は `×`) |
    # | 5 | `量子耐性-` | 上のどれでもない |
    #
    # | 定数 | 型 | 説明 |
    # |---|---|---|
    # | `QR_MARK` | `dict[str, str]` | 記号 → タグ(`○` は量子暗号に当てはまらない場合のタグ) |
    # | `QR_QUANTUM` | `str` | 量子暗号のタグ |
    # | `QR_QUANTUM_WORDS` | `tuple[str, ...]` | 量子暗号とみなす語(名称・分類に含まれるか調べる) |
    # | `QR_NONE` | `str` | 記号が無いときのタグ |
    QR_MARK = {"○": "量子耐性○(PQC)", "△": "量子耐性△", "✖": "量子耐性×"}
    QR_QUANTUM = "量子耐性○(量子暗号)"
    QR_QUANTUM_WORDS = ("量子鍵配送", "ワンタイムパッド")
    QR_NONE = "量子耐性-"

    # ## PFS のタグ(備考の `<b>PFS</b><br>記号` で判定する。PFS の項目が無い行(`-`)にはタグを付けない)
    #
    # | 定数 | 型 | 説明 |
    # |---|---|---|
    # | `PFS_MARK` | `dict[str, str]` | 記号 → タグ |
    # | `PQC_LIST_RE` | `str` | 量子耐性列の補足のうち、CRYPTREC種別に移すもの(PQCリスト関連の行) |
    PFS_MARK = {"○": "PFS○", "✖": "PFS×"}
    PQC_LIST_RE = r"PQCリスト|Category|ハッシュ長"

    # ## 上部のボタンのグループ
    #
    # | キー | 見出し | 絞り込みの意味 |
    # |---|---|---|
    # | `field` | 分野 | md の `### 見出し` |
    # | `kind` | 分類 | md の「分類」列の先頭の1行(表の列としては出さず、タグだけで表す) |
    # | `cryptrec` | CRYPTREC種別 | 上の `CRYPTREC` |
    # | `qr` | 量子耐性 | 上の `QR_MARK` など |
    # | `pfs` | PFS | 上の `PFS_MARK`(鍵共有だけ) |
    GROUPS = (("field", "分野"), ("kind", "分類"), ("cryptrec", "CRYPTREC種別"), ("qr", "量子耐性"), ("pfs", "PFS"))

    # ## ボタンの並び順
    #
    # 指定したグループは、ここに書いた順に並べる(書いていないタグは最後に出てきた順)。
    # 指定しないグループは、md に出てきた順になる。
    #
    # | キー | 並び順 |
    # |---|---|
    # | `qr` | `○(量子暗号)` → `○(PQC)` → `△` → `×` |
    # | `pfs` | `PFS○` → `PFS×` |
    ORDER = {"qr": ("量子耐性○(量子暗号)", "量子耐性○(PQC)", "量子耐性△", "量子耐性×", "量子耐性-"), "pfs": ("PFS○", "PFS×")}

    PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>暗号一覧(確認用)</title>
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

    def __init__(self, src, out=None, template="template/template.html",
                 css_template="template/template.css", js_template="template/template.js"):
        """
        ## 初期化

        相対パスは、このスクリプトのあるフォルダを基準に解決する。

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `src` | `str` | (必須) | 整形済みの md |
        | `out` | `str` または `None` | `crypt.html` | 出力 HTML(`src` と同じフォルダ) |
        | `template` | `str` | `"template/template.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template/template.css"` | CSS の元ファイル |
        | `js_template` | `str` | `"template/template.js"` | JavaScript の元ファイル |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        self.out = self._path(out) if out else os.path.join(os.path.dirname(self.src), "crypt.html")
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
        | 文字列 | `str` | `__APP_ID__` `__INPUT_ID__` `__COUNT_ID__` `__CLEAR_ID__` を置換したもの |
        """
        for key, value in (("__APP_ID__", self.APP_ID), ("__INPUT_ID__", self.INPUT_ID),
                           ("__COUNT_ID__", self.COUNT_ID), ("__CLEAR_ID__", self.CLEAR_ID)):
            text = text.replace(key, value)
        return text

    @staticmethod
    def _write(path, text):
        """
        ## ファイルを UTF-8 で書き出す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `path` | `str` | 出力先パス |
        | `text` | `str` | 書き出す内容 |
        """
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    def parse(self):
        """
        ## md をセクション・行に変換する

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | セクションのリスト | `list[tuple[str, list[list[str]]]]` | (見出し, 行のリスト)。行は8セル |

        8列でない行があれば `ValueError` にする(`normalize.py` の出力以外を渡したときの検出用)。
        """
        text = self._read(self.src)
        parts = re.split(r"^### (.+)$", text, flags=re.M)
        sections = []
        for i in range(1, len(parts), 2):
            rows = []
            for line in parts[i + 1].split("\n"):
                if not line.startswith("|") or re.match(r"^\|[\s:|-]+\|$", line):
                    continue
                cells = [c.strip() for c in line.strip()[1:-1].split(" | ")]
                if len(cells) != 8:
                    raise ValueError(f"{parts[i]}: 8列ではありません({len(cells)}列): {cells[0]}")
                rows.append(cells)
            sections.append((parts[i].strip(), rows[1:]))      # 先頭は見出し行
        return sections

    @staticmethod
    def _first(cell):
        """
        ## セルの先頭の1行(`<br>` の前)から、タグ・括弧書き・空白を除く

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cell` | `str` | セルの中身 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | 先頭の1行(空白と `,` を除いたもの) |
        """
        s = re.sub(r"<[^>]+>", "", re.split(r"<br>|<ul>", cell)[0])
        return re.sub(r"[\s,]", "", html.unescape(s))

    def tags_of(self, section, cells):
        """
        ## 1行のタグを決める

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `section` | `str` | 分野(`### 見出し`) |
        | `cells` | `list[str]` | 8セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タグの辞書 | `dict[str, str]` | `GROUPS` のキー → タグ名 |
        """
        cr = self._first(cells[2])
        tags = {
            "field": section,
            "kind": self._first(cells[1]),
            "cryptrec": next((t for p, t in self.CRYPTREC if cr.startswith(p)), "リスト外・対象外"),
            "qr": self._qr_tag(cells),
        }
        m = re.search(r"<b>PFS</b><br>([○✖])", cells[7])
        if m:
            tags["pfs"] = self.PFS_MARK[m.group(1)]
        return tags

    def _qr_tag(self, cells):
        """
        ## 量子耐性のタグを決める

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 8セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タグ名 | `str` | `QR_QUANTUM` / `QR_MARK` のどれか。記号が無ければ `QR_NONE` |

        複数の記号が並ぶセル(`△<br>✖<br>△` など)は、先頭の記号で判定する。
        """
        mark = self._first(cells[3])[:1]
        if mark == "○" and any(w in cells[0] + cells[1] for w in self.QR_QUANTUM_WORDS):
            return self.QR_QUANTUM
        return self.QR_MARK.get(mark, self.QR_NONE)

    def _qr_split(self, tags, cells):
        """
        ## 「量子耐性」列の補足を、CRYPTREC種別に移すものと備考に移すものに分ける

        量子耐性の列は表に出さない(○△✖はタグで表す)。タグにならない補足だけを移す。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `tags` | `dict[str, str]` | `tags_of` の結果 |
        | `cells` | `list[str]` | 8セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | (CRYPTREC種別に足す HTML, 備考に足す HTML) | `tuple[str, str]` | どちらも補足が無ければ空文字 |

        | セルの形 | 移し先 |
        |---|---|
        | `○` だけ | (なし) |
        | 量子暗号(タグで説明済み) | (なし。`物理法則に基づくため…` などの説明はタグと重複するため) |
        | `○<br>(PQCリスト : …)` `(Category 4)` など(`PQC_LIST_RE` に当てはまる行) | CRYPTREC種別 |
        | `○<br>192bit以上` など(上以外の2行目以降) | 備考(`<b>量子耐性</b><br>…`) |
        | 名称と同じ行数の記号の並び(`△<br>✖<br>△`) | 備考。名称の各行に対応づけて `名称 : 記号` |
        """
        if tags["qr"] == self.QR_QUANTUM:
            return "", ""
        lines, names = cells[3].split("<br>"), cells[0].split("<br>")
        if len(lines) > 1 and len(lines) == len(names) and all(len(l) == 1 for l in lines):
            return "", "<b>量子耐性</b><br>" + "<br>".join(f"{n} : {l}" for n, l in zip(names, lines))
        rest = lines[1:]
        pqc = [l for l in rest if re.search(self.PQC_LIST_RE, l)]
        other = [l for l in rest if l not in pqc]
        return "<br>".join(pqc), (f"<b>量子耐性</b><br>{'<br>'.join(other)}" if other else "")

    def row_html(self, tags, cells):
        """
        ## 1項目分の `<tr>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `tags` | `dict[str, str]` | `tags_of` の結果 |
        | `cells` | `list[str]` | 8セル(中身は md のまま HTML として出す) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr data-tags="…">…</tr>` |

        | 列 | 出力 |
        |---|---|
        | 1 | `<th class="name">`(左に固定)。名称の下にタグのバッジを並べる |
        | 2〜5 | `<td>`(概要・CRYPTREC種別・基盤・鍵長)。概要には備考を続けて入れ、備考の項目(`オプション` など。`PFS` はタグにするので出さない)ごとに `<div class="note">` で囲んで前に空行分の余白を付ける |
        | (出さない) | 分類(`cells[1]`)・量子耐性(`cells[3]`)。タグ(`kind` `qr`)で表すため、列としては出さない。量子耐性の補足だけ備考に足す(`_qr_note`) |
        """
        esc = html.escape
        badges = "".join(
            f'<button type="button" class="tag badge rounded-pill text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags.values()
        )
        cryptrec, note = self._qr_split(tags, cells)
        if cryptrec:
            cells = [*cells[:2], cryptrec if cells[2] == "-" else f"{cells[2]}<br>{cryptrec}", *cells[3:]]
        if note:
            cells = [*cells[:7], note if cells[7] == "-" else f"{cells[7]}<br>{note}"]
        items = [] if cells[7] == "-" else re.split(r"<br>(?=<b>)", cells[7])     # 備考は `<b>項目</b>…` の並び
        items = [i for i in items if not i.startswith("<b>PFS</b>")]              # PFS はタグで表すので項目としては出さない
        overview = cells[6] + "".join(f'<div class="note">{i}</div>' for i in items)   # 項目の前に空行(余白)を入れて概要と区別する
        out = [
            f'        <tr data-tags="{esc(self.TAG_SEP.join(tags.values()))}">',
            f'            <th scope="row" class="name">{cells[0]}<div class="tags">{badges}</div></th>',
            *(f"            <td>{c}</td>" for c in (overview, cells[2], cells[4], cells[5])),
            "        </tr>",
        ]
        return "\n".join(out)

    def filters(self, used):
        """
        ## 上部のタグのボタン群を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `used` | `dict[str, dict[str, int]]` | グループのキー → {使われているタグ: 該当件数}(出てきた順) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | グループごとの `<div>`(見出し + `data-tag` のボタンと該当件数のバッジ。並びは `ORDER` に従う) |
        """
        esc, out = html.escape, []
        for key, title in self.GROUPS:
            order = self.ORDER.get(key, ())
            tags = sorted(used[key], key=lambda t: order.index(t) if t in order else len(order))   # sorted は安定なので、指定なしは出てきた順のまま
            btns = "\n".join(
                f'                <button type="button" class="btn btn-sm btn-outline-secondary" data-tag="{esc(t)}">{esc(t)} <span class="badge text-bg-light">{used[key][t]}</span></button>'
                for t in tags
            )
            out.append(
                f"""\
<div class="d-flex flex-wrap gap-1 align-items-center mb-1 pb-3">
            <div class="me-1">{title}</div>
            <div>
{btns}
            </div>
        </div>"""
            )
        return "\n        ".join(out)

    def build(self):
        """
        ## HTML 全体を組み立てる

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | テンプレートの `__ROWS__` と `__FILTERS__` を置換したもの |

        行数は `self.rows` に入る。
        """
        used = {k: {} for k, _ in self.GROUPS}
        rows = []
        for title, items in self.parse():
            for cells in items:
                tags = self.tags_of(title, cells)
                for k, t in tags.items():
                    used[k][t] = used[k].get(t, 0) + 1
                rows.append(self.row_html(tags, cells))
        self.rows = len(rows)
        return (self._fill(self.template)
                .replace("__ROWS__", "\n".join(rows))
                .replace("__FILTERS__", self.filters(used)))

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
        ## 確認用ページ(Bootstrap CDN + CSS + スクリプト込み)を書き出す

        `self.out` の拡張子の前に `-preview` を付けたファイルに書き出す。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        path = f"{os.path.splitext(self.out)[0]}-preview.html"
        page = (self.PREVIEW.replace("__CSS__", self.CSS).replace("__LIB__", self.LIB)
                .replace("__JS__", self.JS).replace("__FRAGMENT__", self.build()))
        self._write(path, page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = CryptMd2HTML("crypt_normalized.md")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
