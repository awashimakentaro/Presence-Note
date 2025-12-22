"""
app/receiver.py

【責務】
ntfy から画像メッセージを1件だけ受信し、バイト列として呼び出し側へ渡す。

【使用箇所】
- main.py
- ntfy_print_daemon.py

【やらないこと】
- データ内容の意味解釈
- 再試行や履歴管理
- 受信可否の報告

【他ファイルとの関係】
- config で定義された URL やトークンを入力として受け取り、image_processor へ渡す素材を生成する。
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Dict, Optional

import requests


class ReceiverError(RuntimeError):
    """受信が完了する前に終了した場合に送出される例外。"""


@dataclass(frozen=True)
class ReceivedPayload:
    """ntfy から受信した1件のメッセージ内容。

    Attributes
    ----------
    image_bytes: 添付画像の生バイト列
    caption: メッセージ本文（空文字列を許容）
    """

    image_bytes: bytes
    caption: str


def wait_for_image(topic_url: str, token: Optional[str] = None, request_timeout: int = 90) -> ReceivedPayload:
    """ntfy トピックを購読し、最初の添付付きメッセージを同期的に受信する。

    呼び出し元: main.py, ntfy_print_daemon.py

    入力:
    - topic_url: ntfy topic の完全 URL。末尾に /json を付与することで JSON ストリームを期待する。
    - token: Bearer 認証が必要な場合のトークン（任意）
    - request_timeout: ネットワークタイムアウト秒数

    出力:
    - ReceivedPayload（画像バイト列と本文）

    副作用:
    - HTTP GET を発行し、ストリームを読み取る。ファイル保存などの永続化は行わない。
    """

    endpoint = _ensure_json_endpoint(topic_url)
    headers = _build_headers(token)
    with requests.get(endpoint, headers=headers, stream=True, timeout=request_timeout) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            payload = _parse_line(line)
            if not payload:
                continue
            attachment = payload.get("attachment")
            if not isinstance(attachment, dict):
                continue
            attachment_url = attachment.get("url")
            if not attachment_url:
                continue
            image_bytes = _download_attachment(attachment_url, headers, request_timeout)
            caption = payload.get("message") or ""
            return ReceivedPayload(image_bytes=image_bytes, caption=caption)

    raise ReceiverError("画像付きメッセージを取得できませんでした")


def _parse_line(raw_line: bytes) -> Dict[str, object] | None:
    """ntfy の JSON ラインを辞書に変換する。

    JSON でない行や event!=message の行は None を返し、呼び出し元がスキップする。
    副作用はない。
    """

    try:
        decoded = raw_line.decode("utf-8")
        parsed = json.loads(decoded)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return None
    if parsed.get("event") != "message":
        return None
    return parsed


def _build_headers(token: Optional[str]) -> Dict[str, str]:
    """ntfy 呼び出しに使用する HTTP ヘッダーを生成する。

    Authorization が必要な場合のみ Bearer ヘッダーを追加する。
    それ以外の副作用は持たない。
    """

    headers: Dict[str, str] = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _download_attachment(url: str, headers: Dict[str, str], timeout: int) -> bytes:
    """添付ファイルの URL から画像データをダウンロードして返す。

    受信に成功するとバイト列を返し、失敗時は requests の例外をそのまま伝搬させる。
    ファイル保存や再試行は行わない。
    """

    response = requests.get(url, headers=headers, timeout=timeout)
    response.raise_for_status()
    return response.content


def _ensure_json_endpoint(topic_url: str) -> str:
    """ntfy の JSON エンドポイントを指す URL を返す。

    呼び出し元: wait_for_image

    入力:
    - topic_url: 利用者が設定した URL（末尾に /json があるとは限らない）

    出力 / 副作用:
    - /json が付いていなければ付与した文字列を返す。
    - 文字列操作のみで副作用はない。
    """

    if topic_url.endswith("/json"):
        return topic_url
    if topic_url.endswith("/"):
        return f"{topic_url}json"
    return f"{topic_url}/json"
