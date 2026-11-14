#!/usr/bin/env python3
"""
sitemap.md から "/" で始まり ".html" で終わる href を読み込み、
TEMPLATE に合成して sitemap.js に出力する。

使い方:
    python gen_sitemap_js.py [sitemap.md] [出力ファイル] [template.json]
    (省略時: ./sitemap.md  ->  ./sitemap.js、テンプレートは ./template.json)

template.json は [{"href" : "...", "word" : ["..."]}, ...] 形式 (JSONなので末尾カンマ不可)。
template.json 内で href が重複している場合は、最初の位置に word を追記してまとめる。

word の決め方 (sitemap.md の href ごと):
  1. キー名がある場合 : キー名から "Tip" を除いた値 (linuxTipMemo -> linuxMemo)
                        キー名が複数あれば全て配列に入れる
  2. キー名が無い場合 (-) : href の最後の "/" から ".html" までの値から
                        "-" "_" などを詰めた値 (critical-cyber-attack -> criticalcyberattack)
                        index.html は重複するので親フォルダ名 (/API/index.html -> API)
  ※ 大文字小文字は変えない

TEMPLATE に同じ href があれば、キー名由来の word だけ追記する (重複は除く)。
TEMPLATE に無ければ新規エントリを追加する (キー名が無ければ href から作る)。
並び順:
  1. ページ番号が無い内部リンク (TEMPLATE の順、新規は末尾)
  2. ページ番号がある内部リンク
       ページ番号の昇順 -> 同じ番号ならファイル名 (hrefの最後の "/" 以降) の昇順
       (大文字小文字は区別しない。例: linux.html は linuxMemo.html より前)
       -> それも同じなら href 全体の昇順
  3. 外部リンク (TEMPLATE の順、新規は末尾)
ページ番号は sitemap.md の4カラム目。同じ href に複数あれば最小値を使う (ページ番号が無い行 (-) は無視)。
"""
import json
import re
import sys
from pathlib import Path

class GenSiteMapJS:
    
    def __init__(self, mdFile="sitemap.md", out="sitemap.js", template = "template.json"):
        self.md_path = Path(mdFile)
        self.out_path = Path(out)
        if not self.md_path.is_file():
            sys.exit(f"ファイルが見つかりません: {self.md_path}")
        self.TEMPLATE = self.load_template(template)
        self.pages = {}  # href -> ページ番号 (load_md で設定)

        self.entries = self.merge(self.load_md())
        self.write()

    @staticmethod
    def word_from_key(key: str) -> str:
        """キー名から Tip を除く (linuxTipMemo -> linuxMemo)"""
        return key.replace("Tip", "")

    @staticmethod
    def word_from_href(href: str) -> str:
        """hrefの最後の / から .html までの値。- などは詰める。index.html は親フォルダ名"""
        parts = href.split("/")
        stem = parts[-1][: -len(".html")]
        if stem == "index":
            stem = parts[-2] if len(parts) >= 3 and parts[-2] else "index"
        return re.sub(r"[-_.\s]+", "", stem)

    @staticmethod
    def add_words(words: list, new: list):
        """大文字小文字を区別せず、未登録の word だけ追加する"""
        lower = {w.lower() for w in words}
        for w in new:
            if w and w.lower() not in lower:
                words.append(w)
                lower.add(w.lower())

    def load_template(self, path) -> list:
        """template.json を読み込む。href が重複していれば最初の位置にwordをappendする"""
        path = Path(path)
        if not path.is_file():
            sys.exit(f"ファイルが見つかりません: {path}")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            sys.exit(f"JSONの読み込みに失敗しました: {path} ({e})")

        merged = {}  # 辞書は挿入順を保つ -> 最初に出た位置が残る
        for i, item in enumerate(data):
            if not isinstance(item, dict) or "href" not in item:
                sys.exit(f"{path}: {i + 1}番目の要素に href がありません")
            entry = merged.setdefault(item["href"], {"href": item["href"], "word": []})
            self.add_words(entry["word"], item.get("word", []))
        return list(merged.values())

    def load_md(self) -> dict:
        """sitemap.md の表を読み、href -> キー名由来の word のリスト (出現順) を返す
        (ページ番号は self.pages に href -> 番号 で入れる。複数あれば最小値。- は無視)"""
        keys = {}  # href -> [キー名, ...]
        for line in self.md_path.read_text(encoding="utf-8").splitlines():
            if not line.startswith("|"):
                continue
            cells = [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)[1:-1]]
            if len(cells) < 3:
                continue  # 先頭3カラム (href / 出典 / キー名) だけ使う (ページ列は無視)
            href, _source, key = cells[:3]
            page = cells[3] if len(cells) > 3 else "-"
            if not (href.startswith("/") and href.endswith(".html")):
                continue  # ヘッダ行・区切り行・外部リンク・html以外
            keys.setdefault(href, [])
            if page.isdigit():
                self.pages[href] = min(int(page), self.pages.get(href, int(page)))
            if key != "-":
                keys[href].append(key)

        result = {}
        for href, key_list in keys.items():
            words = []
            self.add_words(words, [self.word_from_key(k) for k in key_list])
            result[href] = words  # キー名が無ければ空 (merge で href から補う)
        return result

    def merge(self, md_words: dict) -> list:
        """TEMPLATE (コピー) に合成する。最後に
        ページ番号なしの内部リンク -> ページ番号順 (同じ番号はファイル名順) の内部リンク -> 外部リンク の順に並べ直す
        (ページ番号なしと外部は TEMPLATE の順を保ち、新規は末尾に追加。TEMPLATE の途中に外部リンクがあってもよい)"""
        entries = [{"href": e["href"], "word": list(e["word"])} for e in self.TEMPLATE]
        index = {e["href"]: e for e in entries}

        for href, words in md_words.items():
            if href in index:
                # TEMPLATE に word があるので、キー名由来の word だけ追記する
                self.add_words(index[href]["word"], words)
            else:
                # キー名が無ければ href から作る
                entry = {"href": href, "word": list(words) or [self.word_from_href(href)]}
                entries.append(entry)
                index[href] = entry

        # 内部 (ページ番号なし) -> 内部 (ページ番号順 -> ファイル名順) -> 外部
        internal = [e for e in entries if e["href"].startswith("/")]
        external = [e for e in entries if not e["href"].startswith("/")]
        no_page = [e for e in internal if e["href"] not in self.pages]
        paged = sorted(
            (e for e in internal if e["href"] in self.pages),
            key=lambda e: (
                self.pages[e["href"]],
                e["href"].rsplit("/", 1)[-1].casefold(),
                e["href"],
            ),
        )
        return no_page + paged + external

    def write(self):
        q = lambda s: '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
        lines = ["let sitemap = ["]
        for e in self.entries:
            lines.append("    {")
            lines.append(f'        "href" : {q(e["href"])},')
            lines.append('        "word" : [' + ", ".join(q(w) for w in e["word"]) + "]")
            lines.append("    },")
        lines.append("]")

        self.out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{len(self.entries)} 件を {self.out_path} に出力しました")


if __name__ == "__main__":
    GenSiteMapJS(
        mdFile=sys.argv[1] if len(sys.argv) > 1 else "sitemap.md",
        out=sys.argv[2] if len(sys.argv) > 2 else "sitemap.js",
        template=sys.argv[3] if len(sys.argv) > 3 else "template.json",
    )
