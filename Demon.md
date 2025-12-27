# ntfy_print_daemon 常駐化ガイド

 qiita https://qiita.com/nnhkrnk/items/5082485e680606e74982

`app/ntfy_print_daemon.py` を Raspberry Pi 上で常に稼働させるための systemd サービス構築手順。

## 0. 今回構築した具体例
- 仮想環境を有効化して `python app/ntfy_print_daemon.py --topic https://ntfy.sh/YOUR_TOPIC/json --connection usb` を実行し、正常に動く状態を確認済み。
- `readlink -f .venv/bin/python` の結果 `/home/juggler/Karin/.venv/bin/python` を `ExecStart` に使用。
- `/etc/systemd/system/ntfy-print.service` を以下内容で作成し、`sudo systemctl daemon-reload && sudo systemctl enable --now ntfy-print.service` を実行。
````
[Unit]
Description=ntfy print daemon
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/juggler/Karin
ExecStart=/home/juggler/Karin/.venv/bin/python /home/juggler/Karin/app/ntfy_print_daemon.py --topic https://ntfy.sh/YOUR_TOPIC/json --connection usb
Restart=always
RestartSec=5
User=juggler

[Install]
WantedBy=multi-user.target
````
- `systemctl status ntfy-print.service` で稼働確認、`journalctl -u ntfy-print.service -f` でリアルタイムログ監視。

## 1. 事前チェック
- Raspberry Pi に本リポジトリを配置済みで、`python3 /home/juggler/Karin/app/ntfy_print_daemon.py --topic ...` が手動実行で成功すること。
- 仮想環境を使う場合は `ExecStart` に該当 venv の Python パスを設定する。
- 実行ユーザー（例: `pi`）がプリンタやネットワークにアクセスできる。

## 2. 環境変数ファイルの作成 (任意)
認証トークンやトピック URL を外出ししたい場合は `/etc/default/ntfy-print` を作り、以下のように設定する。

```
TOKEN=xxxxx
TOPIC=https://ntfy.sh/YOUR_TOPIC/json
```

## 3. systemd サービスファイル `/etc/systemd/system/ntfy-print.service`
以下をベースに、`User` や `ExecStart` などを環境に合わせて調整する。

```
[Unit]
Description=ntfy print daemon
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/juggler/Karin
EnvironmentFile=/etc/default/ntfy-print
ExecStart=/usr/bin/python3 /home/juggler/Karin/app/ntfy_print_daemon.py \
    --topic ${TOPIC} --token ${TOKEN} --connection usb
Restart=always
RestartSec=5
User=pi

[Install]
WantedBy=multi-user.target
```

ポイント:
- `EnvironmentFile` を使わない場合は `ExecStart` に直接オプションを書く。
- ネットワークプリンタなら `--connection network --ip-address 192.168.XX.XX` を追加。
- 常に復帰させたいので `Restart=always` と `RestartSec` を指定。

## 4. デーモン登録と起動
```
sudo systemctl daemon-reload
sudo systemctl enable --now ntfy-print.service
```

## 5. 運用コマンド
- 状態確認: `systemctl status ntfy-print.service`
- ログ監視: `journalctl -u ntfy-print.service -f`
- 設定変更時: `sudo systemctl restart ntfy-print.service`

## 6. トラブルシュートのヒント
- トークンや URL が誤っていないか `journalctl` のログで確認。
- `WorkingDirectory` や `ExecStart` のパスが実際の配置と一致しているか。
- プリンタ接続に応じて `Senior.MUNBYNPrinter` が必要とする USB / ネットワーク権限を満たしているか。

## 7. 実行記録の例
以下は 2025-12-18 (JST) に実際に行った一連の操作ログ。

```
sudo systemctl daemon-reload
sudo systemctl enable --now ntfy-print.service
# → /etc/systemd/system/multi-user.target.wants/ntfy-print.service へシンボリックリンクが作成されたログを確認

systemctl status ntfy-print.service
# → Main PID: 11009 で `/home/juggler/Karin/.venv/bin/python /home/juggler/Karin/app/ntfy_print_daemon.py ...` が active (running)

journalctl -u ntfy-print.service -f
# → 「Started ntfy-print.service - ntfy print daemon.」のログが継続的に表示され、リアルタイム監視できることを確認
```

上記のように `systemctl daemon-reload`→`enable --now`→`status`→`journalctl -f` の順に確認すれば、サービス登録から稼働状況まで一気通貫で把握できる。
