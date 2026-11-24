<div align="center">

<sub><strong>L0NE-6 · DAILY SIGNAL</strong></sub>

# 🪙 Trustoken Daily

**Trustoken 每日签到 · 每日任务领取 · 多账号单文件 Python**

> 当前版本：**v1.0.0**（2026-11-24）

[简体中文](README.md) · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

🔐 Token / UID 隔离 · ✅ 服务端签到回读 · 🎯 每日任务 claim · 🧾 JSONL · 👥 多账号 · 📢 多渠道推送 · 🐧 青龙 · ☁️ Actions

<img src="https://img.shields.io/badge/version-v1.0.0-2ea44f?style=for-the-badge" />
<img src="https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white" />
<img src="https://img.shields.io/badge/Deploy-Actions%20%7C%20Qinglong-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" />

[✨ 速览](#-30-秒速览) · [🔧 环境变量](#-环境变量) · [☁️ Actions](#-github-actions) · [✅ 回读判据](#-严格回读) · [🧪 测试](#-离线测试) · [🚫 使用边界](#-使用边界) · [✦ 星轨](#-星轨-star-trail)

</div>

---

## ✨ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **做什么** | 执行 Trustoken 每日签到，并领取服务端已判定为 `claimable` 的每日任务。 |
| **输入** | `TRUSTOKEN_TOKENS`：`备注|access_token|uid`，也支持省略 uid 后自动从 `/api/user/self` 解析。 |
| **流程** | 签到状态 → 签到 → 再查签到状态 → 每日任务状态 → claim → 再查任务状态。 |
| **成功判据** | 签到必须回读 `checked_in_today=true`；任务领取必须回读为已完成/已领取。 |
| **输出** | 中文汇总 + 可选推送 + 每账号一行 JSONL。 |
| **依赖** | Python 3.8+，仅 `requests`。 |

---

## 🔐 账号格式

```text
主号|access_token_xxx|12345
备号|access_token_yyy|67890
```

也支持：

```text
主号|access_token_xxx
access_token_zzz
```

规则：

1. 每行一个账号，也支持用 `&` 分隔。
2. 三段格式是 `备注|access_token|uid`。
3. 省略 uid 时，脚本会调用 `/api/user/self` 解析账号 id。
4. `TRUSTOKEN_UID` 可用于单账号兼容模式。
5. 不要把真实 Token、UID、Cookie 写进脚本、README、Issue 或公开日志。

---

## 🔧 环境变量

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `TRUSTOKEN_TOKENS` | ⬜ | 多账号，换行或 `&` 分隔。 |
| `TRUSTOKEN_TOKEN` | ⬜ | 单账号兼容变量。 |
| `TRUSTOKEN_UID` | ⬜ | 单账号兼容 UID。 |
| `TRUSTOKEN_JSONL` | ⬜ | JSONL 路径，默认 `trustoken_results.jsonl`。 |
| `TRUSTOKEN_NOTIFY` | ⬜ | `always`（默认）/ `fail` / `0`。 |
| `PUSHPLUS_TOKEN` | ⬜ | PushPlus Token。 |
| `BARK_URL` | ⬜ | Bark 完整地址。 |
| `SERVERCHAN_SENDKEY` | ⬜ | Server酱 SendKey。 |
| `WXPUSHER_APP_TOKEN` | ⬜ | WxPusher App Token。 |
| `WXPUSHER_UID` | ⬜ | WxPusher UID，多个用逗号或分号分隔。 |
| `WECOM_WEBHOOK` | ⬜ | 企业微信群机器人 Webhook。 |
| `DINGTALK_WEBHOOK` | ⬜ | 钉钉机器人 Webhook。 |
| `DINGTALK_SECRET` | ⬜ | 钉钉加签密钥。 |

至少配置 `TRUSTOKEN_TOKENS` 或 `TRUSTOKEN_TOKEN`。

---

## 🐧 青龙面板

```bash
pip3 install -r requirements.txt
python3 trustoken_daily.py
```

青龙定时任务建议使用运行器：

```bash
task trustoken_daily.py
```

建议北京时间：`07:27`。

---

## ☁️ GitHub Actions

仓库内置：

- `.github/workflows/trustoken.yml`：每日北京时间约 07:27 执行。
- `.github/workflows/test.yml`：push / PR 自动运行离线测试。

在 `Settings → Secrets and variables → Actions` 添加 `TRUSTOKEN_TOKENS`，或使用 `TRUSTOKEN_TOKEN` + `TRUSTOKEN_UID`。

---

## ✅ 严格回读

```text
GET  /api/user/checkin/status
POST /api/user/checkin
GET  /api/user/checkin/status
GET  /api/user/daily_tasks/status
POST /api/user/daily_tasks/claim
GET  /api/user/daily_tasks/status
```

结果：

| 结果 | 含义 |
| :--- | :--- |
| `done` | 签到前服务端已确认今日完成，任务无需领取。 |
| `claimed` | 签到或每日任务在服务端回读中确认完成。 |
| `failed` | 网络、协议、签到或任务回读未通过。 |

不会把 HTTP 200、`success:true` 或 claim 请求本身当成完成。

---

## 🧾 JSONL

每个账号追加一行，字段包括：

```json
{"provider":"trustoken","label":"主号","outcome":"claimed","ok":true,"credit":15,"message":"签到与每日任务已完成"}
```

JSONL 不写入 Token、UID 或请求头。

---

## 🧪 离线测试

```bash
python -m unittest discover -s tests -v
python -m compileall -q trustoken_daily.py tests
```

覆盖签到短路、完整签到、任务 claim 回读、失败判定、UID 解析和 JSONL 脱敏。

---

## 🚫 使用边界

> **官方版本永久免费。** 未经作者书面许可，禁止付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。完整规则见 [NOTICE.md](NOTICE.md)。

---

## ☕ 支持与投喂

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>
<p align="center"><sub>💚 微信支付（左） &nbsp;|&nbsp; 💙 支付宝（右）</sub></p>

收款码仅用于向作者自愿赞赏。

---

## ✦ 星轨 Star Trail

<a href="https://star-history.com/#L0NE-6/Trustoken-Daily&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/Trustoken-Daily&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/Trustoken-Daily&type=Date" />
    <img alt="Trustoken Daily Star Trail" src="https://api.star-history.com/svg?repos=L0NE-6/Trustoken-Daily&type=Date" />
  </picture>
</a>

<div align="center"><sub>L0NE-6 · DAILY SIGNAL · 点个 Star，让下一轮自动化有迹可循 ✨</sub></div>
