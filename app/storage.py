"""
app/storage.py

【責務】
Presence Note v1 では履歴を保持しないため、呼び出しを受けても何も保存しない明示的な空実装として振る舞う。

【使用箇所】
- main.py
- ntfy_print_daemon.py

【やらないこと】
- ファイル書き込み
- 履歴管理
- 集計・分析

【他ファイルとの関係】
- main から呼ばれても即座に復帰し、副作用を生まないことで AGENTS.md の「永続化禁止」を担保する。
"""

from __future__ import annotations

from typing import Any, Mapping


def save_history(_: str | None = None, metadata: Mapping[str, Any] | None = None) -> None:
    """履歴保存を行わずに即座に戻るノップ関数。

    呼び出し元: main.py, ntfy_print_daemon.py

    入力:
    - _: 受け取るが使用しない画像パス
    - metadata: 任意の追加情報（未使用）

    出力 / 副作用:
    - 何も返さず、副作用も生まない。
    - AGENTS.md の永続化禁止に従い、あえて空実装として残す。
    """

    return None
