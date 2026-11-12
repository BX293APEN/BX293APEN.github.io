import re, html, os, sys, json


class AuthMD2HTML:
    """
    ## 認証技術まとめ(Markdown の表)を、タグ検索付きの Bootstrap 用 HTML に変換するクラス

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `load_words` | タグの定義(別名・認証要素・用途・トピック)を読み込む |
    | `split_cells` | 表の1行を、セルのリストに分ける(`\\|` は区切りにしない) |
    | `parse` | Markdown の表を行データに変換する |
    | `category_paths` | 「分類」列を、分類の経路(`大分類 > 分類`)のリストにする |
    | `class_tree` | 全行の経路から、大分類ごとの分類の一覧(木)を作り、タグ名の衝突を調べる |
    | `tags_of` | 行ごとにタグを決める |
    | `is_child` | 名前が `└` で始まる(子の行)かを判定する |
    | `inherit` | 子の行のタグを、親の行に足す |
    | `md_inline` | セル内に残った Markdown の強調(`**…**`)を `<strong>` にする |
    | `fit_tables` | セルの中の `<table>` を、列幅・見出しの固定が崩れないように整える |
    | `mermaid_body` | `mermaid-source` の中身から、mermaid の本文を取り出す(`<br>` を改行に戻す) |
    | `table_steps` | 「認証手順」セルの手順表から、手順番号を取り出す |
    | `step_numbers` | mermaid 内のメッセージから、手順番号を取り出す |
    | `check_steps` | mermaid の手順番号と、手順表の手順番号が合っているか確認する |
    | `mermaid_init` | mermaid の先頭に付ける `%%{init: …}%%` を作る |
    | `flow_html` | 「認証手順」セルの HTML(整えた図 + 手順表)を作る |
    | `row_html` | 1行分の `<tr>` を作る |
    | `group` | 上部のタグボタン群(認証要素・用途)を作る |
    | `class_group` | 上部の分類ボタン群を、大分類ごとのブロックにして作る |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `save_html` | HTML の断片を書き出す |
    | `save_css` | CSS を書き出す |
    | `save_js` | JavaScript を書き出す |
    | `save` | 上の3つをまとめて書き出す |
    | `save_preview` | 単体で開ける確認用ページを書き出す(任意。mermaid も描画する) |

    ## auth.md の書式

    | 列 | 内容 | 変換後 |
    |---|---|---|
    | 1 認証技術 | 名前 | 固定列。名前の下にタグ(バッジ)を並べる |
    | 2 分類 | `大分類 > 分類`(書式は下の表) | **表示しない**。経路の全要素を、タグにする |
    | 3 概要 | HTML | そのまま |
    | 4 認証手順 | `<div class="mermaid-source">…</div>` + `<table>…</table>` | 図(mermaid)を整える + 手順表はそのまま |
    | 5 メリット | HTML | そのまま |
    | 6 デメリット | HTML | そのまま |
    | 7 主な用途 | HTML | そのまま |

    ## 分類列の決まり

    | 決まり | 内容 |
    |---|---|
    | 経路 | `大分類 > 分類` のように ` > ` で区切る。左ほど大きい分類。3段以上も可 |
    | 複数の経路 | 1行に複数あるときは `<br>` で区切る(例 : PAP は「パスワード系」と「ネットワーク接続のプロトコル」の両方) |
    | タグ | 経路の全要素がタグになる。大分類を選ぶと、その下の分類の行もすべて残る |
    | 名前 | 1件だけの分類でも上部に出す。単独で意味が分かる名前にする(`実現方式` `総称` のような補足語だけにしない) |
    | 重複 | 同じ名前を、別の大分類の下や、認証要素・用途のタグ名と重ねるとエラー |
    | 空 | 分類が空の行はエラー |

    ## 親子の行(`└`)の決まり

    | 決まり | 内容 |
    |---|---|
    | 親 | 直前の、名前が `└` で始まらない行 |
    | タグの引き継ぎ | 子のタグを、親にも付ける(子で絞り込んだとき、親の行も残る) |
    | 見た目 | 子から引き継いだタグは、破線のバッジで表示する(親自身のタグと区別する) |

    ## 認証手順セルの決まり

    | 決まり | 内容 |
    |---|---|
    | 図 | `<div class="mermaid-source">` の中に mermaid を書く。Markdown の表は1行なので、mermaid の改行は `<br>` で表す |
    | 手順表 | 図の後ろに `<table>` で書く。`<tbody>` の行のうち、先頭セルが `<b>N</b>` で始まる行が1手順(`rowspan` で複数行にまたがる手順は、先頭の行だけ数える) |
    | 手順番号 | mermaid のメッセージ・Note の文頭を `N.` にする。`N` は手順表の `<b>N</b>` と一致させる(合わないとエラー)。**手順0を除く** |
    | 1手順に複数メッセージ | 同じ番号を付けてよい(番号は小さい順に並べる) |
    | 手順表の番号 | `1` から順に並べる(飛んでいたり、逆順だったりするとエラー) |
    | 手順0(事前準備) | 手順表の**先頭にだけ**、`<b>0</b>` の手順を置いてよい(`PRE_STEP`)。ログインのたびに行う手順ではなく、事前に1回行う準備(メタデータ・証明書・URL・属性の交換など)のため、**図(mermaid)には書かない**。図に `0.` があるとエラー |
    | 図の前後 | 補足の説明など。そのまま残す |
    | 手順表があるのに図がない | エラー |
    | 手順表がない | 図があれば、図だけ整える(手順番号の突き合わせはしない)。図も表もなければ、そのまま出す |
    """

    CSS = "auth-style.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "auth-script.js"    # 出力する JavaScript のファイル名(確認用ページも読み込む)
    COLS = 7                 # Markdown の表の列数
    CLASS_SEP = ">"          # 「分類」列の経路の区切り(`大分類 > 分類`)
    CHILD_MARK = "└"         # 子の行の名前の先頭につく印
    PRE_STEP = 0             # 手順表の先頭にだけ置ける「手順0(事前準備)」の番号(図には書かない)
    MERMAID_SRC = re.compile(r'<div class="mermaid-source">(.*?)</div>', re.S)  # 「認証手順」セルの図

    # ## mermaid の見た目の設定(`%%{init: …}%%` として、全図の先頭に付ける)
    #
    # | キー | 値 | 説明 |
    # |---|---|---|
    # | `theme` | `base` | `themeVariables` を効かせるには `base` が必要 |
    # | `fontFamily` | `HGPGothicE, arial` | フォント |
    # | `primaryColor` | `#EEE` | 図形の塗り(参加者の箱など) |
    # | `primaryTextColor` | `#000000` | 文字色 |
    # | `primaryBorderColor` | `#000000` | 図形の枠線 |
    # | `lineColor` | `#000000` | 線・矢印 |
    # | `secondaryColor` | `#EEE` | 補助の塗り(Note など) |
    #
    # `None` にすると何も付けない。`auth.md` の図が自前で `%%{` から始まっていれば、そちらを優先する。
    MERMAID_INIT = {
        "theme": "base",
        "themeVariables": {
            "fontFamily": "HGPGothicE, arial",
            "primaryColor": "#EEE",
            "primaryTextColor": "#000000",
            "primaryBorderColor": "#000000",
            "lineColor": "#000000",
            "secondaryColor": "#EEE",
        },
    }

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
        | `self.factor` | `dict[str, str]` | 認証要素タグ名 → 認証技術名にマッチする正規表現 |
        | `self.use` | `dict[str, str]` | 用途タグ名 → 「主な用途」列にマッチする正規表現 |
        | `self.prev` | `str` | 確認用ページのひな形 |

        「分類」のタグは、ここでは定義しない。`auth.md` の「分類」列に書いたものが、そのままタグになる
        (`category_paths` を参照)。
        """
        GROUPS = ("分類", "認証要素", "用途")

        # ## 認証要素タグ(認証技術名にマッチすれば付与)
        #
        # | キー | 値 |
        # |---|---|
        # | タグ名 | 認証技術名にマッチする正規表現 |
        FACTOR = {
            "知識情報": r"パスワード認証|PAP|チャレンジレスポンス|CHAP",
            "所持情報": r"ワンタイム|セキュリティトークン|FIDO|WebAuthn|パスキー|クライアント証明書",
            "生体情報": r"生体|指紋|虹彩|静脈|顔認証|声紋|行動認証",
        }

        # ## 用途タグ(「主な用途」列にマッチすれば付与)
        #
        # | キー | 値 |
        # |---|---|
        # | タグ名 | 「主な用途」列にマッチする正規表現 |
        USE = {
            "リモートアクセス・VPN": r"リモートアクセス|VPN|ダイヤルアップ",
            "Web・クラウド": r"Webサービス|クラウド|SaaS|ログインフォーム|会員登録|ソーシャルログイン|SNS",
            "モバイル": r"スマートフォン|スマホ|モバイル",
            "金融・決済": r"バンキング|銀行|送金|決済|金融|カード|ATM",
            "企業内システム": r"企業内|社内|Windowsドメイン|Active Directory|レガシー",
            "無線LAN・ネットワーク機器": r"無線LAN|ネットワーク機器|802\.1X|WPA",
            "電子契約・電子申請": r"電子契約|電子申請|長期署名|電子帳簿",
            "API・システム間連携": r"(?<![A-Za-z])API(?![A-Za-z])|SOAP|WS-Security",
            "不正検知・なりすまし対策": r"不正利用検知|内部不正|乗っ取り|不正ログイン|なりすまし",
            "入退室・施設": r"入退室|勤怠|空港|入出国|高セキュリティ施設",
        }

        PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>認証技術まとめ(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="https://cdn.jsdelivr.net/npm/mermaid@11.4.1/dist/mermaid.min.js"></script>
<script>
// 確認用: .mermaid-source の中身を mermaid で描画する(本番ページ側の仕組みがある場合は不要)
mermaid.initialize({ startOnLoad: false, sequence: { useMaxWidth: false } });
mermaid.run({ querySelector: '.mermaid-source' });
</script>
<script src="__JS__"></script>
</body>
</html>
"""
        self.groups, self.factor, self.use, self.prev = GROUPS, FACTOR, USE, PREVIEW
        names = [n for d in (FACTOR, USE) for n in d]
        assert len(names) == len(set(names)), "タグ名が系統をまたいで重複しています"

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
        ## Markdown の表を行データにする

        見出し行(`| 認証技術`)と区切り行(`| ---`)は読み飛ばす。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行リスト | `list[tuple[int, list[str]]]` | (Markdown の行番号, 7セル) |
        """
        rows = []
        with open(self.src, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for no, ln in enumerate(lines, 1):
            if ln.startswith("|") and not re.match(r"\|\s*-{3}", ln) and not ln.startswith("| 認証技術"):
                cells = self.split_cells(ln)
                assert len(cells) == self.COLS, (no, len(cells), ln[:60])
                rows.append((no, cells))
        return rows

    def category_paths(self, name, cell):
        """
        ## 「分類」列を、分類の経路のリストにする

        経路の中は `>` で区切り、左ほど大きい分類になる。
        1行に複数の経路を書くときは `<br>` で区切る。

        | 元のセル | 経路 |
        |---|---|
        | `シングルサインオン(SSO) > エージェント型SSO` | `[["シングルサインオン(SSO)", "エージェント型SSO"]]` |
        | `生体認証(バイオメトリクス)` | `[["生体認証(バイオメトリクス)"]]` |
        | `A > B<br>C > D` | `[["A", "B"], ["C", "D"]]` |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `name` | `str` | 認証技術名(エラーメッセージ用) |
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

    def class_tree(self, all_paths):
        """
        ## 全行の経路から、大分類ごとの分類の一覧(木)を作る

        同じ名前が、次のように重なっているとエラーにする。
        1件だけでも上部のボタンに出すため、件数による足切りはしない。

        | 重なり | 理由 |
        |---|---|
        | 別の大分類の下に同じ名前の分類がある | 1つのタグが2か所に出て、どちらか分からなくなる |
        | 大分類と、別の大分類の下の分類が同じ名前 | 同上 |
        | 認証要素・用途のタグ名と同じ | 系統をまたいで同じタグ名になる |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `all_paths` | `list[list[list[str]]]` | 行ごとの経路のリスト(`category_paths` の結果) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 木 | `dict[str, list[str]]` | 大分類名 → その下の分類名。どちらも初めて出てきた順 |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 上の表の重なりがある |
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
        clash = sorted(set(owner) & (set(self.factor) | set(self.use)))
        if clash:
            raise ValueError(f"分類タグが、認証要素・用途のタグ名と重なっています: {clash}")
        return tree

    def tags_of(self, cells, paths):
        """
        ## 行のタグを系統ごとに返す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 7セル |
        | `paths` | `list[list[str]]` | その行の分類の経路(`category_paths` の結果) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タプル | `tuple[list, list, list]` | `self.groups` の順(分類・認証要素・用途)のタグ。分類は経路の全要素(重複なし) |
        """
        name, use = self.plain(cells[0]), self.plain(cells[6])
        return (
            list(dict.fromkeys(t for path in paths for t in path)),
            [t for t, rx in self.factor.items() if re.search(rx, name)],
            [t for t, rx in self.use.items() if re.search(rx, use)],
        )

    def is_child(self, name):
        """
        ## 名前が `└` で始まる(子の行)かを判定する

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `name` | `str` | 「認証技術」列のセル(`&emsp;└ …` のように HTML のままでよい) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 判定 | `bool` | 子の行なら `True` |
        """
        return self.plain(name).startswith(self.CHILD_MARK)

    def inherit(self, tags, child):
        """
        ## 子の行のタグを、親の行に足す

        親は、直前の、子でない行。親が子のタグを持たないと、子のタグで絞り込んだときに
        子だけが残り、親の行が消えて、検索結果が不自然になるため。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `tags` | `list[list[str]]` | 行ごとのタグ(自分のタグだけ) |
        | `child` | `list[bool]` | 行ごとの、子の行かどうか(`is_child` の結果) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | `merged` | `list[list[str]]` | 行ごとのタグ(親には子のタグを足したもの。順序は、自分のタグ、子のタグの順) |
        | `inherited` | `list[list[str]]` | 行ごとの、子から引き継いだタグ(表示で区別するため) |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 先頭の行が子で、親がない |
        """
        merged = [list(t) for t in tags]
        inherited = [[] for _ in tags]
        parent = None
        for i, is_child in enumerate(child):
            if not is_child:
                parent = i
                continue
            if parent is None:
                raise ValueError(f"{i + 1} 番目の行が子ですが、親の行がありません")
            for t in tags[i]:
                if t not in merged[parent]:
                    merged[parent].append(t)
                    inherited[parent].append(t)
        return merged, inherited

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

        CSS(`auth-style.css`)は、表の全セルに「最小幅17rem」と、見出しの固定(sticky)を指定している。
        そのままだと、セル内の表が横に非常に広がり、見出しが上の固定見出しに重なる。
        CSS を変えずに済むよう、セル内の表にだけ HTML 側で指定を足す。

        | 対象 | 足すもの | 理由 |
        |---|---|---|
        | `<table>` | `class="table table-sm table-bordered mb-2"` | Bootstrap の表にする |
        | `<th>` | `style="position:static;min-width:0"` | 見出しの固定を外し、最小幅を解除する |
        | `<td>` | `style="min-width:0"` | 最小幅を解除する |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `s` | `str` | セルの HTML |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | 整えた HTML |
        """
        s = s.replace("<table>", '<table class="table table-sm table-bordered mb-2">')
        s = re.sub(r"<th(\s[^>]*)?>", lambda m: self._with_style(m, "position:static;min-width:0"), s)
        s = re.sub(r"<td(\s[^>]*)?>", lambda m: self._with_style(m, "min-width:0"), s)
        return s

    @staticmethod
    def mermaid_body(raw):
        """
        ## `mermaid-source` の中身から、mermaid の本文を取り出す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `raw` | `str` | `<div class="mermaid-source">` の中身(Markdown の表は1行なので、改行が `<br>` になっている) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 本文 | `str` | `<br>` を改行に、HTML の文字参照を元の文字に戻したもの(前後の空白は除去) |
        """
        return html.unescape(re.sub(r"<br\s*>", "\n", raw)).strip()

    @staticmethod
    def table_steps(cell):
        """
        ## 手順表から、手順番号を取り出す

        `<tr>` の先頭セルが `<b>N</b>` で始まる行を、1手順とみなす。
        `rowspan` で手順の続きになっている行は、先頭セルが別の内容なので数えない。
        手順0(事前準備。`PRE_STEP`)も、他の手順と同じ方法で取り出す(`0` も番号として拾う)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cell` | `str` | 「認証手順」セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 番号のリスト | `list[int]` | 表に出てきた順(手順0があれば先頭に `0`)。手順表がなければ空 |
        """
        return [int(n) for n in re.findall(r"<tr>\s*<td\b[^>]*>\s*<b>(\d+)</b>", cell)]

    @staticmethod
    def step_numbers(mermaid):
        """
        ## mermaid のメッセージ・Note の文頭から、手順番号を取り出す

        `送信元->>宛先: 3. 内容` の `3` を取る(最初の `:` の直後が `数字.` の行だけ)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `mermaid` | `str` | mermaid の本文 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 番号のリスト | `list[int]` | 出てきた順。1手順に複数メッセージがあれば同じ番号が並ぶ |
        """
        nums = []
        for ln in mermaid.splitlines():
            m = re.match(r"[^:]*:\s*(\d+)\.\s", ln)
            if m:
                nums.append(int(m.group(1)))
        return nums

    def check_steps(self, name, mermaid, steps):
        """
        ## mermaid の手順番号と、手順表の手順番号が合っているか確認する

        手順表の先頭に手順0(事前準備。`PRE_STEP`)があるときは、手順0を除いた番号で確認する。
        手順0は図に書かないため、mermaid と突き合わせない。

        | 確認 | 合わないとき |
        |---|---|
        | 手順表の番号が、(手順0を除いて)`1` から順に並んでいる | `ValueError` |
        | mermaid に手順0が書かれていない | `ValueError` |
        | mermaid の番号が小さい順に並んでいる | `ValueError` |
        | mermaid の番号が、手順表の番号(手順0を除く)と過不足なく同じ | `ValueError` |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `name` | `str` | 認証技術名(エラーメッセージ用) |
        | `mermaid` | `str` | mermaid の本文 |
        | `steps` | `list[int]` | 手順表の手順番号(`table_steps` の結果。先頭に `0` があってよい) |
        """
        nums = self.step_numbers(mermaid)
        main = steps[1:] if steps[:1] == [self.PRE_STEP] else steps  # 手順0は表の先頭にだけ置ける
        if main != list(range(1, len(main) + 1)):
            raise ValueError(
                f"{name}: 手順表の番号 {steps} が、1 から順に並んでいません"
                f"(手順{self.PRE_STEP}は先頭にだけ置けます)"
            )
        if self.PRE_STEP in nums:
            raise ValueError(f"{name}: 手順{self.PRE_STEP}(事前準備)は手順表だけに書き、mermaid には書かないでください")
        if nums != sorted(nums) or sorted(set(nums)) != main:
            raise ValueError(f"{name}: mermaid の手順番号 {nums} が、手順表の番号 {main} と合いません")

    @classmethod
    def mermaid_init(cls, mermaid):
        """
        ## mermaid の先頭に付ける `%%{init: …}%%` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `mermaid` | `str` | mermaid の本文 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | ディレクティブ | `str` | `%%{init: {...}}%%` + 改行。付けないときは空文字 |

        次の場合は、空文字を返す(付けない)。

        | 条件 | 理由 |
        |---|---|
        | `MERMAID_INIT` が `None` または空 | 設定なし |
        | 本文がすでに `%%{` から始まる | 図ごとの指定を優先する |
        """
        if not cls.MERMAID_INIT or mermaid.lstrip().startswith("%%{"):
            return ""
        return f"%%{{init: {json.dumps(cls.MERMAID_INIT, ensure_ascii=False, indent=4)}}}%%\n"

    def flow_html(self, name, cell):
        """
        ## 「認証手順」セルの HTML を作る

        `mermaid-source` の中身を整える(`<br>` を改行に戻し、`%%{init: …}%%` を付ける)。
        手順表は auth.md に書かれたものをそのまま使う。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `name` | `str` | 認証技術名(エラーメッセージ用) |
        | `cell` | `str` | 「認証手順」セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `mermaid-source` を整えたセル。図も手順表もなければ元のまま |

        | 例外 | 条件 |
        |---|---|
        | `ValueError` | 手順表があるのに mermaid がない |
        | `ValueError` | 手順番号が合わない(`check_steps` を参照) |
        """
        steps = self.table_steps(cell)
        mm = self.MERMAID_SRC.search(cell)
        if mm is None:
            if steps:
                raise ValueError(f"{name}: 認証手順に mermaid-source がありません")
            return cell
        mermaid = self.mermaid_body(mm.group(1))
        if steps:
            self.check_steps(name, mermaid, steps)
        body = self.mermaid_init(mermaid) + mermaid
        diagram = f'<div class="mermaid-source">\n{html.escape(body, quote=False).replace("&gt;", ">")}\n</div>'
        return cell[:mm.start()] + diagram + cell[mm.end():]

    def row_html(self, name_no, cells, tags, inherited=()):
        """
        ## 1行分の `<tr>` を作る

        「分類」列(`cells[1]`)は出力しない(タグとして名前の下に出す)。

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `name_no` | `int` | (必須) | Markdown の行番号(エラーメッセージ用) |
        | `cells` | `list[str]` | (必須) | 元の7セル |
        | `tags` | `list[str]` | (必須) | この行のタグ(分類+認証要素+用途。子から引き継いだものを含む) |
        | `inherited` | `list[str]` | `()` | `tags` のうち、子の行から引き継いだもの(破線のバッジにする) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr>…</tr>` |
        """
        esc = html.escape
        fix = lambda s: s if s not in ("-", "") else '<span class="text-body-tertiary">—</span>'
        cell = lambda s: f"<td>{fix(self.fit_tables(self.md_inline(s)))}</td>"
        name = cells[0]
        flow = self.flow_html(f"{self.plain(name)}(auth.md {name_no}行目)", cells[3])
        badge = lambda t: (
            f'<button type="button" class="tag badge tag-child" title="下位の項目({self.CHILD_MARK})のタグ" data-tag="{esc(t)}">{esc(t)}</button>'
            if t in inherited else
            f'<button type="button" class="tag badge text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
        )
        badges = "".join(badge(t) for t in tags)
        return (
            f"""\
                <tr data-tags="{esc("|".join(tags))}">
                    <th scope="row" class="name">{self.md_inline(name)}<div class="tags">{badges}</div></th>
                    {cell(cells[2])}
                    {cell(flow)}
                    {cell(cells[4])}
                    {cell(cells[5])}
                    {cell(cells[6])}
                </tr>"""
        )

    def group(self, title, names, count):
        """
        ## 上部のタグボタン群(1系統分)を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(認証要素・用途) |
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

        出力のイメージ。

        | 行 | 内容 |
        |---|---|
        | 1 | 分類 |
        | 2 | **大分類** |
        | 3 | 分類 分類 分類 |
        | 4 | (空行) |
        | 5 | **大分類** |
        | 6 | 分類 分類 |
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
        all_paths, tags, child = [], [], []
        for no, c in rows:
            paths = self.category_paths(f"{self.plain(c[0])}(auth.md {no}行目)", c[1])
            cat, fac, use = self.tags_of(c, paths)
            all_paths.append(paths)
            tags.append(list(dict.fromkeys(cat + fac + use)))
            child.append(self.is_child(c[0]))
        tree = self.class_tree(all_paths)
        tags, inherited = self.inherit(tags, child)
        count = {}
        for ts in tags:
            for t in ts:
                count[t] = count.get(t, 0) + 1
        body = [self.row_html(no, c, ts, inh) for (no, c), ts, inh in zip(rows, tags, inherited)]
        self.rows, self.count, self.tree = len(body), count, tree
        filters = (
            self.class_group(self.groups[0], tree, count)
            + self.group(self.groups[1], list(self.factor), count)
            + self.group(self.groups[2], list(self.use), count)
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
        ## 確認用ページ(Bootstrap CDN + CSS + JS + mermaid CDN 込み)を書き出す

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
    conv = AuthMD2HTML("auth.md")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
