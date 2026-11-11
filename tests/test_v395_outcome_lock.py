import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_regression  # noqa: E402

SHOT = ROOT / "references" / "shot-execution-contract.md"
VIDEO = ROOT / "references" / "video-acceptance-testing.md"
HIGH_SPEED = ROOT / "references" / "high-speed-combat-generation.md"
SKILL = ROOT / "SKILL.md"
REGISTRY = ROOT / "rules" / "rule-registry.yaml"


def read(path):
    return path.read_text(encoding="utf-8")


def cases():
    data = json.loads((ROOT / "tests" / "execution_cases.json").read_text(encoding="utf-8"))
    return {case["id"]: case for case in data["cases"]}


class OutcomeLockContractTests(unittest.TestCase):
    def test_t60_has_separate_positive_and_negative_assertions(self):
        case = cases()["T60"]
        self.assertEqual(
            set(case),
            {"id", "request", "criteria", "must_hold", "must_reject"},
        )
        self.assertGreaterEqual(len(case["criteria"]), 3)
        self.assertTrue(case["must_hold"])
        self.assertTrue(case["must_reject"])
        self.assertFalse(set(case["must_hold"]) & set(case["must_reject"]))
        self.assertIn("T60", run_regression.STRUCTURED_IDS)

    def test_t60_compares_overload_with_settlement(self):
        case = cases()["T60"]
        request = case["request"]
        self.assertIn("九", request)
        self.assertIn("六", request)
        self.assertIn("只允许结果发生后的尾段事件容量不同", request)

        hold = "\n".join(case["must_hold"])
        reject = "\n".join(case["must_reject"])
        self.assertIn("结果发生点与实际结尾分开", hold)
        self.assertIn("只承接直接余波", hold)
        self.assertIn("至少各有一项可辨", hold)
        self.assertIn("新巨物", reject)
        self.assertIn("第二结局", reject)
        self.assertIn("没有前置触发", reject)

    def test_authority_has_outcome_lock_and_conditional_reversal(self):
        text = read(SHOT)
        self.assertIn('<a id="katil-outcome-lock"></a>', text)
        self.assertIn("### 结果发生后的尾段锁定", text)
        self.assertIn("结果点之后的尾段只承接直接余波", text)
        self.assertIn("不再新开独立攻击、召唤、领域、增援、追逐目标或第二结局", text)
        self.assertIn("没有前置触发、只靠尾段追加翻盘，仍按新开事件处理", text)
        self.assertIn("不限制结果发生前的多线并发、交叉剪辑、必要反击", text)

    def test_acceptance_and_high_speed_reference_the_lock(self):
        video = read(VIDEO)
        self.assertIn("是否又新开独立攻击、召唤、领域、增援、追逐或第二结局", video)
        self.assertIn("替换已分出胜负的主体", video)

        high_speed = read(HIGH_SPEED)
        self.assertIn("尾段只承接直接余波、存亡与状态沉降", high_speed)
        self.assertIn("不再开新回合、换新巨物或补第二结局", high_speed)
        self.assertIn("shot-execution-contract.md#katil-outcome-lock", high_speed)

    def test_registry_witness_is_revision_1_3_0(self):
        registry = json.loads(read(REGISTRY))
        witness = next(rule for rule in registry["rules"] if rule["rule_id"] == "WITNESS")
        self.assertEqual(witness["rule_revision"], "1.3.0")
        self.assertEqual(witness["summary_refs"][0]["marker"], "SUMMARY of WITNESS@1.3.0")
        self.assertEqual(witness["summary_refs"][0]["rule_revision"], "1.3.0")
        self.assertRegex(witness["authority_sha256"], r"^[0-9a-f]{64}$")
        self.assertRegex(witness["summary_refs"][0]["summary_sha256"], r"^[0-9a-f]{64}$")

        skill = read(SKILL)
        self.assertIn("<!-- SUMMARY of WITNESS@1.3.0 -->", skill)
        self.assertNotIn("<!-- SUMMARY of WITNESS@1.2.0 -->", skill)
        self.assertIn("尾段只承接直接余波与状态沉降", skill)


if __name__ == "__main__":
    unittest.main()
