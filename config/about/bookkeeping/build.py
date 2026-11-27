import re, html, os, sys


class BookkeepingMD2HTML:
    """
    ## 簿記・企業会計まとめ(Markdown の表)を、タグ検索付きの Bootstrap 用 HTML に変換するクラス

    `auth/build.py`(AuthMD2HTML)を参考に、表が5列(用語・説明・計算式・備考・タグ)・分類が見出し由来になるよう作り変えたもの。
    JavaScript と CSS は、テンプレート(`template/`)の ID・引数だけを `auth` 用から変えてある。

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `plain` | HTML タグを除いた検索用の文字列にする |
    | `split_cells` | 表の1行を、セルのリストに分ける(`\\\\|` は区切りにしない) |
    | `parse` | Markdown を、見出し(大分類・分類)つきの行データに変換する |
    | `class_tree` | 全行の経路から、大分類ごとの分類の一覧(木)を作り、タグ名の衝突を調べる |
    | `tags_of` | 行ごとにタグを決める(見出しの経路 + `タグ` 列) |
    | `check_clean` | 級・出題区分など、簿記の内容ではない情報が残っていないか確認する |
    | `check_tags` | 特徴タグが、他の列の内容と食い違っていないか確認する(食い違いは警告) |
    | `md_inline` | セル内に残った Markdown の強調(`**…**`)を `<strong>` にする |
    | `load_fragments` | `FS.html` などの断片ファイルを、差し込み指示コメントごとに分ける |
    | `inject` | 断片を、指示された行・列のセルにネストして入れ込む |
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
    | 表 | `用語 \\| 説明 \\| 計算式 \\| 備考 \\| タグ` の5列。見出し行・区切り行は読み飛ばす | 1つの表にまとめる |
    | `# …` | 表記ルールなど、表のない説明 | 変換しない(表を置くとエラー) |

    | 列 | 内容 | 変換後 |
    |---|---|---|
    | 1 用語 | 名前 | 固定列。名前の下にタグ(バッジ)を並べる |
    | 2 説明 | HTML | そのまま |
    | 3 計算式 | `<div class="boki-formula">\\\\[…\\\\]</div>`(TeX) | そのまま(数式の描画は貼り付け先の MathJax が行う) |
    | 4 備考 | HTML | そのまま |
    | 5 タグ | 見出し以外で決めるタグを、コンマ(`,`)区切りで書く。なければ `-` | 名前の下のバッジと、上部の絞り込みボタンになる |

    ## タグの決まり

    | 系統 | 内容 |
    |---|---|
    | 分類 | 見出しの経路(`大分類 > 分類`)の全要素 + `タグ` 列に書いた見出し名(その大分類も加わる)。大分類を選ぶと、その下の分類の行もすべて残る |
    | 特徴 | `タグ` 列に書いた特徴タグ(`FEATURE` に定義したもの) |

    `タグ` 列に書けるのは、次のどちらかだけ。

    | 書くもの | 使いどころ |
    |---|---|
    | 見出しの名前(`###` の名前。`###` がなければ `##` の名前) | 同じ用語が別の見出しの下にも属するとき。重複する行は1行にまとめ、行は最初に出てくる見出しの下に置く |
    | 特徴タグ(`FEATURE`) | `計算式あり` `仕訳あり` `評価勘定` など、見出しからは決まらない性質 |

    | 決まり | 内容 |
    |---|---|
    | 名前の重複 | 同じ名前を、別の大分類の下や、特徴のタグ名と重ねるとエラー |
    | 未定義のタグ | `タグ` 列に、見出しにも `FEATURE` にもない名前があるとエラー(誤字の検出) |
    | 特徴タグの食い違い | `計算式あり` `仕訳あり` が、計算式列・`(借)` の有無と合わないと警告(`check_tags`) |
    | 表が見出しの外 | `##` より前に表があるとエラー |
    | 余分な情報 | 級・年度・区分表・未確認などが残っているとエラー(`CLEAN_NG`) |

    ## 断片 HTML(`FS.html`)の書式

    `FS.html` のような断片ファイルに、差し込み指示コメント `<!-- into: 用語名; col: 列; at: 位置 -->` を書くと、
    次の指示コメントまで(またはファイル末尾まで)の HTML が、指示した行のセルにネストして入る。
    1つのファイルに、指示コメントを何個でも書ける。

    | キー | 必須 | 既定値 | 内容 |
    |---|---|---|---|
    | `into` | 必須 | (なし) | 差し込み先の行の `用語` 列(完全一致。例: `貸借対照表(B/S)`)。0件・2件以上にマッチするとエラー |
    | `col` | 任意 | `説明` | 差し込み先の列。`説明` `計算式` `備考` のどれか |
    | `at` | 任意 | `end` | セル内の位置。`end`(既存の内容の後ろ)か `start`(前) |

    | 決まり | 内容 |
    |---|---|
    | 区切り | キーは `;` で区切る(`:` の左がキー、右が値) |
    | 包み方 | 差し込む HTML は `<div class="boki-nested">…</div>` で包む(CSS が、入れ子の表の見た目を整える) |
    | 先頭の内容 | 最初の指示コメントより前には、通常のコメント以外を書けない(書き忘れの検出) |
    | 空の断片 | 指示コメントの後ろに HTML がないとエラー |
    """

    CSS = "bookkeeping-style.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "bookkeeping-script.js"    # 出力する JavaScript のファイル名(確認用ページも読み込む)
    COLS = 5                        # Markdown の表の列数(用語・説明・計算式・備考・タグ)
    FRAG_DIRECTIVE = re.compile(r"<!--\s*into\s*:(.+?)-->", re.S)   # 差し込み指示コメント(`<!-- into: … -->`)
    FRAG_COLS = {"説明": 1, "計算式": 2, "備考": 3}               # 差し込める列名 → `cells` の添字
    FRAG_AT = ("end", "start")                                  # 差し込む位置(既存の内容の後ろ・前)
    FRAG_CLASS = "boki-nested"                                  # 差し込む HTML を包む `<div>` のクラス名
    CLASS_SEP = " > "               # 経路の表示用の区切り(エラーメッセージ用)
    # 簿記の内容ではない情報(何級か・出題区分表・試験年度・未確認の印)。残っているとエラーにする
    CLEAN_NG = re.compile(r"区分表(?!示)|未確認|標準勘定科目表|20\d\d年|範囲外|[1-3１-３]級|出題|※|\d章を")

    def __init__(
        self,
        src,
        out=None,
        template="template/template.html",
        css_template="template/template.css",
        js_template="template/template.js",
        fragments=("FS.html",)
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
        | `fragments` | `tuple[str, ...]` | `("FS.html",)` | 表のセルにネストして入れ込む HTML 断片のファイル(書式はクラスの説明を参照)。空のタプルなら何も入れ込まない |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        self.out = self._path(out) if out else f"{os.path.splitext(self.src)[0]}.html"
        self.template = self._read(template)
        self.css_text = self._read(css_template)
        self.js_text = self._read(js_template)
        self.fragments = [self._path(p) for p in fragments]
        out_dir = os.path.dirname(self.out)
        self.out_css = os.path.join(out_dir, self.CSS)
        self.out_js = os.path.join(out_dir, self.JS)
        self.rows = 0
        self.heads = []       # 見出しの経路(表のない見出しも含む)の出現順のリスト(`parse` が設定)
        self.owner = {}       # 分類タグ名 → 大分類名(`class_tree` が設定)
        self.warnings = []    # 警告のリスト(`build` が設定。`save_html` が表示)
        self.nested = 0       # セルに入れ込んだ断片の数(`inject` が設定)
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
        | `self.feature` | `tuple[str, ...]` | `タグ` 列に書ける特徴タグ名。上部のボタン・行のタグは、この順に並ぶ |
        | `self.feature_check` | `dict[str, tuple[str, str]]` | 特徴タグ名 → (対象の列, マッチする正規表現)。`check_tags` の確認用 |
        | `self.prev` | `str` | 確認用ページのひな形 |

        「分類」のタグは、ここでは定義しない。`bookkeeping.md` の見出しがそのままタグになる
        (`parse` を参照)。
        """
        GROUPS = ("分類", "特徴")

        # ## 特徴タグ
        #
        # `タグ` 列に書けるのは、見出しの名前か、ここに定義した名前だけ(`tags_of` を参照)。
        FEATURE = ("計算式あり", "仕訳あり", "評価勘定", "表あり")

        # ## 特徴タグの確認規則
        #
        # 他の列の内容から機械的に判断できる特徴タグだけ、書き忘れ・書き間違いを警告する(`check_tags`)。
        #
        # | キー | 値 |
        # |---|---|
        # | タグ名 | `(対象, 正規表現)`。対象は `formula`(計算式列が `-` でない行)、または `text`(用語・説明・備考にマッチする行) |
        FEATURE_CHECK = {
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
        self.groups, self.feature, self.feature_check, self.prev = GROUPS, FEATURE, FEATURE_CHECK, PREVIEW

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

        表のない見出し(`### 財務三表の基本構造` のように、見出しだけで中身が空のもの)も、
        分類タグとして使えるよう、見出しの経路を `self.heads` に出現順で記録する。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行リスト | `list[tuple[int, list[str], list[str]]]` | (Markdown の行番号, 5セル, 経路 `[大分類]` または `[大分類, 分類]`) |

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.heads` | `list[list[str]]` | 見出しの経路(`[大分類]` または `[大分類, 分類]`)。表の有無にかかわらず、出現順に並べる |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | `##` より前、または `#` の下に表がある |
        | `AssertionError` | 表の列数が5でない |
        """
        rows, top, sub = [], None, None
        self.heads = []
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
                    self.heads.append([top])          # 表がなくても、大分類をタグにする
                else:
                    if top is None:
                        raise ValueError(f"{no}行目: 「{title}」の前に大分類(##)がありません")
                    sub = title
                    self.heads.append([top, sub])     # 表がなくても、分類をタグにする
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
        ## 見出しと全行の経路から、大分類ごとの分類の一覧(木)を作る

        表のない見出しも木に入れる(`build` が `self.heads` を先に渡す)。
        同じ名前が、次のように重なっているとエラーにする。
        1件だけでも上部のボタンに出すため、件数による足切りはしない。

        | 重なり | 理由 |
        |---|---|
        | 別の大分類の下に同じ名前の分類がある | 1つのタグが2か所に出て、どちらか分からなくなる |
        | 大分類と、別の大分類の下の分類が同じ名前 | 同上 |
        | 特徴のタグ名と同じ | 系統をまたいで同じタグ名になる |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `all_paths` | `list[list[str]]` | 見出しの経路(`self.heads`)に続けて、行ごとの経路(`parse` の結果)を並べたもの |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 木 | `dict[str, list[str]]` | 大分類名 → その下の分類名。どちらも初めて出てきた順 |

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.owner` | `dict[str, str]` | 分類タグ名(大分類・分類) → その大分類名。`tags_of` が `タグ` 列の見出し名を引くのに使う |

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
        self.owner = owner
        return tree

    def tags_of(self, no, cells, path):
        """
        ## 行のタグを系統ごとに返す

        見出しの経路に、`タグ` 列(コンマ区切り)のタグを加える。`タグ` 列の名前は、次のように振り分ける。

        | `タグ` 列の名前 | 振り分け先 | 備考 |
        |---|---|---|
        | 見出しの名前(`self.owner` にある) | 分類 | その大分類も加える(先に並べる)。自分の経路にあるものは重ねない |
        | `self.feature` にある名前 | 特徴 | `self.feature` の順に並べる |
        | どちらでもない | (エラー) | 誤字を見つけるため |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `no` | `int` | Markdown の行番号(エラーメッセージ用) |
        | `cells` | `list[str]` | 5セル |
        | `path` | `list[str]` | その行の経路(`[大分類]` または `[大分類, 分類]`) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タプル | `tuple[list, list]` | `self.groups` の順(分類・特徴)のタグ。分類は経路の全要素 + `タグ` 列の見出し名 |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | `タグ` 列に、見出しにも `self.feature` にもない名前がある |
        """
        names = [t.strip() for t in cells[4].split(",") if t.strip() not in ("", "-")]
        cls, feats = list(path), []
        for t in dict.fromkeys(names):  # 同じ名前の重複は除く(書いた順は保つ)
            if t in self.owner:
                cls += [x for x in (self.owner[t], t) if x not in cls]
            elif t in self.feature:
                feats.append(t)
            else:
                raise ValueError(
                    f"{self.plain(cells[0])}(bookkeeping.md {no}行目): "
                    f"タグ {t!r} は、見出しの名前にも特徴のタグ名({', '.join(self.feature)})にもありません")
        return cls, sorted(feats, key=self.feature.index)

    def check_clean(self, no, cells):
        """
        ## 級・出題区分など、簿記の内容ではない情報が残っていないか確認する

        `タグ` 列は対象にしない(タグ名は `tags_of` が確認する)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `no` | `int` | Markdown の行番号(エラーメッセージ用) |
        | `cells` | `list[str]` | 5セル |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | `CLEAN_NG` にマッチする文字列がある |
        """
        m = self.CLEAN_NG.search(self.plain(" ".join(cells[:4])))
        if m:
            raise ValueError(f"{self.plain(cells[0])}(bookkeeping.md {no}行目): 余分な情報 {m.group(0)!r} が残っています")

    def check_tags(self, no, cells, feats):
        """
        ## 特徴タグが、他の列の内容と食い違っていないか確認する

        `self.feature_check` にある特徴タグだけが対象(`評価勘定` のように機械的に判断できないタグは対象外)。
        食い違っていてもエラーにはせず、警告の文字列を返す(`タグ` 列を正とするため)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `no` | `int` | Markdown の行番号(警告用) |
        | `cells` | `list[str]` | 5セル |
        | `feats` | `list[str]` | `tags_of` が返した、その行の特徴タグ |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 警告のリスト | `list[str]` | 食い違いごとに1件。なければ空リスト |
        """
        text = self.plain(" ".join((cells[0], cells[1], cells[3])))
        warns = []
        for tag, (kind, rx) in self.feature_check.items():
            expect = cells[2] not in ("-", "") if kind == "formula" else bool(re.search(rx, text))
            if expect != (tag in feats):
                warns.append(
                    f"{self.plain(cells[0])}(bookkeeping.md {no}行目): "
                    + (f"{tag!r} の内容があるのに、タグ列にありません" if expect
                       else f"タグ列に {tag!r} がありますが、内容がありません"))
        return warns

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

    def load_fragments(self):
        """
        ## 断片ファイルを、差し込み指示コメントごとに分ける

        `self.fragments` のファイルを順に読み、`<!-- into: … -->` ごとに、次の指示コメントまでの HTML を1件にする。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 断片のリスト | `list[dict]` | ファイルの順・書いた順。空なら空リスト |

        | 戻り値の要素のキー | 型 | 説明 |
        |---|---|---|
        | `term` | `str` | 差し込み先の `用語` |
        | `col` | `str` | 差し込み先の列名(`説明` `計算式` `備考`) |
        | `at` | `str` | 位置(`end` `start`) |
        | `html` | `str` | 差し込む HTML(前後の空白は除去済み) |
        | `where` | `str` | `ファイル名 N行目`(エラーメッセージ用) |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 最初の指示コメントより前に、コメント以外の内容がある |
        | `ValueError` | 指示コメントに、`into` の用語がない・未知のキー・`col` や `at` の値が不正 |
        | `ValueError` | 指示コメントの後ろに HTML がない |
        """
        frags = []
        for p in self.fragments:
            text, name = self._read(p), os.path.basename(p)
            marks = list(self.FRAG_DIRECTIVE.finditer(text))
            head = text[:marks[0].start()] if marks else text
            if re.sub(r"<!--.*?-->", "", head, flags=re.S).strip():
                raise ValueError(f"{name}: 最初の指示コメント(<!-- into: … -->)より前に、内容があります")
            for i, m in enumerate(marks):
                where = f"{name} {text.count(chr(10), 0, m.start()) + 1}行目"
                parts = [s.strip() for s in m.group(1).split(";")]
                opt = {"col": "説明", "at": "end"}
                for s in parts[1:]:
                    k, sep, v = s.partition(":")
                    if not sep or k.strip() not in opt:
                        raise ValueError(f"{where}: 指示 {s!r} が分かりません(使えるキー: col, at)")
                    opt[k.strip()] = v.strip()
                if not parts[0]:
                    raise ValueError(f"{where}: into の用語がありません")
                if opt["col"] not in self.FRAG_COLS:
                    raise ValueError(f"{where}: col {opt['col']!r} は使えません({', '.join(self.FRAG_COLS)})")
                if opt["at"] not in self.FRAG_AT:
                    raise ValueError(f"{where}: at {opt['at']!r} は使えません({', '.join(self.FRAG_AT)})")
                end = marks[i + 1].start() if i + 1 < len(marks) else len(text)
                body = text[m.end():end].strip()
                if not body:
                    raise ValueError(f"{where}: 指示コメントの後ろに HTML がありません")
                frags.append({"term": parts[0], "col": opt["col"], "at": opt["at"], "html": body, "where": where})
        return frags

    def inject(self, rows):
        """
        ## 断片を、指示された行・列のセルにネストして入れ込む

        `用語` 列(`**…**` と HTML タグを除いたもの)が、断片の `term` と完全一致する行を探す。
        元のセルが `-` または空なら、断片だけにする。`rows` 自体は書き換えない(コピーを返す)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `rows` | `list[tuple[int, list[str], list[str]]]` | `parse` の結果 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行リスト | `list[tuple[int, list[str], list[str]]]` | `rows` と同じ形。指示された行のセルだけ断片入り |

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.nested` | `int` | 入れ込んだ断片の数 |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 断片の `term` にマッチする行が、0件または2件以上(誤字・曖昧さの検出) |
        """
        out = [(no, list(c), p) for no, c, p in rows]
        frags = self.load_fragments()
        for f in frags:
            hit = [r for r in out if self.plain(self.md_inline(r[1][0])) == f["term"]]
            if len(hit) != 1:
                raise ValueError(
                    f"{f['where']}: 用語 {f['term']!r} にマッチする行が {len(hit)} 件あります(1件だけにしてください)")
            cells, i = hit[0][1], self.FRAG_COLS[f["col"]]
            box = f'<div class="{self.FRAG_CLASS}">{f["html"]}</div>'
            if cells[i] in ("-", ""):
                cells[i] = box
            else:
                cells[i] = cells[i] + "\n" + box if f["at"] == "end" else box + "\n" + cells[i]
        self.nested = len(frags)
        return out

    def row_html(self, cells, tags):
        """
        ## 1行分の `<tr>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 元のセル(先頭の4セルを使う。`タグ` 列は `tags` に反映済み) |
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
        | `count` | `dict[str, int]` | タグ名 → 該当件数(表のない見出しで、どの行も使っていないタグは `0` 件として表示する) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | 系統名 + 大分類ごとのブロック。木が空なら空文字列 |
        """
        esc = html.escape
        btn = lambda t, extra="": (
            f'<button type="button" class="btn btn-sm btn-outline-primary{extra}" data-tag="{esc(t)}">'
            f'{esc(t)} <span class="badge text-bg-light">{count.get(t, 0)}</span></button>'
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

        行数は `self.rows` に、タグごとの件数は `self.count` に、分類の木は `self.tree` に、
        警告は `self.warnings` に入る。
        """
        rows = self.parse()
        tree = self.class_tree(self.heads + [p for _, _, p in rows])  # 表のない見出しもタグにする
        tags, self.warnings = [], []
        for no, c, path in rows:
            self.check_clean(no, c)
            cat, feat = self.tags_of(no, c, path)
            self.warnings += self.check_tags(no, c, feat)
            tags.append(cat + feat)
        count = {}
        for ts in tags:
            for t in ts:
                count[t] = count.get(t, 0) + 1
        rows = self.inject(rows)  # 検査(`check_clean` `check_tags`)のあとで入れ込む(断片は検査の対象外)
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

        `build` が集めた警告(`check_tags`)があれば、標準エラーに `WARN` 付きで表示する。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        out = self.build()
        self._write(self.out, out)
        print(self.rows, "rows,", self.nested, "nested,", len(out), "bytes ->", self.out)
        for w in self.warnings:
            print("WARN", w, file=sys.stderr)
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
