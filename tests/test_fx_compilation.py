import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from fx_compilation_check import check_case, check_payload


def fixtures():
    return json.loads((ROOT / 'tests' / 'fx_compilation_cases.json').read_text(encoding='utf-8'))['cases']


class FxCompilationTests(unittest.TestCase):
    def test_three_distinct_review_fixtures_have_coverage_and_order(self):
        cases = fixtures()
        self.assertEqual([case['id'] for case in cases], ['FCC01', 'FCC02', 'FCC03'])
        for case in cases:
            with self.subTest(case=case['id']):
                result = check_case(case)
                self.assertEqual(result['status'], 'ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED')
                self.assertEqual(result['evidence_boundary'], 'EV1_LITERAL_ONLY')
                self.assertLess(result['compiled_characters_without_whitespace'], result['source_characters_without_whitespace'])
                self.assertEqual(result['issues'], [])

    def test_deleted_full_screen_impact_is_detected(self):
        case = copy.deepcopy(fixtures()[0])
        case['compiled_text'] = case['compiled_text'].replace('全屏朱砂裂墨', '轻微红光')
        result = check_case(case)
        self.assertEqual(result['status'], 'MISSING_OR_ORDER_VIOLATION')
        self.assertTrue(any(i['id'] == 'impact' for i in result['issues']))

    def test_weapon_hand_or_end_state_loss_is_detected(self):
        case = copy.deepcopy(fixtures()[1])
        case['compiled_text'] = case['compiled_text'].replace('右臂银色机械刀', '左臂银色机械刀')
        case['compiled_text'] = case['compiled_text'].replace('弧盾保持展开', '弧盾恢复为刀')
        ids = {item['id'] for item in check_case(case)['issues']}
        self.assertTrue({'transform', 'tail'} <= ids)

    def test_required_event_order_is_checked(self):
        case = copy.deepcopy(fixtures()[2])
        case['compiled_text'] = case['compiled_text'].replace(
            '灯一盏盏熄灭，最后女孩缓缓抬头', '最后女孩缓缓抬头，灯一盏盏熄灭')
        result = check_case(case)
        self.assertTrue(any(item['kind'] == 'compiled_order_changed' for item in result['issues']))

    def test_literal_coverage_can_miss_negation_and_never_proves_semantics(self):
        case = copy.deepcopy(fixtures()[0])
        case['compiled_text'] = case['compiled_text'].replace('甲取胜', '并非甲取胜')
        result = check_case(case)
        self.assertEqual(result['status'], 'ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED')
        self.assertIn('否定', result['warning'])
        self.assertNotIn('PASS', result['status'])

    def test_duplicate_or_invalid_annotation_is_rejected(self):
        case = copy.deepcopy(fixtures()[0])
        case['requirements'].append(copy.deepcopy(case['requirements'][0]))
        with self.assertRaises(ValueError):
            check_case(case)
        case = copy.deepcopy(fixtures()[0])
        case['required_order'].append(['contact', 'no-such-fact'])
        with self.assertRaises(ValueError):
            check_case(case)

    def test_cli_reports_literal_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'case.json'
            path.write_text(json.dumps(fixtures()[0], ensure_ascii=False), encoding='utf-8')
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts' / 'fx_compilation_check.py'), str(path)],
                capture_output=True, text=True, encoding='utf-8', check=True, env=env)
            report = json.loads(result.stdout)
            self.assertEqual(report['status'], 'ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED')
            self.assertEqual(report['evidence_boundary'], 'EV1_LITERAL_ONLY')



    def test_cli_supports_bundled_cases_suite(self):
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        env['PYTHONUTF8'] = '1'
        suite_path = ROOT / 'tests' / 'fx_compilation_cases.json'
        result = subprocess.run(
            [sys.executable, str(ROOT / 'scripts' / 'fx_compilation_check.py'), str(suite_path)],
            capture_output=True, text=True, encoding='utf-8', check=True, env=env)
        report = json.loads(result.stdout)
        self.assertEqual(report['status'], 'ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED')
        self.assertEqual(report['case_count'], 3)
        self.assertEqual(report['issues'], [])
        self.assertEqual(report['evidence_boundary'], 'EV1_LITERAL_ONLY')

    def test_cli_suite_reports_issue_exit_code(self):
        broken_suite = {'version': '1.0.0', 'cases': copy.deepcopy(fixtures())}
        broken_suite['cases'][0]['compiled_text'] = broken_suite['cases'][0]['compiled_text'].replace('全屏朱砂裂墨', '轻微红光')
        report = check_payload(broken_suite)
        self.assertEqual(report['status'], 'MISSING_OR_ORDER_VIOLATION')
        self.assertTrue(any(item['case_id'] == 'FCC01' and item['id'] == 'impact' for item in report['issues']))


if __name__ == '__main__':
    unittest.main()
