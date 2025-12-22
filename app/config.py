"""
app/config.py

【責務】
Presence Note の動作に必要な設定値を集約し、明示的に取り扱う。

【使用箇所】
- main.py および ntfy_print_daemon.py から読み込まれる。

【やらないこと】
- 入力値の解釈ロジック
- ファイル I/O や保存
- 条件分岐による振る舞いの変更

【他ファイルとの関係】
- receiver や printer などが参照する定数を提供するのみ。
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Tuple

DEFAULT_OUTPUT_SIZE_MM: Tuple[int, int] = (54, 86)
DEFAULT_DPI: int = 300


@dataclass(frozen=True)
class Settings:
    """Presence Note 全体で共有する設定値の集合体。

    属性は environment variable から与えられることを想定し、
    main.py / ntfy_print_daemon.py から参照される。
    参照側では設定値を書き換えない。
    """

    ntfy_topic_url: str
    printer_name: str
    ntfy_token: str | None
    output_size_mm: Tuple[int, int]
    dpi: int


def load_settings() -> Settings:
    """環境変数から設定値を読み込み、構造化して返す。

    期待する環境変数:
    - NTFY_TOPIC_URL: 購読対象の ntfy トピック URL
    - PRINTER_NAME: CUPS に登録されたプリンタ名
    - NTFY_TOKEN (任意): ntfy API の Bearer Token

    いずれも指定がない場合は ValueError を送出し、
    呼び出し側が静かに終了する判断を行う。
    副作用としての永続化やログ出力は行わない。
    """

    topic_url = os.getenv("NTFY_TOPIC_URL")
    printer_name = os.getenv("PRINTER_NAME")
    token = os.getenv("NTFY_TOKEN")

    if not topic_url:
        raise ValueError("NTFY_TOPIC_URL is required")
    if not printer_name:
        raise ValueError("PRINTER_NAME is required")

    return Settings(
        ntfy_topic_url=topic_url,
        printer_name=printer_name,
        ntfy_token=token,
        output_size_mm=DEFAULT_OUTPUT_SIZE_MM,
        dpi=DEFAULT_DPI,
    )
