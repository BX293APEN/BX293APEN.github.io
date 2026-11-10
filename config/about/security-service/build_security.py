"""
# security-service.md → Bootstrap 5 用 HTML 変換

## 出力の構成(3ファイル)

| 出力 | 元になるファイル | 内容 |
|---|---|---|
| `security-service.html` | `template/security-service.html` + `security-service.md` | `<div id="security-app">` の断片のみ |
| `security-service.css` | `template/template.css`(攻撃表と共通) | ID を差し替え、このページ用の指定を追加したもの |
| `security-service.js` | `template/security-service.js` | `createTableSearch` を呼ぶだけ |

関数 `createTableSearch` 本体は `attack-script.js` を使い回すので、このスクリプトでは出力しない。

**編集は元になるファイル側で行う。** 出力側を直接編集しても、再生成すると上書きされる。
3ファイルは、`out`(HTML の出力先)と同じフォルダに書き出す。

## 使い方

```python
SecurityServiceMD2HTML("security-service.md").save()
```

| コマンド | 内容 |
|---|---|
| `python3 build_security.py` | 3ファイルを書き出す |
| `python3 build_security.py --preview` | 確認用ページも書き出す |
| `python3 build_security.py --osi` | 各サービスの OSI 層の割り当て一覧を表示する |
"""
import re, html, os, sys


class SecurityServiceMD2HTML:
    """
    ## Markdown の表を、タグ検索付きの Bootstrap 用 HTML に変換するクラス

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・元ファイルの読み込み |
    | `load_words` | OSI 層の割り当てルール・CSS の差分・確認用ページの定義を読み込む |
    | `plain` | HTML タグを除いた文字列にする |
    | `parse` | Markdown の表を行データに変換する |
    | `inspect_text` | 説明の「検査箇所」の項目(`<li>`)を取り出す |
    | `layers_in` | 「検査箇所」の文字列を OSI 層の番号に変換する |
    | `osi_of` | 各行の OSI 層と、その根拠を決める |
    | `tags_of` | 行ごとにタグ(分類・OSI層)を決める |
    | `row_html` | 1行分の `<tr>` を作る |
    | `group` | 上部のタグボタン群を作る |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `osi_table` | OSI 層の割り当て一覧(確認用)を Markdown の表で返す |
    | `save_html` | HTML の断片を書き出す |
    | `save_css` | CSS を書き出す |
    | `save_js` | JavaScript を書き出す |
    | `save` | 上の3つをまとめて書き出す |
    | `save_preview` | 単体で開ける確認用ページを書き出す(任意) |
    """

    CSS = "security-service.css"   # 出力する CSS のファイル名
    JS = "security-service.js"     # 出力する JavaScript のファイル名
    LIB_JS = "attack-script.js"    # 共通の JavaScript(`createTableSearch`)。確認用ページだけが読み込む

    NONE_TAG = "OSI層なし"
    LAYERS = {
        1: "L1 物理層",
        2: "L2 データリンク層",
        3: "L3 ネットワーク層",
        4: "L4 トランスポート層",
        5: "L5 セッション層",
        6: "L6 プレゼンテーション層",
        7: "L7 アプリケーション層",
    }

    # ## 層の名前 → 番号(説明の「検査箇所」の読み取りに使う。「〜層」の「〜」の部分)
    LAYER_NAMES = {
        "物理": 1,
        "データリンク": 2,
        "ネットワーク": 3,
        "トランスポート": 4,
        "セッション": 5,
        "プレゼンテーション": 6,
        "アプリケーション": 7,
    }
    CHILD_MARKS = "└┗"   # 名前の先頭にこの文字があれば子の項目

    def __init__(
        self,
        src,
        out=None,
        template="template/security-service.html",
        css_template="template/template.css",
        js_template="template/security-service.js",
    ):
        """
        ## 初期化

        相対パスは、このスクリプトのあるフォルダを基準に解決する。

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `src` | `str` | (必須) | 入力 Markdown |
        | `out` | `str` または `None` | `src` の拡張子を `.html` にしたもの | 出力 HTML |
        | `template` | `str` | `"template/security-service.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template/template.css"` | CSS の元ファイル(攻撃表と共通) |
        | `js_template` | `str` | `"template/security-service.js"` | JavaScript の元ファイル |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        self.out = self._path(out) if out else f"{os.path.splitext(self.src)[0]}.html"
        self.template = self._read(template)
        self.css_base = self._read(css_template)
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
        ## OSI 層の割り当てルール・CSS の差分・確認用ページを読み込む

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.osi_rules` | `list[tuple[str, list[int]]]` | (サービス名にマッチする正規表現, OSI 層の番号) の一覧。上から順に見て、最初にマッチしたものを使う |
        | `self.css_replace` | `list[tuple[str, str]]` | CSS の元ファイルで置換する (旧, 新) の一覧 |
        | `self.css_extra` | `str` | CSS の末尾に追加する、このページ固有の指定 |
        | `self.prev` | `str` | 確認用ページの雛形 |

        ## OSI 層の決め方(上から順に優先)

        | 優先 | 方法 | 内容 |
        |---|---|---|
        | 1 | 説明の「検査箇所」 | Markdown に `検査箇所：…` と書かれている行は、その記載どおりにする(下の変換表) |
        | 2 | `osi_rules` | 下の表のとおり、判断で割り当てたもの(自動判定ではない) |
        | 3 | 親子の関係 | 子の項目(`└` `┗`)は親から引き継ぐ。親の項目は子の層の和集合にする |

        ### 「検査箇所」の変換

        | 記載 | OSI 層 |
        |---|---|
        | `ネットワーク層` `トランスポート層` `アプリケーション層` など、OSI の層の名前 | その層(ネットワーク層=L3、トランスポート層=L4、アプリケーション層=L7) |
        | `A層〜B層` | A から B までのすべての層(例: ネットワーク層〜アプリケーション層 = L3〜L7) |
        | `全層` | L1〜L7 のすべて |
        | `エンドポイント層` | OSI の層ではないため「OSI層なし」 |

        ### `osi_rules`(判断で割り当てたもの)

        | サービス | 層 | 根拠 |
        |---|---|---|
        | パケットフィルタリング型・ダイナミック型・ステートフル型 | L3, L4 | 本文に「第3層・第4層で動作」とある |
        | アプリケーションゲートウェイ型 | L7 | 本文に「アプリケーション層(OSI第7層)」とある |
        | UTM | L3, L4, L7 | FW・IDS/IPS・URL フィルタ等を統合している |
        | IDS・NIDS・IPS・NDR | L3, L4, L7 | パケットのヘッダとペイロードを検査する |
        | 検疫ネットワーク | L2, L3 | 接続前の検査と隔離ネットワーク(VLAN 等)による接続制御 |
        | ZTNA | L4, L7 | アプリケーション単位の制御と、SPA(1パケット認可) |
        | DDoS 対策サービス | L3, L4 | BGP・DNS の切り替えで大量のパケットを迂回・選別する |
        | CDN・DNSSEC・CSP・WAF・WAAP・各プロキシ・URL フィルタリング・RBI・迷惑メール対策・送信ドメイン認証・CASB・DLP | L7 | HTTP・DNS・SMTP 等のアプリケーション層のプロトコルを扱う |
        | 通信の暗号化 | L3, L5, L6, L7 | IPsec(L3)、TLS(L5・L6)、SSH・STARTTLS(L7) |
        | ダークネット監視 | L3 | 未使用の IP アドレス空間に届くパケットを観測する |
        | 上記以外 | OSI層なし | 端末・データ・運用・物理が対象で、通信の層に当てはまらない |

        """
        self.osi_rules = [
            (r"^(パケットフィルタリング型|ダイナミックパケットフィルタリング型|ステートフルパケットフィルタリング型)", [3, 4]),
            (r"^アプリケーションゲートウェイ型", [7]),
            (r"^UTM", [3, 4, 7]),
            (r"^(IDS$|NIDS|IPS|NDR)", [3, 4, 7]),
            (r"^検疫ネットワーク", [2, 3]),
            (r"^ZTNA", [4, 7]),
            (r"^DDoS対策サービス", [3, 4]),
            (r"^(CDN|DNSSEC|CSP\b|WAF$|WAAP$|フォワードプロキシ|リバースプロキシ|メールプロキシ|URLフィルタリング|RBI|迷惑メール対策|送信ドメイン認証|CASB|DLP)", [7]),
            (r"^通信の暗号化", [3, 5, 6, 7]),
            (r"^ダークネット監視", [3]),
        ]

        # ## CSS の置換(攻撃表用 → このページ用)
        self.css_replace = [
            ("attack-app", "security-app"),
            ("attack-style.css", self.CSS),
            ("サイバー攻撃まとめ表", "セキュリティサービス表"),
            ("攻撃手法", "サービスの種類"),
        ]

        self.css_extra = """

/* ## このページ固有の追加指定(攻撃表用の CSS との差分)

| 項目 | 内容 | 理由 |
|---|---|---|
| 説明列の幅 | 2列目を `40rem` にする | 長い箇条書きが多く、他の列と同じ `17rem` だと縦に長くなりすぎるため |
| 入れ子の表 | 説明セル内の `<table>` では、見出しの固定(sticky)・最小幅・全体幅・背景の指定を打ち消す | 表全体用の指定が入れ子の表にも当たり、見出しが固定されたり列が広がりすぎたりするため |

`> table > tbody > tr > td` のように子セレクタで指定し、入れ子の表のセルには当たらないようにしている。
*/
#security-app .scroller > table > thead > tr > th:nth-child(2),
#security-app .scroller > table > tbody > tr > td:nth-child(2) {
  min-width: 40rem;
}
#security-app td table {
  width: auto;
  min-width: 0;
  margin: .25rem 0;
}
#security-app td table th,
#security-app td table td {
  min-width: 0;
  position: static;
}
#security-app td table td {
  background: transparent;
}
"""

        self.prev = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>セキュリティサービス(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="__LIB_JS__"></script>
<script src="__JS__"></script>
</body>
</html>
"""

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

    def parse(self):
        """
        ## Markdown の表を行データにする

        `## ` の見出しを分類名として使う。見出し行・区切り行(`| --- |`)は読み飛ばす。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行リスト | `list[tuple[str, list[str]]]` | (分類名, 3セル) |
        """
        rows, sec = [], None
        with open(self.src, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for ln in lines:
            if ln.startswith("## "):
                sec = ln[3:].strip()
            elif ln.startswith("|") and not re.match(r"^\|[\s\-:|]+\|$", ln):
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                assert len(cells) == 3, (len(cells), ln[:60])
                if self.plain(cells[0]) == "サービスの種類":
                    continue
                rows.append((sec, cells))
        return rows

    @staticmethod
    def inspect_text(desc):
        """
        ## 説明セルから「検査箇所」の項目(`<li>検査箇所…</li>`)を取り出す

        `<li>検査箇所：ネットワーク層</li>` のほか、
        `<li>検査箇所<ul><li>ネットワーク層(IP)</li>…</ul></li>` のように入れ子になっている書き方にも対応する。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `desc` | `str` | 説明セルの HTML |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` または `None` | 該当する `<li>…</li>`。なければ `None` |
        """
        m = re.search(r"<li>\s*検査箇所", desc)
        if not m:
            return None
        depth = 0
        for t in re.finditer(r"<li\b|</li>", desc[m.start():]):
            depth += -1 if t.group() == "</li>" else 1
            if depth == 0:
                return desc[m.start(): m.start() + t.end()]
        return desc[m.start():]

    def layers_in(self, text):
        """
        ## 「検査箇所」の文字列を OSI 層の番号に変換する

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `text` | `str` | `inspect_text` の戻り値 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 層のリスト | `list[int]` | OSI 層の番号(昇順)。OSI の層でないもの(エンドポイント層)だけなら空リスト |
        """
        t = self.plain(text)
        if "全層" in t:
            return sorted(self.LAYERS)
        names = "|".join(self.LAYER_NAMES)
        found = set()
        for a, b in re.findall(rf"({names})層\s*〜\s*({names})層", t):
            found.update(range(self.LAYER_NAMES[a], self.LAYER_NAMES[b] + 1))
        found.update(self.LAYER_NAMES[n] for n in re.findall(rf"({names})層", t))
        return sorted(found)

    def osi_of(self, rows):
        """
        ## 各行の OSI 層と、その根拠を決める

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `rows` | `list[tuple[str, list[str]]]` | `parse` の戻り値 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 層のリスト | `list[list[int]]` | 行ごとの OSI 層の番号(昇順)。該当なしは空リスト |
        | 根拠のリスト | `list[str]` | 行ごとの根拠。`検査箇所`・`ルール`・`親から継承`・`子の和集合`・`該当なし` のどれか |
        """
        names = [self.plain(c[0]) for _, c in rows]
        mark = f"^[{self.CHILD_MARKS}]"
        is_child = [bool(re.match(mark, n)) for n in names]
        names = [re.sub(mark + r"\s*", "", n) for n in names]

        own, basis = [], []
        for n, (_, c) in zip(names, rows):
            text = self.inspect_text(c[1])
            if text is not None:                                  # 1. 説明の「検査箇所」
                own.append(self.layers_in(text))
                basis.append("検査箇所")
                continue
            rule = next((ly for rx, ly in self.osi_rules if re.search(rx, n)), None)
            own.append(rule)                                      # 2. osi_rules
            basis.append("ルール" if rule is not None else None)

        layers, children, parent = [None] * len(rows), {}, None  # 3. 親子の関係
        for i, child in enumerate(is_child):
            if not child:
                parent = i
                children[i] = []
                layers[i] = own[i]
            else:
                assert parent is not None, names[i]
                children[parent].append(i)
                if own[i] is not None:
                    layers[i] = own[i]
                else:
                    layers[i] = list(layers[parent] or [])
                    basis[i] = "親から継承" if layers[i] else "該当なし"
        for p, kids in children.items():
            if layers[p] is None:
                layers[p] = sorted({ly for k in kids for ly in layers[k]})
                basis[p] = "子の和集合" if layers[p] else "該当なし"
        return layers, basis

    def tags_of(self, sec, layers):
        """
        ## 行のタグを (分類, OSI層) で返す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `sec` | `str` | 分類名(`## ` の見出し) |
        | `layers` | `list[int]` | `osi_of` で決めた OSI 層の番号 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タプル | `tuple[list[str], list[str]]` | 分類のタグ・OSI 層のタグ(該当なしは `OSI層なし`) |
        """
        return [sec], [self.LAYERS[ly] for ly in layers] or [self.NONE_TAG]

    def row_html(self, cells, tags):
        """
        ## 1行分の `<tr>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 元の3セル |
        | `tags` | `list[str]` | この行のタグ(分類+OSI層) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr>…</tr>` |
        """
        esc = html.escape
        fix = lambda s: s if s not in ("-", "") else '<span class="text-body-tertiary">—</span>'
        badges = "".join(
            f'<button type="button" class="tag badge text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags
        )
        return (
            f"""\
<tr data-tags="{esc("|".join(tags))}">
    <th scope="row" class="name">{cells[0]}<div class="tags">{badges}</div></th>
    <td>{fix(cells[1])}</td>
    <td>{fix(cells[2])}</td>
</tr>"""
        )

    @staticmethod
    def group(title, names, count):
        """
        ## 上部のタグボタン群(1系統分)を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(分類・OSI層) |
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
            for n in names
            if n in count
        )
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
        | HTML | `str` | テンプレートの `__ROWS__` と `__FILTERS__` を置換したもの |

        行数は `self.rows` に入る。
        """
        rows = self.parse()
        layers, _ = self.osi_of(rows)
        body, count = [], {}
        for (sec, c), ly in zip(rows, layers):
            cat, osi = self.tags_of(sec, ly)
            tags = cat + osi
            for t in tags:
                count[t] = count.get(t, 0) + 1
            body.append(self.row_html(c, tags))
        self.rows = len(body)
        sections = list(dict.fromkeys(sec for sec, _ in rows))   # 出現順
        filters = self.group("分類", sections, count) + self.group(
            "OSI層", list(self.LAYERS.values()) + [self.NONE_TAG], count
        )
        return self.template.replace("__ROWS__", "\n".join(body)).replace("__FILTERS__", filters)

    def osi_table(self):
        """
        ## OSI 層の割り当て一覧(確認用)を Markdown の表で返す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 表 | `str` | `#`・サービス名・OSI 層・根拠の4列の Markdown の表 |
        """
        rows = self.parse()
        layers, basis = self.osi_of(rows)
        lines = ["| # | サービス | OSI層 | 根拠 |", "|---|---|---|---|"]
        for i, ((_, c), ly, b) in enumerate(zip(rows, layers, basis), 1):
            text = ", ".join(f"L{n}" for n in ly) or "なし"
            lines.append(f"| {i} | {self.plain(c[0])} | {text} | {b} |")
        return "\n".join(lines)

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

        `css_base` の ID などを置換し、末尾に `css_extra` を足したものを書き出す。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        css = self.css_base
        for old, new in self.css_replace:
            css = css.replace(old, new)
        self._write(self.out_css, css + self.css_extra)
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
        共通の `attack-script.js` は同じフォルダに置いておくこと。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        path = f"{os.path.splitext(self.out)[0]}-preview.html"
        page = (
            self.prev.replace("__CSS__", self.CSS)
            .replace("__LIB_JS__", self.LIB_JS)
            .replace("__JS__", self.JS)
            .replace("__FRAGMENT__", self.build())
        )
        self._write(path, page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = SecurityServiceMD2HTML("security-service.md")
    if "--osi" in sys.argv:
        print(conv.osi_table())
    else:
        conv.save()
        if "--preview" in sys.argv:
            conv.save_preview()
