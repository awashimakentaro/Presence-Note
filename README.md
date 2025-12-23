# README.md

【責務】
Presence Note v1 のソフトウェア構成・セットアップ・運用方法を人間オペレーター向けにまとめる。

【使用箇所】
- リポジトリ開封直後の参照
- systemd サービス構築や手動デバッグ時の手順書

【やらないこと】
- エージェント実装の詳細解説（各モジュールの docstring を参照）
- プリンタ固有のトラブルシュート
- v1 で禁止されている機能の追加検討

【他ファイルとの関係】
- AGENTS.md / docs 配下の要件を参照しつつ、`app/` 配下の実装に接続するためのハブ文書。

---

## 1. プロジェクト概要
Presence Note は **返信や行動を要求しない “思われている証跡” を静かに印刷する装置** です。設計思想や禁止事項は `AGENTS.md`, `docs/要件定義書.md`, `docs/設計書.md` を必ず参照してください。

本リポジトリはその v1 実装であり、以下のシンプルな 3 エージェント構成を順番に実行します。

1. `Receiver Agent` (`app/receiver.py`): ntfy から添付付きメッセージを 1 件受信
2. `Processor Agent` (`app/image_processor.py`): 受信写真を 90° 回転させる（サイズ調整はプリンタ側に委ねる）
3. `Printer Agent` (`app/printer.py`): CUPS (`lp`) で Canon SELPHY 等へ印刷命令

履歴保持・分析・再試行は一切行いません。失敗しても沈黙し、外部へ通知しません。

---

## 2. ディレクトリ構成
```
Presence Note/
├── AGENTS.md               # 行動規範（最優先）
├── docs/
│   ├── 要件定義書.md
│   └── 設計書.md
├── app/
│   ├── config.py           # 設定値
│   ├── receiver.py         # ntfy 受信
│   ├── image_processor.py  # 画像整形
│   ├── printer.py          # CUPS 印刷
│   ├── logger.py           # 節目の独り言
│   ├── storage.py          # v1 では空実装
│   ├── main.py             # 1 サイクル実行
│   └── ntfy_print_daemon.py# 常駐ループ
├── requirements.txt
└── README.md (本ファイル)
```

---

## 3. セットアップ
1. Python 3.11 以上推奨
2. 仮想環境を任意に作成
3. 依存インストール
   ```bash
   pip install -r requirements.txt
   ```
4. CUPS に Canon SELPHY CP1500 など目的のプリンタを登録し、`lpstat -p` でキュー名を確認

---

## 4. 環境変数
`app/config.py` は以下の環境変数を参照します。`.env` ファイル（UTF-8, `KEY=VALUE` 形式）をリポジトリ直下に置いておけば、`python-dotenv` によって起動時に自動読み込みされます。systemd などで別ファイルを参照する場合は同じ変数名で設定してください。

| 変数名 | 例 | 必須 | 用途 |
| --- | --- | --- | --- |
| `NTFY_TOPIC_URL` | `https://ntfy.sh/karin` | ✔ | 受信トピック。末尾 `/json` は自動付与されます |
| `PRINTER_NAME` | `Canon-SELPHY` | ✔ | `lp -d` に渡す CUPS キュー名 |
| `NTFY_TOKEN` | `secret-token` | 任意 | ntfy が Bearer 認証を要求する場合のみ |

`.env` の例:
```
NTFY_TOPIC_URL=https://ntfy.sh/karin
PRINTER_NAME=Canon_SELPHY_CP1500
NTFY_TOKEN=
```

---

## 5. 1 サイクル実行（手動）
```bash
python app/main.py
```
動作: 設定値を読み込み → 受信待機 → 1 枚だけ印刷 → 終了。失敗時は標準出力に節目メッセージを残して静かに戻ります。

---

## 6. 常駐実行
`app/ntfy_print_daemon.py` は CLI 引数と環境変数を統合し、`run_cycle` を無限ループで呼び出します。

```bash
python app/ntfy_print_daemon.py \
  --topic https://ntfy.sh/karin \
  --printer Canon-SELPHY \
  --token secret-token \
  --idle-wait 1.0
```
- `--topic`/`--printer`/`--token` を省略すると環境変数で補われます
- `--idle-wait` は 1 サイクル完了後に再度受信待機へ戻る前のディレイ（秒）
- systemd 化は `Demon.md` の具体例を参照してください

---

## 7. history ディレクトリ
- `app/history/` に受信画像を日付（`YYYY-MM-DD`）ごとに保存します
- ファイル名は `HHMMSS_uuuuuu.ext`（拡張子は自動判別）
- `app/history/README.md` にも説明あり。Git には `.gitignore` でコミットされません

---

## 8. systemd 常駐
- `systemd/ntfy-print.service` を `/etc/systemd/system/` へ配置し、`systemd/ntfy-print.env` を `/etc/default/ntfy-print` としてコピーします
- 仮想環境や WorkingDirectory のパスは環境に合わせて編集します
- 有効化手順:
  ```bash
  sudo cp systemd/ntfy-print.service /etc/systemd/system/
  sudo cp systemd/ntfy-print.env /etc/default/ntfy-print
  sudo systemctl daemon-reload
  sudo systemctl enable --now ntfy-print.service
  systemctl status ntfy-print.service
  ```
- Wifi や本体電源が復帰した際も `ntfy_print_daemon` が継続して ntfy を監視します

---

## 9. 失敗時の扱い
- ntfy 受信・画像処理・印刷のいずれかが例外を投げた場合、そのサイクルは終了し「何も起きなかった」ことになります
- 再試行やエラー通知は実装しません（AGENTS.md 4章・5章の制約）
- 常駐デーモンでは例外をログに記録後、`idle_wait` だけ待機して次サイクルに進みます

---

## 10. 制約の再確認
- 永続化禁止: `storage.py` は空実装、履歴フォルダも作成しません
- 意味解釈禁止: `image_processor` は文字列を等幅で折り返すだけで、内容分析はしません
- 条件分岐による振る舞い変更禁止: 直列処理のみで役割が変わる分岐は入れていません

この README は運用の入口であり、疑義があれば必ず `AGENTS.md` と要件ドキュメントへ立ち返ってください。
