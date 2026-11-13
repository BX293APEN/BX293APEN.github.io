import html, os, re, sys
from bs4 import BeautifulSoup


class NetConnectionSrc2HTML:
    """
    ## ネットワーク接続機器の表(HTML)を、タグ検索付きの Bootstrap 用 HTML に変換するクラス

    機器ごとに 1 つの `<tbody>` にまとめ、`<tbody>` 単位で絞り込む。
    `rowspan` を含む行を 1 行ずつ隠すと表が崩れるため。

    「動作するOSI層」列は表から削除し、次の 2 系統のタグに変換する。

    | タグの系統 | 元になる情報 | 付ける場所 |
    |---|---|---|
    | OSI層 | 「動作するOSI層」列の `第N層` | 機器名のセル(全行の合算)・種類・規格名のセル(その行の層だけ) |
    | 接続方式 | 「動作するOSI層」列の2行目(`LANケーブル` `電波` など) | 機器名のセル(全行の合算) |

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `load_words` | OSI層・接続方式・確認用ページの定義を読み込む |
    | `osi_of` | 「動作するOSI層」セルから、層の集合と接続方式の元表記を取り出す |
    | `conns_of` | 接続方式の元表記を、接続方式タグに変換する |
    | `parse` | 元の表を機器ごとのまとまりに分解する |
    | `tbody_html` | 1機器分の `<tbody>` を作る |
    | `thead_html` | 表の見出し行の中身を作る |
    | `group` | 上部のタグボタン群を作る |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `save_html` | HTML の断片を書き出す |
    | `save_css` | CSS を書き出す |
    | `save_js` | JavaScript を書き出す |
    | `save` | 上の3つをまとめて書き出す |
    | `save_preview` | 単体で開ける確認用ページを書き出す(任意) |

    ## ファイルの置き場所

    相対パスは、**実行時のカレントディレクトリではなく、このスクリプトのあるフォルダ**を基準に解決する。

    | ファイル | 場所 | 役割 |
    |---|---|---|
    | `net-connection-source.html` | `build.py` と同じフォルダ | 入力(元の表) |
    | `net-connection.html` | `build.py` と同じフォルダ | 出力(HTML の断片) |
    | `net-connection-style.css` | `build.py` と同じフォルダ | 出力(`template/` の複製) |
    | `net-connection-script.js` | `build.py` と同じフォルダ | 出力(`template/` の複製) |
    | `net-connection-preview.html` | `build.py` と同じフォルダ | 出力(確認用ページ。`--preview` 指定時) |
    | `template/net-connection-template.html` | `template/` | HTML テンプレート |
    | `template/net-connection-style.css` | `template/` | CSS の元ファイル |
    | `template/net-connection-script.js` | `template/` | JavaScript の元ファイル |

    ## 元の表の列

    | 列番号 | 見出し | 出力での扱い |
    |---|---|---|
    | 0 | 機器名 | `<th scope="rowgroup" class="name">` に変換し、OSI層・接続方式タグを追加する |
    | 1 | 動作するOSI層 | **削除**(タグに変換する) |
    | 2 | 説明 | そのまま |
    | 3 | 種類・規格名 | その行のOSI層タグを追加する(`-` の行は付けない) |
    | 4 | 特徴 | そのまま |
    """

    CSS = "net-connection-style.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "net-connection-script.js"    # 出力する JavaScript のファイル名(確認用ページも読み込む)

    COLS = 5          # 元の表の列数
    COL_NAME = 0      # 機器名
    COL_OSI = 1       # 動作するOSI層(削除してタグにする)
    COL_KIND = 3      # 種類・規格名
    COL_LAST = 4      # 特徴

    def __init__(
        self,
        src,
        out=None,
        template="template/net-connection-template.html",
        css_template="template/net-connection-style.css",
        js_template="template/net-connection-script.js",
    ):
        """
        ## 初期化

        相対パスは、このスクリプトのあるフォルダを基準に解決する。

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `src` | `str` | (必須) | 入力 HTML(元の表) |
        | `out` | `str` または `None` | `src` から `-source` を除いたもの | 出力 HTML。`src` と同じ名前にはできない(元ファイルを上書きしてしまうため) |
        | `template` | `str` | `"template/net-connection-template.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template/net-connection-style.css"` | CSS の元ファイル |
        | `js_template` | `str` | `"template/net-connection-script.js"` | JavaScript の元ファイル |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        self.out = self._path(out) if out else self._default_out(self.src)
        assert self.out != self.src, f"出力先が入力と同じです: {self.src}"
        self.template = self._read(template)
        self.css_text = self._read(css_template)
        self.js_text = self._read(js_template)
        out_dir = os.path.dirname(self.out)
        self.out_css = os.path.join(out_dir, self.CSS)
        self.out_js = os.path.join(out_dir, self.JS)
        self.rows = 0
        self.count = {}
        self.load_words()

    @staticmethod
    def _default_out(src):
        """
        ## 入力パスから出力パスを決める

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `src` | `str` | 入力のパス(例: `.../net-connection-source.html`) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 語尾の `-source` を除いたパス(例: `.../net-connection.html`)。`-source` が無ければ `-out` を付ける |
        """
        stem, ext = os.path.splitext(src)
        return f"{stem[:-len('-source')]}{ext}" if stem.endswith("-source") else f"{stem}-out{ext}"

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
        ## OSI層・接続方式・確認用ページの定義を読み込む

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.layers` | `dict[int, str]` | 層の番号 → 層の名前 |
        | `self.conn_names` | `list[str]` | 上部に出す「接続方式」のタグ名(表示順) |
        | `self.conn_map` | `dict[str, list[str]]` | 元の表記(「動作するOSI層」列の2行目) → 付与する接続方式タグ |
        | `self.prev` | `str` | 確認用ページのひな形(`__CSS__` `__JS__` `__FRAGMENT__` を置換する) |
        """
        # ## OSI参照モデルの層
        #
        # | 要素 | 型 | 説明 |
        # |---|---|---|
        # | キー | `int` | 層の番号(1〜7) |
        # | 値 | `str` | 層の名前 |
        LAYERS = {
            1: "物理層",
            2: "データリンク層",
            3: "ネットワーク層",
            4: "トランスポート層",
            5: "セッション層",
            6: "プレゼンテーション層",
            7: "アプリケーション層",
        }

        # ## 接続方式タグの表示順
        CONN_NAMES = [
            "LANケーブル", "ツイストペアケーブル", "光ファイバ", "銅線", "メタリック", "電話回線",
            "同軸ケーブル", "電力線", "屋内配線", "電波", "インターネット回線(共用)", "通信事業者網",
        ]

        # ## 元の表記 → 接続方式タグ
        #
        # 「動作するOSI層」列の2行目に書かれていた文字列を、そのままキーにする。
        # 知らない表記が出たら `conns_of` が `AssertionError` にする(分類漏れに気づけるように)。
        #
        # | キー(元の表記) | 値(接続方式タグ) | 補足 |
        # |---|---|---|
        # | `LANケーブル(ツイストペアケーブル)` | `LANケーブル` `ツイストペアケーブル` | 括弧書きも別のタグにする |
        # | `銅線(メタリック)` | `銅線` `メタリック` | 同上 |
        # | `電力線(屋内配線)` | `電力線` `屋内配線` | 同上 |
        # | `同軸ケーブル(HFC : 光ファイバ + 同軸ケーブル)` | `同軸ケーブル` `光ファイバ` | HFC は両方を使う |
        # | `電話回線(銅線)` | `電話回線` `銅線` | 電話回線は銅線を使う |
        # | `光ファイバ等(通信事業者網)` | `光ファイバ` `通信事業者網` | 括弧書きも別のタグにする |
        CONN_MAP = {
            "LANケーブル(ツイストペアケーブル)": ["LANケーブル", "ツイストペアケーブル"],
            "LANケーブル(ツイストペアケーブル) / 光ファイバ": ["LANケーブル", "ツイストペアケーブル", "光ファイバ"],
            "LANケーブル / 光ファイバ": ["LANケーブル", "光ファイバ"],
            "光ファイバ": ["光ファイバ"],
            "光ファイバ等(通信事業者網)": ["光ファイバ", "通信事業者網"],
            "銅線 / 光ファイバ": ["銅線", "光ファイバ"],
            "銅線(メタリック)": ["銅線", "メタリック"],
            "電話回線(銅線)": ["電話回線", "銅線"],
            "同軸ケーブル(HFC : 光ファイバ + 同軸ケーブル)": ["同軸ケーブル", "光ファイバ"],
            "電力線(屋内配線)": ["電力線", "屋内配線"],
            "電波": ["電波"],
            "インターネット回線等(共用)": ["インターネット回線(共用)"],
        }

        PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ネットワーク接続機器(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="__JS__"></script>
</body>
</html>
"""
        self.layers, self.conn_names, self.conn_map, self.prev = LAYERS, CONN_NAMES, CONN_MAP, PREVIEW

    # 「第3層」「第3〜7層」を見つける正規表現。`〜` は全角の波ダッシュ
    LAYER_RE = re.compile(r"第(\d)(?:〜(\d))?層")

    def layer_tag(self, n):
        """
        ## 層の番号からOSI層タグの文字列を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `n` | `int` | 層の番号(1〜7) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タグ | `str` | 例: `第7層 アプリケーション層` |
        """
        return f"第{n}層 {self.layers[n]}"

    def osi_of(self, td):
        """
        ## 「動作するOSI層」セルから、層の集合と接続方式の元表記を取り出す

        セルの中身は `<br>` で区切られた 1〜2 行。1行目が層、2行目(あれば)が接続方式。

        | 書き方 | 読み取る層 |
        |---|---|
        | `アプリケーション層 (第7層)` | 7 |
        | `トランスポート層〜アプリケーション層 (第4〜7層)` | 4, 5, 6, 7 |
        | `ネットワーク層 (第3層) + データリンク層 (第2層)` | 3, 2 |
        | `物理層 (第1層) 〜データリンク層 (第2層)` | 1, 2(`〜` でつないだ2つの間は埋める) |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `td` | BeautifulSoup の要素 | 「動作するOSI層」のセル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 層の集合 | `set[int]` | 動作する層の番号 |
        | 接続方式の元表記 | `str` または `None` | 2行目の文字列。無ければ `None` |
        """
        lines = [s.strip() for s in td.stripped_strings]
        assert len(lines) in (1, 2), f"OSI層セルの行数が想定外: {lines}"
        matches = list(self.LAYER_RE.finditer(lines[0]))
        assert matches, f"層を読み取れません: {lines[0]}"
        layers, prev = set(), None
        for m in matches:
            a = int(m.group(1))
            b = int(m.group(2) or a)
            layers.update(range(a, b + 1))
            if prev is not None and "〜" in lines[0][prev.end():m.start()]:   # `(第1層) 〜…(第2層)` の間を埋める
                lo, hi = sorted((int(prev.group(2) or prev.group(1)), a))
                layers.update(range(lo, hi + 1))
            prev = m
        medium = lines[1] if len(lines) == 2 else None
        assert medium is None or "第" not in medium, f"2行目が層の記述: {medium}"
        return layers, medium

    def conns_of(self, medium):
        """
        ## 接続方式の元表記を、接続方式タグに変換する

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `medium` | `str` または `None` | `osi_of` が返した元表記 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タグ | `list[str]` | 接続方式タグ。`None` なら空リスト |

        未知の表記は `AssertionError` にする(`CONN_MAP` への追加漏れに気づけるように)。
        """
        if medium is None:
            return []
        assert medium in self.conn_map, f"接続方式が未定義: {medium}"
        return self.conn_map[medium]

    def parse(self):
        """
        ## 元の表を機器ごとのまとまりに分解する

        `rowspan` で結合されたセルは、結合元のセルを覚えておいて各行に割り当てる。
        「動作するOSI層」列のセルは、ここでは読み取るだけで削除はしない(削除は `tbody_html`)。
        削除は読み込んだ DOM に対して行うので、呼ぶたびに元ファイルから読み直す。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 見出しと機器 | `tuple[list[str], list[dict]]` | 下表の2要素 |

        | 戻り値の要素 | 型 | 説明 |
        |---|---|---|
        | 1つ目 | `list[str]` | 見出し行の文字列(「動作するOSI層」列は除く) |
        | 2つ目 | `list[dict]` | 機器ごとの辞書(下表) |

        | 機器の辞書のキー | 型 | 説明 |
        |---|---|---|
        | `name` | BeautifulSoup の要素 | 機器名のセル |
        | `rows` | `list[dict]` | 機器に属する行(下表) |

        | 行の辞書のキー | 型 | 説明 |
        |---|---|---|
        | `tr` | BeautifulSoup の要素 | `<tr>` |
        | `osi` | BeautifulSoup の要素 | この行に適用される「動作するOSI層」のセル(結合されていれば結合元) |
        | `own_osi` | BeautifulSoup の要素 または `None` | この行に実体がある「動作するOSI層」のセル(結合されていれば `None`)。削除に使う |
        | `kind` | BeautifulSoup の要素 | 種類・規格名のセル |
        """
        soup = BeautifulSoup(self._read(self.src), "html.parser")
        table = soup.find("table")   # 最初の `<table>` が外側の表(入れ子の表は説明セルの中にある)
        heads = [th.get_text(strip=True) for th in table.thead.find_all("th")]
        assert len(heads) == self.COLS, heads
        heads.pop(self.COL_OSI)   # 動作するOSI層カラムは削除

        pending = {}   # 列番号 → [残り行数, 結合元のセル]
        groups = []
        for tr in table.find("tbody", recursive=False).find_all("tr", recursive=False):
            own = {}   # 列番号 → この行に実体があるセル
            tds = iter(tr.find_all("td", recursive=False))   # 入れ子の表の `td` は含めない
            for col in range(self.COLS):
                if pending.get(col, [0])[0] > 0:   # 上の行から結合されている列
                    pending[col][0] -= 1
                    continue
                td = next(tds)
                own[col] = td
                span = int(td.get("rowspan", 1))
                if span > 1:
                    pending[col] = [span - 1, td]
            assert next(tds, None) is None, "セル数が想定より多い行があります"
            assert self.COL_KIND in own, "種類・規格名が結合されている行があります"

            if self.COL_NAME in own:   # 機器名のセルが現れたら新しい機器
                groups.append({"name": own[self.COL_NAME], "rows": []})
            assert groups, "最初の行に機器名がありません"
            groups[-1]["rows"].append({
                "tr": tr,
                "osi": own.get(self.COL_OSI) or pending[self.COL_OSI][1],
                "own_osi": own.get(self.COL_OSI),
                "kind": own[self.COL_KIND],
            })

        for g in groups:   # 機器名の rowspan と行数が合っているか確認する
            span = int(g["name"].get("rowspan", 1))
            assert span == len(g["rows"]), (g["name"].get_text(" ", strip=True), span, len(g["rows"]))
        return heads, groups

    def badge(self, tag, color):
        """
        ## タグボタン(表中)1つ分の HTML を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `tag` | `str` | タグ名 |
        | `color` | `str` | Bootstrap の `text-bg-◯◯` の `◯◯`(`secondary` = OSI層 / `success` = 接続方式) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<button class="tag badge …" data-tag="…">…</button>` |
        """
        esc = html.escape
        return (f'<button type="button" class="tag badge text-bg-{color}" '
                f'data-tag="{esc(tag)}">{esc(tag)}</button>')

    def tbody_html(self, g):
        """
        ## 1機器分の `<tbody>` を作る

        | 変更する場所 | 内容 |
        |---|---|
        | 機器名のセル | `<th scope="rowgroup" class="name">` に変え、OSI層タグ(灰)と接続方式タグ(緑)を追加する |
        | 動作するOSI層のセル | 削除する |
        | 種類・規格名のセル | その行のOSI層タグ(灰)を追加する。`-` の行は付けない |

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `g` | `dict` | `parse` が返した機器の辞書 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tbody data-tags="…">…</tbody>` |
        | タグ | `list[str]` | この機器のタグ(OSI層 → 接続方式の順)。`<tbody>` の絞り込みに使う |
        """
        osi_all, conn_all = set(), set()
        for r in g["rows"]:
            layers, medium = self.osi_of(r["osi"])
            conns = self.conns_of(medium)
            osi_all |= layers
            conn_all |= set(conns)
            if r["kind"].get_text(strip=True) != "-":   # 種類・規格名のタグ = その行が使う層
                badges = "".join(self.badge(self.layer_tag(n), "secondary") for n in sorted(layers))
                r["kind"].append(BeautifulSoup(f'<div class="tags">{badges}</div>', "html.parser"))

        for r in g["rows"]:   # 結合されたセルは後続の行も参照するので、全行を読み終えてから削除する
            if r["own_osi"] is not None:
                r["own_osi"].decompose()   # 動作するOSI層カラムは削除(タグで表現する)

        osi_tags = [self.layer_tag(n) for n in sorted(osi_all)]
        conn_tags = [c for c in self.conn_names if c in conn_all]
        assert conn_all <= set(self.conn_names), conn_all - set(self.conn_names)
        tags = osi_tags + conn_tags

        th = g["name"]
        th.name = "th"   # `<td>` → `<th scope="rowgroup">`(CSS の `.name` で左端に固定される)
        th["scope"] = "rowgroup"
        th["class"] = [c for c in th.get("class", []) if c != "text-nowrap"] + ["name"]
        badges = (
            "".join(self.badge(t, "secondary") for t in osi_tags)
            + "".join(self.badge(t, "success") for t in conn_tags)
        )
        th.append(BeautifulSoup(f'<div class="tags">{badges}</div>', "html.parser"))

        rows = "\n".join("                " + str(r["tr"]) for r in g["rows"])
        body = f'            <tbody data-tags="{html.escape("|".join(tags))}">\n{rows}\n            </tbody>'
        return body, tags

    @staticmethod
    def thead_html(heads):
        """
        ## 表の見出し行(`<tr class="r1">`)の中身を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `heads` | `list[str]` | 見出しの文字列。1つ目だけ `name` クラスを付ける(左端に固定するため) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<th>…</th>` の並び |
        """
        return "".join(
            f'<th class="name">{h}</th>' if i == 0 else f"<th>{h}</th>" for i, h in enumerate(heads))

    def group(self, title, names, count):
        """
        ## 上部のタグボタン群(1系統分)を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(OSI層・接続方式) |
        | `names` | `list[str]` | タグ名の候補 |
        | `count` | `dict[str, int]` | タグ名 → 該当件数。0件のタグは表示しない |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | ボタンの並び |
        """
        esc = html.escape
        btns = "".join(
            f"""\
<button type="button" class="btn btn-sm btn-outline-primary" data-tag="{esc(n)}">
                    {esc(n)} 
                    <span class="badge text-bg-light">{count[n]}</span>
                </button>
                """
            for n in names if n in count)
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
        | HTML | `str` | テンプレートの `__FILTERS__` `__THEAD__` `__ROWS__` を置換したもの。改行コードはテンプレートに合わせる |

        機器数は `self.rows`、タグごとの件数は `self.count` に入る。
        """
        heads, groups = self.parse()
        count, bodies = {}, []
        for g in groups:
            body, tags = self.tbody_html(g)
            for t in tags:
                count[t] = count.get(t, 0) + 1
            bodies.append(body)
        self.rows, self.count = len(bodies), count
        filters = (
            self.group("OSI層", [self.layer_tag(n) for n in sorted(self.layers)], count)
            + self.group("接続方式", self.conn_names, count)
        )
        out = (self.template.replace("__FILTERS__", filters)
               .replace("__THEAD__", self.thead_html(heads))
               .replace("__ROWS__", "\n".join(bodies)))
        newline = "\r\n" if "\r\n" in self.template else "\n"   # テンプレートの改行コードにそろえる
        return out.replace("\r\n", "\n").replace("\n", newline)

    def save_html(self):
        """
        ## HTML の断片を `self.out` に書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        out = self.build()
        self._write(self.out, out)
        print(self.rows, "devices,", len(out), "bytes ->", self.out)
        print(self.count)
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
        ## 確認用ページ(Bootstrap CDN + CSS + JS 込み)を書き出す

        貼り付け先のページがなくても、ブラウザで開くだけで動作を確認できる。
        `self.out` の拡張子の前に `-preview` を付けたファイルに書き出す。
        読み込む CSS・JS は `self.out_css` `self.out_js`(`save` で書き出したもの)と同じフォルダにある。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        path = f"{os.path.splitext(self.out)[0]}-preview.html"
        page = (self.prev.replace("__CSS__", self.CSS).replace("__JS__", self.JS)
                .replace("__FRAGMENT__", self.build()))
        self._write(path, page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = NetConnectionSrc2HTML("net-connection-source.html", "net-connection.html")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
