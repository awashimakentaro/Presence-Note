"""
app/storage.py

【責務】
ntfy から受信した元画像を `app/history` 配下に日付単位で保存する。

【使用箇所】
- main.py
- ntfy_print_daemon.py

【やらないこと】
- メタデータの分析
- 画像内容の評価
- 保存データのローテーション

【他ファイルとの関係】
- history ディレクトリの構造はこのモジュールが一元管理し、他モジュールは介入しない。
"""

from __future__ import annotations

from datetime import datetime
import imghdr
from pathlib import Path
from typing import Any, Mapping

HISTORY_ROOT = Path(__file__).resolve().parent / "history"


def save_history(image_bytes: bytes, metadata: Mapping[str, Any] | None = None) -> Path:
    """受信した画像を history ディレクトリへ保存する。"""

    timestamp = datetime.now()
    day_dir = HISTORY_ROOT / timestamp.strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)

    extension = _detect_extension(image_bytes)
    filename = f"{timestamp.strftime('%H%M%S_%f')}.{extension}"
    file_path = day_dir / filename
    file_path.write_bytes(image_bytes)
    _ = metadata
    return file_path


def _detect_extension(image_bytes: bytes) -> str:
    """画像バイト列から適切な拡張子を推定する。"""

    guessed = imghdr.what(None, h=image_bytes)
    if guessed == "jpeg":
        return "jpg"
    if not guessed:
        return "bin"
    return guessed
