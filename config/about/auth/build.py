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
    | `category_tags` | 「分類」列から、分類タグを作る(列そのものは表示しない) |
    | `tags_of` | 行ごとにタグを決める |
    | `md_inline` | セル内に残った Markdown の強調(`**…**`)を `<strong>` にする |
    | `fit_tables` | セルの中の `<table>` を、列幅・見出しの固定が崩れないように整える |
    | `mermaid_body` | `mermaid-source` の中身から、mermaid の本文を取り出す(`<br>` を改行に戻す) |
    | `table_steps` | 「認証手順」セルの手順表から、手順番号を取り出す |
    | `step_numbers` | mermaid 内のメッセージから、手順番号を取り出す |
    | `check_steps` | mermaid の手順番号と、手順表の手順番号が合っているか確認する |
    | `mermaid_init` | mermaid の先頭に付ける `%%{init: …}%%` を作る |
    | `flow_html` | 「認証手順」セルの HTML(整えた図 + 手順表)を作る |
    | `row_html` | 1行分の `<tr>` を作る |
    | `group` | 上部のタグボタン群を作る |
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
    | 2 分類 | `主分類<br>(補足)` | **表示しない**。主分類と補足の両方を、タグにする |
    | 3 概要 | HTML | そのまま |
    | 4 認証手順 | `<div class="mermaid-source">…</div>` + `<table>…</table>` | 図(mermaid)を整える + 手順表はそのまま |
    | 5 メリット | HTML | そのまま |
    | 6 デメリット | HTML | そのまま |
    | 7 主な用途 | HTML | そのまま |

    ## 認証手順セルの決まり

    | 決まり | 内容 |
    |---|---|
    | 図 | `<div class="mermaid-source">` の中に mermaid を書く。Markdown の表は1行なので、mermaid の改行は `<br>` で表す |
    | 手順表 | 図の後ろに `<table>` で書く。`<tbody>` の行のうち、先頭セルが `<b>N</b>` で始まる行が1手順(`rowspan` で複数行にまたがる手順は、先頭の行だけ数える) |
    | 手順番号 | mermaid のメッセージ・Note の文頭を `N.` にする。`N` は手順表の `<b>N</b>` と一致させる(合わないとエラー) |
    | 1手順に複数メッセージ | 同じ番号を付けてよい(番号は小さい順に並べる) |
    | 手順表の番号 | `1` から順に並べる(飛んでいたり、逆順だったりするとエラー) |
    | 図の前後 | 補足の説明など。そのまま残す |
    | 手順表があるのに図がない | エラー |
    | 手順表がない | 図があれば、図だけ整える(手順番号の突き合わせはしない)。図も表もなければ、そのまま出す |
    """

    CSS = "auth-style.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "auth-script.js"    # 出力する JavaScript のファイル名(確認用ページも読み込む)
    COLS = 7                 # Markdown の表の列数
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
        | `self.alias` | `dict[str, str]` | 分類タグの別名 → 正式名(表記ゆれをそろえる) |
        | `self.factor` | `dict[str, str]` | 認証要素タグ名 → 認証技術名にマッチする正規表現 |
        | `self.use` | `dict[str, str]` | 用途タグ名 → 「主な用途」列にマッチする正規表現 |
        | `self.topic` | `dict[str, str]` | トピックタグ名 → 認証技術名にマッチする正規表現 |
        | `self.min_count` | `int` | 分類タグを上部のボタンに出す最小件数(これ未満は、行のタグとして表示するだけ) |
        | `self.prev` | `str` | 確認用ページのひな形 |
        """
        GROUPS = ("分類", "認証要素", "用途", "トピック")

        # ## 分類タグの別名
        # 「分類」列の語を、タグにするときの表記ゆれの補正。
        #
        # | キー(列の語) | 値(タグ名) | 理由 |
        # |---|---|---|
        # | `AAA認証・認可・課金` | `AAA` | `<br>` で折り返した括弧内を短くする |
        # | `パスワードを使わない認証` | `パスワードレス認証` | 同じ意味の分類を1つにまとめる |
        # | `パスワードレス` | `パスワードレス認証` | 同上 |
        ALIAS = {
            "AAA認証・認可・課金": "AAA",
            "パスワードを使わない認証": "パスワードレス認証",
            "パスワードレス": "パスワードレス認証",
        }

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

        # ## トピックタグ(認証技術名にマッチすれば付与)
        #
        # | キー | 値 |
        # |---|---|
        # | タグ名 | 認証技術名にマッチする正規表現 |
        TOPIC = {
            "チャレンジレスポンス": r"チャレンジ|CHAP",
            "署名・証跡": r"署名|タイムスタンプ",
            "MAC": r"MAC",
            "FIDO": r"FIDO|WebAuthn|パスキー|CTAP",
            "OTP": r"ワンタイム|OTP|セキュリティトークン",
            "リスク判定・継続的認証": r"リスクベース|継続的|UEBA|行動認証|3Dセキュア",
            "SSO・ID連携": r"SSO|シングルサインオン|SAML|OAuth|OpenID|PKCE|JWT|Kerberos|フェデレーション",
            "OAuth・OIDC系": r"OAuth|PKCE|OpenID|JWT",
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
        self.groups, self.alias, self.factor, self.use, self.topic, self.prev = GROUPS, ALIAS, FACTOR, USE, TOPIC, PREVIEW
        self.min_count = 2
        names = [n for d in (FACTOR, USE, TOPIC) for n in d]
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

    def category_tags(self, cell):
        """
        ## 「分類」列から分類タグを作る

        `主分類<br>(補足)` の形式を、主分類・補足の2つのタグにする。
        補足がない場合は主分類だけ。`<br>` で折り返された括弧も1つにつなげる。

        | 元のセル | タグ |
        |---|---|
        | `生体認証<br>(身体的特徴)` | `生体認証` `身体的特徴` |
        | `総称<br>(生体認証)` | `総称` `生体認証` |
        | `XML署名の形式` | `XML署名の形式` |
        | `プロトコル<br>(AAA<br>認証・認可・課金)` | `プロトコル` `AAA`(別名で補正) |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cell` | `str` | 「分類」列のセル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タグのリスト | `list[str]` | 重複なし・別名補正済み |
        """
        s = self.plain(re.sub(r"<br\s*/?>", "", cell))
        m = re.match(r"^(.*?)\s*[(\uff08](.*)[)\uff09]$", s)
        words = [m.group(1), m.group(2)] if m else [s]
        tags = []
        for w in words:
            w = self.alias.get(w.strip(), w.strip())
            if w and w not in tags:
                tags.append(w)
        return tags

    def tags_of(self, cells):
        """
        ## 行のタグを系統ごとに返す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 7セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タプル | `tuple[list, list, list, list]` | `self.groups` の順(分類・認証要素・用途・トピック)のタグ |
        """
        name, use = self.plain(cells[0]), self.plain(cells[6])
        return (
            self.category_tags(cells[1]),
            [t for t, rx in self.factor.items() if re.search(rx, name)],
            [t for t, rx in self.use.items() if re.search(rx, use)],
            [t for t, rx in self.topic.items() if re.search(rx, name)],
        )

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
        return html.unescape(re.sub(r"<br\s*/?>", "\n", raw)).strip()

    @staticmethod
    def table_steps(cell):
        """
        ## 手順表から、手順番号を取り出す

        `<tr>` の先頭セルが `<b>N</b>` で始まる行を、1手順とみなす。
        `rowspan` で手順の続きになっている行は、先頭セルが別の内容なので数えない。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cell` | `str` | 「認証手順」セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 番号のリスト | `list[int]` | 表に出てきた順。手順表がなければ空 |
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

        | 確認 | 合わないとき |
        |---|---|
        | 手順表の番号が `1` から順に並んでいる | `ValueError` |
        | mermaid の番号が小さい順に並んでいる | `ValueError` |
        | mermaid の番号が、手順表の番号と過不足なく同じ | `ValueError` |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `name` | `str` | 認証技術名(エラーメッセージ用) |
        | `mermaid` | `str` | mermaid の本文 |
        | `steps` | `list[int]` | 手順表の手順番号(`table_steps` の結果) |
        """
        nums = self.step_numbers(mermaid)
        if steps != list(range(1, len(steps) + 1)):
            raise ValueError(f"{name}: 手順表の番号 {steps} が、1 から順に並んでいません")
        if nums != sorted(nums) or sorted(set(nums)) != steps:
            raise ValueError(f"{name}: mermaid の手順番号 {nums} が、手順表の番号 {steps} と合いません")

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

    def row_html(self, name_no, cells, tags):
        """
        ## 1行分の `<tr>` を作る

        「分類」列(`cells[1]`)は出力しない(タグとして名前の下に出す)。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `name_no` | `int` | Markdown の行番号(エラーメッセージ用) |
        | `cells` | `list[str]` | 元の7セル |
        | `tags` | `list[str]` | この行のタグ(分類+認証要素+用途+トピック) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr>…</tr>` |
        """
        esc = html.escape
        fix = lambda s: s if s not in ("-", "") else '<span class="text-body-tertiary">—</span>'
        cell = lambda s: f"<td>{fix(self.fit_tables(self.md_inline(s)))}</td>"
        name = cells[0]
        flow = self.flow_html(f"{self.plain(name)}(auth.md {name_no}行目)", cells[3])
        badges = "".join(
            f'<button type="button" class="tag badge text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags)
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

    def group(self, title, names, count, min_count=1):
        """
        ## 上部のタグボタン群(1系統分)を作る

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `title` | `str` | (必須) | 系統名(分類・認証要素・用途・トピック) |
        | `names` | `list[str]` | (必須) | タグ名の候補(表示順) |
        | `count` | `dict[str, int]` | (必須) | タグ名 → 該当件数 |
        | `min_count` | `int` | `1` | この件数未満のタグは表示しない |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | ボタンの並び。表示するタグがなければ空文字列 |
        """
        esc = html.escape
        btns = "".join(
            f"""\
<button type="button" class="btn btn-sm btn-outline-primary" data-tag="{esc(n)}">
                    {esc(n)} 
                    <span class="badge text-bg-light">{count[n]}</span>
                </button>
                """
            for n in names if count.get(n, 0) >= min_count)
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

    def build(self):
        """
        ## HTML 全体を組み立てる

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | テンプレートの `__ROWS__` と `__FILTERS__` を置換したもの(改行は CRLF にそろえる) |

        行数は `self.rows` に、タグごとの件数は `self.count` に入る。
        """
        body, count, cat_order = [], {}, []
        for no, c in self.parse():
            cat, fac, use, top = self.tags_of(c)
            tags = list(dict.fromkeys(cat + fac + use + top))
            for t in tags:
                count[t] = count.get(t, 0) + 1
            cat_order += [t for t in cat if t not in cat_order]
            body.append(self.row_html(no, c, tags))
        self.rows, self.count = len(body), count
        filters = (
            self.group(self.groups[0], cat_order, count, self.min_count)
            + self.group(self.groups[1], list(self.factor), count)
            + self.group(self.groups[2], list(self.use), count)
            + self.group(self.groups[3], list(self.topic), count)
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
