# 🪙 Trustoken Daily

[简体中文](../README.md) · [English](README.en.md) · [繁體中文](README.zh-Hant.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Português (BR)](README.pt-BR.md)

단일 Python 파일로 실행하는 Trustoken 다중 계정 일일 체크인 및 데일리 작업 수령.

## 계정 형식

```bash
export TRUSTOKEN_TOKENS='메인|access_token|12345'
python3 trustoken_daily.py
```

형식은 `라벨|access_token|uid`입니다. uid를 생략하면 `/api/user/self`에서 읽습니다.

## 성공 판정

체크인 상태를 읽고 제출 후 다시 읽습니다. 데일리 작업은 `claimable`만 수령하며 수령 후 작업 상태를 다시 확인합니다. HTTP 200만으로 성공 처리하지 않습니다.

## 배포

Qinglong: `pip3 install -r requirements.txt && task trustoken_daily.py`

GitHub Actions: `TRUSTOKEN_TOKENS` 또는 `TRUSTOKEN_TOKEN` + `TRUSTOKEN_UID` Secrets를 추가합니다.

## 보안

access token, UID, Cookie 또는 자격 증명이 포함된 로그를 Git, Issue, 공개 스크린샷에 올리지 마세요.

사용 범위는 [NOTICE.md](../NOTICE.md)를 참고하세요.

<p align="center">
  <img src="../assets/donate-wechat.png" width="240" alt="WeChat 후원 QR" />
  &nbsp;&nbsp;
  <img src="../assets/donate-alipay.jpg" width="240" alt="Alipay 후원 QR" />
</p>
