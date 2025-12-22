"""
app/environment.py

【責務】
`.env` ファイルを読み込み、環境変数へ反映するための極小ヘルパーを提供する。

【使用箇所】
- app/main.py
- app/ntfy_print_daemon.py

【やらないこと】
- 環境変数の検証
- 設定値の生成
- ファイル監視

【他ファイルとの関係】
- config.py が読む環境変数の前処理として使われる。
- 他モジュールに副作用を与えないため、`load_env_file` の戻り値は常に None。
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


def load_env_file(env_path: Optional[str] = None) -> None:
    """`.env` を読み込み、環境変数に反映する。

    呼び出し元:
    - main.py / ntfy_print_daemon.py のエントリポイント

    入力:
    - env_path: 明示的に `.env` のパスを指定したい場合のみ使用

    出力 / 副作用:
    - `python-dotenv` の `load_dotenv` を呼び出し、プロセス環境へ追加する
    - 既存の環境変数があれば優先し、`.env` は上書きしない
    """

    path = Path(env_path) if env_path else None
    load_dotenv(dotenv_path=path, override=False)
