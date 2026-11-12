import html, os, sys
from bs4 import BeautifulSoup


class HttpHeaderSrc2HTML:
    """
    ## HTTP ヘッダの表(HTML)を、タグ検索付きの Bootstrap 用 HTML に変換するクラス

    見出し(フィールド名)ごとに 1 つの `<tbody>` にまとめ、`<tbody>` 単位で絞り込む。
    `rowspan` を含む行を 1 行ずつ隠すと表が崩れるため。

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `load_words` | 分類タグ・種別タグ・確認用ページの定義を読み込む |
    | `parse` | 元の表をヘッダごとのまとまりに分解する |
    | `tags_of` | ヘッダごとにタグを決める |
    | `tbody_html` | 1ヘッダ分の `<tbody>` を作る |
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
    | `http-header-source.html` | `build.py` と同じフォルダ | 入力(元の表) |
    | `http-header.html` | `build.py` と同じフォルダ | 出力(HTML の断片) |
    | `http-header-style.css` | `build.py` と同じフォルダ | 出力(`template/` の複製) |
    | `http-header-script.js` | `build.py` と同じフォルダ | 出力(`template/` の複製) |
    | `http-header-preview.html` | `build.py` と同じフォルダ | 出力(確認用ページ。`--preview` 指定時) |
    | `template/http-header-template.html` | `template/` | HTML テンプレート |
    | `template/http-header-style.css` | `template/` | CSS の元ファイル |
    | `template/http-header-script.js` | `template/` | JavaScript の元ファイル |
    """

    CSS = "http-header-style.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "http-header-script.js"    # 出力する JavaScript のファイル名(確認用ページも読み込む)

    def __init__(
        self,
        src,
        out=None,
        template="template/http-header-template.html",
        css_template="template/http-header-style.css",
        js_template="template/http-header-script.js",
    ):
        """
        ## 初期化

        相対パスは、このスクリプトのあるフォルダを基準に解決する。

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `src` | `str` | (必須) | 入力 HTML(元の表) |
        | `out` | `str` または `None` | `src` から `-source` を除いたもの | 出力 HTML。`src` と同じ名前にはできない(元ファイルを上書きしてしまうため) |
        | `template` | `str` | `"template/http-header-template.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template/http-header-style.css"` | CSS の元ファイル |
        | `js_template` | `str` | `"template/http-header-script.js"` | JavaScript の元ファイル |
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
        | `src` | `str` | 入力のパス(例: `.../http-header-source.html`) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 語尾の `-source` を除いたパス(例: `.../http-header.html`)。`-source` が無ければ `-out` を付ける |
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
        ## 分類タグ・種別タグ・確認用ページの定義を読み込む

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.cats` | `dict[str, list[str]]` | 分類タグ名 → 該当するヘッダ名(小文字)。1ヘッダに複数の分類が付くことがある |
        | `self.kinds` | `list[str]` | 上部に出す「種別」のタグ名 |
        | `self.kind_tags` | `dict[str, list[str]]` | 元の表の「種別」列の値 → 付与する種別タグ。`共通` は両方付く |
        | `self.prev` | `str` | 確認用ページのひな形(`__CSS__` `__JS__` `__FRAGMENT__` を置換する) |
        """
        # ## 分類タグ
        # キーはヘッダ名(小文字)の先頭語と照合する。
        #
        # | 要素 | 型 | 説明 |
        # |---|---|---|
        # | キー | `str` | 分類タグ名 |
        # | 値 | `list[str]` | 該当するヘッダ名(小文字) |
        CATS = {
            "基本・接続": ["date", "host", "referer", "user-agent", "server", "location", "allow",
                           "retry-after", "connection", "x-runtime", "x-request-id"],
            "コンテンツ": ["content-type", "content-length", "content-encoding", "transfer-encoding",
                           "content-disposition", "accept", "accept-language", "accept-encoding"],
            "キャッシュ": ["cache-control", "etag", "last-modified", "expires", "vary",
                           "if-modified-since", "if-none-match", "if-match"],
            "部分取得": ["range", "accept-ranges"],
            "認証": ["authorization", "www-authenticate"],
            "Cookie": ["cookie", "set-cookie"],
            "プロキシ": ["x-forwarded-for", "x-forwarded-proto", "x-forwarded-host"],
            "Ajax・CSRF": ["x-requested-with", "x-csrf-token", "origin",
                           "sec-fetch-site", "sec-fetch-mode", "sec-fetch-dest"],
            "CORS": ["origin", "access-control-request-method", "access-control-request-headers",
                     "access-control-allow-origin", "access-control-allow-methods",
                     "access-control-allow-headers", "access-control-allow-credentials",
                     "access-control-max-age", "access-control-expose-headers"],
            "セキュリティ": ["set-cookie", "upgrade-insecure-requests", "sec-fetch-site", "sec-fetch-mode",
                             "sec-fetch-dest", "x-frame-options", "x-xss-protection",
                             "x-content-type-options", "strict-transport-security",
                             "content-security-policy", "referrer-policy", "permissions-policy"],
        }
        KINDS = ["リクエスト", "レスポンス"]   # 上部に出す種別タグ
        KIND_TAGS = {"共通": ["リクエスト", "レスポンス"], "リクエスト": ["リクエスト"], "レスポンス": ["レスポンス"]}

        PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HTTPヘッダ(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="__JS__"></script>
</body>
</html>
"""
        self.cats, self.kinds, self.kind_tags, self.prev = CATS, KINDS, KIND_TAGS, PREVIEW

    def parse(self):
        """
        ## 元の表をヘッダごとのまとまりに分解する

        「種別」列は表から削除する(タグで表現するため)。
        削除は読み込んだ DOM に対して行うので、呼ぶたびに元ファイルから読み直す。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 見出しと行 | `tuple[list[str], list[tuple[str, str, list]]]` | 下表の2要素 |

        | 戻り値の要素 | 型 | 説明 |
        |---|---|---|
        | 1つ目 | `list[str]` | 見出し行の文字列(「種別」列は除く) |
        | 2つ目 | `list[tuple[str, str, list]]` | ヘッダごとの (ヘッダ名(小文字), 種別, `<tr>` のリスト) |
        """
        soup = BeautifulSoup(self._read(self.src), "html.parser")
        table = soup.find("table")
        heads = [th.get_text(strip=True) for th in table.thead.find_all("th")]
        heads.pop(1)   # 種別カラムは削除

        # 見出し(rowgroup の th)が現れるたびに新しいまとまりを始める
        groups = []
        for tr in table.find_all("tr"):
            if tr.find_parent("thead"):
                continue
            if tr.find("th", scope="rowgroup"):
                groups.append([tr])
            else:
                groups[-1].append(tr)

        result = []
        for trs in groups:
            th = trs[0].find("th", scope="rowgroup")
            name = th.get_text().split()[0].lower()
            kind_td = trs[0].find_all("td")[0]
            kind = kind_td.get_text(strip=True)
            kind_td.decompose()   # 種別カラムは削除(タグで表現する)
            result.append((name, kind, trs))
        return heads, result

    def tags_of(self, name, kind):
        """
        ## ヘッダのタグを (種別 + 分類) で返す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `name` | `str` | ヘッダ名(小文字) |
        | `kind` | `str` | 元の表の「種別」列の値(`共通` `リクエスト` `レスポンス`) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タグ | `list[str]` | 種別タグ → 分類タグの順 |

        未知の種別・未分類のヘッダは `AssertionError` にする(分類漏れに気づけるように)。
        """
        assert kind in self.kind_tags, (name, kind)
        cats = [c for c, names in self.cats.items() if name in names]
        assert cats, f"未分類: {name}"
        return self.kind_tags[kind] + cats

    def tbody_html(self, trs, tags):
        """
        ## 1ヘッダ分の `<tbody>` を作る

        見出しセル(`<th scope="rowgroup">`)に、`name` クラスとタグボタンを追加する。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `trs` | `list` | このヘッダの `<tr>`(BeautifulSoup の要素) |
        | `tags` | `list[str]` | このヘッダのタグ(種別 + 分類) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tbody data-tags="…">…</tbody>` |
        """
        esc = html.escape
        th = trs[0].find("th", scope="rowgroup")
        th["class"] = th.get("class", []) + ["name"]
        th["scope"] = "rowgroup"
        badges = "".join(
            f'<button type="button" class="tag badge text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags)
        th.append(BeautifulSoup(f'<div class="tags">{badges}</div>', "html.parser"))
        rows = "\n".join("                " + str(tr) for tr in trs)
        return f'            <tbody data-tags="{esc("|".join(tags))}">\n{rows}\n            </tbody>'

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
        | `title` | `str` | 系統名(種別・分類) |
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

        ヘッダ数は `self.rows`、タグごとの件数は `self.count` に入る。
        """
        heads, items = self.parse()
        count, bodies = {}, []
        for name, kind, trs in items:
            tags = self.tags_of(name, kind)
            for t in tags:
                count[t] = count.get(t, 0) + 1
            bodies.append(self.tbody_html(trs, tags))
        self.rows, self.count = len(bodies), count
        filters = self.group("種別", self.kinds, count) + self.group("分類", list(self.cats), count)
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
        print(self.rows, "headers,", len(out), "bytes ->", self.out)
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
    conv = HttpHeaderSrc2HTML("http-header-source.html", "http-header.html")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
