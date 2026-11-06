import os
import re
import sys
from io import BytesIO
from pathlib import Path, PurePosixPath
from urllib.parse import urlparse

import requests
from PIL import Image, UnidentifiedImageError

ROOT = Path(os.getenv("GITHUB_WORKSPACE") or Path(__file__).resolve().parent.parent.parent)

class DownloadImage:
    """
    ## DownloadImage

    画像のダウンロードと PNG 変換を行うクラス。

    ### クラス定数

    | 名前 | 値 | 説明 |
    | --- | --- | --- |
    | `MAX_BYTES` | 10 MiB | ダウンロード上限サイズ |
    | `MAX_PIXELS` | 50,000,000 | 画素数の上限 (decompression bomb 対策) |
    | `TIMEOUT` | 15 | HTTP タイムアウト (秒) |
    | `ALLOWED_FORMATS` | PNG / JPEG / GIF / WEBP | 受け付ける画像形式 |

    ### インスタンス属性

    | 名前 | 型 | 説明 |
    | --- | --- | --- |
    | `dl_image` | `list[dict]` | ダウンロード対象 (`source`, `targetDir`) |
    | `base_dir` | `Path` | 保存の基準ディレクトリ (既定 `ROOT` = リポジトリのトップ) |
    | `failed` | `int` | 直近の `run()` で失敗した件数 |
    """

    MAX_BYTES = 10 * 1024 * 1024
    MAX_PIXELS = 50_000_000
    TIMEOUT = 15
    ALLOWED_FORMATS = ["PNG", "JPEG", "GIF", "WEBP"]

    def __init__(self, dl_image: list[dict], base_dir: str | Path = ROOT) -> None:
        """
        ## コンストラクタ

        ### 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `dl_image` | `list[dict]` | `{"source": URL, "targetDir": 保存先}` のリスト |
        | `base_dir` | `str \\| Path` | 保存の基準ディレクトリ (既定 `ROOT`) |
        """
        self.dl_image = dl_image
        self.base_dir = Path(base_dir)
        self.failed = 0
        Image.MAX_IMAGE_PIXELS = self.MAX_PIXELS

    def build_dest_path(self, source: str, target_dir: str) -> Path:
        """
        ## 保存先パスを生成する

        URL の末尾要素をファイル名にし、拡張子を `.png` に統一する。

        ### 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `source` | `str` | 取得元 URL |
        | `target_dir` | `str` | 保存先ディレクトリ (`/img/...` 形式) |

        ### 戻り値

        | 型 | 説明 |
        | --- | --- |
        | `Path` | 保存先ファイルのパス (`base_dir` 配下であることを保証) |

        ### 例外

        | 例外 | 条件 |
        | --- | --- |
        | `ValueError` | ファイル名が空、または保存先が `base_dir` の外を指す |
        """
        name = PurePosixPath(urlparse(source).path).stem
        name = re.sub(r"[^A-Za-z0-9_-]", "_", name)
        if not name:
            raise ValueError(f"ファイル名を決定できません: {source}")

        base = self.base_dir.resolve()
        dest_dir = (base / target_dir.lstrip("/")).resolve()
        dest_dir.relative_to(base)  # 範囲外なら ValueError

        return dest_dir / f"{name}.png"

    def download(self, source: str) -> bytes:
        """
        ## URL からバイト列を取得する

        ### 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `source` | `str` | 取得元 URL (`http` / `https` のみ) |

        ### 戻り値

        | 型 | 説明 |
        | --- | --- |
        | `bytes` | 取得したデータ (最大 `MAX_BYTES`) |

        ### 例外

        | 例外 | 条件 |
        | --- | --- |
        | `ValueError` | スキームが不正、またはサイズ超過 |
        | `requests.RequestException` | 通信エラー・HTTP エラー |
        """
        if urlparse(source).scheme not in ("http", "https"):
            raise ValueError(f"許可されていないスキームです: {source}")

        buf = bytearray()
        with requests.get(source, timeout=self.TIMEOUT, stream=True) as res:
            res.raise_for_status()
            for chunk in res.iter_content(chunk_size=64 * 1024):
                buf.extend(chunk)
                if len(buf) > self.MAX_BYTES:
                    raise ValueError(f"サイズ上限を超過しました: {source}")
        return bytes(buf)

    def save_as_png(self, data: bytes, dest: Path) -> None:
        """
        ## 画像データを検証して PNG で保存する

        画像として解釈できないデータ (文字列・SVG・HTML など) は
        `UnidentifiedImageError` となり、保存されない。

        ### 引数

        | 名前 | 型 | 説明 |
        | --- | --- | --- |
        | `data` | `bytes` | 画像のバイト列 |
        | `dest` | `Path` | 保存先ファイルパス |

        ### 例外

        | 例外 | 条件 |
        | --- | --- |
        | `PIL.UnidentifiedImageError` | 許可形式の画像として読めない |
        | `PIL.Image.DecompressionBombError` | 画素数が `MAX_PIXELS` 超過 |
        """
        # verify() 後は画像を再利用できないため、開き直す
        Image.open(BytesIO(data), formats=self.ALLOWED_FORMATS).verify()
        with Image.open(BytesIO(data), formats=self.ALLOWED_FORMATS) as img:
            img.load()
            if img.mode not in ("RGB", "RGBA", "L", "LA"):
                img = img.convert("RGBA")
            dest.parent.mkdir(parents=True, exist_ok=True)
            img.save(dest, format="PNG")

    def run(self) -> int:
        """
        ## 全件を処理する

        ### 戻り値

        | 型 | 説明 |
        | --- | --- |
        | `int` | 失敗した件数 (`0` なら全件成功) |
        """
        self.failed = 0
        for item in self.dl_image:
            source, target_dir = item["source"], item["targetDir"]
            try:
                dest = self.build_dest_path(source, target_dir)
                self.save_as_png(self.download(source), dest)
                print(f"OK   {source} -> {dest}")
            except (ValueError, UnidentifiedImageError, Image.DecompressionBombError,
                    requests.RequestException, OSError) as e:
                self.failed += 1
                print(f"FAIL {source}: {type(e).__name__}: {e}", file=sys.stderr)
        return self.failed


if __name__ == "__main__":
    DL_IMAGE = [
        {
            "source": "https://opengraph.github.com/1/BX293APEN/Yocto_Docker",
            "targetDir": "/img/linuxMemo",
        },
        {
            "source": "https://opengraph.github.com/1/BX293APEN/LFS_Docker",
            "targetDir": "/img/linuxMemo",
        },
        {
            "source": "https://opengraph.github.com/1/BX293APEN/OpenWrt_Docker",
            "targetDir": "/img/linuxMemo",
        },
        {
            "source": "https://opengraph.github.com/1/BX293APEN/Gentoo_Docker",
            "targetDir": "/img/linuxMemo",
        },
    ]

    DownloadImage(DL_IMAGE).run()
