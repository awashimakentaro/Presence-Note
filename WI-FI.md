sudo nmcli dev wifi connect "1C3E8480534F" password "2211581895258"


sudo nmcli connection up 1C3E8480534F

ls /etc/NetworkManager/system-connections  これはジャグラーのwifi設定ファイルの情報
preconfigured.nmconnection

```
[connection]
id=preconfigured
uuid=71cb4284-2644-442b-a6b1-9b12e64fbbb9
type=wifi
[wifi]
mode=infrastructure
ssid=elecom-30fb2f
hidden=false
[ipv4]
method=auto
[ipv6]
addr-gen-mode=default
method=auto
[proxy]
[wifi-security]
key-mgmt=wpa-psk
psk=17fe0caf8f65a210f1c0b1872413a825ebf6fd6022231d55dadcf45067b4b4fd
```