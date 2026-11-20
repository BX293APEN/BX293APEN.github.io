"""
# find_texjs.py

スクリプトを置いたフォルダ以下の `.html` / `.htm` を再帰的に探索し、
`tex.js` という文字列を含むファイルをすべて表示する。
最後に `input()` で待機するため、ダブルクリック実行でも画面がすぐ閉じない。

## 定数

| 名前 | 値 | 説明 |
|---|---|---|
| `KEYWORD` | `"tex.js"` | 検索する文字列 |
| `EXTENSIONS` | `(".html", ".htm")` | 対象とする拡張子 |
| `ENCODINGS` | `("utf-8", "cp932", "euc-jp")` | 読み込み時に順に試す文字コード |
"""

import sys
import traceback
from pathlib import Path

KEYWORD = "tex.js"
EXTENSIONS = (".html", ".htm")
ENCODINGS = ("utf-8", "cp932", "euc-jp")


def read_text(path):
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
    for enc in ENCODINGS:
        try:
            return path.read_text(encoding=enc)
        except UnicodeDecodeError:
            continue
    # **最終手段**: 読めない文字は置換して読み込む
    return path.read_text(encoding="utf-8", errors="replace")


def find_matches(root):
    """
    ## find_matches

    `root` 以下のHTMLから `KEYWORD` を含むファイルと該当行を集める。

    ### 引数

    | 引数 | 型 | 説明 |
    |---|---|---|
    | `root` | `Path` | 探索を開始するフォルダ |

    ### 戻り値

    | 型 | 説明 |
    |---|---|
    | `list[tuple[Path, list[tuple[int, str]]]]` | `(ファイルパス, [(行番号, 行の内容), ...])` のリスト |
    """
    results = []

    # **再帰的に探索** (パス順に並べて出力を安定させる)
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue

        try:
            text = read_text(path)
        except OSError as e:
            # **読み込めないファイルはスキップして続行**
            print(f"[スキップ] {path} ({e})")
            continue

        if KEYWORD not in text:
            continue

        # **該当行を行番号付きで収集**
        hits = [
            (no, line.strip())
            for no, line in enumerate(text.splitlines(), start=1)
            if KEYWORD in line
        ]
        results.append((path, hits))

    return results


def main():
    """
    ## main

    探索を実行して結果を表示する。

    ### 引数

    なし

    ### 戻り値

    | 型 | 説明 |
    |---|---|
    | `None` | 戻り値なし |
    """
    # **スクリプト自身のあるフォルダを基準にする** (ダブルクリック実行でもずれない)
    root = Path(sys.argv[0]).resolve().parent
    print(f"探索フォルダ: {root}")
    print(f"検索文字列  : {KEYWORD}\n")

    results = find_matches(root)

    if not results:
        print("該当するHTMLファイルは見つかりませんでした。")
        return

    print(f"{len(results)} 件のHTMLが見つかりました。\n")
    for path, hits in results:
        print(f"■ {path.relative_to(root)}")
        for no, line in hits:
            # **長すぎる行は切り詰める**
            short = line if len(line) <= 120 else line[:120] + " ..."
            print(f"    {no:>5}: {short}")
        print()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # **エラーが出ても内容を読めるようにする**
        traceback.print_exc()
    finally:
        # **ウィンドウがすぐ閉じるのを防止**
        input("\nEnterキーを押すと終了します...")
