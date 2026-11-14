#!/usr/bin/env python3
"""
model フォルダ内の全ファイルから "href" キーの値を抽出し、sitemap.md に出力する。

使い方:
    python gen_sitemap.py [modelフォルダ] [出力ファイル]
    (省略時: ./model  ->  ./sitemap.md)

- model/index/index.js は検索対象外 (EXCLUDE)
- JSは実行せず、文字列として読み取る (コメント内の "href" は無視)
- 出力は href / 出典 / キー名 の3カラム (1出現につき1行、hrefの昇順)
- キー名が無い (page リストなど) 場合は -
"""
import re
import sys
from pathlib import Path


class GenerateSiteMap:
    HREF_RE = re.compile(r"""["']href["']\s*:\s*(["'])((?:\\.|(?!\1).)*)\1""")
    KEY_RE = re.compile(r"""["']([^"'\n]+)["']\s*:\s*\{""")
    # 検索対象外 (modelフォルダからの相対パス。index.js は bookmark.js に移行済み)
    EXCLUDE = ("index/index.js",)

    def __init__(self, modelDir="model", out="sitemap.md"):
        self.model_dir = Path(modelDir).resolve()
        self.out_path = Path(out)
        if not self.model_dir.is_dir():
            sys.exit(f"フォルダが見つかりません: {self.model_dir}")

        self.rows = self.collect()
        self.write()

    @staticmethod
    def strip_comments(src: str) -> str:
        """文字列リテラルを考慮してコメントを空白に置換する (行番号・桁位置は保つ)"""
        out = []
        i, n = 0, len(src)
        quote = None
        while i < n:
            c = src[i]
            if quote:
                out.append(c)
                if c == "\\" and i + 1 < n:
                    out.append(src[i + 1])
                    i += 2
                    continue
                if c == quote:
                    quote = None
                i += 1
            elif c in "\"'`":
                quote = c
                out.append(c)
                i += 1
            elif src.startswith("//", i):
                while i < n and src[i] != "\n":
                    out.append(" ")
                    i += 1
            elif src.startswith("/*", i):
                end = src.find("*/", i + 2)
                end = n if end == -1 else end + 2
                out.extend(ch if ch == "\n" else " " for ch in src[i:end])
                i = end
            else:
                out.append(c)
                i += 1
        return "".join(out)

    @staticmethod
    def esc(s: str) -> str:
        return s.replace("|", "\\|")

    def collect(self) -> list:
        """[(href, 出典 'ファイル:行', キー名 or '-'), ...] を href 順で返す"""
        rows = []
        for path in sorted(self.model_dir.rglob("*.js")):
            if path.relative_to(self.model_dir).as_posix() in self.EXCLUDE:
                continue
            text = self.strip_comments(path.read_text(encoding="utf-8"))
            keys = [(m.start(), m.group(1)) for m in self.KEY_RE.finditer(text)]
            rel = path.relative_to(self.model_dir.parent).as_posix()
            for m in self.HREF_RE.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                key = "-"
                for pos, name in keys:
                    if pos < m.start():
                        key = name
                    else:
                        break
                rows.append((m.group(2), f"{rel}:{line}", key))
        rows.sort(key=lambda r: r[0])  # 安定ソート: 同一hrefはファイル順を保つ
        return rows

    def write(self):
        lines = [
            "# sitemap",
            "",
            f"`{self.model_dir.name}/` 内の JS から抽出した href の一覧 ({len(self.rows)} 件)。",
            "",
            "| href | 出典 | キー名 |",
            "| --- | --- | --- |",
        ]
        for href, source, key in self.rows:
            lines.append(f"| {self.esc(href)} | {self.esc(source)} | {self.esc(key)} |")

        self.out_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{len(self.rows)} 件の href を {self.out_path} に出力しました")


if __name__ == "__main__":
    GenerateSiteMap(
        modelDir=sys.argv[1] if len(sys.argv) > 1 else "../../model",
        out=sys.argv[2] if len(sys.argv) > 2 else "sitemap.md",
    )
