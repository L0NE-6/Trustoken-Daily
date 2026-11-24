# 🪙 Trustoken Daily

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · **Português (BR)**
> Versão: **v1.0.0** (2026-11-24)

Check-in diário e resgate de tarefas do Trustoken para várias contas em um único arquivo Python.

## Formato da conta

```bash
export TRUSTOKEN_TOKENS='principal|access_token|12345'
python3 trustoken_daily.py
```

O formato é `rótulo|access_token|uid`. Sem uid, o script consulta `/api/user/self`.

## Critério de sucesso

O script lê o estado, envia o check-in e lê novamente. Depois lê as tarefas, resgata apenas `claimable` e confirma o novo estado. HTTP 200 isolado não é sucesso.

## Implantação

Qinglong: `pip3 install -r requirements.txt && task trustoken_daily.py`

GitHub Actions: adicione `TRUSTOKEN_TOKENS` ou `TRUSTOKEN_TOKEN` + `TRUSTOKEN_UID` aos Secrets.

## Segurança

Não envie access tokens, UIDs, cookies ou logs com credenciais para Git, Issues ou capturas públicas.

Consulte [NOTICE.md](../NOTICE.md) para a política de uso.

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="QR de gorjeta WeChat" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="QR de gorjeta Alipay" />
</p>
