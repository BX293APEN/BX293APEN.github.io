import re, os, sys


class CryptMdNormalizer:
    """
    ## `crypt_source.md` を、全セクション同じ8列の Markdown 表に整形するクラス

    元の md は、セクションごとに列数が違い(6〜9列)、表の書式も Markdown 表と HTML 表(`rowspan` あり)が混在している。
    そのため、次の方針で全セクションを同じ8列の Markdown 表にそろえる。

    | 方針 | 内容 |
    |---|---|
    | 列 | 下の `COLUMNS` の8列に統一する |
    | `rowspan` | 展開して、1行 = 1項目にする(`DH` の Static / E などは別の行になる) |
    | 元に無い列 | `-` を入れる |
    | 8列に収まらない列 | 「備考」列にまとめる(下の `NOTE_COLUMNS`)。値が `-` の項目は入れない |
    | セルの中身 | HTML のまま維持する(`<br>` `<ul>` など)。改行とインデントだけ除く |

    | メソッド | 役割 |
    |---|---|
    | `__init__` | パスの解決・元ファイルの読み込み |
    | `sections` | `### 見出し` ごとに分ける |
    | `parse_md_table` | Markdown 表を行・セルに分解する |
    | `parse_html_table` | HTML 表を `rowspan` を展開して行・セルに分解する |
    | `to_unified` | 1行を8列にそろえる |
    | `build` | 整形後の Markdown 全体を作る |
    | `save` | 書き出す |
    """

    # ## 統一後の列
    #
    # | 番号 | 列 | 元の列(セクションにより異なる) |
    # |---|---|---|
    # | 0 | 名称 | 名称 |
    # | 1 | 分類 | 分類 / 暗号形式(共通鍵) |
    # | 2 | CRYPTREC種別 | CRYPTREC種別 |
    # | 3 | 量子耐性 | PQC(元の列名は `PQC` のまま。`MAP` で対応づける) |
    # | 4 | 基盤となる数学的問題 | 基盤となる数学的問題(無いセクションは `-`) |
    # | 5 | 鍵長・生成ビット数 | 鍵長・生成ビット数(暗号モードは `-`) |
    # | 6 | 仕組みの概要 | 仕組みの概要 |
    # | 7 | 備考 | 下の `NOTE_COLUMNS`(無いセクションは `-`) |
    COLUMNS = [
        "名称", "分類", "CRYPTREC種別", "量子耐性",
        "基盤となる数学的問題", "鍵長・生成ビット数", "仕組みの概要", "備考",
    ]

    # 元の列名(先頭一致) → 統一後の列番号
    #
    # `PQC` は元の md の列名。統一後は「量子耐性」(QKD やワンタイムパッドも含めて見るため)
    MAP = {
        "名称": 0, "分類": 1, "暗号形式": 1, "CRYPTREC種別": 2, "PQC": 3,
        "基盤となる数学的問題": 4, "鍵長・生成ビット数": 5, "仕組みの概要": 6,
    }

    # ## 備考列にまとめる元の列
    #
    # | 元の列 | 出るセクション | 備考での表記 |
    # |---|---|---|
    # | オプション | 鍵共有 | `<b>オプション</b><br>…` |
    # | PFS | 鍵共有 | `<b>PFS</b><br>…` |
    # | 並列処理 | 暗号モード | `<b>並列処理</b><br>…` |
    NOTE_COLUMNS = ("オプション", "PFS", "並列処理")

    def __init__(self, src, out="crypt_normalized.md"):
        """
        ## 初期化

        | 引数 | 型 | 既定値 | 説明 |
        |---|---|---|---|
        | `src` | `str` | (必須) | 元の md |
        | `out` | `str` | `crypt_normalized.md` | 出力する md |
        """
        here = os.path.dirname(os.path.abspath(__file__))
        self.src = src if os.path.isabs(src) else os.path.join(here, src)
        self.out = out if os.path.isabs(out) else os.path.join(here, out)
        with open(self.src, encoding="utf-8", newline="") as f:
            self.text = f.read().replace("\r\n", "\n")

    @staticmethod
    def clean(cell):
        """
        ## セルの中身を1行にする

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cell` | `str` | 元のセルの中身 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | 各行の前後の空白を除いてつなぎ、`<ul class="…">` などの `class` を除いたもの |
        """
        s = "".join(line.strip() for line in cell.split("\n"))
        s = re.sub(r"<(ul|li)\s+class=\"[^\"]*\"", r"<\1", s).strip()
        return CryptMdNormalizer.sentences_to_br(s)

    @staticmethod
    def sentences_to_br(s):
        """
        ## 文の区切りの `。` を `<br>` にする

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `s` | `str` | セルの中身(1行にしたもの) |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | 下の変換をしたもの |

        | 変換 | 例 |
        |---|---|
        | `(…。…)` の括弧内の `。` は `<br>` にし、改行で意味が切れて不自然になる外側の括弧は外す | `(A。B)` → `A<br>B` |
        | 括弧の外の `。` も `<br>` にする | `A。B` → `A<br>B` |
        | 文末の `。` は消す(`<br>` を残さない) | `A。` → `A` |
        """
        s = re.sub(r"\(([^()]*。[^()]*)\)", lambda m: m.group(1), s)   # 括弧内に 。 があるものは括弧を外す
        s = re.sub(r"。(?=$|<br>|</li>|</ul>)", "", s)                   # 文末・行末の 。 は消す
        return s.replace("。", "<br>")

    @staticmethod
    def plain(cell):
        """
        ## 列名の判定用に、タグと括弧書きを除く

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `cell` | `str` | 見出しのセル |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 文字列 | `str` | `PQC<br>(ポスト量子暗号)` → `PQC` |
        """
        return re.sub(r"\s+", "", re.split(r"<br>|\(", cell)[0]).strip()

    def sections(self):
        """
        ## `### 見出し` ごとに分ける

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | セクションのリスト | `list[tuple[str, str]]` | (見出し, 本文) |
        """
        parts = re.split(r"^### (.+)$", self.text, flags=re.M)
        return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts), 2)]

    def parse_md_table(self, body):
        """
        ## Markdown 表を行・セルに分解する

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `body` | `str` | セクションの本文 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行のリスト | `list[list[str]]` | 先頭が見出し行。区切り行(`---`)は除く |
        """
        rows = []
        for line in body.split("\n"):
            if line.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", line):
                rows.append([self.clean(c) for c in line.strip()[1:-1].split("|")])
        return rows

    def parse_html_table(self, body):
        """
        ## HTML 表を、`rowspan` を展開して行・セルに分解する

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `body` | `str` | セクションの本文 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行のリスト | `list[list[str]]` | 先頭が見出し行。`rowspan` で結合されたセルは、下の行にも同じ値を入れる |
        """
        body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
        rows, pending = [], {}              # pending: 列番号 → (残り行数, 中身)
        for tr in re.findall(r"<tr\b[^>]*>(.*?)</tr>", body, flags=re.S):
            cells = re.findall(r"<(?:td|th)\b([^>]*)>(.*?)</(?:td|th)>", tr, flags=re.S)
            row, it, col = [], iter(cells), 0
            while True:
                if col in pending:
                    left, val = pending[col]
                    row.append(val)
                    pending[col] = (left - 1, val)
                    if left - 1 == 0:
                        del pending[col]
                else:
                    c = next(it, None)
                    if c is None:
                        break
                    val = self.clean(c[1])
                    row.append(val)
                    m = re.search(r"rowspan=\"(\d+)\"", c[0])
                    if m and int(m.group(1)) > 1:
                        pending[col] = (int(m.group(1)) - 1, val)
                col += 1
            rows.append(row)
        return rows

    def to_unified(self, head, row):
        """
        ## 1行を8列にそろえる

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `head` | `list[str]` | 元の見出し行 |
        | `row` | `list[str]` | 元の1行 |

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | 行 | `list[str]` | `COLUMNS` と同じ8セル |
        """
        out, notes = ["-"] * len(self.COLUMNS), []
        for h, v in zip(head, row):
            key = self.plain(h)
            if key in self.NOTE_COLUMNS:
                if v.strip() != "-":                    # 値が `-` の項目は備考に出さない
                    notes.append(f"<b>{key}</b><br>{v}")
            else:
                out[self.MAP[key]] = v
        if notes:
            out[7] = "<br>".join(notes)
        return out

    def build(self):
        """
        ## 整形後の Markdown 全体を作る

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | Markdown | `str` | セクションごとに `### 見出し` と8列の表を並べたもの |
        """
        lines = []
        for title, body in self.sections():
            rows = (self.parse_html_table(body) if "<table" in body else self.parse_md_table(body))
            head, rows = rows[0], rows[1:]
            lines += [f"### {title}", "", "| " + " | ".join(self.COLUMNS) + " |", "|" + "---|" * len(self.COLUMNS)]
            for r in rows:
                if len(r) != len(head):
                    raise ValueError(f"{title}: 列数が違います: {len(r)} / {len(head)} ({r[0]})")
                lines.append("| " + " | ".join(self.to_unified(head, r)) + " |")
            lines.append("")
            print(f"{title}: {len(rows)} 行(元 {len(head)} 列 → {len(self.COLUMNS)} 列)")
        return "\n".join(lines)

    def save(self):
        """
        ## 整形後の Markdown を `self.out` に書き出す

        | 戻り値 | 型 | 説明 |
        |---|---|---|
        | パス | `str` | 書き出したファイルのパス |
        """
        with open(self.out, "w", encoding="utf-8", newline="") as f:
            f.write(self.build())
        print("->", self.out)
        return self.out


if __name__ == "__main__":
    CryptMdNormalizer(sys.argv[1] if len(sys.argv) > 1 else "crypt_source.md").save()
