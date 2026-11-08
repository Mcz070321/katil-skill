"""V3.8.2 text contracts, carried forward into V3.9.0.

These tests prove the fourteen 3.8.2 rules, including S1/S2, are still in the
intended authority files and that the registry revisions and SKILL markers
agree with the current tree (ADAPTER/EVIDENCE moved in 3.9.0).
They do not prove semantic quality, model compliance, or finished-video gains.
"""

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references"


def read(name):
    return (REFS / name).read_text(encoding="utf-8")


class EffectContractTests(unittest.TestCase):
    def test_effect_source_axis_impact_present(self):
        text = read("effects-and-damage.md")
        self.assertIn("先写源头、路径、兑现点。", text)
        self.assertIn("无源头、无路径、无兑现点的全屏光斑、无接触光刃、粒子雾，不得当作命中", text)
        self.assertIn("用户明确要求无源、抽象或不可见时，按该设定写受影响物体、声音或身体反应", text)

    def test_effect_explosion_and_environment_present(self):
        text = read("effects-and-damage.md")
        self.assertIn("爆炸与冲击波按三层写。", text)
        self.assertIn("接触点或爆心先确认", text)
        self.assertIn("同源、同时刻的环／几何波带起介质", text)
        self.assertIn("大效果到达后，至少一种环境承接。", text)
        self.assertIn("只有角色光边、拖尾或屏幕闪白不算环境承接", text)

    def test_effect_peak_identity_present(self):
        text = read("effects-and-damage.md")
        self.assertIn("峰值帧仍要认得出主体。", text)
        self.assertIn("主体剪影、兵器朝向、力量轴线、恢复后同相位承接", text)

    def test_effect_entity_boundary_present(self):
        text = read("visual-material-grammar.md")
        self.assertIn("特效层与实体层分开。", text)
        self.assertIn("角色皮肤、服装结构、建筑、道具默认保持实体可读", text)
        self.assertIn("全屏材质化通常只做一次有动机的升维硬切", text)


class ActionCameraContractTests(unittest.TestCase):
    def test_action_rules_present(self):
        text = read("action-and-shot-compiler.md")
        for phrase in (
            "对手按可达状态应答。",
            "命中承认可以分流，不默认震屏。",
            "点名落点，落点决定局部材料与后续功能。",
            "可见打击至少带动一种当场介质。",
            "闪／格／受",
        ):
            self.assertIn(phrase, text)

    def test_camera_and_continuity_rules_present(self):
        camera = read("camera-direction.md")
        self.assertIn("每次切镜换一个观看任务。", camera)
        self.assertIn("跨尺度允许硬切，不假装连续变焦。", camera)
        continuity = read("viewpoint-and-continuity.md")
        self.assertIn("真一镜至少写清四项：起幅观察状态、主体锁点、转向／航点、环境变化作证。", continuity)

    def test_seedance_material_and_time_rules_present(self):
        text = read("seedance-2.5.md")
        self.assertIn("每份实际多模态素材写清三件事：提取什么、排除什么、是否允许作为画面帧／构图直接入帧。", text)
        self.assertIn("多图职责可在正文开头紧凑合写，不为每张图堆重复禁令。", text)
        self.assertIn("**A 事件序**（默认，不写秒，用事件编号／分镜／镜内阶段推进）", text)
        self.assertIn("**B 锁定秒轴**（用户明确要求秒轴或时间码", text)
        self.assertIn("只给总长、不要求秒轴时，仍按 A 事件序", text)
        self.assertIn("不得用“约3秒”“几秒后”伪造精确", text)
        self.assertIn("也不得在用户锁定秒轴时改成纯事件序", text)

    def test_registry_revisions_and_markers(self):
        registry = json.loads((ROOT / "rules" / "rule-registry.yaml").read_text(encoding="utf-8"))
        rules = {rule["rule_id"]: rule for rule in registry["rules"]}
        self.assertEqual(rules["CONTINUITY"]["rule_revision"], "1.2.0")
        self.assertEqual(rules["SEEDANCE"]["rule_revision"], "1.3.0")
        expected = {
            "REF": "1.2.0",
            "SOUND": "1.0.0",
            "SPACE": "1.1.0",
            "WITNESS": "1.2.0",
            "DELIVERY": "1.2.0",
            "ADAPTER": "1.3.0",
            "EVIDENCE": "1.0.0",
            "TIME": "1.0.0",
        }
        self.assertEqual({key: rules[key]["rule_revision"] for key in expected}, expected)
        self.assertEqual(rules["CONTINUITY"]["authority"]["path"], "references/viewpoint-and-continuity.md")
        self.assertEqual(rules["SEEDANCE"]["authority"]["path"], "references/seedance-2.5.md")
        self.assertEqual(rules["EVIDENCE"]["authority"]["path"], "references/evidence-and-claims.md")
        self.assertEqual(rules["EVIDENCE"]["authority"]["anchor"], "katil-evidence")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("<!-- SUMMARY of CONTINUITY@1.2.0 -->", skill)
        self.assertIn("<!-- SUMMARY of SEEDANCE@1.3.0 -->", skill)
        self.assertIn("<!-- SUMMARY of ADAPTER@1.3.0 -->", skill)
        self.assertIn("<!-- SUMMARY of EVIDENCE@1.0.0 -->", skill)
        self.assertNotIn("<!-- SUMMARY of CONTINUITY@1.1.0 -->", skill)
        self.assertNotIn("<!-- SUMMARY of SEEDANCE@1.2.0 -->", skill)


if __name__ == "__main__":
    unittest.main()
