import json
from pathlib import Path
import unittest

from test_run_regression import run_runner

ROOT = Path(__file__).resolve().parents[1]


class FxVideoComparisonPlanTests(unittest.TestCase):
    def test_three_named_cases_have_real_evidence_requirements(self):
        cases = json.loads((ROOT / 'tests/generation_cases.json').read_text(encoding='utf-8'))['cases']
        selected = {case['id']: case for case in cases if case['id'] in {'G07', 'G08', 'G09'}}
        self.assertEqual(set(selected), {'G07', 'G08', 'G09'})
        for case in selected.values():
            self.assertEqual(case['comparison'], 'V3.9.5 vs V3.10.1')
            self.assertGreaterEqual(case['runs_min'], 3)
            self.assertTrue(case['evidence_required'])
            self.assertTrue(case['positive_control'])
            self.assertTrue((ROOT / case['protocol']).is_file())
            self.assertGreaterEqual(len(case['focus']), 4)

    def test_new_video_trials_remain_pending_without_media(self):
        proc, report = run_runner(ROOT / 'tests')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        selected = {case['test_case']: case for case in report['results'] if case['test_case'] in {'G07', 'G08', 'G09'}}
        self.assertEqual(set(selected), {'G07', 'G08', 'G09'})
        for case in selected.values():
            self.assertEqual(case['status'], 'PENDING_VIDEO')
            self.assertEqual(case['video'], 'PENDING_VIDEO')



    def test_g10_and_g11_share_fx_ab_testing_protocol(self):
        cases = json.loads((ROOT / 'tests/generation_cases.json').read_text(encoding='utf-8'))['cases']
        selected = {case['id']: case for case in cases if case['id'] in {'G10', 'G11'}}
        self.assertEqual(set(selected), {'G10', 'G11'})
        protocol_text = (ROOT / 'references/fx-ab-testing.md').read_text(encoding='utf-8')
        self.assertIn('G10', protocol_text)
        self.assertIn('G11', protocol_text)
        for case in selected.values():
            self.assertEqual(case['protocol'], 'references/fx-ab-testing.md')


if __name__ == '__main__':
    unittest.main()
