<div align="center">

<sub><strong>L0NE-6 · TRUSTOKEN SIGNAL</strong></sub>

# Trustoken Daily

**Trustoken 每日签到 · 每日任务领取 · 多账号单文件 Python**

> 当前版本：**v1.0.0**（2026-11-24） · 签到和 claimable 任务分别提交、分别回读

[简体中文](README.md) · [English](docs/README.en.md) · [繁體中文](docs/README.zh-Hant.md) · [日本語](docs/README.ja.md) · [한국어](docs/README.ko.md) · [Português (BR)](docs/README.pt-BR.md)

<img src="https://img.shields.io/badge/Features-Daily%20Tasks-6F42C1?style=for-the-badge" alt="Features" />
<a href="https://github.com/L0NE-6/Trustoken-Daily/releases"><img src="https://img.shields.io/github/v/release/L0NE-6/Trustoken-Daily?style=for-the-badge&label=Release&color=2ea44f&logo=github" alt="Release" /></a>
<a href="https://github.com/L0NE-6/Trustoken-Daily/stargazers"><img src="https://img.shields.io/github/stars/L0NE-6/Trustoken-Daily?style=for-the-badge&label=Stars&color=FFC75F&logo=github" alt="Stars" /></a>
<img src="https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20Qinglong-4EAA25?style=for-the-badge&logo=linux&logoColor=white" alt="Platform" />
<img src="https://img.shields.io/badge/License-MIT-F472B6?style=for-the-badge" alt="License" />

🔐 Token / UID 隔离 · ✅ 签到回读 · 🎯 每日任务 claim · 🧾 JSONL · 📢 推送 · 🐧 青龙 · ☁️ Actions

[⚡ 30 秒速览](#quick-look) · [🔁 协议与回读](#protocol) · [🔐 凭据](#credentials) · [🐧 青龙](#qinglong) · [☁️ Actions](#actions) · [⌨️ CLI](#cli-json) · [✅ 成功判据](#success) · [✦ 星轨](#star-trail)

</div>

---

<a id="usage-policy"></a>
## 🚫 使用边界与禁止倒卖

> [!IMPORTANT]
> **官方版本永久免费。** 未经作者书面许可，禁止倒卖、付费包装、搬运引流、冒充作者，或使用作者身份与二维码制造官方授权假象。

本仓库、脚本、部署说明和 Release 下载保持免费公开。禁止将本项目或其轻度改名版本包装为付费资源、内部版、独家版、会员权益、收费课程、代部署服务或包更新服务；禁止搬运到其他账号、群组、频道、网盘、电商平台或付费社群进行涨粉、截流、倒卖和引流；禁止删除作者与版权信息后冒充原创。

完整规则见 [NOTICE.md](NOTICE.md)。第三方以“下载费 / 激活费 / 内部版 / 代部署 / 会员门槛”等名义收费，均与作者无关，请停止付款并保留证据。

---

<a id="quick-look"></a>
## ⚡ 30 秒速览

| 维度 | 说明 |
| :--- | :--- |
| **做什么** | 执行 Trustoken 每日签到，并领取服务端判定为 `claimable` 的每日任务。 |
| **输入** | `TRUSTOKEN_TOKENS`，格式 `备注\|access_token\|uid`。 |
| **流程** | 签到状态 → 签到 → 再查状态 → 每日任务状态 → claim → 再查任务。 |
| **成功判据** | 签到回读 `checked_in_today=true`；任务回读为完成/已领取。 |
| **输出** | 中文汇总 + 可选推送 + 每账号一行 JSONL。 |
| **依赖** | Python 3.8+，仅 `requests`。 |

---

## 🧭 这是什么 / 覆盖范围

Trustoken 脚本先解析 UID，再执行签到和每日任务。签到与任务领取是两条独立链路，任一链路失败都会进入最终失败原因，不会用签到成功掩盖任务回读失败。

### 覆盖范围

- `备注|access_token|uid`、省略 UID 和裸 access token。
- UID 缺失时读取 `/api/user/self` 的 `id` / `user_id`。
- `checked_in_today` 严格布尔回读。
- 仅领取 `status=claimable` 的任务，按 `task_type` 提交。
- 任务状态、进度、目标和奖励回读。
- JSONL、中文摘要和可选多渠道通知。

---

<a id="protocol"></a>
## 🔁 协议与回读流程

### 请求链

```http
GET  /api/user/self
GET  /api/user/checkin/status
POST /api/user/checkin
GET  /api/user/checkin/status
GET  /api/user/daily_tasks/status
POST /api/user/daily_tasks/claim
GET  /api/user/daily_tasks/status
Authorization: Bearer <access_token>
New-Api-User: <uid>
```

### 关键字段

| 字段 | 说明 |
| :--- | :--- |
| `checked_in_today` | 签到状态布尔字段。 |
| `data.tasks[]` | 每日任务列表。 |
| `status=claimable` | 可领取任务。 |
| `task_type` | 任务领取请求字段。 |
| `progress` / `target` | 任务进度与目标。 |
| `total_reward` / `reward` / `reward_amount` | 奖励候选字段。 |

签到 POST 后必须重新读取 `checked_in_today=true`。任务 claim 后必须重新读取该任务为 `claimed`、`completed`、`complete`、`done` 或 `progress >= target`。

---

<a id="credentials"></a>
## 🔐 凭据与环境变量

### 账号格式

```text
主号|access_token|12345
备号|access_token|67890
主号|access_token
access_token
```

| 变量 | 必填 | 说明 |
| :--- | :---: | :--- |
| `TRUSTOKEN_TOKENS` | 二选一 | 多账号，换行或 `&` 分隔。 |
| `TRUSTOKEN_TOKEN` | 二选一 | 单账号 access token。 |
| `TRUSTOKEN_UID` | 否 | 单账号 UID。 |
| `TRUSTOKEN_JSONL` | 否 | JSONL 路径，默认 `trustoken_results.jsonl`。 |
| `TRUSTOKEN_NOTIFY` | 否 | `always` / `fail` / `0`。 |
| `PUSHPLUS_TOKEN` / `BARK_URL` | 否 | 推送。 |
| `SERVERCHAN_SENDKEY` | 否 | Server酱。 |
| `WXPUSHER_APP_TOKEN` / `WXPUSHER_UID` | 否 | WxPusher。 |
| `WECOM_WEBHOOK` | 否 | 企业微信机器人。 |
| `DINGTALK_WEBHOOK` / `DINGTALK_SECRET` | 否 | 钉钉机器人。 |

---

## 💻 本地快速开始

### PowerShell

```powershell
python -m pip install -r requirements.txt
$env:TRUSTOKEN_TOKENS = "主号|access_token|12345"
python trustoken_daily.py
```

### Bash

```bash
python -m pip install -r requirements.txt
export TRUSTOKEN_TOKENS='主号|access_token|12345'
python trustoken_daily.py
```

常用参数：`--only 2`、`--no-notify`、`--jsonl trustoken_results.jsonl`、`--version`。

---

<a id="qinglong"></a>
## 🐧 青龙

1. 在青龙依赖管理中安装 `requests`，或执行 `pip3 install -r requirements.txt`。
2. 上传 `trustoken_daily.py` 到脚本目录。
3. 在环境变量中配置 `TRUSTOKEN_TOKENS`，或 `TRUSTOKEN_TOKEN` + `TRUSTOKEN_UID`。
4. 新建定时任务，命令使用 `task trustoken_daily.py`，不要直接写裸 `python`。
5. 建议北京时间：`27 7 * * *`。青龙按面板本地时间执行。

```bash
pip3 install -r requirements.txt
task trustoken_daily.py
```

---

<a id="actions"></a>
## ☁️ GitHub Actions、Secrets 与定时

工作流：`.github/workflows/trustoken.yml`；测试工作流：`.github/workflows/test.yml`。

| 事件 | 行为 |
| :--- | :--- |
| `schedule` | 每天执行离线测试和签到/任务领取。 |
| `workflow_dispatch` | 手动执行。 |
| 未配置账号 | 输出 warning 并跳过在线执行。 |

### Secrets

| Secret | 说明 |
| :--- | :--- |
| `TRUSTOKEN_TOKENS` | 多账号。 |
| `TRUSTOKEN_TOKEN` / `TRUSTOKEN_UID` | 单账号。 |
| `TRUSTOKEN_JSONL` / `TRUSTOKEN_NOTIFY` | 输出路径与推送策略。 |
| `PUSHPLUS_TOKEN` / `BARK_URL` / `SERVERCHAN_SENDKEY` | 推送。 |
| `WXPUSHER_APP_TOKEN` / `WXPUSHER_UID` | WxPusher。 |
| `WECOM_WEBHOOK` | 企业微信机器人。 |
| `DINGTALK_WEBHOOK` / `DINGTALK_SECRET` | 钉钉机器人。 |

内置定时为 UTC `27 23 * * *`，对应北京时间约 07:27。工作流不单独上传 artifact，JSONL 按 `TRUSTOKEN_JSONL` 写入。

---

<a id="cli-json"></a>
## ⌨️ CLI 与 JSON 输出

```powershell
python trustoken_daily.py
python trustoken_daily.py --only 2
python trustoken_daily.py --no-notify
python trustoken_daily.py --jsonl trustoken_results.jsonl
```

JSONL 每账号一行：

```json
{"ts":"2026-11-24T00:00:00+00:00","provider":"trustoken","label":"主号","outcome":"claimed","ok":true,"credit":15,"message":"签到与每日任务已完成","detail":{"checkin":{"outcome":"claimed"},"daily_tasks":[{"task_type":"daily","status":"claimed"}]}}
```

| 字段 | 说明 |
| :--- | :--- |
| `provider` / `label` | 服务名与脱敏备注。 |
| `outcome` / `ok` | 结果码与是否成功。 |
| `credit` | 签到与任务奖励合计。 |
| `message` | 脱敏后的中文说明。 |
| `detail` | 签到、任务前后状态和领取明细。 |

---

<a id="result-codes"></a>
## 🧾 结果码

| 结果码 | 成功 | 含义 |
| :--- | :---: | :--- |
| `done` | 是 | 签到与任务在运行前或回读中均已处于完成状态。 |
| `claimed` | 是 | 签到或至少一个每日任务完成领取并回读确认。 |
| `failed` | 否 | 网络、鉴权、协议、签到或任务回读失败。 |

底层错误类别包括 `NetworkError`、`ProtocolError`、`AuthError` 和 `ApiError`。进程退出码为 0 表示全部账号成功，否则为 1。

---

<a id="success"></a>
## ✅ 成功判据

| 场景 | 必须满足 |
| :--- | :--- |
| 签到 | 回读 `checked_in_today=true`。 |
| 每日任务 | 只提交 `status=claimable` 的任务，且回读状态为完成/已领取或进度达标。 |
| 部分失败 | 任一任务领取失败、缺 `task_type` 或回读未确认时整体 `failed`。 |
| 无任务 | 签到成功且任务列表无需领取时返回 `done` 或 `claimed`。 |

---

## 🧪 测试与静态检查

```bash
python -m unittest discover -s tests -v
python -m compileall -q trustoken_daily.py tests
python -m ruff check .
```

离线测试覆盖三段账号解析、UID 自动解析、已签到短路、完整签到与任务领取、POST 后状态未翻转、任务回读未确认和 JSONL 不含 Token。

---

## 🧱 设计原则

- **UID 显式注入**：解析后写入 `New-Api-User`。
- **签到与任务分开**：两条链路分别回读。
- **只领 claimable**：不扫描或提交未达标任务。
- **失败聚合**：任务异常逐项记录并影响最终结果。
- **输出脱敏**：Token、UID 和请求头不进入 JSONL。

---

## 🔒 隐私

仓库不包含 Token、UID、账号、手机号、邮箱、日志或真实响应。`trustoken_results.jsonl`、`trustoken_state.json`、`.env`、日志和缓存已由 `.gitignore` 排除。

---

## 📁 目录结构

```text
Trustoken-Daily/
├── .github/workflows/trustoken.yml
├── .github/workflows/test.yml
├── assets/
│   ├── donate-alipay.jpg
│   └── donate-wechat.png
├── docs/
│   ├── README.en.md
│   ├── README.zh-Hant.md
│   ├── README.ja.md
│   ├── README.ko.md
│   └── README.pt-BR.md
├── tests/test_trustoken_daily.py
├── CHANGELOG.md
├── LICENSE
├── NOTICE.md
├── THIRD_PARTY_NOTICES.md
├── trustoken_daily.py
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## 📦 版本与发布

- 当前清单版本：`v1.0.0`，日期 `2026-11-24`。
- 脚本版本与 `trustoken_daily.py` 内的 `VERSION` 保持一致。
- 更新记录见 [CHANGELOG.md](CHANGELOG.md)，下载入口见 [Releases](https://github.com/L0NE-6/Trustoken-Daily/releases)。
- Release 徽标由 GitHub 实时生成；如果页面尚未创建对应 Release，以 `CHANGELOG.md` 和仓库提交为准。

---

## ⚠️ 免责声明

本项目用于个人学习与个人自动化。Trustoken 的活动规则、接口、奖励、风控策略和账号资格由服务方决定。使用前请确认对应服务条款，并自行承担接口变化、账号限制和网络环境带来的风险。

---

## ☕ 支持与投喂

脚本完全免费，赞赏纯自愿，不影响任何功能，也不影响 Issue 响应。

<p align="center">
  <img src="assets/donate-wechat.png" width="260" alt="微信赞赏码" />
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="assets/donate-alipay.jpg" width="260" alt="支付宝收款码" />
</p>
<p align="center"><sub>💚 微信支付（左） &nbsp;|&nbsp; 💙 支付宝（右，支持信用卡 / 花呗）</sub></p>

> 收款码仅用于向作者自愿赞赏。任何第三方以代下载、代部署、内部资源或会员群为由收费，均与作者无关。

---

## 💬 反馈与贡献

- 提交 [Issue](https://github.com/L0NE-6/Trustoken-Daily/issues) 时附运行日志、脱敏后的错误字段和复现步骤。
- 发起 [Pull Request](https://github.com/L0NE-6/Trustoken-Daily/pulls) 时保持单文件运行、离线测试和凭据脱敏约束。
- 不要在任何 Issue、PR、截图或日志中粘贴真实 Token、Cookie、密码、UID、手机号或邮箱。

---

<a id="star-trail"></a>
## ✦ Star History / 星轨

<a href="https://star-history.com/#L0NE-6/Trustoken-Daily&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=L0NE-6/Trustoken-Daily&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=L0NE-6/Trustoken-Daily&type=Date" />
    <img alt="Trustoken-Daily Star History" src="https://api.star-history.com/svg?repos=L0NE-6/Trustoken-Daily&type=Date" />
  </picture>
</a>

<div align="center">
  <sub>L0NE-6 · DAILY SIGNAL &nbsp;|&nbsp; 点个 <b>Star</b>，让下一轮自动化有迹可循</sub>
</div>
