import re, html, os, sys

class AppTestMD2HTML:
    """
    ## Markdown の表を、タグ検索付きの Bootstrap 用 HTML に変換するクラス

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・テンプレートの読み込み |
    | `load_words` | 状況タグの定義(dict)・確認用ページを読み込む |
    | `parse` | Markdown の表を行データに変換する |
    | `tags_of` | 行ごとにタグを決める |
    | `row_html` | 1行分の `<tr>` を作る |
    | `group` | 上部のタグボタン群(分類)を作る |
    | `listbox` | 上部のリストボックス(状況)を作る |
    | `build` | HTML 全体を組み立てて文字列で返す |
    | `save_html` | HTML の断片を書き出す |
    | `save_css` | CSS を書き出す |
    | `save_js` | JavaScript を書き出す |
    | `save` | 上の3つをまとめて書き出す |
    | `save_preview` | 単体で開ける確認用ページを書き出す(任意) |

    """

    CSS = "apptest.css"   # 出力する CSS のファイル名(確認用ページも読み込む)
    JS = "apptest.js"     # 出力する JavaScript のファイル名(確認用ページも読み込む)
    LIB = "attack-script.js"   # 確認用ページが先に読み込む共有スクリプト(createTableSearch の定義)
    SELECT_ID = "situation"    # 「状況」リストボックスの ID(apptest.js の selectId と同じ値にする)

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
        ## 状況タグの定義を読み込む

        | 設定する属性 | 型 | 説明 |
        |---|---|---|
        | `self.situation` | `dict[str, list[str]]` | 状況タグ名 → 適した技法名のリスト。元は apptest.md の2つ目の表(状況 / 適した技法) |
        | `self.prev` | `str` | 確認用ページのひな形 |
        """
        # ## 状況タグ(状況 → 適した技法)
        # 技法名は、表の1列目(テスト技法)と完全に一致させる。一致しない名前は build() でエラーになる。
        #
        # | 要素 | 型 | 説明 |
        # |---|---|---|
        # | キー | `str` | 状況。タグ名(上部ボタン・表中のバッジ)にもなる |
        # | 値 | `list[str]` | その状況に適した技法名。該当する技法の行にこのタグが付く |
        SITUATION = {
            "入力値の範囲を検証したい": ["同値分割", "境界値分析"],
            "条件の組合せでルールが決まる": ["デシジョンテーブルテスト"],
            "設定・環境の組合せが多い": ["実験計画法"],  # 元の表: 実験計画法 (直交表・ペアワイズ)
            "状態によって振る舞いが変わる": ["状態遷移テスト"],
            "大規模で仕様変更が多い": ["モデルベースドテスト"],
            "仕様が不十分・時間がない": ["探索的テスト", "エラー推測"],
            "設計書・仕様書を早い段階で気軽にレビューしたい": ["ウォークスルー"],
            "安全性が重要で、欠陥データも集めて厳格にレビューしたい": ["インスペクション"],
            "日常的なコード変更を確認したい": ["ピアレビュー"],
            "コードの規約違反や潜在的な欠陥を機械的に検出したい": ["静的解析"],
            "小規模なロジックを実行せずに確認したい": ["デスクチェック"],
            "関数・クラス単位の動作を確認したい": ["単体テスト"],
            "モジュール間の連携・インターフェースを確認したい": ["結合テスト"],
            "結合するモジュールが少なく、小規模である": ["ビッグバンテスト"],
            "上位の制御や主要フローを先に確認したい": ["トップダウンテスト"],
            "下位の基盤機能が先に完成している": ["ボトムアップテスト"],
            "大規模で階層が深く、結合を並行して進めたい": ["サンドイッチテスト"],
            "システム全体が要件を満たすか確認したい": ["システムテスト"],
            "納品前に発注者・利用部門が受け入れの可否を判断したい": ["受け入れテスト"],
            "正式リリース前に、実際の利用者の声や実環境での問題を知りたい": ["アルファテスト・ベータテスト"],
            "稼働前に、バックアップ・監視・障害対応など運用面を確認したい": ["運用受け入れテスト"],
            "主要なユーザーフローを入口から出口まで確認したい": ["E2E テスト"],
            "画面を介さず API の機能を確認したい": ["API テスト"],
            "サービス間のインターフェースの取り決めを守りたい": ["契約テスト"],
            "複雑な関数のテスト数の目安を知りたい": ["基本パステスト"],
            "変数の未初期化・誤った参照を検出したい": ["データフローテスト"],
            "ループ処理の境界の不具合を確認したい": ["ループテスト"],
            "テストそのものの質を評価したい": ["ミューテーションテスト"],
            "状態数が多い並行・分散システムで、デッドロックや競合がないか網羅的に調べたい": ["モデル検査"],
            "すべての経路を通る入力を、自動で生成したい": ["シンボリック実行"],
            "複雑な処理でも、自動でカバレッジを高めたい": ["コンコリックテスト"],
            "全組合せは多すぎるので、2 因子の組合せに絞りたい": ["ペアワイズ法"],
            "条件と結果の論理関係が複雑で、図にして整理したい": ["原因結果グラフ"],
            "入力の観点が多く、テスト設計の抜けを防ぎたい": ["分類木法"],
            "要件がユースケースで書かれている": ["ユースケーステスト"],
            "業務の一連の流れに沿って確認したい": ["シナリオテスト"],
            "期待値は不明だが、入力と出力の関係は分かる": ["メタモルフィックテスト"],
            "常に成り立つ性質を定義できる": ["プロパティベーステスト"],
            "旧システムや別実装と結果を比較できる": ["差分テスト"],
            "仕様が不明なレガシーコードの、現状の動作を保ちたい": ["スナップショットテスト"],
            "不正・異常な入力でクラッシュや脆弱性を調べたい": ["ファジング"],
            "想定外の入力パターンで堅牢性を確認したい": ["ランダムテスト"],
            "画面の表示・操作・遷移を確認したい": ["GUI テスト"],
            "画面を無作為に操作して、クラッシュ・フリーズを調べたい": ["モンキーテスト"],
            "経験の浅い担当者でも確認漏れを防ぎたい": ["チェックリストベーステスト"],
            "準備する時間がなく、簡易的に確認したい": ["アドホックテスト"],
            "変更によって既存機能が壊れていないか確認したい": ["回帰テスト"],
            "不具合を修正したので、直っているか確認したい": ["確認テスト"],
            "新しいビルドが詳細テストに進める状態か、短時間で確認したい": ["スモークテスト"],
            "軽微な修正後に、該当部分だけ素早く確認したい": ["サニティテスト"],
            "UI の変更で、意図しない見た目の崩れがないか確認したい": ["ビジュアルリグレッションテスト"],
            "応答時間・処理能力の要件を確認したい": ["性能テスト"],
            "想定するアクセスの集中に耐えられるか確認したい": ["負荷テスト"],
            "想定を超える負荷での限界点や、破綻時の挙動を知りたい": ["ストレステスト"],
            "長時間稼働でのメモリリークや性能劣化を確認したい": ["耐久テスト"],
            "認証・認可・入力検証などのセキュリティ要件を確認したい": ["セキュリティテスト"],
            "既知の脆弱性や設定不備を、広く効率的に調べたい": ["脆弱性診断"],
            "攻撃者の視点で、実際に侵入できるか確認したい": ["ペネトレーションテスト"],
            "使いやすさを、実際の利用者で評価したい": ["ユーザビリティテスト"],
            "高齢者や障害のある人を含む、多様な利用者が使えるか確認したい": ["アクセシビリティテスト"],
            "複数の OS・ブラウザ・端末で動作を確認したい": ["互換性テスト"],
            "障害時に正しく復旧できるか確認したい": ["障害回復テスト"],
            "海外展開や多言語対応をしている": ["国際化・ローカライズテスト"],
            "導入・更新・削除が正しく行えるか確認したい": ["インストールテスト"],
            "法令や業界基準への適合を確認したい": ["法規制適合テスト"],
            "システム更改で、データが正確に移行されるか確認したい": ["移行テスト"],
            "本番データで、基幹処理 (給与・会計等) を独立に検証したい": ["並行シミュレーション"],
            "監査で、事前に算出した期待結果と処理結果を比較したい": ["テストデータ法"],
            "本番稼働中に、継続的に処理を検証したい": ["統合テストファシリティ法"],
            "複数案の効果を、実際のユーザー行動で比較したい": ["A/B テスト"],
            "仕様の曖昧さや矛盾を、設計の初期に数学的な記述で排除したい": ["形式仕様記述"],
            "すべての入力でプログラムが性質を満たすことを保証したい": ["定理証明"],
            "実行時エラーが起きないことを、実行せずに網羅的に示したい": ["抽象解釈"],
        }

        PREVIEW = """<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>アプリのテスト技法まとめ(確認用)</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="__CSS__" rel="stylesheet">
</head>
<body class="container-fluid">
__FRAGMENT__
<script src="__LIB__"></script>
<script src="__JS__"></script>
</body>
</html>
"""
        self.situation, self.prev = {key: SITUATION[key] for key in sorted(SITUATION)}, PREVIEW

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

        見出し行(`#####`)は読み飛ばす。表は1つだけ(テスト技法の表)で、2つ目の表(状況 / 適した技法)は
        `load_words` の `SITUATION` に移してあるため、Markdown には残していない。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行リスト | `list[list[str]]` | 各行の8セル(テスト技法・別名・分類・説明・手順・長所・短所・主な用途) |
        """
        rows = []
        with open(self.src, encoding="utf-8") as f:
            lines = f.read().splitlines()
        for ln in lines:
            if ln.startswith("|") and not ln.startswith("|---") and not ln.startswith("| テスト技法"):
                cells = [c.strip() for c in ln.strip().strip("|").split("|")]
                assert len(cells) == 8, (len(cells), ln[:60])
                rows.append(cells)
        return rows

    def tags_of(self, cells):
        """
        ## 行のタグを (分類, 状況) で返す

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 8セル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | タプル | `tuple[list, list]` | 分類のタグ(表の「分類」列)・状況のタグ(`SITUATION` で、この技法が挙がっている状況) |
        """
        name = self.plain(cells[0])
        cat = self.plain(cells[2])
        return ([cat] if cat not in ("", "-") else []), [s for s, techs in self.situation.items() if name in techs]

    def row_html(self, cells, tags):
        """
        ## 1行分の `<tr>` を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cells` | `list[str]` | 元の8セル |
        | `tags` | `list[str]` | この行のタグ(分類+状況) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | `<tr>…</tr>` |

        状況タグは文が長いので、バッジは折り返せるようにしている(Bootstrap の `text-wrap` `text-start` `lh-sm`)。
        """
        esc = html.escape
        fix = lambda s: s if s not in ("-", "") else '<span class="text-body-tertiary">—</span>'
        cell = lambda s: f'<td>{fix(s)}</td>'
        badges = "".join(
            f'<button type="button" class="tag badge text-bg-secondary text-wrap text-start lh-sm" data-tag="{esc(t)}">{esc(t)}</button>'
            for t in tags)
        others = "\n                    ".join(cell(c) for c in cells[1:])
        return (
            f"""\
                <tr data-tags="{esc("|".join(tags))}">
                    <th scope="row" class="name">{cells[0]}<div class="tags">{badges}</div></th>
                    {others}
                </tr>"""
        )

    def group(self, title, names, count):
        """
        ## 上部のタグボタン群(1系統分)を作る

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(分類) |
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

    def listbox(self, title, names, count):
        """
        ## 上部のリストボックス(1つだけ選ぶタグ群)を作る

        選択肢が多いタグ群(状況)は、ボタンではなく `<select>` にする。
        `option` の `value` がタグ名で、`apptest.js` の `selectId` に `self.SELECT_ID` を渡すと絞り込みに使われる。

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `title` | `str` | 系統名(状況) |
        | `names` | `list[str]` | タグ名の候補(この順に並ぶ) |
        | `count` | `dict[str, int]` | タグ名 → 該当件数。0件のタグは表示しない |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | 先頭に「指定なし」を置いた `<select>` |
        """
        esc = html.escape
        opts = "\n".join(f'                <option value="{esc(n)}">{esc(n)}</option>' for n in names if n in count)
        return (
            f"""\
<div class="pt-3 d-flex flex-wrap gap-1 align-items-center mb-1">
            <label class="me-1" for="{self.SELECT_ID}">{title}</label>
            <select id="{self.SELECT_ID}" class="form-select form-select-sm w-auto mw-100">
                <option value="">指定なし</option>
{opts}
            </select>
        </div>
        """
        )

    def build(self):
        """
        ## HTML 全体を組み立てる

        `SITUATION` に書かれた技法名が表に存在しない場合は `ValueError` にする(表記ゆれの検出)。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | HTML | `str` | テンプレートの `__ROWS__` と `__FILTERS__` を置換したもの |

        行数は `self.rows` に入る。
        """
        rows = self.parse()
        known = {self.plain(c[0]) for c in rows}
        missing = [(s, t) for s, techs in self.situation.items() for t in techs if t not in known]
        if missing:
            raise ValueError(f"SITUATION の技法名が表にありません: {missing}")
        body, count, cats = [], {}, []
        for c in rows:
            cat, sit = self.tags_of(c)
            tags = cat + sit
            for t in tags:
                count[t] = count.get(t, 0) + 1
            cats += [t for t in cat if t not in cats]   # 分類は表に出てきた順
            body.append(self.row_html(c, tags))
        self.rows = len(body)
        filters = (self.group("分類", cats, count)
                   + self.listbox("状況", list(self.situation), count))
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
        ## 確認用ページ(Bootstrap CDN + CSS + 共有スクリプト + JS 込み)を書き出す

        貼り付け先のページがなくても、ブラウザで開くだけで動作を確認できる。
        `self.out` の拡張子の前に `-preview` を付けたファイルに書き出す。

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        path = f"""{os.path.splitext(self.out)[0]}-preview.html"""
        page = (self.prev.replace("__CSS__", self.CSS).replace("__LIB__", self.LIB).replace("__JS__", self.JS)
                .replace("__FRAGMENT__", self.build()))
        with open(path, "w", encoding="utf-8") as f:
            f.write(page)
        print("preview ->", path)
        return path


if __name__ == "__main__":
    conv = AppTestMD2HTML("apptest.md")
    conv.save()
    if "--preview" in sys.argv:
        conv.save_preview()
