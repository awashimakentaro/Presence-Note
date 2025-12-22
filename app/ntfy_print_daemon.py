"""
app/ntfy_print_daemon.py

【責務】
Presence Note を常駐プロセスとして動作させ、ntfy 受信→印刷の連続フローを監視する。

【使用箇所】
- systemd などのサービス設定から実行される想定。

【やらないこと】
- 履歴管理
- 失敗時の再送
- 条件付きの複雑な分岐

【他ファイルとの関係】
- config から設定を取得し、main.run_cycle を繰り返し呼ぶ。
"""

from __future__ import annotations

import argparse
import time
from typing import Optional

from . import config
from .config import Settings
from .environment import load_env_file
from .logger import log_event
from .main import run_cycle


def main() -> None:
    """コマンドライン引数と環境変数を統合し、常駐ループを開始する。"""

    load_env_file()
    args = _parse_args()
    settings = _prepare_settings(args)
    if not settings:
        log_event("設定値が不足しているため終了します")
        return

    _run_loop(settings, args.idle_wait)


def _parse_args() -> argparse.Namespace:
    """ntfy_print_daemon.py 用の CLI 引数を定義し、解析する。"""

    parser = argparse.ArgumentParser(description="Presence Note ntfy daemon")
    parser.add_argument("--topic", help="ntfy topic URL (例: https://ntfy.sh/xxx/json)")
    parser.add_argument("--printer", help="CUPS 登録済みのプリンタ名")
    parser.add_argument("--token", help="ntfy Bearer token", default=None)
    parser.add_argument(
        "--idle-wait",
        type=float,
        default=1.0,
        help="1 サイクル完了後に待機する秒数",
    )
    return parser.parse_args()


def _prepare_settings(args: argparse.Namespace) -> Optional[Settings]:
    """環境変数の設定と CLI の上書きを統合し、Settings を生成する。"""

    try:
        base = config.load_settings()
    except ValueError:
        base = None

    topic = args.topic or (base.ntfy_topic_url if base else None)
    printer = args.printer or (base.printer_name if base else None)
    token = args.token or (base.ntfy_token if base else None)

    if not topic or not printer:
        return None

    output_size = base.output_size_mm if base else config.DEFAULT_OUTPUT_SIZE_MM
    dpi = base.dpi if base else config.DEFAULT_DPI

    return Settings(
        ntfy_topic_url=topic,
        printer_name=printer,
        ntfy_token=token,
        output_size_mm=output_size,
        dpi=dpi,
    )


def _run_loop(settings: Settings, idle_wait: float) -> None:
    """無限ループで run_cycle を呼び出し続ける。"""

    log_event("ntfy_print_daemon を開始します")
    while True:
        try:
            run_cycle(settings)
        except Exception as exc:  # noqa: BLE001 - 失敗内容を握りつぶす
            log_event(f"処理が失敗しました: {exc}")
        time.sleep(idle_wait)


if __name__ == "__main__":
    main()
