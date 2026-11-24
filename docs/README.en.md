# 🪙 Trustoken Daily

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

Multi-account Trustoken daily check-in and daily-task claiming in one Python file.

## Account format

```bash
export TRUSTOKEN_TOKENS='main|access_token|12345'
python3 trustoken_daily.py
```

The three fields are `label|access_token|uid`. If UID is omitted, the script reads `/api/user/self`.

## Success contract

The script reads `/api/user/checkin/status`, posts `/api/user/checkin`, then reads the status again. It then reads `/api/user/daily_tasks/status`, claims `claimable` tasks, and re-reads the task state. HTTP 200 alone is never treated as success.

## Deployment

Qinglong: `pip3 install -r requirements.txt && task trustoken_daily.py`

GitHub Actions: add `TRUSTOKEN_TOKENS` or `TRUSTOKEN_TOKEN` + `TRUSTOKEN_UID` in repository Secrets.

## Tests

```bash
python -m unittest discover -s tests -v
python -m compileall -q trustoken_daily.py tests
```

## Security

Never commit access tokens, UIDs, cookies, or logs containing credentials. The JSONL file contains only labels, outcomes, messages, and non-secret status details.

## Usage policy

The official repository and releases are free. Paid repackaging, traffic diversion, identity impersonation, and credential abuse are not permitted. See [NOTICE.md](../NOTICE.md).

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="WeChat tip QR" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="Alipay tip QR" />
</p>
