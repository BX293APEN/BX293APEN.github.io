import re, html, os, sys
from dataclasses import dataclass, field


@dataclass
class Block:
    """
    ## Markdown の1ブロック(見出し・段落・表)

    | メンバ | 型 | 既定値 | 説明 |
    |---|---|---|---|
    | `kind` | `str` | (必須) | `h1` `h2` `h3` `p` `table` のいずれか |
    | `line` | `int` | (必須) | Markdown 内の開始行番号(エラーメッセージ用) |
    | `text` | `str` | `""` | 見出し・段落の本文(段落は複数行を `<br>` でつなぐ) |
    | `header` | `list[str]` | `[]` | 表の見出し行のセル(`kind == "table"` のとき) |
    | `rows` | `list[tuple[int, list[str]]]` | `[]` | 表の本文行。(Markdown の行番号, セルのリスト) |
    """
    kind: str
    line: int
    text: str = ""
    header: list = field(default_factory=list)
    rows: list = field(default_factory=list)


class TexMD2HTML:
    """
    ## LaTeX 書き方一覧(Markdown)を、検索付きの Bootstrap 用 HTML・CSS・JavaScript に分割するクラス

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `plain` | 検索用の文字列(マークアップ除去済み)を作る |
    | `split_cells` | 表の1行を、セルのリストに分ける(`\\|` は区切りにしない) |
    | `inline` | セルや段落の Markdown 記法(`` ` `` `**` `<br>` `texClass`)を HTML にする |
    | `parse` | Markdown を `Block` のリストに変換する |
    | `section_tree` | 見出し(`##` `###`)から、タグの木を作り、タグ名の衝突を調べる |
    | `table_rows` | 表1つ分を、「説明・書き方・数式・備考」の行にする(見出し名と空の説明を検査する) |
    | `row_html` | 1行分の `<tr>`(説明 + タグ・書き方・数式・備考)を作る |
    | `group` | 上部のタグボタン群を、`##` ごとのブロックにして作る |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `save_html` | HTML の断片を書き出す |
    | `save_css` | CSS を書き出す |
    | `save_js` | JavaScript を書き出す |
    | `save` | 上の3つをまとめて書き出す |
    | `save_preview` | 単体で開ける確認用ページを書き出す(任意。MathJax も読み込む) |

    ## tex.md の書式

    | 要素 | 書き方 | 変換後 |
    |---|---|---|
    | タイトル | `# …`(1つだけ) | `<h1>`(テンプレートの `__TITLE__`) |
    | セクション | `## …` | 各行のタグ(バッジ・絞り込みボタン) |
    | 小セクション | `### …`(`##` の下) | 各行のタグ(親の `##` のタグも付く) |
    | 段落 | 見出しでも表でもない行(連続する行は1段落) | 表の上の注記(「`##` の名前: 本文」) |
    | 表 | `\\| … \\|` の行(2行目は `\\| --- \\|`) | **すべて1つの表**にまとめる(列は 説明・書き方・数式・備考)。本文の1行が、絞り込み・検索の1件 |
    | `` `…` `` | セル・段落の中 | `<code>`(中身はエスケープ) |
    | `**…**` | セル・段落の中 | `<strong>` |
    | `<div class="texClass">…</div>` | セルの中 | そのまま残す(中身の LaTeX はエスケープ。貼り付け先のページが数式にする) |
    | `<br>` | セル・段落の中 | そのまま残す |

    ## エラーにするもの

    | 条件 | 理由 |
    |---|---|
    | `##` より前に `###` や表がある | タグが決まらない |
    | 表の見出し行が `説明` `書き方` `数式` `備考` の4つ(順不同)でない | 列の役割が決まらない |
    | 表の本文行のセル数が、見出し行と違う | 列がずれる |
    | 説明が空の行がある | 何の行か分からなくなる(`説明` は必須。`書き方` `数式` `備考` は空でもよい) |
    | 表の2行目が `\\| --- \\|` の区切り行でない | 表として読めない |
    | 同じ名前のタグが2か所にある | 1つのタグが2か所に出て、どちらか分からなくなる |
    | `#` が2つ以上ある | タイトルが決まらない |
    """

    CSS = "tex_source.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "tex_source.js"     # 出力する JavaScript のファイル名(確認用ページも読み込む)

    # ## セル・段落の中の記法(`inline` が使う)
    #
    # | グループ名 | 記法 | 変換後 |
    # |---|---|---|
    # | `tex` | `<div class="texClass">…</div>` | 中身をエスケープして、同じ `<div>` に戻す |
    # | `code` | `` `…` ``(バッククォートの個数は可変) | `<code>` |
    # | `br` | `<br>` | そのまま |
    # | `bold` | `**…**` | `<strong>` |
    INLINE = re.compile(
        r'<div class="texClass">(?P<tex>.*?)</div>'
        r'|(?P<tick>`+)(?P<code>.+?)(?P=tick)'
        r'|(?P<br><br\s*/?>)'
        r'|\*\*(?P<bold>.+?)\*\*',
        re.S,
    )
    # ## 検索用の文字列を作るとき、取り除くもの(HTML タグ・バッククォート・強調の `**`)
    STRIP = re.compile(r"<[^>]+>|`|\*\*")
    TABLE_SEP = re.compile(r"\|\s*:?-{3,}")   # 表の2行目(区切り行)

    # ## 表の列の役割(`table_rows` が使う)
    #
    # 見出し名は、すべての表で同じ4つを使う。列の並びは自由(見出し名で役割を決める)。
    #
    # | 見出し名 | 役割 | 出力先 | 空にできるか |
    # |---|---|---|---|
    # | `説明` | `desc` | 1列目(`th.name`)。何の記法か・どんな症状かを書く | できない |
    # | `書き方` | `code` | 「書き方」列 | できる |
    # | `数式` | `math` | 「数式」列(`<div class="texClass">…</div>`) | できる |
    # | `備考` | `note` | 「備考」列。補正のポイント・使い方の注意を書く | できる |
    ROLE = {"説明": "desc", "書き方": "code", "数式": "math", "備考": "note"}

    # ## 出力の改行コード
    #
    # | 値 | 説明 |
    # |---|---|
    # | `"\r\n"` | CRLF。`auth` と同じ(テンプレートの改行もここでそろえる) |
    NEWLINE = "\r\n"

    def __init__(
        self,
        src,
        out=None,
        template="template/template.html",
        css_template="template/template.css",
        js_template="template/template.js",
    ):
        """
        ## 初期化

        相対パスは、このスクリプトのあるフォルダを基準に解決する。

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `src` | `str` | (必須) | 入力 Markdown |
        | `out` | `str` または `None` | `{src の名前}_source.html` | 出力 HTML |
        | `template` | `str` | `"template/template.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template/template.css"` | CSS の元ファイル |
        | `js_template` | `str` | `"template/template.js"` | JavaScript の元ファイル |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        stem = os.path.splitext(self.src)[0]
        self.out = self._path(out) if out else f"{stem}_source.html"
        self.template = self._read(template)
        self.css_text = self._read(css_template)
        self.js_text = self._read(js_template)
        out_dir = os.path.dirname(self.out)
        self.out_css = os.path.join(out_dir, self.CSS)
        self.out_js = os.path.join(out_dir, self.JS)
        self.rows = 0
        self.title = ""
        self.preview_page = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
<script>
// 確認用: .texClass の中だけを MathJax で数式にする(コード表示の `<code>` は数式にしない)
window.MathJax = { options: { ignoreHtmlClass: '.*', processHtmlClass: 'texClass' } };
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-svg.js" async></script>
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="__JS__"></script>
</body>
</html>
"""

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
        ## ファイルを UTF-8 で読み込む(改行コードを `\\n` にそろえる)

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `p` | `str` | パス(相対パスはスクリプト基準) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | ファイルの内容(改行は `\\n`。書き出すときに `NEWLINE` へ戻す) |
        """
        with open(self._path(p), encoding="utf-8-sig", newline=None) as f:  # BOM 付きも読める。改行は \n になる
            return f.read()

    def _write(self, path, text):
        """
        ## ファイルを UTF-8 で書き出す(改行コードは `NEWLINE` にそろえる)

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `path` | `str` | 出力先パス |
        | `text` | `str` | 書き出す内容(改行は `\\n` でも `\\r\\n` でもよい) |
        """
        text = re.sub(r"\r?\n", self.NEWLINE, text)
        with open(path, "w", encoding="utf-8", newline="") as f:  # 改行コードを変換しない
            f.write(text)

    @classmethod
    def plain(cls, s):
        """
        ## 検索用の文字列を返す(マークアップを除去して空白をそろえる)

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `s` | `str` | セルの Markdown(`<div class="texClass">…</div>` や `` ` `` を含んでよい) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | HTML タグ・`` ` ``・`**` を除いて、空白を1つにしたもの |
        """
        return re.sub(r"\s+", " ", cls.STRIP.sub(" ", s)).strip()

    @staticmethod
    def split_cells(line):
        """
        ## 表の1行をセルに分ける

        セル内の `\\|`(エスケープした縦線)は区切りにせず、`|` に戻す(GitHub の Markdown と同じ)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `line` | `str` | `\\|` で始まり `\\|` で終わる1行 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | セルのリスト | `list[str]` | 前後の空白は除去済み |
        """
        parts = re.split(r"(?<!\\)\|", line.strip())
        return [p.strip().replace("\\|", "|") for p in parts[1:-1]]

    @classmethod
    def inline(cls, s):
        """
        ## セル・段落の中の Markdown 記法を HTML にする

        上の `INLINE` に当てはまらない部分は、すべてエスケープする(`<` `>` `&` が文字として残る)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `s` | `str` | セル・段落の Markdown |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<code>` `<strong>` `<br>` `<div class="texClass">` に変換したもの |
        """
        esc = lambda t: html.escape(t, quote=False)
        out, pos = [], 0
        for m in cls.INLINE.finditer(s):
            out.append(esc(s[pos:m.start()]))
            if m.group("tex") is not None:
                out.append(f'<div class="texClass">{esc(m.group("tex"))}</div>')
            elif m.group("code") is not None:
                out.append(f"<code>{esc(m.group('code').strip())}</code>")
            elif m.group("br") is not None:
                out.append("<br>")
            else:
                out.append(f"<strong>{cls.inline(m.group('bold'))}</strong>")
            pos = m.end()
        out.append(esc(s[pos:]))
        return "".join(out)

    def parse(self):
        """
        ## Markdown を `Block` のリストにする

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | ブロックのリスト | `list[Block]` | 出てきた順 |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 表の2行目が区切り行でない / 本文行のセル数が見出し行と違う |
        """
        lines = self._read(self.src).split("\n")
        blocks, para, i = [], [], 0

        def flush_para():
            if para:
                blocks.append(Block("p", para[0][0], text="<br>".join(t for _, t in para)))
                para.clear()

        while i < len(lines):
            ln, no = lines[i], i + 1
            m = re.match(r"(#{1,3})\s+(.*\S)\s*$", ln)
            if m:
                flush_para()
                blocks.append(Block(f"h{len(m.group(1))}", no, text=m.group(2)))
                i += 1
            elif ln.startswith("|"):
                flush_para()
                header = self.split_cells(ln)
                if i + 1 >= len(lines) or not self.TABLE_SEP.match(lines[i + 1]):
                    raise ValueError(f"tex.md {no}行目: 表の2行目が区切り行(| --- |)ではありません")
                blk = Block("table", no, header=header)
                i += 2
                while i < len(lines) and lines[i].startswith("|"):
                    cells = self.split_cells(lines[i])
                    if len(cells) != len(header):
                        raise ValueError(
                            f"tex.md {i + 1}行目: セル数 {len(cells)} が、見出し行の {len(header)} と違います"
                        )
                    blk.rows.append((i + 1, cells))
                    i += 1
                blocks.append(blk)
            elif ln.strip():
                para.append((no, ln.strip()))
                i += 1
            else:
                flush_para()
                i += 1
        flush_para()
        return blocks

    def section_tree(self, blocks):
        """
        ## 見出しから、タグの木を作る

        `##` の名前と、その下の `###` の名前が、タグになる。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `blocks` | `list[Block]` | `parse` の結果 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 木 | `dict[str, list[str]]` | `##` の名前 → その下の `###` の名前。どちらも出てきた順 |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | `#` が2つ以上ある |
        | `ValueError` | `##` より前に `###` や表がある |
        | `ValueError` | 同じ名前のタグが、2か所以上にある |
        """
        tree, seen, titles, top = {}, set(), 0, None
        for b in blocks:
            if b.kind == "h1":
                titles += 1
                if titles > 1:
                    raise ValueError(f"tex.md {b.line}行目: # が2つ以上あります")
            elif b.kind == "h2":
                top = b.text
                if top in seen:
                    raise ValueError(f"tex.md {b.line}行目: タグ {top!r} が重複しています")
                seen.add(top)
                tree[top] = []
            elif b.kind in ("h3", "table") and top is None:
                raise ValueError(f"tex.md {b.line}行目: ## より前に ### または表があります")
            elif b.kind == "h3":
                if b.text in seen:
                    raise ValueError(f"tex.md {b.line}行目: タグ {b.text!r} が重複しています")
                seen.add(b.text)
                tree[top].append(b.text)
        return tree

    def table_rows(self, blk):
        """
        ## 表1つ分を、「説明・書き方・数式・備考」の行のリストにする

        列の役割は `ROLE` で決める(見出し名で決めるので、列の並びは自由)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `blk` | `Block` | `kind == "table"` のブロック |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行のリスト | `list[tuple[str, str, str, str]]` | (説明, 書き方, 数式, 備考)。説明以外は、なければ空文字列 |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | `ROLE` にない見出しがある / 同じ役割の列が2つ以上ある / 4つの役割がそろっていない |
        | `ValueError` | 説明が空の行がある |
        """
        pos = {}
        for i, h in enumerate(blk.header):
            if h not in self.ROLE:
                raise ValueError(f"tex.md {blk.line}行目: 見出し {h!r} の役割が ROLE にありません")
            role = self.ROLE[h]
            if role in pos:
                raise ValueError(f"tex.md {blk.line}行目: {h!r} の列が2つ以上あります")
            pos[role] = i
        missing = [h for h, r in self.ROLE.items() if r not in pos]
        if missing:
            raise ValueError(f"tex.md {blk.line}行目: 見出しに {missing} がありません")
        out = []
        for no, cells in blk.rows:
            desc, code, math, note = (cells[pos[r]] for r in ("desc", "code", "math", "note"))
            if not desc:
                raise ValueError(f"tex.md {no}行目: 説明が空です")
            out.append((desc, code, math, note))
        return out

    def row_html(self, desc, code, math, note, tags):
        """
        ## 1行分の `<tr>` を作る

        1列目(`th.name`)に、説明とタグ(バッジ)を入れる。
        絞り込み用のタグ(`data-tags`)と、検索用の文字列(`data-text`)は、行の属性に持たせる
        (数式の描画後の DOM は使わない)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `desc` | `str` | 説明の Markdown |
        | `code` | `str` | 書き方の Markdown(なければ空文字列) |
        | `math` | `str` | 数式のセル(`<div class="texClass">…</div>`。なければ空文字列) |
        | `note` | `str` | 備考の Markdown(なければ空文字列) |
        | `tags` | `list[str]` | この行のタグ(`##` と、あれば `###`) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr>…</tr>`(セルが空のときは `—` を出す) |
        """
        esc = html.escape
        fix = lambda t: t if t else '<span class="text-body-tertiary">—</span>'
        badges = "".join(
            f'<button type="button" class="tag badge text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags
        )
        text = " ".join(dict.fromkeys(self.plain(x) for x in [desc, code, math, note] + tags if x))
        return (
            f'                <tr data-tags="{esc("|".join(tags))}" data-text="{esc(text)}">\n'
            f'                    <th scope="row" class="name">{self.inline(desc)}<div class="tags">{badges}</div></th>\n'
            f"                    <td>{fix(self.inline(code))}</td>\n"
            f"                    <td>{fix(self.inline(math))}</td>\n"
            f"                    <td>{fix(self.inline(note))}</td>\n"
            f"                </tr>"
        )

    def group(self, title, tree, count):
        """
        ## 上部のタグボタン群を、`##` ごとのブロックにして作る

        1行目が `##` のボタン(太字)、改行して2行目に、その下の `###` のボタンを並べる。
        `##` を選ぶと、その下の `###` の行もすべて残る(行が両方のタグを持つため)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(ボタン群の見出し) |
        | `tree` | `dict[str, list[str]]` | `section_tree` の結果 |
        | `count` | `dict[str, int]` | タグ名 → 該当する行の数 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | 系統名 + ブロックの並び。表の行が1つもないタグは出さない。何も出せなければ空文字列 |
        """
        esc = html.escape
        btn = lambda t, extra="": (
            f'<button type="button" class="btn btn-sm btn-outline-primary{extra}" data-tag="{esc(t)}">'
            f'{esc(t)} <span class="badge text-bg-light">{count[t]}</span></button>'
        )
        blocks = []
        for top, subs in tree.items():
            if count.get(top, 0) < 1:
                continue
            subs = [t for t in subs if count.get(t, 0) >= 1]
            blocks.append(
                f'<div class="d-inline-block align-top me-3 mb-2">'
                f'{btn(top, " fw-bold")}{"<br>" if subs else ""}'
                f'{" ".join(btn(t) for t in subs)}'
                f"</div>"
            )
        if not blocks:
            return ""
        return (
            f'<div class="pt-3">\n'
            f'            <div class="me-1">{esc(title)}</div>\n'
            f"            <div>\n                {chr(10).join(blocks)}\n            </div>\n"
            f"        </div>"
        )

    def build(self):
        """
        ## HTML 全体を組み立てる

        表は1つにまとめる(見出しごとの表には分けない)。`##` `###` の見出しは、各行のタグになる。
        段落は、表の上の注記(`__NOTES__`)に、「`##` の名前: 本文」で並べる。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | テンプレートの `__TITLE__` `__FILTERS__` `__NOTES__` `__ROWS__` を置換したもの(改行は `\\n`) |

        次の属性に結果が入る。

        | 属性 | 型 | 説明 |
        |---|---|---|
        | `self.title` | `str` | `#` のタイトル(なければ空文字列) |
        | `self.rows` | `int` | 表の行の合計 |
        | `self.count` | `dict[str, int]` | タグ名 → 該当する行の数 |
        | `self.tree` | `dict[str, list[str]]` | タグの木(`section_tree` の結果) |
        """
        blocks = self.parse()
        tree = self.section_tree(blocks)

        rows, notes, count = [], [], {}
        top = sub = None          # いま開いている `##` / `###` の名前
        for b in blocks:
            if b.kind == "h1":
                self.title = b.text
            elif b.kind == "h2":
                top, sub = b.text, None
            elif b.kind == "h3":
                sub = b.text
            elif b.kind == "p":
                label = f"<b>{html.escape(top)}</b>: " if top else ""
                notes.append(f'<div class="small text-body-secondary mb-1">{label}{self.inline(b.text)}</div>')
            else:
                tags = [top] + ([sub] if sub else [])
                for desc, code, math, note in self.table_rows(b):
                    rows.append(self.row_html(desc, code, math, note, tags))
                    for t in tags:
                        count[t] = count.get(t, 0) + 1

        self.rows = len(rows)
        self.count, self.tree = count, tree
        values = {
            "__TITLE__": html.escape(self.title),
            "__FILTERS__": self.group("セクション", tree, count),
            "__NOTES__": "\n    ".join(notes),
            "__ROWS__": "\n".join(rows),
        }
        return re.sub("|".join(values), lambda m: values[m.group(0)], self.template)

    def save_html(self):
        """
        ## HTML の断片を `self.out` に書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        out = self.build()
        self._write(self.out, out)
        print(self.rows, "rows,", len(out), "chars ->", self.out)
        return self.out

    def save_css(self):
        """
        ## CSS を `self.out_css` に書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        self._write(self.out_css, self.css_text)
        print("css ->", self.out_css)
        return self.out_css

    def save_js(self):
        """
        ## JavaScript を `self.out_js` に書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        self._write(self.out_js, self.js_text)
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
        ## 確認用ページ(Bootstrap CDN + CSS + JS + MathJax CDN 込み)を書き出す

        貼り付け先のページがなくても、ブラウザで開くだけで動作を確認できる。
        `self.out` の拡張子の前に `-preview` を付けたファイルに書き出す。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        path = f"{os.path.splitext(self.out)[0]}-preview.html"
        fragment = self.build()
        page = (self.preview_page.replace("__TITLE__", html.escape(self.title))
                .replace("__CSS__", self.CSS).replace("__JS__", self.JS)
                .replace("__FRAGMENT__", fragment))
        self._write(path, page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = TexMD2HTML("tex.md")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
