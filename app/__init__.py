"""
app パッケージ

【責務】
Presence Note を構成する各エージェント実装を論理的にまとめる。

【使用箇所】
- main.py / ntfy_print_daemon.py からモジュール単位で参照される。

【やらないこと】
- 初期化処理の実行
- グローバル状態の保持
- 依存解決

【他ファイルとの関係】
- config / receiver / image_processor / printer / storage / logger などのモジュールを名前空間として公開するだけ。
"""

from .config import Settings, load_settings
from .receiver import ReceivedPayload, wait_for_image
from .image_processor import compose_image
from .printer import print_image
from .storage import save_history
from .logger import log_event

__all__ = [
    "Settings",
    "load_settings",
    "ReceivedPayload",
    "wait_for_image",
    "compose_image",
    "print_image",
    "save_history",
    "log_event",
]
