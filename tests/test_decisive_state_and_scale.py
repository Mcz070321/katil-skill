import json
import unittest
from pathlib import Path

from test_run_regression import run_runner
from run_regression import STRUCTURED_IDS

ROOT = Path(__file__).resolve().parents[1]


class DecisiveStateAndScaleTests(unittest.TestCase):
    def test_routes_and_text_cases(self):
        topic = 'decisive-state-and-scale.md'
        self.assertTrue((ROOT / 'references' / topic).is_file())
        for path in ('SKILL.md', 'references/shot-execution-contract.md'):
            self.assertIn(topic, (ROOT / path).read_text(encoding='utf-8'))
        self.assertTrue({'T61', 'T62'} <= STRUCTURED_IDS)
        cases = json.loads((ROOT / 'tests/execution_cases.json').read_text(encoding='utf-8'))
        selected = {case['id']: case for case in cases['cases'] if case['id'] in {'T61', 'T62'}}
        self.assertEqual(set(selected), {'T61', 'T62'})
        for case in selected.values():
            self.assertTrue(case['must_hold'])
            self.assertTrue(case['must_reject'])

    def test_generation_trials_and_external_samples_are_separate(self):
        path = ROOT / 'tests'
        cases = json.loads((path / 'generation_cases.json').read_text(encoding='utf-8'))
        selected = {case['id']: case for case in cases['cases'] if case['id'] in {'G10', 'G11'}}
        self.assertEqual(set(selected), {'G10', 'G11'})
        self.assertIn('V3.10.5 新增逐条评审判据覆盖检查', cases['description'])
        self.assertTrue({'right_arm_and_blade', 'left_arm_and_blade', 'head_separation'}
                        <= selected['G10']['review_criteria'].keys())
        self.assertTrue({'giant_fist_form', 'giant_sword_form', 'contact_point', 'impact_and_recovery'}
                        <= selected['G11']['review_criteria'].keys())
        for case in selected.values():
            # The recorded version experiment keeps its original comparison.
            self.assertEqual(case['comparison'], 'V3.10.1 vs V3.10.2')
            self.assertEqual(case['runs_min'], 3)
            self.assertIs(case['evidence_required'], True)
            self.assertTrue((ROOT / case['protocol']).is_file())
        proc, report = run_runner(path)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rows = {row['test_case']: row for row in report['results']}
        for case_id in selected:
            self.assertEqual(rows[case_id]['video'], 'PENDING_VIDEO')
        samples = json.loads((path / 'video_regression_manifest.json').read_text(encoding='utf-8'))
        external = [sample for sample in samples['samples'] if sample.get('case_candidate') in selected]
        self.assertEqual({sample['case_candidate'] for sample in external}, set(selected))
        for sample in external:
            self.assertIs(sample['usable_as_baseline'], False)
            self.assertEqual(sample['prompt_status'], 'comparison_draft_only')
            self.assertEqual(sample['observations']['full_playback_review'], False)
