"""
app/logger.py

【責務】
Presence Note の節目を最小限のメッセージとして出力する。

【使用箇所】
- main.py および ntfy_print_daemon.py から呼び出される。

【やらないこと】
- 詳細なデバッグログ
- 失敗通知や再試行判断
- ログファイルへの永続化

【他ファイルとの関係】
- config, receiver, printer とは疎結合であり、メッセージ文字列のみを受け取る。
"""

from __future__ import annotations

import datetime as _dt
import sys


def log_event(message: str) -> None:
    """節目の出来事を静かに標準出力へ書き出す。

    呼び出し元:
    - main.py や ntfy_print_daemon.py

    入力:
    - message: 出力したい短い文言

    出力 / 副作用:
    - タイムスタンプ付きの文字列を stdout に出力する以外の副作用は持たない。
    """

    timestamp = _dt.datetime.now().isoformat(timespec="seconds")
    print(f"[{timestamp}] {message}", file=sys.stdout, flush=True)
