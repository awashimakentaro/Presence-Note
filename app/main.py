"""
app/main.py

【責務】
Presence Note の直列ワークフローを 1 サイクルだけ実行するエントリポイント。

【使用箇所】
- 手動実行時 (`python app/main.py`)

【やらないこと】
- ループ処理（常駐は ntfy_print_daemon.py が担う）
- 再試行
- 永続化

【他ファイルとの関係】
- config, receiver, image_processor, printer, storage を順番に呼び出すだけで、状態は保持しない。
"""

from __future__ import annotations

from typing import Any

from .config import Settings, load_settings
from .environment import load_env_file
from .image_processor import compose_image
from .logger import log_event
from .printer import print_image
from .receiver import wait_for_image
from .storage import save_history


def main() -> None:
    """設定を読み込み、1 件の印刷処理を直列に行う。"""

    load_env_file()
    try:
        settings = load_settings()
    except ValueError as exc:
        log_event(f"設定が不足しています: {exc}")
        return

    try:
        run_cycle(settings)
    except Exception as exc:  # noqa: BLE001 - 失敗内容は静かに伝えて終了
        log_event(f"処理が失敗しました: {exc}")


def run_cycle(settings: Settings) -> None:
    """1 サイクル分の受信 → 合成 → 印刷を実行する。

    途中で失敗した場合は例外を上位へ伝搬させ、呼び出し元が終了判断を行う。
    余計な副作用は生まない。
    """

    log_event("受信を待機します")
    payload = wait_for_image(settings.ntfy_topic_url, settings.ntfy_token)
    log_event("画像を受信しました")

    final_image = compose_image(
        payload.image_bytes,
        payload.caption,
        settings.output_size_mm,
        settings.dpi,
    )
    log_event("印刷データを整形しました")

    print_image(final_image, settings.printer_name)
    log_event("印刷を依頼しました")

    metadata: dict[str, Any] = {
        "caption": payload.caption,
        "topic": settings.ntfy_topic_url,
    }
    save_history(payload.image_bytes, metadata)


if __name__ == "__main__":
    main()
