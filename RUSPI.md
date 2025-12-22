# RUSPI.md

【責務】
Raspberry Pi で Presence Note をセットアップ・実行する手順を記す。

【使用箇所】
- Raspberry Pi 上での初期構築
- 仮想環境の再構築

【やらないこと】
- 依存ライブラリの詳細説明
- systemd サービス化の手順（`Demon.md` を参照）

【他ファイルとの関係】
- `requirements.txt` に列挙された依存を参照する。
- systemd 周りは `Demon.md` に委任する。

---

## 1. 事前準備
- Raspberry Pi OS (Bookworm 以降) を想定
- `python3` がインストール済みであること
- 本リポジトリを `~/Karin` など任意のディレクトリに配置済みであること
- CUPS クライアント（またはサーバー）を apt でインストール済みであること
  ```bash
  sudo apt update
  sudo apt install cups-client   # クライアントのみ
  # またはプリンタ共有ごと扱う場合
  sudo apt install cups
  ```
- `lpstat` が使えない場合やプリンタ登録ができない場合は上記コマンドを実施
- `lpadmin` コマンドを使用する場合は `sudo usermod -aG lpadmin $USER` で権限を追加
- SELPHY CP1500 を USB で利用する場合は PPD (プリンタ記述ファイル) を用意する。例: [`Canon-SELPHY-CP1500-AirPrint.ppd`](https://github.com/…/APCANONS.PPD) など。
- AirPrint/IPP で利用する場合はプリンタ側で Wi-Fi を有効にし、`driverless` コマンドで URI を取得して登録する。

### 1.1 Wi-Fi (AirPrint/IPP) 接続の流れ
1. SELPHY 本体の Wi-Fi をオンにし、Raspberry Pi と同じネットワークへ接続する。
2. ラズパイで以下を順に実行し、`ipps://Canon-SELPHY-CP1500.local:631/ipp/print` 形式の URI を確認。
   ```bash
   driverless
   ```
3. 既存のキューがあれば削除。
   ```bash
   sudo lpadmin -x Canon_SELPHY_CP1500
   ```
4. 以下のコマンドで登録し、デフォルト設定する。
   ```bash
   sudo lpadmin -p Canon_SELPHY_CP1500 \
     -E \
     -v "ipps://Canon-SELPHY-CP1500.local:631/ipp/print" \
     -m everywhere
   lpoptions -d Canon_SELPHY_CP1500
   ```
5. `lpoptions -p Canon_SELPHY_CP1500 -l | grep PageSize` で 54x86mm.Fullbleed が表示されることを確認。
6. `lp -d Canon_SELPHY_CP1500 /usr/share/cups/data/testprint` でテスト印刷。

---

## 2. 仮想環境の作成と有効化
```bash
cd ~/Karin  # プロジェクトルート
python3 -m venv .venv
source .venv/bin/activate
```

- `.venv/bin/activate` が存在しない場合は、先に `python3 -m venv .venv` を実行してから再度 `source` する

---

## 3. 依存インストール
```bash
pip install -r requirements.txt
```

- PEP 668 対応環境ではシステム Python への `pip install` が拒否されるため、必ず仮想環境上で行う
- インストールされる主なライブラリ: `Pillow`, `requests`, `python-dotenv`

---

## 4. 環境変数の設定
- プロジェクトルートに `.env` を作成し、以下のように `KEY=VALUE` 形式で設定値を書く
```
NTFY_TOPIC_URL=https://ntfy.sh/karin
PRINTER_NAME=Canon_SELPHY_CP1500
NTFY_TOKEN=
```
- `.env` は `python-dotenv` により自動読み込みされる

---

## 5. 動作確認
```bash
python -m app.main
```
- `.env` の値が正しければ 1 サイクル分の受信→印刷が実行される
- 出力されるログは節目のみ

---

## 6. よくあるエラーと対処
- `ModuleNotFoundError: No module named 'PIL'`
  - 仮想環境を有効化しているか確認し、`pip install -r requirements.txt` を再実行する
- `source .venv/bin/activate: No such file or directory`
  - 仮想環境が未作成。`python3 -m venv .venv` を実行後に再度 `source` する
- `pip install ... error: externally-managed-environment`
  - 仮想環境外で `pip` を実行している。`.venv` を作成してから再実行する
    - `lpoptions: Unable to get PPD file ...`
      - driverless 登録前の状態。`driverless` で表示された `ipps://...` を使い `lpadmin -p ... -m everywhere` で登録する
    - `lpinfo: Forbidden`
      - 一時的に `sudo lpinfo ...` を使うか、`sudo usermod -aG lpadmin $USER` で権限を付与
    - `driverless` に何も出ない
      - プリンタ側の AirPrint/Wi-Fi が無効。`ipp-usb` を無効化し、SEL PHY を同じネットワークに接続してから再実行
    - `lpoptions -p ... -l` で PageSize を確認できない
      - まだプリンタ登録が完了していない。driverless で登録後に再度確認
    - `lp -d ...` でジョブは通るが印刷されない
      - プリンタ本体の用紙/インク/カセットを確認、必要なら電源再投入。USB ではなく AirPrint/IPP 接続に切り替える

---

## 7. 参考
- systemd 常駐化の手順は `Demon.md`
- NTFY/CUPS 設定の詳細は `README.md` を参照
