# 🪙 Trustoken Daily

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

多帳號 Trustoken 每日簽到與每日任務領取，單檔 Python。

## 帳號格式

```bash
export TRUSTOKEN_TOKENS='主號|access_token|12345'
python3 trustoken_daily.py
```

格式為 `備註|access_token|uid`；省略 uid 時會讀取 `/api/user/self`。

## 驗收

先讀取簽到狀態，提交簽到後再次回讀；每日任務只領取 `claimable`，領取後再次回讀任務狀態。HTTP 200 不算成功。

## 部署

青龍：`pip3 install -r requirements.txt && task trustoken_daily.py`

GitHub Actions：加入 `TRUSTOKEN_TOKENS` 或 `TRUSTOKEN_TOKEN` + `TRUSTOKEN_UID` Secrets。

## 安全

不要把 access token、UID、Cookie 或含憑據的日誌提交到倉庫、Issue 或公開截圖。

完整使用規則見 [NOTICE.md](../NOTICE.md)。

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="微信讚賞碼" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="支付寶收款碼" />
</p>
