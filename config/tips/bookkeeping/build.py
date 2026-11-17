import re, html, os, sys


class BookkeepingMD2HTML:
    """
    ## 簿記・企業会計まとめ(Markdown の表)を、タグ検索付きの Bootstrap 用 HTML に変換するクラス

    `auth/build.py`(AuthMD2HTML)を参考に、表が4列・分類が見出し由来になるよう作り変えたもの。
    JavaScript と CSS は、テンプレート(`template/`)の ID・引数だけを `auth` 用から変えてある。

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `plain` | HTML タグを除いた検索用の文字列にする |
    | `split_cells` | 表の1行を、セルのリストに分ける(`\\\\|` は区切りにしない) |
    | `parse` | Markdown を、見出し(大分類・分類)つきの行データに変換する |
    | `class_tree` | 全行の経路から、大分類ごとの分類の一覧(木)を作り、タグ名の衝突を調べる |
    | `tags_of` | 行ごとにタグを決める |
    | `check_clean` | 級・出題区分など、簿記の内容ではない情報が残っていないか確認する |
    | `md_inline` | セル内に残った Markdown の強調(`**…**`)を `<strong>` にする |
    | `row_html` | 1行分の `<tr>` を作る |
    | `group` | 上部のタグボタン群(特徴)を作る |
    | `class_group` | 上部の分類ボタン群を、大分類ごとのブロックにして作る |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `save_html` | HTML の断片を書き出す |
    | `save_css` | CSS を書き出す |
    | `save_js` | JavaScript を書き出す |
    | `save` | 上の3つをまとめて書き出す |
    | `save_preview` | 単体で開ける確認用ページを書き出す(任意。数式も描画する) |

    ## bookkeeping.md の書式

    | 要素 | 書き方 | 変換後 |
    |---|---|---|
    | `## 大分類` | 大分類の見出し | 分類タグ(大分類)になる |
    | `### 分類` | 分類の見出し(省略可。省略したときは大分類だけが分類になる) | 分類タグになる |
    | 表 | `用語 \\| 説明 \\| 計算式 \\| 備考` の4列。見出し行・区切り行は読み飛ばす | 1つの表にまとめる |
    | `# …` | 表記ルールなど、表のない説明 | 変換しない(表を置くとエラー) |

    | 列 | 内容 | 変換後 |
    |---|---|---|
    | 1 用語 | 名前 | 固定列。名前の下にタグ(バッジ)を並べる |
    | 2 説明 | HTML | そのまま |
    | 3 計算式 | `<div class="boki-formula">\\\\[…\\\\]</div>`(TeX) | そのまま(数式の描画は貼り付け先の MathJax が行う) |
    | 4 備考 | HTML | そのまま |

    ## タグの決まり

    | 系統 | 内容 |
    |---|---|
    | 分類 | 見出しの経路(`大分類 > 分類`)の全要素。大分類を選ぶと、その下の分類の行もすべて残る |
    | 特徴 | `計算式あり`(計算式列が `-` でない)と `仕訳あり`(用語・説明・備考に `(借)` がある) |

    | 決まり | 内容 |
    |---|---|
    | 名前の重複 | 同じ名前を、別の大分類の下や、特徴のタグ名と重ねるとエラー |
    | 表が見出しの外 | `##` より前に表があるとエラー |
    | 余分な情報 | 級・年度・区分表・未確認などが残っているとエラー(`CLEAN_NG`) |
    """

    CSS = "bookkeeping-style.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "bookkeeping-script.js"    # 出力する JavaScript のファイル名(確認用ページも読み込む)
    COLS = 4                        # Markdown の表の列数
    CLASS_SEP = " > "               # 経路の表示用の区切り(エラーメッセージ用)
    # 簿記の内容ではない情報(何級か・出題区分表・試験年度・未確認の印)。残っているとエラーにする
    CLEAN_NG = re.compile(r"区分表(?!示)|未確認|標準勘定科目表|20\d\d年|範囲外|[1-3１-３]級|出題|※|\d章を")

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
        | `src` | `str` | (必須) | 入力 Markdown |
        | `out` | `str` または `None` | `src` の拡張子を `.html` にしたもの | 出力 HTML |
        | `template` | `str` | `"template/template.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template/template.css"` | CSS の元ファイル |
        | `js_template` | `str` | `"template/template.js"` | JavaScript の元ファイル |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        self.out = self._path(out) if out else f"{os.path.splitext(self.src)[0]}.html"
        self.template = self._read(template)
        self.css_text = self._read(css_template)
        self.js_text = self._read(js_template)
        out_dir = os.path.dirname(self.out)
        self.out_css = os.path.join(out_dir, self.CSS)
        self.out_js = os.path.join(out_dir, self.JS)
        self.rows = 0
        self.load_words()

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

    def load_words(self):
        """
        ## タグの定義を読み込む

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.groups` | `tuple[str, ...]` | タグの系統名。上部のボタン群・行のタグは、この順に並ぶ |
        | `self.feature` | `dict[str, tuple[str, str]]` | 特徴タグ名 → (対象の列, マッチする正規表現) |
        | `self.prev` | `str` | 確認用ページのひな形 |

        「分類」のタグは、ここでは定義しない。`bookkeeping.md` の見出しがそのままタグになる
        (`parse` を参照)。
        """
        GROUPS = ("分類", "特徴")

        # ## 特徴タグ
        #
        # | キー | 値 |
        # |---|---|
        # | タグ名 | `(対象, 正規表現)`。対象は `formula`(計算式列が `-` でない行)、または `text`(用語・説明・備考にマッチする行) |
        FEATURE = {
            "計算式あり": ("formula", r""),
            "仕訳あり": ("text", r"\(借\)"),
        }

        PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>簿記・企業会計まとめ(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
<script>
// 確認用: 計算式(TeX)を MathJax で描画する(本番ページ側の仕組みがある場合は不要)
window.MathJax = { tex: { inlineMath: [], displayMath: [['\\\\[', '\\\\]']] } };
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-chtml.js" async></script>
</head>
<body class="container-fluid">
__FRAGMENT__
<script>
// 確認用: 本番ページが持つ createTableSearch の代わりの簡易版(タグ・キーワードの絞り込みだけ)
if (typeof createTableSearch === 'undefined') {
    window.createTableSearch = (o) => {
        const app = document.getElementById(o.appId), q = document.getElementById(o.inputId);
        const cnt = document.getElementById(o.countId), clr = document.getElementById(o.clearId);
        const rows = [...app.querySelectorAll(o.rowSelector)];
        const sel = new Set();
        const norm = (s) => s.normalize('NFKC').toLowerCase();
        const run = () => {
            const words = norm(q.value).split(/\\s+/).filter(Boolean);
            let n = 0;
            rows.forEach((r) => {
                const tags = r.getAttribute(o.rowTagsAttr).split('|');
                const ok = [...sel].every((t) => tags.includes(t)) && words.every((w) => norm(r.textContent).includes(w));
                r.hidden = !ok; if (ok) n++;
            });
            app.querySelectorAll('[' + o.tagAttr + ']').forEach((b) => b.classList.toggle('active', sel.has(b.getAttribute(o.tagAttr))));
            cnt.textContent = n + ' / ' + rows.length + ' 件';
        };
        app.addEventListener('click', (e) => {
            const b = e.target.closest('[' + o.tagAttr + ']');
            if (!b) return;
            const t = b.getAttribute(o.tagAttr);
            sel.has(t) ? sel.delete(t) : sel.add(t);
            run();
        });
        q.addEventListener('input', run);
        clr.addEventListener('click', () => { sel.clear(); q.value = ''; run(); });
        run();
    };
}
</script>
<script src="__JS__"></script>
</body>
</html>
"""
        self.groups, self.feature, self.prev = GROUPS, FEATURE, PREVIEW

    @staticmethod
    def plain(s):
        """
        ## HTMLタグを除去した検索用の文字列を返す

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
        ## Markdown を、見出しつきの行データにする

        `#` `##` `###` の見出しで、いまの大分類・分類を追う。`#` は表記ルールなどの説明で、
        大分類・分類を空にする。見出し行(3・4列目が `計算式` `備考` の行。1列目は `用語` でなくてもよい)と区切り行(`| ---`)は読み飛ばす。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行リスト | `list[tuple[int, list[str], list[str]]]` | (Markdown の行番号, 4セル, 経路 `[大分類]` または `[大分類, 分類]`) |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | `##` より前、または `#` の下に表がある |
        | `AssertionError` | 表の列数が4でない |
        """
        rows, top, sub = [], None, None
        with open(self.src, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for no, ln in enumerate(lines, 1):
            m = re.match(r"(#{1,3})\s+(.+?)\s*$", ln)
            if m:
                depth, title = len(m.group(1)), m.group(2)
                if depth == 1:
                    top = sub = None
                elif depth == 2:
                    top, sub = title, None
                else:
                    if top is None:
                        raise ValueError(f"{no}行目: 「{title}」の前に大分類(##)がありません")
                    sub = title
                continue
            if ln.startswith("|") and not re.match(r"\|\s*-{3}", ln) and self.split_cells(ln)[2:4] != ["計算式", "備考"]:
                if top is None:
                    raise ValueError(f"{no}行目: 表が大分類(##)の外にあります")
                cells = self.split_cells(ln)
                assert len(cells) == self.COLS, (no, len(cells), ln[:60])
                rows.append((no, cells, [top] + ([sub] if sub else [])))
        return rows

    def class_tree(self, all_paths):
        """
        ## 全行の経路から、大分類ごとの分類の一覧(木)を作る

        同じ名前が、次のように重なっているとエラーにする。
        1件だけでも上部のボタンに出すため、件数による足切りはしない。

        | 重なり | 理由 |
        |---|---|
        | 別の大分類の下に同じ名前の分類がある | 1つのタグが2か所に出て、どちらか分からなくなる |
        | 大分類と、別の大分類の下の分類が同じ名前 | 同上 |
        | 特徴のタグ名と同じ | 系統をまたいで同じタグ名になる |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `all_paths` | `list[list[str]]` | 行ごとの経路(`parse` の結果) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 木 | `dict[str, list[str]]` | 大分類名 → その下の分類名。どちらも初めて出てきた順 |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 上の表の重なりがある |
        """
        tree, owner = {}, {}
        for path in all_paths:
            top = path[0]
            tree.setdefault(top, [])
            for t in path:
                if owner.setdefault(t, top) != top:
                    raise ValueError(f"分類タグ {t!r} が、{owner[t]!r} と {top!r} の両方に使われています")
            tree[top] += [t for t in path[1:] if t not in tree[top]]
        clash = sorted(set(owner) & set(self.feature))
        if clash:
            raise ValueError(f"分類タグが、特徴のタグ名と重なっています: {clash}")
        return tree

    def tags_of(self, cells, path):
        """
        ## 行のタグを系統ごとに返す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 4セル |
        | `path` | `list[str]` | その行の経路(`[大分類]` または `[大分類, 分類]`) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タプル | `tuple[list, list]` | `self.groups` の順(分類・特徴)のタグ。分類は経路の全要素 |
        """
        text = self.plain(" ".join((cells[0], cells[1], cells[3])))
        feats = []
        for tag, (kind, rx) in self.feature.items():
            if kind == "formula" and cells[2] not in ("-", ""):
                feats.append(tag)
            elif kind == "text" and re.search(rx, text):
                feats.append(tag)
        return list(path), feats

    def check_clean(self, no, cells):
        """
        ## 級・出題区分など、簿記の内容ではない情報が残っていないか確認する

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `no` | `int` | Markdown の行番号(エラーメッセージ用) |
        | `cells` | `list[str]` | 4セル |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | `CLEAN_NG` にマッチする文字列がある |
        """
        m = self.CLEAN_NG.search(self.plain(" ".join(cells)))
        if m:
            raise ValueError(f"{self.plain(cells[0])}(bookkeeping.md {no}行目): 余分な情報 {m.group(0)!r} が残っています")

    @staticmethod
    def md_inline(s):
        """
        ## セル内の Markdown の強調(`**…**`)を `<strong>` にする

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `s` | `str` | セルの内容 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `**x**` → `<strong>x</strong>` |
        """
        return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)

    def row_html(self, cells, tags):
        """
        ## 1行分の `<tr>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 元の4セル |
        | `tags` | `list[str]` | この行のタグ(分類+特徴) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr>…</tr>` |
        """
        esc = html.escape
        fix = lambda s: s if s not in ("-", "") else '<span class="text-body-tertiary">—</span>'
        cell = lambda s: f"<td>{fix(self.md_inline(s))}</td>"
        badges = "".join(
            f'<button type="button" class="tag badge text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags)
        return (
            f"""\
                <tr data-tags="{esc("|".join(tags))}">
                    <th scope="row" class="name">{self.md_inline(cells[0])}<div class="tags">{badges}</div></th>
                    {cell(cells[1])}
                    {cell(cells[2])}
                    {cell(cells[3])}
                </tr>"""
        )

    def group(self, title, names, count):
        """
        ## 上部のタグボタン群(1系統分)を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(特徴) |
        | `names` | `list[str]` | タグ名の候補(表示順) |
        | `count` | `dict[str, int]` | タグ名 → 該当件数 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | ボタンの並び。該当が1件もないタグは出さない。表示するタグがなければ空文字列 |
        """
        esc = html.escape
        btns = "".join(
            f"""\
<button type="button" class="btn btn-sm btn-outline-primary" data-tag="{esc(n)}">
                    {esc(n)} 
                    <span class="badge text-bg-light">{count[n]}</span>
                </button>
                """
            for n in names if count.get(n, 0) >= 1)
        if not btns:
            return ""
        return (
            f"""\
<div class="pt-3 d-flex flex-wrap gap-1 align-items-center mb-1">
            <div class="me-1">{title}</div>
            <div>
                {btns}
            </div>
        </div>
        """
        )

    def class_group(self, title, tree, count):
        """
        ## 上部の分類ボタン群を、大分類ごとのブロックにして作る

        系統名を1行目に置き、その下に大分類ごとのブロック(`pb-4`)を縦に並べる。
        ブロックの中は、1行目が大分類のボタン(太字)、改行して2行目に、その下の分類のボタンを並べる。
        大分類を選ぶと、その下の分類の行もすべて残る(経路の全要素がタグのため)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(分類) |
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
            <div class="me-1">{title}</div>
            <div>
                {blocks.strip()}
            </div>
        </div>
        """
        )

    def build(self):
        """
        ## HTML 全体を組み立てる

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | テンプレートの `__ROWS__` と `__FILTERS__` を置換したもの(改行は CRLF にそろえる) |

        行数は `self.rows` に、タグごとの件数は `self.count` に、分類の木は `self.tree` に入る。
        """
        rows = self.parse()
        tree = self.class_tree([p for _, _, p in rows])
        tags = []
        for no, c, path in rows:
            self.check_clean(no, c)
            cat, feat = self.tags_of(c, path)
            tags.append(cat + feat)
        count = {}
        for ts in tags:
            for t in ts:
                count[t] = count.get(t, 0) + 1
        body = [self.row_html(c, ts) for (_, c, _), ts in zip(rows, tags)]
        self.rows, self.count, self.tree = len(body), count, tree
        filters = (
            self.class_group(self.groups[0], tree, count)
            + self.group(self.groups[1], list(self.feature), count)
        )
        out = self.template.replace("__ROWS__", "\n".join(body)).replace("__FILTERS__", filters)
        return re.sub(r"\r?\n", "\r\n", out)

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
        path = f"""{os.path.splitext(self.out)[0]}-preview.html"""
        page = (self.prev.replace("__CSS__", self.CSS).replace("__JS__", self.JS)
                .replace("__FRAGMENT__", self.build()))
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = BookkeepingMD2HTML("bookkeeping.md")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
