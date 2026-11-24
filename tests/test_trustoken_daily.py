import json
import os
import tempfile
import unittest

import trustoken_daily as daily


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []
        self.headers = {}
        self.closed = False

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, "json": kwargs.get("json")})
        if not self.responses:
            raise AssertionError("unexpected request")
        return self.responses.pop(0)

    def close(self):
        self.closed = True


def account():
    return daily.Account("主号", "token-abc", "")


class TrustokenDailyTests(unittest.TestCase):
    def test_parse_accounts_supports_label_token_uid(self):
        accounts = daily.parse_accounts("主号|token-abc|123\n备号|token-def|456")
        self.assertEqual(accounts[0].label, "主号")
        self.assertEqual(accounts[0].token, "token-abc")
        self.assertEqual(accounts[0].uid, "123")
        self.assertEqual(len(accounts), 2)

    def test_resolve_uid_from_self(self):
        session = FakeSession([FakeResponse({"success": True, "data": {"id": 99}})])
        resolved = daily.resolve_uid(session, account())
        self.assertEqual(resolved.uid, "99")
        self.assertEqual(session.calls[0]["url"], daily.BASE + daily.SELF_PATH)

    def test_already_checked_in_is_done(self):
        session = FakeSession(
            [
                FakeResponse({"success": True, "data": {"id": 1}}),
                FakeResponse(
                    {
                        "success": True,
                        "data": {"checked_in_today": True, "streak": 4},
                    }
                ),
                FakeResponse({"success": True, "data": {"tasks": []}}),
            ]
        )
        result = daily.run_account(account(), session=session)
        self.assertTrue(result.ok)
        self.assertEqual(result.outcome, "done")
        self.assertEqual(len(session.calls), 3)

    def test_full_checkin_and_task_claim(self):
        session = FakeSession(
            [
                FakeResponse({"success": True, "data": {"id": 1}}),
                FakeResponse({"success": True, "data": {"checked_in_today": False}}),
                FakeResponse({"success": True, "data": {"total_reward": 10}}),
                FakeResponse({"success": True, "data": {"checked_in_today": True}}),
                FakeResponse(
                    {
                        "success": True,
                        "data": {
                            "tasks": [
                                {
                                    "task_type": "daily_ai_1",
                                    "title": "完成一次 AI 任务",
                                    "status": "claimable",
                                    "progress": 1,
                                    "target": 1,
                                }
                            ]
                        },
                    }
                ),
                FakeResponse({"success": True, "data": {"reward": 5}}),
                FakeResponse(
                    {
                        "success": True,
                        "data": {
                            "tasks": [
                                {
                                    "task_type": "daily_ai_1",
                                    "title": "完成一次 AI 任务",
                                    "status": "claimed",
                                    "progress": 1,
                                    "target": 1,
                                }
                            ]
                        },
                    }
                ),
            ]
        )
        result = daily.run_account(account(), session=session)
        self.assertTrue(result.ok)
        self.assertEqual(result.outcome, "claimed")
        self.assertEqual(result.credit, 15)
        self.assertEqual(session.calls[2]["json"], None)
        self.assertEqual(session.calls[5]["json"], {"task_type": "daily_ai_1"})

    def test_checkin_post_without_status_change_is_failure(self):
        session = FakeSession(
            [
                FakeResponse({"success": True, "data": {"id": 1}}),
                FakeResponse({"success": True, "data": {"checked_in_today": False}}),
                FakeResponse({"success": True, "data": {"total_reward": 10}}),
                FakeResponse({"success": True, "data": {"checked_in_today": False}}),
            ]
        )
        with self.assertRaises(daily.ApiError):
            daily.run_account(account(), session=session)

    def test_task_claim_must_be_visible_in_readback(self):
        session = FakeSession(
            [
                FakeResponse({"success": True, "data": {"id": 1}}),
                FakeResponse({"success": True, "data": {"checked_in_today": True}}),
                FakeResponse(
                    {
                        "success": True,
                        "data": {
                            "tasks": [
                                {
                                    "task_type": "daily_ai_1",
                                    "status": "claimable",
                                    "progress": 1,
                                    "target": 1,
                                }
                            ]
                        },
                    }
                ),
                FakeResponse({"success": True, "data": {"reward": 5}}),
                FakeResponse(
                    {
                        "success": True,
                        "data": {
                            "tasks": [
                                {
                                    "task_type": "daily_ai_1",
                                    "status": "claimable",
                                    "progress": 1,
                                    "target": 1,
                                }
                            ]
                        },
                    }
                ),
            ]
        )
        result = daily.run_account(account(), session=session)
        self.assertFalse(result.ok)
        self.assertIn("回读未确认", result.message)

    def test_jsonl_has_no_token(self):
        result = daily.AccountResult(account(), True, "done", "ok", detail={"checked_in": True})
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "result.jsonl")
            daily.append_jsonl(path, result)
            with open(path, encoding="utf-8") as handle:
                line = handle.readline()
        self.assertNotIn("token-abc", line)
        self.assertEqual(json.loads(line)["provider"], "trustoken")


if __name__ == "__main__":
    unittest.main()
