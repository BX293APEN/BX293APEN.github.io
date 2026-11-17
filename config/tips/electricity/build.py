import re, html, os, sys


class ElectricityMD2HTML:
    """
    ## 電気工事士まとめ(Markdown の表)を、タグ検索付きの Bootstrap 用 HTML・CSS・JS に変換するクラス

    1つの Markdown(`md/<stem>.md`)から、1つの HTML 断片・1つの CSS・1つの JS を作る。
    分野(配線器具・工具・電線 など)は `分類` 列の大分類で表し、補助表は説明欄などのセルに `<table>` としてネストする。
    別の Markdown を `md/` に足せば、ID を変えて別の表として出力できる。

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み・ID の決定 |
    | `parse` | Markdown を、見出し・メイン表・補足ブロックに分解する |
    | `split_cells` | 表の1行を、セルのリストに分ける(`\\\\|` は区切りにしない) |
    | `category_paths` | 「分類」列を、分類の経路(`大分類 > 分類`)のリストにする |
    | `class_tree` | 全行の経路から、大分類ごとの分類の一覧(木)を作り、タグ名の衝突を調べる |
    | `md_inline` | セル内の Markdown の強調(`**…**`・`` `…` ``)を HTML にする |
    | `fit_tables` | セルの中の `<table>` を、列幅・見出しの固定が崩れないように整える |
    | `cell_html` | 表の1セルの内容を HTML にする(空欄は `—`) |
    | `head_html` | メイン表の見出し行の `<th>` を作る |
    | `row_html` | メイン表の1行分の `<tr>` を作る |
    | `class_group` | 上部の分類ボタン群を、大分類ごとのブロックにして作る |
    | `static_html` | メイン表の後ろの補足ブロック(小見出し・補足表・注記)を HTML にする |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `save_html` | HTML の断片を書き出す |
    | `save_css` | CSS を書き出す(`template.css` の ID を置き換える) |
    | `save_js` | JavaScript を書き出す(`template.js` の引数を置き換える) |
    | `save` | 上の3つをまとめて書き出す |
    | `save_preview` | この分野だけの確認用ページを書き出す(任意) |
    
    ## 出力ファイルと ID

    `<stem>` は Markdown のファイル名(拡張子なし。例 : `electricity`)。

    | 出力 | ファイル名 | 元 | 置き換えるもの |
    |---|---|---|---|
    | HTML 断片 | `<stem>.html` | `template.html` | `__FILTERS__` `__HEAD__` `__ROWS__` `__EXTRA__` と、下の ID |
    | CSS | `<stem>-style.css` | `template.css` | **ID だけ**(`__APP_ID__`) |
    | JS | `<stem>-script.js` | `template.js` | **引数だけ**(下の4つ) |

    | プレースホルダ | 置き換え後(例 : `electricity`) | 使われる場所 |
    |---|---|---|
    | `__APP_ID__` | `electricity-app` | HTML の最外枠 `id` / CSS のセレクタ / JS の `appId` |
    | `__INPUT_ID__` | `electricity-q` | HTML の検索欄 `id` / JS の `inputId` |
    | `__COUNT_ID__` | `electricity-count` | HTML の件数表示 `id` / JS の `countId` |
    | `__CLEAR_ID__` | `electricity-clear` | HTML の解除ボタン `id` / JS の `clearId` |

    ID は Markdown のファイル名で変わるので、1つのページに複数の表を貼り付けても、CSS・JS が互いに干渉しない。

    ## Markdown の書式(`md/electricity-<key>.md`)

    | 要素 | 書き方 | 変換後 |
    |---|---|---|
    | `## 見出し` | 先頭に1つ | 確認用ページの見出しにだけ使う(断片には出さない。貼り付け先の見出しに任せる) |
    | **最初の表** | 先頭列は名前 | **メイン表**。検索・タグ絞り込み・見出しと先頭列の固定の対象 |
    | `分類` 列 | メイン表の列のうち、見出しが `分類` のもの | **表示しない**。経路の全要素を、タグにする(なければタグなし)。分野は大分類で表す |
    | セル内の `<table>` | 補助表を、関係する行の説明欄などに書く | `fit_tables` で、列幅・見出しの固定が崩れないように整える |
    | `### 見出し` | メイン表の後ろ | 補足の小見出し |
    | 2つ目以降の表 | 〃 | 補足表。検索・固定の対象外(Bootstrap の小さい表) |
    | `> 文` | 〃 | 注記(小さい灰色の文字) |

    ## 分類列の決まり

    | 決まり | 内容 |
    |---|---|
    | 経路 | `大分類 > 分類` のように ` > ` で区切る。左ほど大きい分類。1段だけでも可 |
    | 複数の経路 | 1行に複数あるときは `<br>` で区切る(例 : `遮断器・開閉器<br>電動機・動力`) |
    | タグ | 経路の全要素がタグになる。大分類を選ぶと、その下の分類の行もすべて残る |
    | 重複 | 同じ名前を、別の大分類の下に重ねるとエラー |
    | 空 | `分類` 列があるのに空の行はエラー |

    ## セル内の表の幅

    CSS は表に `width: max-content` を指定しているため、セル内の表の長い文が折り返されず、列が極端に広がる
    (その列の全行が同じ幅になる)。CSS を変えずに済むよう、`<table>` を含むセルは、中身を
    `<div style="width:NEST_WIDTH">` に入れて、その幅の中で折り返す。

    ## 小さい列の決まり

    `NARROW_COLS` の見出しの列(略号・記号・図など、中身が短い列)は、CSS の最小幅(17rem)を、
    HTML 側の `style` で狭める(CSS を変えずに済ませるため)。
    """

    CATEGORY_COL = "分類"                           # タグの元になる列の見出し
    CLASS_SEP = ">"                                 # 「分類」列の経路の区切り(`大分類 > 分類`)
    FILTER_TITLE = "分類"                           # 上部のボタン群の系統名
    NARROW_COLS = ("略号", "記号・図")              # 最小幅を狭める列の見出し
    NARROW_STYLE = "min-width:8rem"                 # 狭める列に足す `style`
    NEST_WIDTH = "38rem"                            # セル内に `<table>` があるとき、中身を入れる箱の幅(下の説明を参照)

    PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css" rel="stylesheet">
__CSS__
</head>
<body class="container-fluid">
__BODY__
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<script>
// 確認用: `$...$` の TeX を KaTeX で描画する(本番ページ側に数式の仕組みがある場合は不要)
if (window.renderMathInElement) {
    renderMathInElement(document.body, { delimiters: [{ left: '$', right: '$', display: false }] });
}
</script>
<script src="__SUPPORT__"></script>
__JS__
</body>
</html>
"""

    def __init__(
        self,
        src,
        out_dir="out",
        template="template/template.html",
        css_template="template/template.css",
        js_template="template/template.js",
    ):
        """
        ## 初期化

        相対パスは、このスクリプトのあるフォルダを基準に解決する。

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `src` | `str` | (必須) | 入力 Markdown(例 : `md/electricity-wiring.md`) |
        | `out_dir` | `str` | `"out"` | 出力フォルダ(なければ作る) |
        | `template` | `str` | `"template/template.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template/template.css"` | CSS の元ファイル |
        | `js_template` | `str` | `"template/template.js"` | JavaScript の元ファイル |

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.stem` | `str` | Markdown のファイル名(拡張子なし) |
        | `self.app_id` `self.input_id` `self.count_id` `self.clear_id` | `str` | 分野ごとの ID(クラスの説明の表を参照) |
        | `self.out` `self.out_css` `self.out_js` | `str` | 出力先の HTML・CSS・JS のパス |
        | `self.rows` | `int` | メイン表の行数(`build` のあとに入る) |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        self.stem = os.path.splitext(os.path.basename(self.src))[0]
        self.app_id = f"{self.stem}-app"
        self.input_id = f"{self.stem}-q"
        self.count_id = f"{self.stem}-count"
        self.clear_id = f"{self.stem}-clear"
        self.out_dir = self._path(out_dir)
        os.makedirs(self.out_dir, exist_ok=True)
        self.out = os.path.join(self.out_dir, f"{self.stem}.html")
        self.out_css = os.path.join(self.out_dir, f"{self.stem}-style.css")
        self.out_js = os.path.join(self.out_dir, f"{self.stem}-script.js")
        self.template = self._read(template)
        self.css_text = self._read(css_template)
        self.js_text = self._read(js_template)
        self.rows = 0
        self.title = ""

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
        ## ファイルを UTF-8 で読み込む(改行コードはそのまま)

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `p` | `str` | パス(相対パスはスクリプト基準) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | ファイルの内容 |
        """
        with open(self._path(p), encoding="utf-8", newline="") as f:  # 改行コードを変換しない
            return f.read()

    @staticmethod
    def _write(path, text):
        """
        ## ファイルを UTF-8 で書き出す(改行コードはそのまま)

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `path` | `str` | 出力先パス |
        | `text` | `str` | 書き出す内容 |
        """
        with open(path, "w", encoding="utf-8", newline="") as f:  # 改行コードを変換しない
            f.write(text)

    @staticmethod
    def plain(s):
        """
        ## HTMLタグを除去した文字列を返す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `s` | `str` | HTML断片 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | タグ除去・空白正規化済み |
        """
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()

    @staticmethod
    def split_cells(line):
        """
        ## 表の1行をセルに分ける

        セル内の `\\|`(エスケープした縦線)は区切りにせず、`|` に戻す。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `line` | `str` | `|` で始まり `|` で終わる1行 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | セルのリスト | `list[str]` | 前後の空白は除去済み |
        """
        parts = re.split(r"(?<!\\)\|", line.strip())
        return [p.strip().replace("\\|", "|") for p in parts[1:-1]]

    def parse(self):
        """
        ## Markdown を、見出し・メイン表・補足ブロックに分解する

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | `## ` の見出し(なければ空文字) |
        | `main` | `tuple[list[str], list[tuple[int, list[str]]]]` | メイン表の(見出しのセル, [(Markdown の行番号, セル)]) |
        | `blocks` | `list[tuple]` | メイン表の後ろのブロック(下の表) |

        | ブロックの種類 | タプルの形 |
        |---|---|
        | 小見出し(`### `) | `("h3", 文字列)` |
        | 補足表 | `("table", 見出しのセル, [セル, ...])` |
        | 注記(`> `) | `("note", 文字列)`(連続する行は1つにまとめる) |
        | 本文 | `("p", 文字列)` |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 表がない / 表の列数が見出しと合わない |
        """
        with open(self.src, encoding="utf-8") as f:
            lines = f.read().splitlines()
        title, main, blocks = "", None, []
        i = 0
        while i < len(lines):
            ln = lines[i]
            if ln.startswith("|"):
                start = i
                tbl = []
                while i < len(lines) and lines[i].startswith("|"):
                    tbl.append((i + 1, lines[i]))
                    i += 1
                head = self.split_cells(tbl[0][1])
                body = []
                for no, t in tbl[1:]:
                    if re.match(r"\|\s*-{3}", t):
                        continue
                    c = self.split_cells(t)
                    if len(c) != len(head):
                        raise ValueError(f"{self.stem}.md {no}行目: 列数 {len(c)} が見出しの列数 {len(head)} と合いません")
                    body.append((no, c))
                if main is None:
                    main = (head, body)
                else:
                    blocks.append(("table", head, [c for _, c in body]))
                continue
            if ln.startswith("### "):
                blocks.append(("h3", ln[4:].strip()))
            elif ln.startswith("## "):
                title = ln[3:].strip()
            elif ln.startswith(">"):
                text = [ln.lstrip("> ").strip()]
                while i + 1 < len(lines) and lines[i + 1].startswith(">"):
                    i += 1
                    text.append(lines[i].lstrip("> ").strip())
                blocks.append(("note", " ".join(text)))
            elif ln.strip():
                blocks.append(("p", ln.strip()))
            i += 1
        if main is None:
            raise ValueError(f"{self.stem}.md: 表がありません")
        return title, main, blocks

    def category_paths(self, name, cell):
        """
        ## 「分類」列を、分類の経路のリストにする

        経路の中は `>` で区切り、左ほど大きい分類になる。1行に複数の経路を書くときは `<br>` で区切る。

        | 元のセル | 経路 |
        |---|---|
        | `スイッチ` | `[["スイッチ"]]` |
        | `遮断器・開閉器<br>電動機・動力` | `[["遮断器・開閉器"], ["電動機・動力"]]` |
        | `A > B<br>C > D` | `[["A", "B"], ["C", "D"]]` |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `name` | `str` | 名前(エラーメッセージ用) |
        | `cell` | `str` | 「分類」列のセル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 経路のリスト | `list[list[str]]` | 1つの経路は、大きい分類から順の分類名のリスト |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 分類が空、または経路の中に空の名前がある |
        """
        paths = []
        for part in re.split(r"<br\s*/?>", cell):
            s = self.plain(part)
            if not s:
                continue
            path = [w.strip() for w in s.split(self.CLASS_SEP)]
            if not all(path):
                raise ValueError(f"{name}: 「分類」列の経路 {s!r} に空の名前があります")
            paths.append(path)
        if not paths:
            raise ValueError(f"{name}: 「分類」列が空です")
        return paths

    @staticmethod
    def class_tree(all_paths):
        """
        ## 全行の経路から、大分類ごとの分類の一覧(木)を作る

        同じ名前が別の大分類の下に重なっているとエラーにする(1つのタグが2か所に出て、どちらか分からなくなるため)。
        1件だけでも上部のボタンに出すため、件数による足切りはしない。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `all_paths` | `list[list[list[str]]]` | 行ごとの経路のリスト(`category_paths` の結果) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 木 | `dict[str, list[str]]` | 大分類名 → その下の分類名。どちらも初めて出てきた順 |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 同じ名前が、2つの大分類の下に使われている |
        """
        tree, owner = {}, {}
        for paths in all_paths:
            for path in paths:
                top = path[0]
                tree.setdefault(top, [])
                for t in path:
                    if owner.setdefault(t, top) != top:
                        raise ValueError(f"分類タグ {t!r} が、{owner[t]!r} と {top!r} の両方に使われています")
                tree[top] += [t for t in path[1:] if t not in tree[top]]
        return tree

    @staticmethod
    def md_inline(s):
        """
        ## セル内の Markdown の強調を HTML にする

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `s` | `str` | セルの内容 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `**x**` → `<strong>x</strong>` / `` `x` `` → `<code>x</code>` |
        """
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        return re.sub(r"`([^`]+)`", r"<code>\1</code>", s)

    @staticmethod
    def _with_style(m, css):
        """
        ## `<th>` `<td>` の開始タグに `style` を足す(`fit_tables` の部品)

        すでに `style` があれば、その先頭に足す。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `m` | `re.Match` | `<th …>` / `<td …>` にマッチした結果。1番目のグループが属性部分 |
        | `css` | `str` | 足す CSS(`;` 区切り) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 開始タグ | `str` | `style` を足した開始タグ |
        """
        tag = m.group(0)[1:3]
        attrs = m.group(1) or ""
        if 'style="' in attrs:
            attrs = attrs.replace('style="', f'style="{css};', 1)
        else:
            attrs += f' style="{css}"'
        return f"<{tag}{attrs}>"

    def fit_tables(self, s):
        """
        ## セルの中の `<table>` を整える

        CSS(`template.css`)は、表の全セルに「最小幅17rem」と、見出しの固定(sticky)を指定している。
        そのままだと、セル内の表が横に広がり、見出しが上の固定見出しに重なる。
        CSS を変えずに済むよう、セル内の表にだけ HTML 側で指定を足す。

        | 対象 | 足すもの | 理由 |
        |---|---|---|
        | `<table>` | `class="table table-sm table-bordered mb-2"` と `style="width:auto;min-width:0"` | Bootstrap の表にし、CSS の `max-content` を解除する |
        | `<th>` | `style="position:static;min-width:0"` | 見出しの固定を外し、最小幅を解除する |
        | `<td>` | `style="min-width:0"` | 最小幅を解除する |
        | 8文字以下の短い `<th>` `<td>`(タグを含まないもの) | `white-space:nowrap` | 幅が足りないとき、「A種」が「A / 種」に割れないようにする |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `s` | `str` | セルの HTML |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | 整えた HTML |
        """
        s = s.replace("<table>", '<table class="table table-sm table-bordered mb-2" style="width:auto;min-width:0">')
        s = re.sub(r"<(t[hd])(\s[^>]*)?>([^<]{1,8})</\1>",
                   lambda m: self._with_style(re.match(r"<t[hd](\s[^>]*)?>", m.group(0)), "white-space:nowrap")
                   + m.group(3) + f"</{m.group(1)}>", s)  # 短いセルは折り返さない
        s = re.sub(r"<th(\s[^>]*)?>", lambda m: self._with_style(m, "position:static;min-width:0"), s)
        s = re.sub(r"<td(\s[^>]*)?>", lambda m: self._with_style(m, "min-width:0"), s)
        return s

    def cell_html(self, s, narrow=False):
        """
        ## メイン表の1セル(`<td>`)を作る

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `s` | `str` | (必須) | セルの内容(HTML 可) |
        | `narrow` | `bool` | `False` | `True` なら最小幅を狭める(`NARROW_COLS` の列) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<td>…</td>`。空欄・`-` は灰色の `—` にする。`<table>` を含むときは中身を `NEST_WIDTH` 幅の `<div>` に入れる |
        """
        body = self.fit_tables(self.md_inline(s)) if s not in ("-", "") else '<span class="text-body-tertiary">—</span>'
        if "<table" in body:  # セル内の表の長い文が列を押し広げないよう、幅を固定する
            body = f'<div style="width:{self.NEST_WIDTH}">{body}</div>'
        style = f' style="{self.NARROW_STYLE}"' if narrow else ""
        return f"<td{style}>{body}</td>"

    def head_html(self, head):
        """
        ## メイン表の見出し行の `<th>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `head` | `list[str]` | 表示する列の見出し(`分類` 列を除いたもの) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | 先頭列は `class="name"`(左に固定)。`NARROW_COLS` の列は最小幅を狭める |
        """
        ths = []
        for i, h in enumerate(head):
            if i == 0:
                ths.append(f'<th class="name">{html.escape(h)}</th>')
            elif h in self.NARROW_COLS:
                ths.append(f'<th style="{self.NARROW_STYLE}">{html.escape(h)}</th>')
            else:
                ths.append(f"<th>{html.escape(h)}</th>")
        return "".join(ths)

    def row_html(self, head, cells, tags):
        """
        ## メイン表の1行分の `<tr>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `head` | `list[str]` | 表示する列の見出し(`head_html` と同じ) |
        | `cells` | `list[str]` | 表示するセル(`分類` 列を除いたもの) |
        | `tags` | `list[str]` | この行のタグ(なければ空) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr data-tags="…">…</tr>`。タグがなくても `data-tags` は付ける(JS の `rowSelector` が使うため) |
        """
        esc = html.escape
        badges = "".join(
            f'<button type="button" class="tag badge text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags
        )
        tag_div = f'<div class="tags">{badges}</div>' if badges else ""
        tds = "\n                    ".join(
            self.cell_html(c, narrow=head[i + 1] in self.NARROW_COLS) for i, c in enumerate(cells[1:])
        )
        return (
            f"""\
                <tr data-tags="{esc("|".join(tags))}">
                    <th scope="row" class="name">{self.md_inline(cells[0])}{tag_div}</th>
                    {tds}
                </tr>"""
        )

    def class_group(self, title, tree, count):
        """
        ## 上部の分類ボタン群を、大分類ごとのブロックにして作る

        系統名を1行目に置き、その下に大分類ごとのブロック(`pb-4`)を縦に並べる。
        ブロックの中は、1行目が大分類のボタン(太字)、改行して2行目に、その下の分類のボタンを並べる。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名 |
        | `tree` | `dict[str, list[str]]` | 大分類名 → その下の分類名(`class_tree` の結果) |
        | `count` | `dict[str, int]` | タグ名 → 該当件数 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | 系統名 + 大分類ごとのブロック。木が空なら空文字列 |
        """
        esc = html.escape
        btn = lambda t, extra="": (
            f'<button type="button" class="btn btn-sm btn-outline-primary{extra}" data-tag="{esc(t)}">'
            f'{esc(t)} <span class="badge text-bg-light">{count[t]}</span></button>'
        )
        blocks = "".join(
            f"""\
                <div class="pb-4">
                    {btn(top, " fw-bold")}{"<br>" if subs else ""}
                    {" ".join(btn(t) for t in subs)}
                </div>
                """
            for top, subs in tree.items())
        if not blocks:
            return ""
        return (
            f"""\
<div class="pt-3">
            <div class="me-1">{html.escape(title)}</div>
            <div>
                {blocks.strip()}
            </div>
        </div>
        """
        )

    def static_html(self, blocks):
        """
        ## メイン表の後ろの補足ブロックを HTML にする

        補足表は検索・固定の対象外。CSS の `max-content` や見出しの固定が効かないよう、HTML 側で指定を足す。

        | ブロック | 出力 |
        |---|---|
        | `h3` | `<h3 class="h5 mt-4 mb-2">` |
        | `table` | `<div class="table-responsive">` に入れた Bootstrap の小さい表(幅は中身に合わせる) |
        | `note` | `<p class="small text-body-secondary mb-2">` |
        | `p` | `<p class="mb-2">` |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `blocks` | `list[tuple]` | `parse` の `blocks` |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | ブロックがなければ空文字列 |
        """
        esc = html.escape
        out = []
        for b in blocks:
            if b[0] == "h3":
                out.append(f'    <h3 class="h5 mt-4 mb-2">{esc(b[1])}</h3>')
            elif b[0] == "note":
                out.append(f'    <p class="small text-body-secondary mb-2">{self.md_inline(esc(b[1]))}</p>')
            elif b[0] == "p":
                out.append(f'    <p class="mb-2">{self.md_inline(esc(b[1]))}</p>')
            else:
                _, head, rows = b
                ths = "".join(
                    f'<th style="position:static;min-width:0">{esc(h)}</th>' for h in head)
                trs = "\n".join(
                    "                <tr>" + "".join(
                        f'<td style="min-width:0">{self.md_inline(c) if c not in ("-", "") else "—"}</td>'
                        for c in r) + "</tr>"
                    for r in rows)
                out.append(
                    '    <div class="table-responsive mb-3">\n'
                    '        <table class="table table-sm table-bordered mb-0" style="width:auto;min-width:0">\n'
                    f"            <thead><tr>{ths}</tr></thead>\n"
                    f"            <tbody>\n{trs}\n            </tbody>\n"
                    "        </table>\n"
                    "    </div>")
        return "\n".join(out)

    def build(self):
        """
        ## HTML 全体を組み立てる

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | テンプレートのプレースホルダを置換したもの(改行は CRLF にそろえる) |

        | 置き換えるプレースホルダ | 内容 |
        |---|---|
        | `__APP_ID__` `__INPUT_ID__` `__COUNT_ID__` `__CLEAR_ID__` | 分野ごとの ID |
        | `__FILTERS__` | 分類ボタン群(`分類` 列がなければ空) |
        | `__HEAD__` | メイン表の見出し行 |
        | `__ROWS__` | メイン表の本文 |
        | `__EXTRA__` | 補足ブロック |

        行数は `self.rows` に、タグごとの件数は `self.count` に、分類の木は `self.tree` に、見出しは `self.title` に入る。

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 分類の書式・重複の誤り(`category_paths` `class_tree`) |
        """
        title, (head, rows), blocks = self.parse()
        ci = head.index(self.CATEGORY_COL) if self.CATEGORY_COL in head else None
        shown = [h for i, h in enumerate(head) if i != ci]
        all_paths, tags, shown_rows = [], [], []
        for no, c in rows:
            name = f"{self.plain(c[0])}({self.stem}.md {no}行目)"
            if ci is not None:
                paths = self.category_paths(name, c[ci])
                all_paths.append(paths)
                tags.append(list(dict.fromkeys(t for p in paths for t in p)))
            else:
                tags.append([])
            shown_rows.append([x for i, x in enumerate(c) if i != ci])
        tree = self.class_tree(all_paths)
        count = {}
        for ts in tags:
            for t in ts:
                count[t] = count.get(t, 0) + 1
        body = [self.row_html(shown, c, ts) for c, ts in zip(shown_rows, tags)]
        self.rows, self.count, self.tree, self.title = len(body), count, tree, title
        out = (
            self.template
            .replace("__APP_ID__", self.app_id)
            .replace("__INPUT_ID__", self.input_id)
            .replace("__COUNT_ID__", self.count_id)
            .replace("__CLEAR_ID__", self.clear_id)
            .replace("__FILTERS__", self.class_group(self.FILTER_TITLE, tree, count))
            .replace("__HEAD__", self.head_html(shown))
            .replace("__EXTRA__", self.static_html(blocks))
            .replace("__ROWS__", "\n".join(body))
        )
        return re.sub(r"\r?\n", "\r\n", out)

    def save_html(self):
        """
        ## HTML の断片を書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        out = self.build()
        self._write(self.out, out)
        print(f"{self.rows:>3} rows, {len(out):>6} bytes -> {self.out}")
        return self.out

    def save_css(self):
        """
        ## CSS を書き出す(`template.css` の ID だけを置き換える)

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        self._write(self.out_css, self.css_text.replace("__APP_ID__", self.app_id))
        return self.out_css

    def save_js(self):
        """
        ## JavaScript を書き出す(`template.js` の引数だけを置き換える)

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        js = (
            self.js_text
            .replace("__APP_ID__", self.app_id)
            .replace("__INPUT_ID__", self.input_id)
            .replace("__COUNT_ID__", self.count_id)
            .replace("__CLEAR_ID__", self.clear_id)
        )
        self._write(self.out_js, js)
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
        ## 確認用ページ(Bootstrap CDN + KaTeX CDN + CSS + JS)を書き出す

        貼り付け先のページがなくても、ブラウザで開くだけで動作を確認できる。
        `createTableSearch` は貼り付け先のページが持つ関数なので、確認用には `preview/table-search.js` の簡易版を読み込む。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | `<stem>-preview.html` のパス |
        """
        path = os.path.join(self.out_dir, f"{self.stem}-preview.html")
        body = f'<h1 class="h4 mt-3">{html.escape(self.title)}</h1>\n{self.build()}'
        page = self._fill_preview(
            self.title or self.stem, body, [f"{self.stem}-style.css"], [f"{self.stem}-script.js"])
        self._write(path, page)
        print("preview ->", path)
        return path

    @classmethod
    def _fill_preview(cls, title, body, css_files, js_files):
        """
        ## 確認用ページのひな形に、タイトル・本文・CSS・JS を入れる(`save_preview*` の部品)

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | `<title>` |
        | `body` | `str` | `<body>` に入れる HTML |
        | `css_files` | `list[str]` | 読み込む CSS(出力フォルダからの相対パス) |
        | `js_files` | `list[str]` | 読み込む JS(出力フォルダからの相対パス) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | 確認用ページ全体 |
        """
        return (
            cls.PREVIEW.replace("__TITLE__", title)
            .replace("__CSS__", "\n".join(f'<link href="{c}" rel="stylesheet">' for c in css_files))
            .replace("__JS__", "\n".join(f'<script src="{j}"></script>' for j in js_files))
            .replace("__SUPPORT__", "../preview/table-search.js")
            .replace("__BODY__", body)
        )


def main(argv):
    """
    ## `md/` の Markdown を変換する

    | 引数 | 型 | 説明 |
    |---|---|---|
    | `argv` | `list[str]` | コマンドライン引数(`sys.argv[1:]`) |

    | 引数の書式 | 内容 |
    |---|---|
    | (なし) | `md/*.md` をすべて変換し、`out/` に HTML・CSS・JS を書き出す |
    | `--preview` | 上に加えて、確認用ページ(`out/<stem>-preview.html`)も書き出す |
    | `<stem> ...` | 指定した Markdown だけ変換する(例 : `electricity`) |
    """
    md_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "md")
    stems = [a for a in argv if not a.startswith("--")] or sorted(
        f[:-3] for f in os.listdir(md_dir) if f.endswith(".md"))
    for s in stems:
        if not os.path.exists(os.path.join(md_dir, s + ".md")):
            raise SystemExit(f"md/{s}.md がありません")
        conv = ElectricityMD2HTML(f"md/{s}.md")
        conv.save()
        if "--preview" in argv:
            conv.save_preview()


if __name__ == "__main__":
    main(sys.argv[1:])
