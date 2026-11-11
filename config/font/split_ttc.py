#!/usr/bin/env python3

import re
import struct
import sys
from pathlib import Path


class SplitTTC:
    """## SplitTTC

    TTC を個別のフォントファイルに分解するクラス。

    ### 定数

    | 名前 | 値 | 説明 |
    |------|----|------|
    | `TTC_TAG` | `b"ttcf"` | TTC ヘッダのタグ |
    | `OTTO_TAG` | `b"OTTO"` | CFF アウトラインを持つ OpenType のバージョン値 |
    | `CHECKSUM_MAGIC` | `0xB1B0AFBA` | `head.checkSumAdjustment` 計算用の定数 |

    ### インスタンス属性

    | 名前 | 型 | 説明 |
    |------|----|------|
    | `src` | `Path` | 入力 TTC ファイルのパス |
    | `outdir` | `Path` | 出力先ディレクトリ (TTC と同じ場所) |
    """

    TTC_TAG = b"ttcf"
    OTTO_TAG = b"OTTO"
    CHECKSUM_MAGIC = 0xB1B0AFBA

    def __init__(self, ttcFontPath):
        """## __init__

        TTC のフォントのパスを受け取り、出力フォルダなどを決める。

        ### 引数

        | 名前 | 型 | 説明 |
        |------|----|------|
        | `ttcFontPath` | `str \\| Path` | 入力 TTC ファイルのパス |

        ### 例外

        | 例外 | 条件 |
        |------|------|
        | `FileNotFoundError` | 指定したファイルが存在しない場合 |
        """
        self.src = Path(ttcFontPath)
        if not self.src.is_file():
            raise FileNotFoundError(f"ファイルが見つかりません: {self.src}")
        # 出力先は TTC と同じディレクトリ
        self.outdir = self.src.parent

    @staticmethod
    def calc_checksum(data: bytes) -> int:
        """## calc_checksum

        SFNT テーブルのチェックサム (32bit 値の総和) を計算する。

        ### 引数

        | 名前 | 型 | 説明 |
        |------|----|------|
        | `data` | `bytes` | チェックサム対象のバイト列 (4 バイト境界に満たない場合は 0 埋め) |

        ### 戻り値

        | 型 | 説明 |
        |----|------|
        | `int` | 32bit に丸めたチェックサム |
        """
        data += b"\0" * (-len(data) % 4)
        return sum(struct.unpack(">%dI" % (len(data) // 4), data)) & 0xFFFFFFFF

    @classmethod
    def read_ttc_offsets(cls, data: bytes) -> list[int]:
        """## read_ttc_offsets

        TTC ヘッダから各フォントの SFNT オフセットを取得する。

        ### 引数

        | 名前 | 型 | 説明 |
        |------|----|------|
        | `data` | `bytes` | TTC ファイル全体 |

        ### 戻り値

        | 型 | 説明 |
        |----|------|
        | `list[int]` | 各フォントのファイル先頭からのオフセット |

        ### 例外

        | 例外 | 条件 |
        |------|------|
        | `ValueError` | TTC ではないファイルが渡された場合 |
        """
        tag, _version, num_fonts = struct.unpack(">4sII", data[:12])
        if tag != cls.TTC_TAG:
            raise ValueError("TTC ファイルではありません (ttcf タグが見つかりません)")
        return list(struct.unpack(">%dI" % num_fonts, data[12:12 + 4 * num_fonts]))

    @staticmethod
    def read_tables(data: bytes, offset: int) -> tuple[bytes, dict[bytes, bytes]]:
        """## read_tables

        1 つのフォントの SFNT テーブルディレクトリを読み、各テーブルの実体を取り出す。

        ### 引数

        | 名前 | 型 | 説明 |
        |------|----|------|
        | `data` | `bytes` | TTC ファイル全体 |
        | `offset` | `int` | 対象フォントの SFNT ヘッダのオフセット |

        ### 戻り値

        | 型 | 説明 |
        |----|------|
        | `tuple[bytes, dict[bytes, bytes]]` | `(sfntVersion, {タグ: テーブルデータ})` |
        """
        sfnt_version, num_tables = struct.unpack(">4sH", data[offset:offset + 6])
        tables: dict[bytes, bytes] = {}
        for i in range(num_tables):
            pos = offset + 12 + 16 * i
            tag, _chk, tbl_off, tbl_len = struct.unpack(">4sIII", data[pos:pos + 16])
            tables[tag] = data[tbl_off:tbl_off + tbl_len]
        return sfnt_version, tables

    @classmethod
    def build_font(cls, sfnt_version: bytes, tables: dict[bytes, bytes]) -> bytes:
        """## build_font

        テーブル群から単独の SFNT フォントを組み立てる。
        TTC 内で共有されていたテーブルも複製して書き出し、
        `head.checkSumAdjustment` を再計算する。

        ### 引数

        | 名前 | 型 | 説明 |
        |------|----|------|
        | `sfnt_version` | `bytes` | SFNT バージョン (`b"\\x00\\x01\\x00\\x00"` または `b"OTTO"` など) |
        | `tables` | `dict[bytes, bytes]` | タグをキー、テーブルデータを値とする辞書 |

        ### 戻り値

        | 型 | 説明 |
        |----|------|
        | `bytes` | 単独フォントファイルのバイト列 |
        """
        tags = sorted(tables)
        num_tables = len(tags)

        # ### searchRange / entrySelector / rangeShift
        # テーブル数から二分探索用のパラメータを算出する。
        entry_selector = num_tables.bit_length() - 1
        search_range = (1 << entry_selector) * 16
        range_shift = num_tables * 16 - search_range

        header = struct.pack(">4sHHHH", sfnt_version, num_tables,
                             search_range, entry_selector, range_shift)

        # ### head テーブルの扱い
        # `checkSumAdjustment` (オフセット 8) は一旦 0 にしてチェックサムを計算する。
        head_tag = b"head"
        if head_tag in tables:
            h = bytearray(tables[head_tag])
            h[8:12] = b"\0\0\0\0"
            tables = dict(tables)
            tables[head_tag] = bytes(h)

        directory = b""
        body = b""
        body_start = 12 + 16 * num_tables
        head_pos = None
        for tag in tags:
            tbl = tables[tag]
            pos = body_start + len(body)
            if tag == head_tag:
                head_pos = pos
            directory += struct.pack(">4sIII", tag, cls.calc_checksum(tbl), pos, len(tbl))
            body += tbl + b"\0" * (-len(tbl) % 4)

        font = bytearray(header + directory + body)

        # ### ファイル全体のチェックサム調整値
        if head_pos is not None:
            adjustment = (cls.CHECKSUM_MAGIC - cls.calc_checksum(bytes(font))) & 0xFFFFFFFF
            font[head_pos + 8:head_pos + 12] = struct.pack(">I", adjustment)
        return bytes(font)

    @staticmethod
    def get_postscript_name(tables: dict[bytes, bytes]) -> str | None:
        """## get_postscript_name

        `name` テーブルから PostScript 名 (nameID = 6) を取得する。

        ### 引数

        | 名前 | 型 | 説明 |
        |------|----|------|
        | `tables` | `dict[bytes, bytes]` | `read_tables` で得たテーブル辞書 |

        ### 戻り値

        | 型 | 説明 |
        |----|------|
        | `str \\| None` | PostScript 名。取得できなければ `None` |
        """
        name = tables.get(b"name")
        if not name or len(name) < 6:
            return None
        _fmt, count, string_offset = struct.unpack(">HHH", name[:6])
        for i in range(count):
            rec = name[6 + 12 * i:18 + 12 * i]
            if len(rec) < 12:
                break
            platform, _enc, _lang, name_id, length, off = struct.unpack(">6H", rec)
            if name_id != 6:
                continue
            raw = name[string_offset + off:string_offset + off + length]
            # Windows / Unicode は UTF-16BE、それ以外は Latin-1 として解釈する
            text = raw.decode("utf-16-be" if platform in (0, 3) else "latin-1", "ignore")
            if text:
                return text
        return None

    def split(self) -> list[Path]:
        """## split

        TTC を分解して、個別のフォントファイルを `self.outdir` に書き出す。

        ### 戻り値

        | 型 | 説明 |
        |----|------|
        | `list[Path]` | 書き出したファイルのパス一覧 |
        """
        data = self.src.read_bytes()
        self.outdir.mkdir(parents=True, exist_ok=True)

        written: list[Path] = []
        for index, offset in enumerate(self.read_ttc_offsets(data)):
            sfnt_version, tables = self.read_tables(data, offset)
            ext = ".otf" if sfnt_version == self.OTTO_TAG else ".ttf"

            # ファイル名に使えない文字は `_` に置換する
            ps_name = self.get_postscript_name(tables) or f"{self.src.stem}_{index}"
            safe = re.sub(r'[\\/:*?"<>|\s]', "_", ps_name)

            dst = self.outdir / f"{safe}{ext}"
            dst.write_bytes(self.build_font(sfnt_version, tables))
            written.append(dst)
            print(f"[{index}] {dst}")
        return written


def main() -> int:
    """## main

    TTC のファイルパスを `input()` で入力させ、分解処理を実行する。

    ### 戻り値

    | 型 | 説明 |
    |----|------|
    | `int` | 終了コード (`0`: 成功, `1`: 失敗) |
    """
    # ドラッグ&ドロップ時に付く前後の空白や引用符を取り除く
    path = input("TTC ファイルのパス: ").strip().strip('"').strip("'")

    try:
        SplitTTC(path).split()
    except (OSError, ValueError, struct.error) as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    # TTC のファイルパスは起動後に input() で入力する
    # TTC と同じディレクトリに分解したフォントを出力する
    sys.exit(main())
