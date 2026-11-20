"""
# find_class.py

指定フォルダ以下の `.html` / `.htm` を再帰的に探索し、
指定した文字列を含むファイルと該当行を表示する。
最後に `input()` で待機するため、ダブルクリック実行でも画面がすぐ閉じない。

## クラス

| 名前 | 説明 |
|---|---|
| `Find` | 探索・読み込み・表示をまとめたクラス |

## `Find` のメンバ

| 名前 | 種別 | 説明 |
|---|---|---|
| `find` | 属性 | 検索する文字列 |
| `root` | 属性 | 探索を開始するフォルダ (`Path`) |
| `exts` | 属性 | 対象とする拡張子 |
| `encodings` | 属性 | 読み込み時に順に試す文字コード |
| `read_text` | メソッド | 文字コードを順に試してファイルを読む |
| `find_matches` | メソッド | 該当ファイルと該当行を集める |
| `show` | メソッド | 結果を表示する |
"""

import traceback
from pathlib import Path


class Find:
    def __init__(
        self,
        find="hello",
        dirName=".",
        exts=(".html", ".htm"),
        encodings=("utf-8", "cp932", "euc-jp"),
    ):
        """
        ## __init__

        設定を属性に保存するだけで、探索はしない (探索は `show` で行う)。

        ### 引数

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `find` | `str` | 検索する文字列 |
        | `dirName` | `str` | 探索を開始するフォルダ |
        | `exts` | `tuple[str, ...]` | 対象とする拡張子 |
        | `encodings` | `tuple[str, ...]` | 順に試す文字コード |

        ### 戻り値

        | 型 | 説明 |
        |---|---|
        | `None` | 戻り値なし |
        """
        # **属性に保存** (他のメソッドから `self.` で参照できるようにする)
        self.find = find
        self.root = Path(dirName).resolve()
        self.exts = exts
        self.encodings = encodings

    def read_text(self, path):
        """
        ## read_text

        複数の文字コードを順に試してファイルを読み込む。

        ### 引数

        | 引数 | 型 | 説明 |
        |---|---|---|
        | `path` | `Path` | 読み込むファイルのパス |

        ### 戻り値

        | 型 | 説明 |
        |---|---|
        | `str` | ファイルの内容。どの文字コードでも失敗した場合は `utf-8` で置換読み込みした結果 |
        """
        # **文字コードを順に試す**
        for enc in self.encodings:
            try:
                return path.read_text(encoding=enc)
            except UnicodeDecodeError:
                continue
        # **最終手段**: 読めない文字は置換して読み込む
        return path.read_text(encoding="utf-8", errors="replace")

    def find_matches(self):
        """
        ## find_matches

        `self.root` 以下のHTMLから `self.find` を含むファイルと該当行を集める。

        ### 引数

        なし

        ### 戻り値

        | 型 | 説明 |
        |---|---|
        | `list[tuple[Path, list[tuple[int, str]]]]` | `(ファイルパス, [(行番号, 行の内容), ...])` のリスト |
        """
        results = []

        # **再帰的に探索** (パス順に並べて出力を安定させる)
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in self.exts:
                continue

            try:
                text = self.read_text(path)
            except OSError as e:
                # **読み込めないファイルはスキップして続行**
                print(f"[スキップ] {path} ({e})")
                continue

            if self.find not in text:
                continue

            # **該当行を行番号付きで収集**
            hits = [
                (no, line.strip())
                for no, line in enumerate(text.splitlines(), start=1)
                if self.find in line
            ]
            results.append((path, hits))

        return results

    def show(self):
        """
        ## show

        探索を実行して結果を表示する。

        ### 引数

        なし

        ### 戻り値

        | 型 | 説明 |
        |---|---|
        | `None` | 戻り値なし |
        """
        print(f"探索フォルダ: {self.root}")
        print(f"検索文字列  : {self.find}\n")

        results = self.find_matches()

        if not results:
            print("該当するHTMLファイルは見つかりませんでした。")
            return

        print(f"{len(results)} 件のHTMLが見つかりました。\n")
        for path, hits in results:
            print(f"■ {path.relative_to(self.root)}")
            for no, line in hits:
                # **長すぎる行は切り詰める**
                short = line if len(line) <= 120 else line[:120] + " ..."
                print(f"    {no:>5}: {short}")
            print()


if __name__ == "__main__":
    f = input("検索文字列 : ")
    try:
        Find(f, "../").show()
    except Exception:
        # **エラーが出ても内容を読めるようにする**
        traceback.print_exc()
    finally:
        # **ウィンドウがすぐ閉じるのを防止**
        input("\nEnterキーを押すと終了します...")
