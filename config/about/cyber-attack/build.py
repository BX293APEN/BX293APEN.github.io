"""
# cyber-attack.md → Bootstrap 5 用 HTML 変換

## 出力の構成(3ファイル)

| 出力 | 元になるファイル | 内容 |
|---|---|---|
| `cyber-attack.html` | `template.html` + `cyber-attack.md` | `<div id="attack-app">` の断片のみ |
| `attack-style.css` | `template.css` | 見た目 |
| `attack-script.js` | `template.js` | タグ・キーワードの絞り込み |

**編集は元になるファイル側で行う。** 出力側を直接編集しても、再生成すると上書きされる。
3ファイルは、`out`(HTML の出力先)と同じフォルダに書き出す。

## 使い方

```python
CyberAttackMD2HTML("cyber-attack.md").save()
```

コマンドラインでは `python3 build.py`。確認用ページも作るなら `python3 build.py --preview`。

## クラスの構成

| メソッド | 役割 |
|---|---|
| `__init__` | パスの解決・テンプレートの読み込み |
| `load_words` | タグ・標準手順の定義を読み込む |
| `parse` | Markdown の表を行データに変換する |
| `tags_of` | 行ごとにタグを決める |
| `phase_cells` | 対策列を ①初動 ②調査・根絶 ③再発防止 に分割する |
| `row_html` | 1行分の `<tr>` を作る |
| `group` | 上部のタグボタン群を作る |
| `build` | HTML 全体を組み立てて文字列で返す |
| `save_html` | HTML の断片を書き出す |
| `save_css` | CSS を書き出す |
| `save_js` | JavaScript を書き出す |
| `save` | 上の3つをまとめて書き出す |
| `save_preview` | 単体で開ける確認用ページを書き出す(任意) |
"""
import re, html, os, sys


PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>サイバー攻撃まとめ(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="__JS__"></script>
</body>
</html>
"""


class CyberAttackMD2HTML:
    """## Markdown の表を、タグ検索付きの Bootstrap 用 HTML に変換するクラス"""

    CSS = "attack-style.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "attack-script.js"    # 出力する JavaScript のファイル名(確認用ページも読み込む)

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
        | `template` | `str` | `"template.html"` | HTML テンプレート |
        | `css_template` | `str` | `"template.css"` | CSS の元ファイル |
        | `js_template` | `str` | `"template.js"` | JavaScript の元ファイル |
        """
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.src = self._path(src)
        self.out = self._path(out) if out else os.path.splitext(self.src)[0] + ".html"
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
        ## タグ・標準手順の定義を読み込む

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.short` | `list[str]` | 見出し(分類)の短縮名。Markdown の見出し順 |
        | `self.atk` | `list[str]` | 攻撃者タグ |
        | `self.topic` | `dict[str, str]` | トピックタグ名 → 攻撃手法名にマッチする正規表現 |
        | `self.ph` | `dict[str, tuple]` | 分類・トピック名 → (①初動のリスト, ②調査・根絶のリスト) |
        | `self.override` | `list[str]` | 分類より優先して `ph` のキーに使うトピック |
        """
        SHORT = ["マルウェア", "認証・パスワード", "サプライチェーン・標的型", "詐欺・SE",
                 "Webアプリ", "AI", "ネットワーク", "物理・その他"]

        # ## 攻撃者タグ(攻撃者列の文字列に含まれていれば付与)
        ATK = ["APT攻撃者", "犯罪組織", "国家関与主体", "個人クラッカー", "内部関係者",
               "詐欺犯", "ボットハーダー", "研究者", "ハクティビスト", "産業スパイ", "諜報機関"]

        # ## トピックタグ(攻撃手法名にマッチすれば付与)
        TOPIC = {
            "DoS/DDoS": r"DoS|Flood|リフレク|Smurf|水責め|Octopus",
            "DNS": r"DNS|ドメイン",
            "インジェクション": r"インジェクション|XSS|XXE|ファイルインクルード",
            "セッション": r"セッション|CSRF|クリックジャッキング",
            "無線": r"Evil Twin|ウォードライビング|Blue|ジャミング|GPS|Deauth|KRACK|WPS|偽基地局|リレー",
            "サイドチャネル": r"サイドチャネル|タイミング|電力解析|電磁波|テンペスト",
            "量子": r"量子|Harvest",
            "暗号": r"ハッシュ|レインボー|誕生日|TLS|POODLE|量子",
            "C2・遠隔操作": r"C&C|RAT|バックドア|コネクトバック|ボットネット|トンネリング|フロンティング",
            "フィッシング": r"フィッシング|スミッシング|ビッシング|ホエーリング|BEC|ビジネスメール|ファーミング",
            "金銭": r"バンキング|クリプト|トランザクション|カード|ランサム|BEC|ビジネスメール",
        }

        # ## ①初動 / ②調査・根絶 の標準手順(分類ごと)
        # ③再発防止は元の表の「対策サービス・方法」をそのまま使う
        PH = {
            "マルウェア": (["感染端末をネットワークから隔離(LAN抜線・Wi-Fi切断)\n※電源は落とさない", "関係部署へ報告し、影響範囲を仮判断", "関連アカウントのパスワード変更・無効化"],
                          ["メモリ・ディスク・ログを保全", "IoC(ハッシュ・C2通信先)で他端末を調査", "駆除、またはクリーン再構築・バックアップから復旧"]),
            "認証・パスワード": (["対象アカウントのロック・パスワードリセット・セッション失効", "不審な送信元IPの遮断"],
                            ["認証ログから試行元・成功ログインを特定", "侵害アカウントの操作履歴・権限を確認", "漏えいした資格情報を洗い出す"]),
            "サプライチェーン・標的型": (["侵害端末・サーバを隔離", "供給元・取引先へ連絡し、当該ソフトの利用・更新を停止", "特権アカウントの資格情報を無効化"],
                                ["EDR・ログで侵入経路と横展開範囲を特定", "IoCで全社をハンティング", "認証基盤(AD等)の侵害有無を確認し、鍵・資格情報を再発行"]),
            "詐欺・SE": (["被害アカウントのパスワード変更・利用停止", "金融機関へ連絡(送金組戻し・カード停止)", "不審メール・SMSの注意喚起(拡散防止)"],
                       ["メールヘッダ・URL・添付を保全して解析", "同種メールの受信者・クリック者を洗い出す", "警察・IPA等の関係機関へ相談"]),
            "Webアプリ": (["該当機能・ページを停止、またはWAFで遮断", "影響セッションの失効・パスワード変更"],
                        ["Web・DB・WAFログを保全して解析", "改ざん・漏えい範囲を特定", "不正ファイル(Webシェル等)の削除と脆弱箇所の特定"]),
            "AI": (["該当機能・APIキーを停止または制限", "疑わしい入力・利用者を遮断"],
                  ["入出力ログ・学習データの出所を調査", "影響モデルを切り離し、クリーンなモデル・データで再構築"]),
            "ネットワーク": (["不審な通信元・先をFW/ACLで遮断", "該当機器を隔離"],
                         ["パケット・通信ログ・機器ログを保全して解析", "機器の設定・ファームウェアを確認して復旧"]),
            "DoS/DDoS": (["ISP・DDoS対策サービスへ連絡し緩和(スクラビング)を開始", "攻撃元・攻撃種別を特定し、FW/ACLで遮断", "利用者へ状況を告知"],
                        ["攻撃トラフィックを記録・保全", "自組織の端末が踏み台化されていないか確認", "陽動による侵入・情報窃取の有無を確認"]),
            "DNS": (["不正な応答・レコードを削除(キャッシュクリア)", "レジストラ・DNS事業者へ連絡"],
                   ["DNSログ・ゾーン情報・変更履歴を確認", "影響期間と誘導先を特定し、利用者へ注意喚起"]),
            "無線": (["不審なAP・機器の電源断・隔離", "無線LANの鍵を変更"],
                   ["無線ログ・接続履歴を確認", "不正接続された端末・通信を特定"]),
            "サイドチャネル": (["対象機器の使用停止・物理的な隔離", "影響を受けた鍵・証明書を失効"],
                          ["影響を受けた鍵を洗い出して再発行", "実装・設置環境を再評価"]),
            "量子": (["長期機密データを優先度付け", "暗号資産(利用中の暗号方式)を棚卸し"],
                   ["暗号の利用状況を調査(CBOM)", "危殆化時の鍵・証明書の失効手順を整備"]),
            "物理・その他": (["該当機器・場所の物理的な隔離、出入りの制限", "関連する認証情報を変更"],
                         ["防犯カメラ・入退室ログを確認", "持ち出された資産・情報を特定"]),
        }
        OVERRIDE = ["DoS/DDoS", "DNS", "無線", "サイドチャネル", "量子"]  # 分類より優先して使うキー
        self.short, self.atk, self.topic, self.ph, self.override = SHORT, ATK, TOPIC, PH, OVERRIDE

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

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行リスト | `list[tuple[int, list[str]]]` | (見出し番号, 7セル) |
        """
        rows, sec = [], -1
        with open(self.src, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for ln in lines:
            if ln.startswith("####"):
                sec += 1
            elif ln.startswith("|") and not ln.startswith("|---") and not ln.startswith("| 攻撃手法"):
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                assert len(cells) == 7, (len(cells), ln[:60])
                rows.append((sec, cells))
        return rows

    def tags_of(self, sec, cells):
        """
        ## 行のタグを (分類, 攻撃者, トピック) で返す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `sec` | `int` | 見出し番号 |
        | `cells` | `list[str]` | 7セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タプル | `tuple[list, list, list]` | 分類・攻撃者・トピックのタグ |
        """
        name = self.plain(cells[0])
        topics = [t for t, rx in self.topic.items() if re.search(rx, name)]
        return [self.short[sec]], [a for a in self.atk if a in cells[6]], topics

    @staticmethod
    def li(items):
        """
        ## リストを `<ul>` にする

        項目内の改行(`\n`)は `<br>` になる。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `items` | `list[str]` | 項目 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<ul><li>…</li></ul>` |
        """
        return "<ul>" + "".join(f"<li>{html.escape(i).replace(chr(10), '<br>')}</li>" for i in items) + "</ul>"

    def phase_cells(self, sec, topics, measure):
        """
        ## 対策を3セルに分割する

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `sec` | `int` | 見出し番号 |
        | `topics` | `list[str]` | トピックタグ |
        | `measure` | `str` | 元の「対策サービス・方法」セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 3要素 | `tuple[str, str, str]` | ①初動・②調査・根絶・③再発防止の HTML |
        """
        key = next((t for t in self.override if t in topics), self.short[sec])
        a, b = self.ph[key]
        return self.li(a), self.li(b), re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", measure)

    def row_html(self, cells, tags, phases):
        """
        ## 1行分の `<tr>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 元の7セル |
        | `tags` | `list[str]` | この行のタグ(分類+攻撃者+トピック) |
        | `phases` | `tuple[str, str, str]` | `phase_cells` の戻り値 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr>…</tr>` |
        """
        esc = html.escape
        fix = lambda s: s if s not in ("-", "") else '<span class="text-body-tertiary">—</span>'
        cell = lambda s, cls="": f'<td class="{cls}">{fix(s)}</td>'
        badges = "".join(
            f'<button type="button" class="tag badge text-bg-secondary" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags)
        p1, p2, p3 = phases
        return (
            f"""\
                <tr data-tags="{esc("|".join(tags))}">
                    <th scope="row" class="name">{cells[0]}<div class="tags">{badges}</div></th>
                    {cell(cells[1])}
                    {cell(cells[2])}
                    {cell(cells[3])}
                    {cell(cells[4])}
                    {cell(p1, "std")}
                    {cell(p2, "std")}
                    {cell(p3, "own")}
                    {cell(cells[6])} 
                </tr>"""
        )

    @staticmethod
    def group(title, names, count):
        """
        ## 上部のタグボタン群(1系統分)を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(分類・攻撃者・トピック) |
        | `names` | `list[str]` | タグ名の候補 |
        | `count` | `dict[str, int]` | タグ名 → 該当件数。0件のタグは表示しない |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | ボタンの並び |
        """
        esc = html.escape
        btns = "".join(
            f'<button type="button" class="btn btn-sm btn-outline-primary" data-tag="{esc(n)}">'
            f'{esc(n)} <span class="badge text-bg-light">{count[n]}</span></button>'
            for n in names if n in count)
        return (f'<div class="d-flex flex-wrap gap-1 align-items-center mb-1">'
                f'<span class="small text-body-secondary me-1">{title}</span>{btns}</div>')

    def build(self):
        """
        ## HTML 全体を組み立てる

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | テンプレートの `__ROWS__` と `__FILTERS__` を置換したもの |

        行数は `self.rows` に入る。
        """
        body, count = [], {}
        for sec, c in self.parse():
            cat, atk, top = self.tags_of(sec, c)
            tags = cat + atk + top
            for t in tags:
                count[t] = count.get(t, 0) + 1
            body.append(self.row_html(c, tags, self.phase_cells(sec, top, c[5])))
        self.rows = len(body)
        filters = (self.group("分類", self.short, count)
                   + self.group("攻撃者", self.atk, count)
                   + self.group("トピック", list(self.topic), count))
        return self.template.replace("__ROWS__", "\n".join(body)).replace("__FILTERS__", filters)

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
        ## 確認用ページ(Bootstrap CDN + CSS + JS 込み)を書き出す

        貼り付け先のページがなくても、ブラウザで開くだけで動作を確認できる。
        `self.out` の拡張子の前に `-preview` を付けたファイルに書き出す。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        path = os.path.splitext(self.out)[0] + "-preview.html"
        page = (PREVIEW.replace("__CSS__", self.CSS).replace("__JS__", self.JS)
                .replace("__FRAGMENT__", self.build()))
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = CyberAttackMD2HTML("cyber-attack.md")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
