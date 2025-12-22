"""
app/printer.py

【責務】
生成された画像を CUPS 経由でプリンタに送信する。

【使用箇所】
- main.py
- ntfy_print_daemon.py

【やらないこと】
- 印刷内容の評価
- 再印刷判断
- 履歴管理

【他ファイルとの関係】
- image_processor から受け取った PIL.Image を一時ファイルに変換し、OS に渡すのみ。
"""

from __future__ import annotations

from pathlib import Path
import subprocess
import tempfile

from PIL import Image


class PrintError(RuntimeError):
    """`lp` コマンドが失敗した場合に送出される例外。"""


def print_image(image: Image.Image, printer_name: str) -> None:
    """CUPS の `lp` コマンドを通じて画像を印刷する。

    呼び出し元: main.py, ntfy_print_daemon.py

    入力:
    - image: 印刷対象の PIL.Image
    - printer_name: `lp -d` へ渡すプリンタ名

    副作用:
    - 一時 JPEG ファイルを作成し、印刷後に削除する。
    - 成功・失敗の評価は行わないが、`lp` が異常終了した場合は PrintError を送出する。
    """

    temp_path = _save_temp_image(image)
    try:
        subprocess.run(["lp", "-d", printer_name, str(temp_path)], check=True)
    except subprocess.CalledProcessError as exc:
        raise PrintError("lp command failed") from exc
    finally:
        temp_path.unlink(missing_ok=True)


def _save_temp_image(image: Image.Image) -> Path:
    """PIL.Image を JPEG 形式の一時ファイルとして保存し、そのパスを返す。

    呼び出し元: print_image
    副作用: tempfile.NamedTemporaryFile により一時ファイルを生成する。
    """

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_path = Path(temp_file.name)
        image.save(temp_file, format="JPEG")
    return temp_path
