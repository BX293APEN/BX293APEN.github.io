import html, json, os, sys, textwrap
from bs4 import BeautifulSoup


class MailAuthSrc2HTML:
    """
    ## メール認証・暗号化の表(HTML)を、タグ検索付きの Bootstrap 用 HTML に変換するクラス

    net-connection の build.py と同じ作り。方式ごとに 1 つの `<tbody>` にまとめ、`<tbody>` 単位で絞り込む。

    元の表にある次の2つの情報は、表から削除して**タグ**に変換し、方式名のセルに付ける。

    | タグの系統 | 元になる情報 | 色 | 付ける場所 |
    |---|---|---|---|
    | 分類 | セル結合の見出し行(`<th colspan="7">` 本文の暗号化・電子署名 など) | 灰 | 方式名のセル |
    | 利用状況 | 「利用状況」列の `〇` `✖` `△` | 緑 / 赤 / 黄 | 方式名のセル |

    | 利用状況の記号 | タグ | 色 |
    |---|---|---|
    | `〇` | `〇 : 推奨` | 緑 |
    | `✖` | `✖ : 非推奨` | 赤 |
    | `△` | `△ : 端末による` | 黄 |

    ## ファイル

    | ファイル | 場所 | 役割 |
    |---|---|---|
    | `mail-auth-source.html` | `build.py` と同じフォルダ | 入力(元の表) |
    | `mail-auth.html` | 同上 | 出力(HTML の断片) |
    | `mail-auth-style.css` / `mail-auth-script.js` | 同上 | 出力(`template/` の複製) |
    | `mail-auth-preview.html` | 同上 | 確認用ページ(`--preview` 指定時) |
    | `template/…` | `template/` | HTML・CSS・JS の元ファイル |

    ## 元の表の列

    | 列番号 | 見出し | 出力での扱い |
    |---|---|---|
    | 0 | 方式 | `<th scope="rowgroup" class="name">` に変換し、分類・利用状況タグを追加 |
    | 1 | 正式名称 | そのまま |
    | 2 | 規格 | そのまま |
    | 3 | 証明書・鍵 | そのまま |
    | 4 | 手順 | そのまま(Mermaid・入れ子の表を含む) |
    | 5 | 利用状況 | **削除**(タグに変換する) |
    | 6 | 概要 | そのまま |

    `STARTTLS` `Implicit TLS` のように 1 方式が複数行(`rowspan`)の場合も、1 つの `<tbody>` にまとめる。
    """

    CSS = "mail-auth-style.css"
    JS = "mail-auth-script.js"

    COLS = 7
    COL_NAME = 0     # 方式
    COL_USAGE = 5    # 利用状況(削除してタグにする)

    # 分類タグの表示順(上部ボタン)
    CATEGORIES = [
        "本文の暗号化・電子署名",
        "送信ドメイン認証",
        "ユーザ認証(ログイン認証)",
        "通信路の暗号化",
        "通信路暗号化の強制(ダウングレード対策)",
        "迷惑メール対策(送信制限・フィルタリング)",
    ]

    # 利用状況: 記号 → (タグ名, Bootstrap の色)
    USAGE = {
        "〇": ("〇 : 推奨", "success"),
        "✖": ("✖ : 非推奨", "danger"),
        "△": ("△ : 端末による", "warning"),
    }

    # mermaid の図に共通で付けるスタイル(`%%{init: …}%%`)。`None` か空にすると付けない。
    # 図ごとに `%%{` から始まる指定が本文にあれば、そちらを優先する。
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

    def apply_mermaid_init(self, tr):
        """
        ## 行の中の `div.mermaid-source` の先頭に、`mermaid_init` のディレクティブを付ける

        本文はインデントを除いて(`textwrap.dedent`)から付ける。`MERMAID_INIT` が空なら何もしない。
        """
        for div in tr.select("div.mermaid-source"):
            body = textwrap.dedent(div.get_text().replace("\r\n", "\n")).strip("\n")
            init = self.mermaid_init(body)
            if init:
                div.string = f"\n{init}{body}\n"

    PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>メール認証・暗号化(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="__JS__"></script>
</body>
</html>
"""

    def __init__(self, src, out=None,
                 template="template/mail-auth-template.html",
                 css_template="template/mail-auth-style.css",
                 js_template="template/mail-auth-script.js"):
        """相対パスは、このスクリプトのあるフォルダを基準に解決する。"""
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

    @staticmethod
    def _default_out(src):
        stem, ext = os.path.splitext(src)
        return f"{stem[:-len('-source')]}{ext}" if stem.endswith("-source") else f"{stem}-out{ext}"

    def _path(self, p):
        return p if os.path.isabs(p) else os.path.join(self.here, p)

    def _read(self, p):
        with open(self._path(p), encoding="utf-8", newline="") as f:   # 改行コードを変換しない
            return f.read()

    @staticmethod
    def _write(path, text):
        with open(path, "w", encoding="utf-8", newline="") as f:
            f.write(text)

    def usage_of(self, td):
        """
        ## 「利用状況」セルの記号を、タグ名と色に変換する

        未知の記号は `AssertionError`(`USAGE` への追加漏れに気づけるように)。
        """
        mark = td.get_text(strip=True)
        assert mark in self.USAGE, f"利用状況の記号が未定義: {mark!r}"
        return self.USAGE[mark]

    def parse(self):
        """
        ## 元の表を方式ごとのまとまりに分解する

        - `<th colspan>` の行は分類の見出しとして覚え、以降の方式に付ける(出力には残さない)
        - `rowspan` のセルは結合元を覚えて各行に割り当てる

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 1つ目 | `list[str]` | 見出し行の文字列(「利用状況」は除く) |
        | 2つ目 | `list[dict]` | 方式ごとの辞書。`name`(方式名のセル)/ `category`(分類)/ `rows`(`tr` と、実体のある利用状況セル)/ `usage`(利用状況セル) |
        """
        soup = BeautifulSoup(self._read(self.src), "html.parser")
        table = soup.find("table")   # 最初の `<table>` が外側の表(入れ子の表は手順セルの中)
        heads = [th.get_text(strip=True) for th in table.thead.find_all("th")]
        assert len(heads) == self.COLS, heads
        heads.pop(self.COL_USAGE)

        pending = {}   # 列番号 → [残り行数, 結合元のセル]
        groups, category = [], None
        for tr in table.find("tbody", recursive=False).find_all("tr", recursive=False):
            cells = tr.find_all(["th", "td"], recursive=False)
            if len(cells) == 1 and cells[0].get("colspan"):   # 分類の見出し行
                category = cells[0].get_text(strip=True)
                assert category in self.CATEGORIES, f"分類が未定義: {category}"
                tr.decompose()
                continue
            own = {}
            it = iter(cells)
            for col in range(self.COLS):
                if pending.get(col, [0])[0] > 0:
                    pending[col][0] -= 1
                    continue
                c = next(it)
                own[col] = c
                span = int(c.get("rowspan", 1))
                if span > 1:
                    pending[col] = [span - 1, c]
            assert next(it, None) is None, "セル数が想定より多い行があります"
            if self.COL_NAME in own:
                assert category, "分類より前に方式があります"
                groups.append({"name": own[self.COL_NAME], "category": category, "rows": [],
                               "usage": own[self.COL_USAGE]})
            groups[-1]["rows"].append({"tr": tr, "own_usage": own.get(self.COL_USAGE)})

        for g in groups:   # 方式名の rowspan と行数が合っているか確認
            span = int(g["name"].get("rowspan", 1))
            assert span == len(g["rows"]), (g["name"].get_text(" ", strip=True), span, len(g["rows"]))
        return heads, groups

    @staticmethod
    def badge(tag, color):
        """タグボタン(表中)1つ分。`secondary` = 分類 / `success` `danger` `warning` = 利用状況"""
        esc = html.escape
        text_cls = "text-bg-warning" if color == "warning" else f"text-bg-{color}"
        return (f'<button type="button" class="tag badge {text_cls}" '
                f'data-tag="{esc(tag)}">{esc(tag)}</button>')

    def tbody_html(self, g):
        """
        ## 1方式分の `<tbody>` を作る

        方式名のセルを `<th scope="rowgroup" class="name">` にし、分類タグ(灰)・利用状況タグ(色付き)を追加する。
        利用状況のセルは削除する。タグの順は 分類 → 利用状況。
        """
        usage_tag, usage_color = self.usage_of(g["usage"])
        for r in g["rows"]:
            if r["own_usage"] is not None:
                r["own_usage"].decompose()
        tags = [g["category"], usage_tag]

        th = g["name"]
        th["scope"] = "rowgroup"
        th["class"] = [c for c in th.get("class", []) if c != "text-nowrap"] + ["name"]
        badges = self.badge(g["category"], "secondary") + self.badge(usage_tag, usage_color)
        th.append(BeautifulSoup(f'<div class="tags">{badges}</div>', "html.parser"))

        for r in g["rows"]:
            self.apply_mermaid_init(r["tr"])
        rows = "\n".join("                " + str(r["tr"]) for r in g["rows"])
        body = f'            <tbody data-tags="{html.escape("|".join(tags))}">\n{rows}\n            </tbody>'
        return body, tags

    @staticmethod
    def thead_html(heads):
        return "".join(
            f'<th class="name">{h}</th>' if i == 0 else f"<th>{h}</th>" for i, h in enumerate(heads))

    @staticmethod
    def group(title, items, count):
        """
        ## 上部のタグボタン群(1系統分)

        `items` は `(タグ名, 色)` のリスト。0件のタグは出さない。
        色は `outline-primary`(分類)か、利用状況の `success` `danger` `warning`。
        """
        esc = html.escape
        btns = "".join(
            f"""\
<button type="button" class="btn btn-sm btn-outline-{color}" data-tag="{esc(n)}">
                    {esc(n)} 
                    <span class="badge text-bg-light">{count[n]}</span>
                </button>
                """
            for n, color in items if n in count)
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
        heads, groups = self.parse()
        count, bodies = {}, []
        for g in groups:
            body, tags = self.tbody_html(g)
            for t in tags:
                count[t] = count.get(t, 0) + 1
            bodies.append(body)
        self.rows, self.count = len(bodies), count
        filters = (
            self.group("分類", [(c, "primary") for c in self.CATEGORIES], count)
            + self.group("利用状況", [(t, c) for t, c in self.USAGE.values()], count)
        )
        out = (self.template.replace("__FILTERS__", filters)
               .replace("__THEAD__", self.thead_html(heads))
               .replace("__ROWS__", "\n".join(bodies)))
        newline = "\r\n" if "\r\n" in self.template else "\n"
        return out.replace("\r\n", "\n").replace("\n", newline)

    def save_html(self):
        out = self.build()
        self._write(self.out, out)
        print(self.rows, "methods,", len(out), "bytes ->", self.out)
        print(self.count)
        return self.out

    def save_css(self):
        self._write(self.out_css, self.css_text)
        print("css ->", self.out_css)
        return self.out_css

    def save_js(self):
        self._write(self.out_js, self.js_text)
        print("js ->", self.out_js)
        return self.out_js

    def save(self):
        return [self.save_html(), self.save_css(), self.save_js()]

    def save_preview(self):
        """単体で開ける確認用ページ(Bootstrap CDN + CSS + JS)を `mail-auth-preview.html` に書き出す"""
        path = f"{os.path.splitext(self.out)[0]}-preview.html"
        page = (self.PREVIEW.replace("__CSS__", self.CSS).replace("__JS__", self.JS)
                .replace("__FRAGMENT__", self.build()))
        self._write(path, page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = MailAuthSrc2HTML("mail-auth-source.html", "mail-auth.html")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
