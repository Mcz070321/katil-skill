import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'block_lint.py'

class CliTests(unittest.TestCase):
    def lint(self, text, *args):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'prompt.txt'
            target.write_text(text,encoding='utf-8')
            p=subprocess.run([sys.executable,str(SCRIPT),str(target),*args],capture_output=True,text=True,encoding='utf-8')
            self.assertEqual(p.returncode,0,p.stderr)
            return json.loads(p.stdout)

    def test_independent_language_blocks_do_not_overlap(self):
        r=self.lint('中文：\n```text\n0—1.5秒：甲走。\n1.5—3秒：乙走。\n```\nEnglish:\n```text\n0–1.5 s: A walks.\n1.5–3 s: B walks.\n```','--duration','3')
        self.assertEqual(len(r['groups']),2)
        self.assertTrue(all(g['timing']['status']=='PASS' for g in r['groups']))
        self.assertEqual(r['status'],'UNKNOWN')

    def test_hours_and_minutes(self):
        r=self.lint('00:00:01.250–00:00:02.500: A\n00:00:02.500–00:00:04.000: B','--duration','4')
        self.assertEqual(r['groups'][0]['ranges_seconds'],[[1.25,2.5],[2.5,4.0]])
        self.assertEqual(r['groups'][0]['timing']['status'],'PASS')

    def test_single_timestamp_not_range(self):
        r=self.lint('2秒：画面切到门外。','--duration','3')
        self.assertEqual(r['groups'][0]['timing']['status'],'UNKNOWN')
        self.assertEqual(r['groups'][0]['ranges_seconds'],[])

    def test_no_duration_or_timing_is_unknown(self):
        r=self.lint('角色走向窗户。')
        self.assertEqual(r['status'],'UNKNOWN')
        self.assertEqual(r['groups'][0]['timing']['status'],'UNKNOWN')
        self.assertEqual(r['checks']['semantic_content']['status'],'UNKNOWN')

    def test_end_outside_and_reversed_range(self):
        r=self.lint('0—2秒：甲前进。\n3—2秒：甲转身。\n2—4秒：乙后退。','--duration','3')
        self.assertEqual(r['status'],'WARN')
        self.assertEqual(r['groups'][0]['timing']['status'],'WARN')
        self.assertTrue(any('超出' in x for x in r['groups'][0]['timing']['findings']))
        self.assertTrue(any('结束' in x for x in r['groups'][0]['timing']['findings']))

    def test_overlap_and_gap_reported_without_global_failure(self):
        r=self.lint('0—2秒：A\n1—3秒：B\n4—5秒：C','--duration','5')
        findings=' '.join(r['groups'][0]['timing']['findings'])
        self.assertIn('重叠',findings)
        self.assertIn('间隙',findings)
        self.assertEqual(r['status'],'WARN')

    def test_allow_overlap_is_not_an_accuracy_claim(self):
        r=self.lint('0—2秒：第一轨\n1—3秒：第二轨','--duration','3','--allow-overlap')
        self.assertFalse(any('重叠' in x for x in r['groups'][0]['timing']['findings']))
        self.assertNotEqual(r['status'],'PASS')

    def test_parallel_tracks_do_not_conflict(self):
        r=self.lint('[track:camera]\n0–3秒：镜头推近\n[track:sound]\n0–3秒：风声','--duration','3')
        self.assertFalse(any('重叠' in x for x in r['groups'][0]['timing']['findings']))
        self.assertEqual(r['groups'][0]['timing']['status'],'PASS')

    def test_unsupported_timestamp_not_silently_ignored(self):
        r=self.lint('0—1秒：甲走。\n第2帧至第8帧：乙转身。','--duration','3')
        self.assertNotEqual(r['groups'][0]['timing']['status'],'PASS')
        self.assertTrue(any('无法' in x for x in r['groups'][0]['timing']['findings']))

    def test_no_false_single_language_for_product_terms(self):
        r=self.lint('中文：\n```text\n0—2秒：LED 标志亮起。\n```','--duration','2','--language','zh')
        self.assertNotEqual(r['checks']['output_language']['status'],'WARN')
        self.assertEqual(r['checks']['output_language']['status'],'UNKNOWN')

    def test_minute_second_decimal(self):
        r=self.lint('00:01.25–00:02.50: A', '--duration','3')
        self.assertEqual(r['groups'][0]['ranges_seconds'], [[1.25,2.5]])
        self.assertEqual(r['groups'][0]['timing']['status'], 'PASS')

    def test_point_with_valid_range_remains_unknown(self):
        r=self.lint('0—1秒：甲走。\n00:00:02.000：甲停止。', '--duration','3')
        self.assertEqual(r['groups'][0]['timing']['status'], 'UNKNOWN')

    def test_valid_range_without_duration_cannot_pass(self):
        r=self.lint('0—1秒：甲走。')
        self.assertEqual(r['groups'][0]['timing']['status'], 'UNKNOWN')

    def test_bold_timestamp(self):
        r=self.lint('**0—1秒**：甲走。\n**1—2秒**：乙走。', '--duration','2')
        self.assertEqual(r['groups'][0]['ranges_seconds'], [[0.0,1.0],[1.0,2.0]])
        self.assertEqual(r['groups'][0]['timing']['status'], 'PASS')

    def test_second_range_on_same_line_cannot_be_ignored(self):
        r=self.lint('0—1秒：甲走；1—2秒：乙走。', '--duration','2')
        self.assertNotEqual(r['groups'][0]['timing']['status'], 'PASS')

    def test_standalone_point_is_unknown_even_with_range(self):
        r=self.lint('0—1秒：甲走。\n00:02', '--duration','3')
        self.assertEqual(r['groups'][0]['timing']['status'], 'UNKNOWN')

    def test_inline_time_ranges_are_not_silently_ignored(self):
        examples=[
            '0—1秒：甲走；01:30–02:00：乙走。',
            '0—1秒：甲走；1–5：乙走。',
            '0—1秒：甲走。\n镜头二（1—9秒）：乙走。',
            '0–1 s: A walks.\nAt 2–5 seconds: B walks.',
        ]
        for text in examples:
            with self.subTest(text=text):
                result=self.lint(text,'--duration','3')
                self.assertIn(result['groups'][0]['timing']['status'],('UNKNOWN','WARN'))

    def test_distance_in_dialogue_not_a_timing_error(self):
        result=self.lint('0—1秒：她说：“距离1—5米。”','--duration','3')
        self.assertEqual(result['groups'][0]['timing']['status'],'PASS')

    def test_mixed_plain_and_fenced_blocks_are_both_inspected(self):
        result=self.lint('中文：\n0—5秒：中文超时。\nEnglish:\n```text\n0–1 s: A.\n```','--duration','3')
        self.assertEqual(len(result['groups']),2)
        self.assertEqual(result['groups'][0]['language'],'zh')
        self.assertEqual(result['groups'][0]['timing']['status'],'WARN')
        self.assertEqual(result['groups'][1]['language'],'en')
        self.assertEqual(result['groups'][1]['timing']['status'],'PASS')

    def test_huge_number_never_emits_nonstandard_json(self):
        r=self.lint('0—'+'9'*500+'秒：甲走。','--duration','3')
        self.assertIn(r['groups'][0]['timing']['status'],('UNKNOWN','WARN'))
        self.assertEqual(r['groups'][0]['ranges_seconds'],[])

    def test_coverage_boundary_unknown_by_default(self):
        r=self.lint('1—2秒：甲走。','--duration','3')
        self.assertEqual(r['groups'][0]['coverage']['status'],'UNKNOWN')

    def test_invalid_duration_is_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'p.txt';target.write_text('test',encoding='utf-8')
            p=subprocess.run([sys.executable,str(SCRIPT),str(target),'--duration','-2'],capture_output=True,text=True)
            self.assertNotEqual(p.returncode,0)



# --- Event Timing Tests ---
"""Opt-in event timing checks through the public CLI and regression runner."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_run_regression import run_runner, write_minimal_suite


ROOT = Path(__file__).resolve().parents[1]


class EventTimingTests(unittest.TestCase):
    def lint(self, text, policy='forbid'):
        with tempfile.TemporaryDirectory() as temporary:
            prompt = Path(temporary) / 'prompt.md'
            prompt.write_text(text, encoding='utf-8')
            result = subprocess.run(
                [sys.executable, str(ROOT / 'scripts/block_lint.py'), str(prompt),
                 '--timing-policy', policy],
                capture_output=True, text=True, encoding='utf-8')
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)

    def test_editorial_timing_after_numbered_labels_is_warned(self):
        for label in ('分镜01', '镜内阶段01', 'Shot 01', 'Phase 01'):
            for timing in ('0—3秒', '00:05', '第10秒', '时长3秒', '镜长3秒', '3 seconds'):
                with self.subTest(label=label, timing=timing):
                    report = self.lint(f'```text\n{label}（{timing}）：推近窗户。\n```')
                    self.assertEqual(report['checks']['timing_policy']['status'], 'WARN')

    def test_timing_row_and_colon_after_label_are_warned(self):
        for line in ('0–3 s: A walks.', '00:05: A turns.',
                     '分镜01：0—3秒：推近。', 'Shot 01: at 5 seconds: A turns.'):
            with self.subTest(line=line):
                self.assertEqual(self.lint(line)['checks']['timing_policy']['status'], 'WARN')

    def test_explicit_clock_and_duration_headers_are_warned(self):
        for line in ('Shot 01 (00:00:01.250–00:00:02.500): A turns.',
                     'Shot 01 (at 00:05): A turns.',
                     '分镜01（持续3秒）：推近窗户。'):
            with self.subTest(line=line):
                report = self.lint(f'```text\n{line}\n```')
                self.assertEqual(report['checks']['timing_policy']['status'], 'WARN')

    def test_pipe_header_separator_preserves_timing_detection(self):
        for line in ('分镜01｜0—3秒：推近窗户。', 'Shot 01 | 0–3 s: A walks.'):
            with self.subTest(line=line):
                report = self.lint(f'```text\n{line}\n```')
                self.assertEqual(report['checks']['timing_policy']['status'], 'WARN')

    def test_total_story_times_distance_and_clock_face_are_not_warned(self):
        text = ('全片总时长30秒。\n分镜01：3秒后门打开。\n'
                '分镜02：她说：“距离1—5米，三秒后出发。”\n'
                'Shot 03: The clock shows 12:30.\n'
                'Shot 04: 3 seconds later the door opens.\n'
                '分镜05：镜头前移1—5米。\n'
                'Shot 06: 3–5 seconds later the light goes out.\n'
                '分镜07：3—5秒钟后，门打开。')
        report = self.lint(text)
        self.assertEqual(report['checks']['timing_policy']['status'], 'UNKNOWN')

    def test_external_time_notes_do_not_enter_copy_block_check(self):
        report = self.lint('8—10秒：技术编辑窗口。\n```text\n分镜01：推近窗户。\n```')
        self.assertEqual(report['checks']['timing_policy']['status'], 'UNKNOWN')
        self.assertEqual(len(report['groups']), 1)

    def test_auto_preserves_legacy_point_classification(self):
        report = self.lint('00:05：推近窗户。', policy='auto')
        self.assertEqual(report['groups'][0]['timing']['status'], 'UNKNOWN')
        self.assertNotIn('timing_policy', report['checks'])

    def test_relative_delays_are_excluded_from_forbid_interval_comparison(self):
        text = '3–5 seconds later, the door opens.\n2–4 seconds later, she turns.'
        report = self.lint(text)
        self.assertEqual(report['checks']['timing_policy']['status'], 'UNKNOWN')
        self.assertNotEqual(report['status'], 'WARN')
        self.assertNotEqual(report['groups'][0]['timing']['status'], 'WARN')
        self.assertEqual(report['groups'][0]['ranges_seconds'], [])
        legacy = self.lint(text, policy='auto')
        self.assertEqual(legacy['groups'][0]['timing']['status'], 'WARN')

    def test_absolute_overlapping_intervals_still_warn_in_forbid(self):
        report = self.lint('3–5 seconds: The door opens.\n2–4 seconds: She turns.')
        self.assertEqual(report['groups'][0]['timing']['status'], 'WARN')
        self.assertEqual(report['groups'][0]['ranges_seconds'], [[3.0, 5.0], [2.0, 4.0]])

    def test_runner_checks_only_explicit_event_driven_cases(self):
        for mode, expected in ((None, 'UNKNOWN'), ('event_driven', 'WARN'),
                               ('timecoded', 'UNKNOWN'), ('local_anchor', 'UNKNOWN')):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                write_minimal_suite(root)
                path = root / 'execution_cases.json'
                data = json.loads(path.read_text(encoding='utf-8'))
                if mode is not None:
                    data['cases'][0]['timing_mode'] = mode
                path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
                prompts = root / 'prompts'
                prompts.mkdir()
                (prompts / 'T01.md').write_text('```text\nShot 01 (0–3 s): A walks.\n```', encoding='utf-8')
                process, report = run_runner(root, prompts=prompts)
                self.assertEqual(process.returncode, 0, process.stderr)
                result = next(item for item in report['results'] if item['test_case'] == 'T01')
                self.assertEqual(result['status'], expected)

    def test_invalid_timing_mode_fails_structure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_minimal_suite(root)
            path = root / 'execution_cases.json'
            data = json.loads(path.read_text(encoding='utf-8'))
            data['cases'][0]['timing_mode'] = 'unknown_policy'
            path.write_text(json.dumps(data), encoding='utf-8')
            process, report = run_runner(root)
            self.assertEqual(process.returncode, 2)
            self.assertTrue(any('timing_mode' in finding for finding in report['suite']['findings']))




class CopyBlockPurityTests(unittest.TestCase):
    def test_leaked_sd25_and_form_headers_and_self_explain_are_warned(self):
        from block_lint import copy_block_purity_findings, inspect
        sample = """```text
入段转场｜前段→本段
分镜01：按 SD25-03 规则，本片以无时间码分镜推进，主角拔刀。
```"""
        findings = copy_block_purity_findings(sample)
        self.assertEqual(len(findings), 3)
        report = inspect(sample)
        self.assertEqual(report['checks']['duplicated_or_internal_text']['status'], 'WARN')
        self.assertEqual(report['status'], 'WARN')

    def test_outside_sd25_notes_do_not_trigger_copy_block_purity_warn(self):
        from block_lint import copy_block_purity_findings
        sample = """块外说明：已按 SD25-03 与无时间码事件序核对。
```text
分镜01：主角在画面左侧拔刀迎敌。
```"""
        self.assertEqual(copy_block_purity_findings(sample), [])


if __name__ == '__main__':
    unittest.main()
