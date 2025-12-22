# app/history

【責務】
ntfy から受信した元画像を日付単位で保存する。

【使用箇所】
- `app/storage.py` からのみ書き込みが行われる。

【やらないこと】
- 加工済み画像の保存
- メタデータの集計
- ローテーションや自動削除

【他ファイルとの関係】
- `storage.save_history` が `YYYY-MM-DD/HHMMSS_uuuuuu.ext` 形式でファイルを作成する。
- 他のモジュールは直接アクセスしない。
