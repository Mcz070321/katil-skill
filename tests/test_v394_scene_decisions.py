import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import run_regression  # noqa: E402

AUTHORITY = ROOT / "references" / "reference-and-task-handling.md"
CAMERA = ROOT / "references" / "camera-direction.md"
SEEDANCE = ROOT / "references" / "seedance-2.5.md"
SKILL = ROOT / "SKILL.md"

# V3.9.3 及更早版本中要求强制破框的句子；历史发布记录可以保留，现行权威文件不得再出现。
LEGACY = [
    "不锁定原图静态机位与全景画幅",
    "显式解绑原图静态机位与全景画幅",
    "多镜优先从局部中近景起幅破框",
    "必须写明前景地标向画框两侧或下方滑出画外",
    "前景地标向画面两侧或下方滑出画外",
    "前景地标向画框两侧或下方滑出画外",
    "起幅承接首帧后借主体跨前景位移",
    "起幅后借位移或带地标硬切脱框",
    "相邻镜头须变换对同一地标的观察角度与景别尺度",
    "强制 3D 视差",
]


def read(path):
    return path.read_text(encoding="utf-8")


def legacy_conflicts(text):
    return [phrase for phrase in LEGACY if phrase in text]


def cases():
    data = json.loads((ROOT / "tests" / "execution_cases.json").read_text(encoding="utf-8"))
    return {case["id"]: case for case in data["cases"]}


class SceneDecisionContractTests(unittest.TestCase):
    def test_current_authority_files_have_no_legacy_forced_rules(self):
        for path in (AUTHORITY, CAMERA, SEEDANCE, SKILL):
            with self.subTest(path=path.name):
                self.assertEqual(legacy_conflicts(read(path)), [], path.name)

    def test_legacy_detector_rejects_new_rules_plus_old_sentence(self):
        combined = "\n".join(read(path) for path in (AUTHORITY, CAMERA, SEEDANCE, SKILL))
        self.assertEqual(legacy_conflicts(combined), [])
        for phrase in LEGACY:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, legacy_conflicts(combined + "\n" + phrase))

    def test_four_dimensions_and_evidence_classes_present(self):
        text = read(AUTHORITY)
        self.assertIn("场景参考图的四维判断与“一减三留”", text)
        self.assertIn("四项可以同时成立，不是四选一的状态机", text)
        self.assertIn("**A 素材用途：**", text)
        self.assertIn("**B 摄影目标：**", text)
        self.assertIn("**C 叙事任务：**", text)
        self.assertIn("**D 场景证据：**", text)
        self.assertIn("**K 已知**", text)
        self.assertIn("**I 合理推断**", text)
        self.assertIn("**U 未知**", text)
        self.assertIn("K 可约束；I 可作受限延展，但不得声称原图确认；U 不写成原图事实", text)

    def test_sr_a_to_e_are_conditional_not_forced(self):
        text = read(AUTHORITY)
        self.assertIn("不把原图静态机位默认为全片唯一视角", text)
        self.assertIn("首镜由用户锁定条件与叙事任务决定，可大远景、全景、中景、局部近景或特写", text)
        self.assertIn("不要求所有镜头都有前景，不强制前景滑出", text)
        self.assertIn("不得为证明破框强制立即移动、立即硬切或大幅遮挡", text)
        self.assertIn("不要求每相邻两镜都换角度和景别", text)
        self.assertIn("不以静态画面本身判失败", text)
        self.assertIn("用户指定固定机位、纯 Zoom、真一镜或锁首帧时，防锁死建议不得反改这些要求", text)

    def test_camera_and_seedance_only_encode_conditional_execution(self):
        camera = read(CAMERA)
        self.assertIn("不要求每相邻两镜都改变对同一地标的角度与景别", camera)
        self.assertIn("不强制前景滑出", camera)
        self.assertIn("用户要纯Zoom、固定机位或二维平面运动时，不改写成三维平移", camera)

        seedance = read(SEEDANCE)
        self.assertIn("不强制前景滑出、不虚构地标", seedance)
        self.assertIn("不强制立即脱框", seedance)

    def test_t44_and_t45_are_conditional(self):
        by_id = cases()
        t44 = "\n".join(by_id["T44"]["must_hold"])
        self.assertIn("首镜机位由用户要求与叙事任务决定", t44)
        self.assertIn("局部起幅与明确视角转换都只是条件选项", t44)
        self.assertNotIn("不锁定原图静态机位与全景画幅", t44)

        t45 = "\n".join(by_id["T45"]["must_hold"])
        self.assertIn("不强制前景滑出、不虚构地标", t45)
        self.assertNotIn("必须写明前景地标", t45)


class StructuredCoverageTests(unittest.TestCase):
    def test_structured_cases_cover_scene_matrix_and_metamorphic_pairs(self):
        by_id = cases()
        expected = ["T%d" % i for i in range(34, 61)]
        self.assertEqual([cid for cid in expected if cid not in by_id], [])
        self.assertEqual(len({case["id"] for case in by_id.values()}), len(by_id))

        for cid in expected:
            case = by_id[cid]
            self.assertTrue(case["must_hold"], cid)
            self.assertTrue(case["must_reject"], cid)
            self.assertFalse(set(case["must_hold"]) & set(case["must_reject"]), cid)

    def test_runner_structured_ids_match_cases(self):
        by_id = cases()
        expected = {"T%d" % i for i in range(34, 63)} | {"C04"}
        self.assertEqual(run_regression.STRUCTURED_IDS, expected)
        for cid in expected:
            if cid == "C04":
                continue
            self.assertIn(cid, by_id)

    def test_metamorphic_contracts_preserve_story_and_scope(self):
        by_id = cases()
        t58 = "\n".join(by_id["T58"]["must_hold"])
        self.assertIn("两版人物身份、目标、关键事件与结局不变", t58)
        self.assertIn("仅锁定首帧版改变首帧入帧权限与开场承接", t58)
        self.assertIn("总长、镜头数量与叙事结果不因变形而漂移", t58)

        t59 = "\n".join(by_id["T59"]["must_hold"])
        self.assertIn("两版人物动作、参考身份、事件与总长一致", t59)
        self.assertIn("A 版是真实机位前进，B 版是焦距变化且机位不动", t59)
        self.assertIn("摄影路径与空间反馈按版本分别描述", t59)


if __name__ == "__main__":
    unittest.main()
