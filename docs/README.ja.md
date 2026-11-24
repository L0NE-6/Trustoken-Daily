# 🪙 Trustoken Daily

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

単一 Python ファイルで動かす、Trustoken の複数アカウント毎日チェックインとデイリータスク受取。

## アカウント形式

```bash
export TRUSTOKEN_TOKENS='メイン|access_token|12345'
python3 trustoken_daily.py
```

形式は `ラベル|access_token|uid` です。uid を省略すると `/api/user/self` から取得します。

## 成功判定

チェックイン状態を読み、送信後に再読込します。デイリータスクは `claimable` のみを受け取り、受取後にタスク状態を再確認します。HTTP 200 だけでは成功にしません。

## デプロイ

Qinglong: `pip3 install -r requirements.txt && task trustoken_daily.py`

GitHub Actions: `TRUSTOKEN_TOKENS` または `TRUSTOKEN_TOKEN` + `TRUSTOKEN_UID` を Secrets に登録します。

## セキュリティ

access token、UID、Cookie、認証情報を含むログを Git、Issue、公開スクリーンショットへ投稿しないでください。

利用範囲は [NOTICE.md](../NOTICE.md) を参照してください。

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="WeChat 投げ銭 QR" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="Alipay 投げ銭 QR" />
</p>
