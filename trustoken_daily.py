#!/usr/bin/env python3
"""Trustoken Daily - multi-account check-in and daily task claims."""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import re
import sys
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

import requests

VERSION = "1.0.0"
BASE = "https://www.trustoken.cn"
DEFAULT_TIMEOUT = 20
SELF_PATH = "/api/user/self"
CHECKIN_STATUS_PATH = "/api/user/checkin/status"
CHECKIN_PATH = "/api/user/checkin"
DAILY_TASKS_PATH = "/api/user/daily_tasks/status"
DAILY_CLAIM_PATH = "/api/user/daily_tasks/claim"

_SECRET_RE = re.compile(
    r"(?i)(authorization|new-api-user|token|access_token|refresh_token)"
    r"(\s*[:=]\s*)([^\s;,]+)"
)


class TrustokenError(Exception):
    pass


class NetworkError(TrustokenError):
    pass


class ProtocolError(TrustokenError):
    pass


class ApiError(TrustokenError):
    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code


@dataclass(frozen=True)
class Account:
    label: str
    token: str
    uid: str = ""


@dataclass
class AccountResult:
    account: Account
    ok: bool
    outcome: str
    message: str
    credit: float = 0
    detail: Dict[str, Any] = field(default_factory=dict)


def _env(name: str) -> str:
    return (os.getenv(name) or "").strip()


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is None:
            continue
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (LookupError, ValueError):
            pass


def _sanitize(text: Any, limit: int = 300) -> str:
    value = str(text).replace("\r", " ").replace("\n", " ").strip()
    value = _SECRET_RE.sub(r"\1\2[redacted]", value)
    return value[:limit]


def _split_entries(raw: str) -> List[str]:
    if not raw:
        return []
    return [item.strip() for item in re.split(r"[\r\n&]+", raw) if item.strip()]


def _clean_secret(value: str) -> str:
    text = value.strip()
    if text.lower().startswith("bearer "):
        text = text[7:].strip()
    if not text or len(text) > 4096 or any(ord(char) < 32 or ord(char) == 127 for char in text):
        raise ValueError("invalid token")
    return text


def parse_accounts(raw: str, default_uid: str = "") -> List[Account]:
    accounts: List[Account] = []
    for index, entry in enumerate(_split_entries(raw), 1):
        if entry.startswith("#"):
            continue
        label = f"TRUSTOKEN-{index}"
        token = entry
        uid = default_uid
        if "|" in entry:
            parts = [part.strip() for part in entry.split("|")]
            if len(parts) >= 3:
                label, token, uid = parts[0], parts[1], parts[2]
            elif len(parts) == 2:
                label, token = parts[0], parts[1]
        try:
            token = _clean_secret(token)
        except ValueError as exc:
            raise ValueError(f"{label}: {exc}") from exc
        accounts.append(Account(label=label or f"TRUSTOKEN-{index}", token=token, uid=uid))
    return accounts


def load_accounts() -> List[Account]:
    raw = _env("TRUSTOKEN_TOKENS") or _env("TRUSTOKEN_TOKEN")
    return parse_accounts(raw, _env("TRUSTOKEN_UID")) if raw else []


def make_session(account: Account) -> requests.Session:
    session = requests.Session()
    headers = {
        "Authorization": f"Bearer {account.token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "AiPy/2.1.1",
    }
    if account.uid:
        headers["New-Api-User"] = account.uid
    session.headers.update(headers)
    return session


def _message(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ("message", "msg", "error"):
            if payload.get(key):
                return _sanitize(payload[key])
    return ""


def request_json(
    session: requests.Session,
    method: str,
    path: str,
    *,
    body: Optional[Dict[str, Any]] = None,
    soft: bool = False,
    timeout: int = DEFAULT_TIMEOUT,
) -> Dict[str, Any]:
    url = BASE + path
    try:
        response = session.request(method, url, json=body, timeout=timeout)
    except requests.RequestException as exc:
        raise NetworkError(_sanitize(f"网络请求失败：{exc}")) from exc
    try:
        payload = response.json()
    except ValueError as exc:
        raise ProtocolError(f"服务端返回非 JSON（HTTP {response.status_code}）") from exc
    if not isinstance(payload, dict):
        raise ProtocolError("服务端响应不是对象")
    if not 200 <= response.status_code < 300:
        raise ApiError(
            _sanitize(f"HTTP {response.status_code}：{_message(payload) or '请求失败'}"),
            status=response.status_code,
            code=str(payload.get("code") or ""),
        )
    if not soft and payload.get("success") is False:
        raise ApiError(
            _sanitize(_message(payload) or "接口返回 success:false"),
            status=response.status_code,
            code=str(payload.get("code") or ""),
        )
    return payload


def _data(payload: Dict[str, Any]) -> Any:
    return payload.get("data") if "data" in payload else payload


def resolve_uid(session: requests.Session, account: Account) -> Account:
    if account.uid:
        return account
    payload = request_json(session, "GET", SELF_PATH)
    data = _data(payload)
    if not isinstance(data, dict):
        raise ProtocolError("/api/user/self 缺少 data")
    uid = data.get("id") or data.get("user_id")
    if uid is None or str(uid).strip() == "":
        raise ProtocolError("/api/user/self 未返回账号 id")
    return Account(account.label, account.token, str(uid))


def checkin_status(session: requests.Session) -> Dict[str, Any]:
    payload = request_json(session, "GET", CHECKIN_STATUS_PATH)
    data = _data(payload)
    if not isinstance(data, dict) or not isinstance(data.get("checked_in_today"), bool):
        raise ProtocolError("签到状态缺少布尔字段 checked_in_today")
    return data


def do_checkin(session: requests.Session) -> Dict[str, Any]:
    return request_json(session, "POST", CHECKIN_PATH, soft=True)


def daily_task_status(session: requests.Session) -> List[Dict[str, Any]]:
    payload = request_json(session, "GET", DAILY_TASKS_PATH)
    data = _data(payload)
    tasks = data.get("tasks") if isinstance(data, dict) else None
    if not isinstance(tasks, list):
        raise ProtocolError("每日任务状态缺少 data.tasks")
    return [task for task in tasks if isinstance(task, dict)]


def claim_daily_task(session: requests.Session, task_type: str) -> Dict[str, Any]:
    return request_json(
        session,
        "POST",
        DAILY_CLAIM_PATH,
        body={"task_type": task_type},
        soft=True,
    )


def task_done(task: Dict[str, Any]) -> bool:
    status = str(task.get("status") or "").lower()
    if status in ("claimed", "completed", "complete", "done"):
        return True
    if status in ("claimable", "in_progress", "locked"):
        return False
    progress = task.get("progress")
    target = task.get("target")
    try:
        return progress is not None and target is not None and float(progress) >= float(target)
    except (TypeError, ValueError):
        return False


def _reward(payload: Dict[str, Any]) -> float:
    data = _data(payload)
    if not isinstance(data, dict):
        return 0
    for key in ("total_reward", "reward", "reward_amount"):
        try:
            value = float(data.get(key) or 0)
            if value > 0:
                return value
        except (TypeError, ValueError):
            continue
    return 0


def _task_view(tasks: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for task in tasks:
        rows.append(
            {
                "task_type": task.get("task_type"),
                "title": task.get("title"),
                "status": task.get("status"),
                "progress": task.get("progress"),
                "target": task.get("target"),
            }
        )
    return rows


def run_account(
    account: Account,
    *,
    session: Optional[requests.Session] = None,
) -> AccountResult:
    owns_session = session is None
    session = session or make_session(account)
    try:
        account = resolve_uid(session, account)
        if not account.uid:
            raise ProtocolError("无法解析 New-Api-User")
        session.headers["New-Api-User"] = account.uid

        credit = 0.0
        claimed = False
        errors: List[str] = []
        before = checkin_status(session)
        if before["checked_in_today"]:
            checkin_detail = {"outcome": "done", "status": before}
        else:
            post_error: Optional[str] = None
            post_payload: Dict[str, Any] = {}
            try:
                post_payload = do_checkin(session)
            except TrustokenError as exc:
                post_error = _sanitize(exc)
            after = checkin_status(session)
            if not after["checked_in_today"]:
                if post_error:
                    raise ApiError(f"签到提交失败，服务端仍显示未签到：{post_error}")
                raise ApiError("签到提交返回后，服务端仍显示未签到")
            reward = _reward(post_payload)
            credit += reward
            claimed = True
            checkin_detail = {
                "outcome": "claimed",
                "before": before,
                "after": after,
                "reward": reward,
                "post_error": post_error,
            }

        tasks_before = daily_task_status(session)
        claimed_tasks: List[Dict[str, Any]] = []
        for task in tasks_before:
            if str(task.get("status") or "").lower() != "claimable":
                continue
            task_type = str(task.get("task_type") or "").strip()
            if not task_type:
                errors.append("可领取任务缺少 task_type")
                continue
            try:
                response = claim_daily_task(session, task_type)
                reward = _reward(response)
                if response.get("success") is not True:
                    raise ApiError(_sanitize(_message(response) or "每日任务领取失败"))
                credit += reward
                claimed = True
                claimed_tasks.append(
                    {"task_type": task_type, "title": task.get("title"), "reward": reward}
                )
            except TrustokenError as exc:
                errors.append(f"{task_type}: {_sanitize(exc)}")

        tasks_after = daily_task_status(session) if claimed_tasks else tasks_before
        by_type = {
            str(task.get("task_type") or ""): task for task in tasks_after if isinstance(task, dict)
        }
        for item in claimed_tasks:
            task = by_type.get(str(item["task_type"]))
            if not task or not task_done(task):
                errors.append(f"{item['task_type']}: 领取后回读未确认完成")

        if errors:
            return AccountResult(
                account=account,
                ok=False,
                outcome="failed",
                message="；".join(errors),
                credit=credit,
                detail={
                    "checkin": checkin_detail,
                    "daily_tasks_before": _task_view(tasks_before),
                    "daily_tasks_after": _task_view(tasks_after),
                    "claimed_tasks": claimed_tasks,
                },
            )

        return AccountResult(
            account=account,
            ok=True,
            outcome="claimed" if claimed else "done",
            message=("签到与每日任务已完成" if claimed else "服务端确认今日签到与任务状态已完成"),
            credit=credit,
            detail={
                "checkin": checkin_detail,
                "daily_tasks": _task_view(tasks_after),
                "claimed_tasks": claimed_tasks,
            },
        )
    finally:
        if owns_session:
            session.close()


def append_jsonl(path: str, result: AccountResult) -> None:
    if not path:
        return
    record = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "provider": "trustoken",
        "label": result.account.label,
        "outcome": result.outcome,
        "ok": result.ok,
        "credit": result.credit,
        "message": _sanitize(result.message),
        "detail": result.detail,
    }
    parent = os.path.dirname(os.path.abspath(path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def format_summary(results: Sequence[AccountResult]) -> str:
    lines = [f"🪙 Trustoken Daily v{VERSION}", f"账号数: {len(results)}"]
    for result in results:
        icon = "✅" if result.ok else "❌"
        lines.append(
            f"{icon} {result.account.label} · {result.outcome} · "
            f"{result.message} · credit={result.credit:g}"
        )
    lines.append(f"结果: {sum(1 for item in results if item.ok)}/{len(results)} 成功")
    return "\n".join(lines)


def _notify_enabled(results: Sequence[AccountResult]) -> bool:
    mode = _env("TRUSTOKEN_NOTIFY").lower()
    if mode in ("0", "off", "false", "none"):
        return False
    if mode in ("fail", "failure", "failed"):
        return any(not result.ok for result in results)
    return True


def _post(url: str, **kwargs: Any) -> None:
    try:
        response = requests.post(url, timeout=DEFAULT_TIMEOUT, **kwargs)
        if response.status_code >= 400:
            print(f"⚠️ 推送失败 HTTP {response.status_code}", file=sys.stderr)
    except requests.RequestException as exc:
        print(f"⚠️ 推送异常：{_sanitize(exc)}", file=sys.stderr)


def notify(text: str, results: Sequence[AccountResult]) -> None:
    if not _notify_enabled(results):
        return
    title = "Trustoken Daily 签到报告"
    pushplus = _env("PUSHPLUS_TOKEN")
    if pushplus:
        _post(
            "https://www.pushplus.plus/send",
            json={"token": pushplus, "title": title, "content": text, "template": "markdown"},
        )
    bark = _env("BARK_URL")
    if bark:
        _post(bark.rstrip("/"), json={"title": title, "body": text})
    serverchan = _env("SERVERCHAN_SENDKEY")
    if serverchan:
        _post(f"https://sctapi.ftqq.com/{serverchan}.send", data={"title": title, "desp": text})
    wxpusher = _env("WXPUSHER_APP_TOKEN")
    wx_uids = [item.strip() for item in re.split(r"[,;]", _env("WXPUSHER_UID")) if item.strip()]
    if wxpusher and wx_uids:
        _post(
            "https://wxpusher.zjiecode.com/api/send/message",
            json={
                "appToken": wxpusher,
                "content": text,
                "summary": title,
                "contentType": 1,
                "uids": wx_uids,
            },
        )
    wecom = _env("WECOM_WEBHOOK")
    if wecom:
        _post(wecom, json={"msgtype": "markdown", "markdown": {"content": text}})
    dingtalk = _env("DINGTALK_WEBHOOK")
    if dingtalk:
        secret = _env("DINGTALK_SECRET")
        url = dingtalk
        if secret:
            timestamp = str(int(time.time() * 1000))
            string_to_sign = f"{timestamp}\n{secret}"
            sign = base64.b64encode(
                hmac.new(secret.encode(), string_to_sign.encode(), hashlib.sha256).digest()
            ).decode()
            separator = "&" if "?" in url else "?"
            url += f"{separator}timestamp={timestamp}&sign={urllib.parse.quote(sign)}"
        _post(url, json={"msgtype": "markdown", "markdown": {"title": title, "text": text}})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trustoken multi-account daily check-in")
    parser.add_argument("--only", type=int, default=0, help="only run the 1-based account index")
    parser.add_argument("--no-notify", action="store_true")
    parser.add_argument(
        "--jsonl",
        default=os.getenv("TRUSTOKEN_JSONL") or "trustoken_results.jsonl",
        help="append one JSON object per account",
    )
    parser.add_argument("--version", action="version", version=VERSION)
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    _configure_stdio()
    args = build_parser().parse_args(argv)
    try:
        accounts = load_accounts()
    except ValueError as exc:
        print(f"❌ 账号配置错误：{_sanitize(exc)}", file=sys.stderr)
        return 2
    if args.only:
        if args.only < 1 or args.only > len(accounts):
            print(f"❌ --only 超出范围：{args.only}", file=sys.stderr)
            return 2
        accounts = [accounts[args.only - 1]]
    if not accounts:
        print("❌ 未配置 TRUSTOKEN_TOKENS 或 TRUSTOKEN_TOKEN", file=sys.stderr)
        return 2

    results: List[AccountResult] = []
    for account in accounts:
        try:
            result = run_account(account)
        except Exception as exc:
            result = AccountResult(
                account=account,
                ok=False,
                outcome="failed",
                message=_sanitize(exc),
            )
        results.append(result)
        append_jsonl(args.jsonl, result)

    summary = format_summary(results)
    print("\n" + summary)
    if not args.no_notify:
        notify(summary, results)
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
