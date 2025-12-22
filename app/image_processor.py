"""
app/image_processor.py

【責務】
受信した写真を 54mm × 86mm の印刷領域にフィットさせる。

【使用箇所】
- main.py
- ntfy_print_daemon.py

【やらないこと】
- テキストの生成や意味付け
- 履歴保存
- 再試行・分岐ロジック

【他ファイルとの関係】
- receiver から受け取ったバイト列を PIL.Image に変換し、printer が利用できる形へ渡す。
"""

from __future__ import annotations

from io import BytesIO
from typing import Tuple

from PIL import Image


def compose_image(photo_bytes: bytes, caption: str, output_size_mm: Tuple[int, int], dpi: int) -> Image.Image:
    """受信写真を 90 度回転させるだけの最終画像を返す。

    呼び出し元:
    - main.py / ntfy_print_daemon.py

    入力:
    - photo_bytes: 受信した写真データ
    - caption: 互換性のために受け取るが加工には使用しない
    - output_size_mm: (幅mm, 高さmm)
    - dpi: 解像度

    出力:
    - PIL.Image の RGB 画像

    副作用:
    - メモリ上で PIL Image を生成する以外の副作用はない。
    """

    _ = _mm_to_px(output_size_mm, dpi)  # SRP のため計算のみ行い副作用を残さない
    photo = Image.open(BytesIO(photo_bytes)).convert("RGB")
    return _rotate_photo(photo)


def _mm_to_px(size_mm: Tuple[int, int], dpi: int) -> Tuple[int, int]:
    """mm 単位のサイズを DPI を利用してピクセルに変換する。

    永続化せず単純計算のみを行う。
    """

    width_mm, height_mm = size_mm
    width_px = int(round(width_mm / 25.4 * dpi))
    height_px = int(round(height_mm / 25.4 * dpi))
    return width_px, height_px


def _rotate_photo(image: Image.Image) -> Image.Image:
    """受信画像を時計回りに 90 度回転させる。"""

    return image.rotate(90, expand=True)
