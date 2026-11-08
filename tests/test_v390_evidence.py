"""V3.9.0 evidence-level and structured-case contracts.

These tests prove the EV0–EV3 page, source tiers, registry entries, and
must_hold/must_reject fields are present and internally consistent. They do not
prove semantic support, model compliance, or finished-video quality.
"""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references"


def read(name):
    return (REFS / name).read_text(encoding="utf-8")


class EvidenceLevelTests(unittest.TestCase):
    def test_ev0_to_ev3_are_defined(self):
        text = read("evidence-and-claims.md")
        for phrase in ("| EV0 | 设计 |", "| EV1 | 文本与结构 |", "| EV2 | 生成观察 |", "| EV3 | 同条件盲评 |"):
            self.assertIn(phrase, text)
        self.assertIn("证据等级属于**具体声明**，不属于整个版本", text)
        self.assertIn("没有实际生成并观看完整视频时，EV2 及以上不成立", text)

    def test_claim_boundaries_do_not_upgrade_text_to_video(self):
        text = read("evidence-and-claims.md")
        self.assertIn("用 EV1 写“视频通过”“模型已遵循”“效果提升”。", text)
        self.assertIn("用 EV2 写“稳定解决”“全面通过”。", text)
        self.assertIn("结构 PASS 不得改写成成片 PASS", text)
        self.assertIn("版本号、文件数、测试数和绿色 CI 不提升证据等级", text)
        acceptance = read("video-acceptance-testing.md")
        self.assertIn("EV1", acceptance)
        self.assertIn("EV3", acceptance)
        self.assertIn("PENDING_VIDEO", acceptance)


class SourceTierTests(unittest.TestCase):
    def test_source_tiers_and_compatible_boundary(self):
        text = read("model-adaptation.md")
        for tier in ("official", "platform_measured", "unverified_assumption"):
            self.assertIn(tier, text)
        self.assertIn("官方文档不能单独判兼容", text)
        self.assertIn("COMPATIBLE需要platform_measured或同任务的真实视频观察", text)
        self.assertIn("不得支撑COMPATIBLE", text)


class RegistryAndCaseTests(unittest.TestCase):
    def test_registry_has_evidence_rule_and_adapter_revision(self):
        registry = json.loads((ROOT / "rules" / "rule-registry.yaml").read_text(encoding="utf-8"))
        rules = {rule["rule_id"]: rule for rule in registry["rules"]}
        evidence = rules["EVIDENCE"]
        self.assertEqual(evidence["rule_revision"], "1.0.0")
        self.assertEqual(evidence["authority"]["path"], "references/evidence-and-claims.md")
        self.assertEqual(evidence["authority"]["anchor"], "katil-evidence")
        self.assertIn("ADAPTER", evidence["depends_on"])
        self.assertEqual(rules["ADAPTER"]["rule_revision"], "1.3.0")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("<!-- SUMMARY of EVIDENCE@1.0.0 -->", skill)
        self.assertIn("<!-- SUMMARY of ADAPTER@1.3.0 -->", skill)
        self.assertNotIn("<!-- SUMMARY of ADAPTER@1.2.0 -->", skill)

    def test_structured_cases_have_separate_positive_and_negative_assertions(self):
        ids = {"T%d" % i for i in range(34, 44)} | {"C04"}
        seen = set()
        for filename in ("execution_cases.json", "continuity_cases.json"):
            data = json.loads((ROOT / "tests" / filename).read_text(encoding="utf-8"))
            for case in data["cases"]:
                if case["id"] not in ids:
                    continue
                seen.add(case["id"])
                hold = case.get("must_hold")
                reject = case.get("must_reject")
                self.assertIsInstance(hold, list, case["id"])
                self.assertIsInstance(reject, list, case["id"])
                self.assertTrue(hold, case["id"])
                self.assertTrue(reject, case["id"])
                self.assertFalse(set(hold) & set(reject), case["id"])
                self.assertTrue(all(isinstance(item, str) and item.strip() for item in hold + reject), case["id"])
        self.assertEqual(seen, ids)

    def test_generation_g05_g06_compare_v381_and_v382(self):
        data = json.loads((ROOT / "tests" / "generation_cases.json").read_text(encoding="utf-8"))
        cases = {case["id"]: case for case in data["cases"]}
        for case_id in ("G05", "G06"):
            case = cases[case_id]
            self.assertEqual(case["comparison"], "V3.8.1 vs V3.8.2")
            self.assertIs(case["evidence_required"], True)
            self.assertGreaterEqual(case["runs_min"], 3)
            self.assertNotIn("source_sample", case)
            self.assertNotIn("legacy_sample", case)


if __name__ == "__main__":
    unittest.main()
