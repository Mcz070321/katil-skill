import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts' / 'run_regression.py'
MEDIA_CACHE = tempfile.TemporaryDirectory(prefix='katil-unit-media-')


def run_runner(cases, responses=None, prompts=None):
    args = [sys.executable, '-B', str(SCRIPT), '--cases', str(cases)]
    if responses is not None:
        args += ['--responses', str(responses)]
    if prompts is not None:
        args += ['--prompts', str(prompts)]
    proc = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
    return proc, json.loads(proc.stdout)


def write_minimal_suite(root):
    routing = []
    for i in range(1, 21):
        case = {
            'id': i,
            'request': '用例 %d' % i,
            'expected_load': '通用创作核心',
            'prohibited_or_caution': '无',
        }
        if i >= 13:
            case['concept_mode'] = ['约束型', '约束型', '极简型', '作者型', '约束型', '约束型', '极简型', '作者型'][i - 13]
        routing.append(case)
    (root / 'routing_cases.json').write_text(json.dumps({'cases': routing}, ensure_ascii=False), encoding='utf-8')
    (root / 'execution_cases.json').write_text(json.dumps({'cases': [
        {'id': 'T01', 'request': '双人攻防', 'criteria': ['接触可见']}
    ]}, ensure_ascii=False), encoding='utf-8')
    (root / 'continuity_cases.json').write_text(json.dumps({'cases': [
        {'id': 'C01', 'initial': '左手灯', 'next': '放灯', 'expected': '灯位连续'}
    ]}, ensure_ascii=False), encoding='utf-8')
    (root / 'style_cases.json').write_text(json.dumps({'cases': [
        {'id': 'S01', 'request': '彩色水墨', 'expected': '笔触可辨'}
    ]}, ensure_ascii=False), encoding='utf-8')
    audio = []
    for i, decision in enumerate(['music_led', 'sound_design_led', 'music_led', 'information_led'], 1):
        audio.append({'id': 'A%02d' % i, 'request': '声音 %d' % i, 'expected_decision': decision,
                      'required_behavior': ['按目的判断'], 'forbidden_behavior': ['统一无BGM']})
    (root / 'audio_cases.json').write_text(json.dumps({'cases': audio}, ensure_ascii=False), encoding='utf-8')
    generation = []
    for i in range(1, 4):
        generation.append({'id': 'G%02d' % i, 'request': '生成 %d' % i, 'focus': ['关键接触'],
                           'comparison': 'V3.6.1 vs V3.6.2', 'runs_min': 3, 'evidence_required': True})
    (root / 'generation_cases.json').write_text(json.dumps({'cases': generation}, ensure_ascii=False), encoding='utf-8')
    adaptation = [{'id': 'M%02d' % i, 'request': '中文提示词', 'context': '独立新任务', 'material_conditions': '无素材'} for i in range(1,37)]
    (root / 'model_adaptation_cases.json').write_text(json.dumps({'cases': adaptation}, ensure_ascii=False), encoding='utf-8')
    fx = []
    for i in range(1, 22):
        cid = 'FXT%02d' % i
        extra_primary = {16: 'FX10', 17: 'FX05', 18: 'FX07', 19: 'FX11', 20: 'FX14', 21: 'FX04'}
        primary = 'NONE' if i == 10 else ('FX%02d' % i if i <= 15 else extra_primary[i])
        secondary = ['FX10'] if i == 1 else []
        fx.append({'id': cid, 'request': '特效设计 %d' % i, 'primary_fx': primary,
                   'secondary_fx': secondary, 'layers': [['Primary','Secondary','Impact','Environment','Optical','Audio'][(i - 1) % 6]],
                   'criteria': ['来源与结果可读'], 'must_hold': ['效果有可见来源'],
                   'must_reject': ['效果凭空出现'], 'evidence_boundary': 'PENDING_VIDEO'})
    (root / 'fx_cases.json').write_text(json.dumps({'cases': fx}, ensure_ascii=False), encoding='utf-8')


def write_evidence(root, versions=('3.6.1', '3.6.2'), count=3):
    # Synthetic two-frame media fixtures only; never generation or artistic evidence.
    if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
        raise unittest.SkipTest('media integration fixtures require ffmpeg and ffprobe')
    videos = root / 'videos'
    videos.mkdir(exist_ok=True)
    evidence = {}
    for version in versions:
        paths = []
        for index in range(count):
            path = videos / ('%s_%d.mp4' % (version.replace('.', '_'), index))
            cached = Path(MEDIA_CACHE.name) / path.name
            if not cached.exists():
                color = sum(ord(c) for c in version) * 100 + index * 1234
                subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                                'color=c=0x%06x:s=16x16:r=4' % color,
                                '-frames:v', '2', '-c:v', 'mpeg4', '-threads', '1',
                                '-metadata', 'comment=synthetic-unit-%s-%d' % (version, index),
                                str(cached)], check=True, capture_output=True)
            shutil.copyfile(cached, path)
            paths.append(str(path))
        evidence[version] = paths
    return evidence


def generation_response(evidence, reviewed=True, **overrides):
    data = {
        'video': 'PASS',
        'reviewed': reviewed,
        'model': 'test-model',
        'model_version': 'v1',
        'parameters': '10s; 16:9; 24fps; seed=1',
        'runs': {'3.6.1': 3, '3.6.2': 3},
        'evidence': evidence,
    }
    data.update(overrides)
    if reviewed and isinstance(evidence, dict) and evidence:
        first = next(iter(evidence.values()))[0]
        review = {
            'case_id': 'G01',
            'reviewer': {'id': 'synthetic-unit-fixture', 'kind': 'model'},
            'reviewed_at': '2026-11-05T08:00:00+08:00',
            'clips': [
                {'version': version, 'index': i + 1,
                 'sha256': hashlib.sha256(Path(path).read_bytes()).hexdigest() if Path(path).is_file() else 'missing',
                 'viewing': 'full_video', 'verdict': 'PASS',
                 'observations': [{'criterion': 'fixture-only', 'time_seconds': 0.0,
                                   'observation': 'Synthetic test record, not an actual quality review.'}]}
                for version, paths in evidence.items() for i, path in enumerate(paths)
            ],
        }
        review_path = Path(first).parent / 'review.json'
        review_path.write_text(json.dumps(review), encoding='utf-8')
        data['review_file'] = str(review_path)
    return data


class RunnerTests(unittest.TestCase):
    def test_real_suite_is_structural_pass_but_unknown(self):
        proc, report = run_runner(ROOT / 'tests')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(report['suite']['status'], 'PASS')
        self.assertEqual(len(report['results']), 162)
        self.assertEqual(report['summary']['UNKNOWN'], 151)
        self.assertEqual(report['summary']['PENDING_VIDEO'], 11)
        self.assertEqual(report['summary']['PASS'], 0)
        for row in report['results']:
            expected = 'PENDING_VIDEO' if row['test_case'].startswith('G') else 'UNKNOWN'
            self.assertEqual(row['status'], expected, row['test_case'])

    def test_minimal_suite_is_valid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            proc, report = run_runner(root)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(report['suite']['status'], 'PASS')

    def test_new_comparison_versions_require_matching_evidence_groups(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            data = json.loads((root / 'generation_cases.json').read_text(encoding='utf-8'))
            data['cases'][0]['comparison'] = 'V3.6.2 vs V3.6.3'
            (root / 'generation_cases.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            responses = root / 'responses.json'
            old_evidence = write_evidence(root)
            responses.write_text(json.dumps({'G01': generation_response(old_evidence)}), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(report['suite']['status'], 'PASS')
            self.assertEqual(proc.returncode, 1)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertTrue(any('缺少 3.6.3 版视频证据' in n for n in g01['notes']))
            evidence = write_evidence(root, versions=('3.6.2', '3.6.3'))
            responses.write_text(json.dumps({'G01': generation_response(
                evidence, runs={'3.6.2': 3, '3.6.3': 3})}), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertEqual(next(x for x in report['results'] if x['test_case'] == 'G01')['status'], 'PASS')

    def test_comparison_requires_exactly_two_distinct_versions(self):
        for comparison in ('V3.6.3 vs V3.6.3', 'V3.6.1 vs V3.6.2 vs V3.6.3'):
            with self.subTest(comparison=comparison), tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_minimal_suite(root)
                data = json.loads((root / 'generation_cases.json').read_text(encoding='utf-8'))
                data['cases'][0]['comparison'] = comparison
                (root / 'generation_cases.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
                proc, report = run_runner(root)
                self.assertEqual(proc.returncode, 2)
                self.assertTrue(any('两个不同' in x for x in report['suite']['findings']))

    def test_duplicate_id_fails_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            data = json.loads((root / 'routing_cases.json').read_text(encoding='utf-8'))
            data['cases'][1]['id'] = 1
            (root / 'routing_cases.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(report['suite']['status'], 'FAIL')
            self.assertTrue(any('重复 id' in x for x in report['suite']['findings']))

    def test_audio_mismatch_is_a_result_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'A01': {'audio_decision': 'sound_design_led'}}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 1)
            a01 = next(x for x in report['results'] if x['test_case'] == 'A01')
            self.assertEqual(a01['status'], 'FAIL')

    def test_generation_pass_requires_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'G01': {'video': 'PASS'}}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 1)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertEqual(g01['status'], 'FAIL')
            self.assertTrue(any('证据' in n for n in g01['notes']))

    def test_generation_single_path_cannot_prove_ab(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            evidence = write_evidence(root, versions=('3.6.2',))
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'G01': generation_response(evidence['3.6.2'] * 2)}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 1)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertEqual(g01['status'], 'FAIL')
            self.assertTrue(any('单一路径' in n for n in g01['notes']))

    def test_generation_missing_file_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            evidence = write_evidence(root)
            evidence['3.6.1'][0] = str(root / 'not-there.mp4')
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'G01': generation_response(evidence)}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 1)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertEqual(g01['status'], 'FAIL')
            self.assertTrue(any('不存在' in n for n in g01['notes']))

    def test_generation_unreviewed_existing_files_is_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            evidence = write_evidence(root)
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'G01': generation_response(evidence, reviewed=False)}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertEqual(g01['status'], 'PENDING_VIDEO')
            self.assertTrue(any('review_file' in n for n in g01['notes']))
            self.assertEqual(g01['evidence_status'], 'PASS')

    def test_generation_reviewed_full_evidence_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            evidence = write_evidence(root)
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'G01': generation_response(evidence)}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertEqual(g01['status'], 'PASS')
            self.assertEqual(g01['evidence_status'], 'PASS')
            self.assertEqual(g01['review_status'], 'PASS')
            self.assertTrue(any('导入外部评审' in n for n in g01['notes']))

    def test_generation_missing_baseline_version_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            evidence = write_evidence(root, versions=('3.6.2',))
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'G01': generation_response(
                evidence, runs={'3.6.2': 3})}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 1)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertEqual(g01['status'], 'FAIL')
            self.assertTrue(any('缺少 3.6.1 版视频证据' in n for n in g01['notes']))

    def test_generation_too_few_runs_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            evidence = write_evidence(root, count=2)
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'G01': generation_response(
                evidence, runs={'3.6.1': 2, '3.6.2': 2})}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 1)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertEqual(g01['status'], 'FAIL')
            self.assertTrue(any('生成次数不足' in n for n in g01['notes']))

    def test_generation_missing_model_record_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            evidence = write_evidence(root)
            response = generation_response(evidence)
            del response['model_version']
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'G01': response}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 1)
            g01 = next(x for x in report['results'] if x['test_case'] == 'G01')
            self.assertEqual(g01['status'], 'FAIL')
            self.assertTrue(any('缺少模型版本记录' in n for n in g01['notes']))

    def test_invalid_response_value_fails_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'R01': {'routing': 'MAYBE'}}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 2)
            self.assertTrue(any('值非法' in x for x in report['suite']['findings']))

    def test_unknown_response_key_fails_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            responses = root / 'responses.json'
            responses.write_text(json.dumps({'ZZZ': {}}, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root, responses=responses)
            self.assertEqual(proc.returncode, 2)
            self.assertTrue(any('未知用例' in x for x in report['suite']['findings']))

    def test_missing_field_fails_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            data = json.loads((root / 'style_cases.json').read_text(encoding='utf-8'))
            del data['cases'][0]['expected']
            (root / 'style_cases.json').write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root)
            self.assertEqual(proc.returncode, 2)
            self.assertTrue(any('expected' in x for x in report['suite']['findings']))

    def test_prompt_conditional_reference_is_warned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            prompts = root / 'prompts'
            prompts.mkdir()
            (prompts / 'R01.txt').write_text('0—1秒：甲走。\n如有参考图，只提取指定造型。', encoding='utf-8')
            proc, report = run_runner(root, prompts=prompts)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            r01 = next(x for x in report['results'] if x['test_case'] == 'R01')
            self.assertEqual(r01['status'], 'WARN')
            self.assertTrue(any('如有参考图' in n for n in r01['notes']))

    def test_empty_prompt_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            prompts = root / 'prompts'
            prompts.mkdir()
            (prompts / 'R02.txt').write_text('   ', encoding='utf-8')
            proc, report = run_runner(root, prompts=prompts)
            self.assertEqual(proc.returncode, 1)
            r02 = next(x for x in report['results'] if x['test_case'] == 'R02')
            self.assertEqual(r02['status'], 'FAIL')




# --- test_review_status.py ---
import unittest,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from run_regression import build_results
class ReviewStatusTests(unittest.TestCase):
 def result(self,review,decision='music_led'):
  case={'id':'A01','expected_decision':'music_led'};errors=[]
  result=build_results([('audio',case)],{'A01':{'audio_decision':decision,'text_review_status':review}},None,Path.cwd(),errors)
  return result[0],errors
 def test_warn_not_erased(self):self.assertEqual(self.result('WARN')[0]['status'],'WARN')
 def test_fail_not_erased(self):self.assertEqual(self.result('FAIL')[0]['status'],'FAIL')
 def test_unknown_not_pass(self):self.assertEqual(self.result('UNKNOWN')[0]['status'],'UNKNOWN')
 def test_wrong_enum_cannot_pass(self):self.assertEqual(self.result('PASS','sound_design_led')[0]['status'],'FAIL')
 def test_invalid_review(self):self.assertTrue(self.result('EXCELLENT')[1])


# --- test_local_repairs.py ---
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from run_regression import build_results


class LocalRepairTests(unittest.TestCase):
    def test_registry_runs_under_non_utf8_default(self):
        env = dict(os.environ, PYTHONUTF8='0', PYTHONIOENCODING='utf-8')
        result = subprocess.run([sys.executable, '-B', str(ROOT / 'scripts/rule_registry_check.py')],
                                cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_prompt_warning_is_not_erased_by_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, 'R01.txt').write_text('如有参考图', encoding='utf-8')
            rows = build_results([('routing', {'id': 1})], {'R01': {'routing': 'PASS'}},
                                 Path(temp), Path(temp), [])
            self.assertEqual(rows[0]['status'], 'WARN')

    def test_prompt_warning_does_not_erase_pending_video(self):
        with tempfile.TemporaryDirectory() as temp:
            Path(temp, 'G01.txt').write_text('如有参考图', encoding='utf-8')
            case = {'id': 'G01', 'comparison': '3.6.2 vs 3.7.0', 'runs_min': 2}
            rows = build_results([('generation', case)], {}, Path(temp), Path(temp), [])
            self.assertEqual(rows[0]['status'], 'PENDING_VIDEO')
            self.assertTrue(rows[0]['notes'])


# --- test_rule_registry.py ---
import unittest,tempfile,shutil,sys,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from rule_registry_check import check
REF_MARKER=next(r["summary_refs"][0]["marker"] for r in json.loads((ROOT/"rules/rule-registry.yaml").read_text(encoding="utf-8"))["rules"] if r["rule_id"]=="REF")
REF_START="<!-- "+REF_MARKER+" -->"
class RegistryTests(unittest.TestCase):
 def test_valid(self): self.assertEqual(check(ROOT),[])
 def mutate(self,fn,code):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)/'core';shutil.copytree(ROOT,r,ignore=shutil.ignore_patterns('__pycache__'))
   p=r/'rules/rule-registry.yaml';data=json.loads(p.read_text(encoding='utf-8'));fn(data);p.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8');self.assertIn(code,[e['code'] for e in check(r)])
 def test_duplicate(self):self.mutate(lambda d:d['rules'].append(d['rules'][0]),'DUPLICATE_ID')
 def test_anchor(self):self.mutate(lambda d:d['rules'][0]['authority'].update(anchor='missing'),'ANCHOR_MISSING')
 def test_digest(self):self.mutate(lambda d:d['rules'][0].update(authority_sha256='0'*64),'AUTHORITY_DIGEST_MISMATCH')
 def test_revision(self):self.mutate(lambda d:d['rules'][0].update(rule_revision='9.0.0'),'SUMMARY_REVISION_MISMATCH')
 def test_cycle(self):
  def change(d): d['rules'][0]['depends_on']=['SOUND'];d['rules'][1]['depends_on']=['REF']
  self.mutate(change,'RULE_CYCLE')
 def test_escape(self):self.mutate(lambda d:d['rules'][0]['authority'].update(path='../escape.md'),'RULE_INVALID')
 def test_empty_summary_refs(self):self.mutate(lambda d:d['rules'][0].update(summary_refs=[]),'SUMMARY_REFS_EMPTY')
 def test_missing_summary_digest(self):self.mutate(lambda d:d['rules'][0]['summary_refs'][0].pop('summary_sha256',None),'SUMMARY_DIGEST_INVALID')
 def edit_summary(self,fn,code):
  with tempfile.TemporaryDirectory() as d:
   r=Path(d)/'core';shutil.copytree(ROOT,r,ignore=shutil.ignore_patterns('__pycache__'))
   p=r/'SKILL.md';p.write_text(fn(p.read_text(encoding='utf-8')),encoding='utf-8')
   self.assertIn(code,[e['code'] for e in check(r)])
 def test_empty_summary_body(self):
  self.edit_summary(lambda t:re.sub('('+re.escape(REF_START)+r'\n)[^\n]+',r'\1',t),'SUMMARY_EMPTY')
 def test_tampered_summary_body(self):
  self.edit_summary(lambda t:re.sub('('+re.escape(REF_START)+r'\n[^\n]+)',r'\1 tampered',t),'SUMMARY_DIGEST_MISMATCH')
 def test_duplicate_summary_marker(self):
  self.edit_summary(lambda t:t+'\n'+REF_START+'\n','SUMMARY_BLOCK_INVALID')


# --- test_model_adaptation_regression.py ---
"""Adaptation text review must not imply submission readiness or video quality."""
import json
from pathlib import Path
import tempfile
import unittest
from test_run_regression import run_runner, write_minimal_suite

ROOT=Path(__file__).resolve().parents[1]

def add_adaptation(root):
    data={'cases':[{'id':f'M{i:02}','request':'写一份中文提示词','context':'独立新作品','material_conditions':'无参考素材'} for i in range(1,37)]}
    path=root/'model_adaptation_cases.json'
    path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
    return path,data

class AdaptationRegressionTests(unittest.TestCase):
    def test_real_suite_has_151_unknown_tasks(self):
        proc,report=run_runner(ROOT/'tests')
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(len(report['results']),162)
        self.assertEqual(report['suite']['counts']['execution'],62)
        self.assertEqual(report['suite']['counts']['adaptation'],36)
        self.assertEqual(report['suite']['counts']['generation'],11)
        self.assertEqual(report['suite']['counts']['fx'],21)
        self.assertEqual(report['summary']['UNKNOWN'],151)
        self.assertEqual(report['summary']['PENDING_VIDEO'],11)

    def structured_case(self,case):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);write_minimal_suite(root)
            path=root/'execution_cases.json'
            data=json.loads(path.read_text(encoding='utf-8'))
            data['cases'].append(case)
            path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            proc,report=run_runner(root)
            self.assertEqual(proc.returncode,2,proc.stderr)
            self.assertEqual(report['suite']['status'],'FAIL')
            return report['suite']['findings']

    def test_structured_case_requires_both_assertion_fields(self):
        findings=self.structured_case({'id':'T34','request':'一次带墨色剑气的斩击','criteria':['源头、路径与兑现可见'],'must_hold':['剑气从刀锋离体并落到目标']})
        self.assertTrue(any('T34' in finding and 'must_reject' in finding for finding in findings),findings)

    def test_structured_case_rejects_duplicate_assertions(self):
        findings=self.structured_case({'id':'T34','request':'一次带墨色剑气的斩击','criteria':['源头、路径与兑现可见'],'must_hold':['剑气从刀锋离体','剑气从刀锋离体'],'must_reject':['剑气凭空出现在目标体内']})
        self.assertTrue(any('T34' in finding and '含重复断言' in finding for finding in findings),findings)

    def test_structured_case_rejects_contradictory_assertions(self):
        findings=self.structured_case({'id':'T34','request':'一次带墨色剑气的斩击','criteria':['源头、路径与兑现可见'],'must_hold':['剑气从刀锋离体并落到目标'],'must_reject':['剑气从刀锋离体并落到目标']})
        self.assertTrue(any('T34' in finding and '互相矛盾' in finding for finding in findings),findings)

    def invalid_case(self,mutate):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);write_minimal_suite(root);path,data=add_adaptation(root)
            mutate(data);path.write_text(json.dumps(data,ensure_ascii=False),encoding='utf-8')
            proc,report=run_runner(root)
            self.assertEqual(proc.returncode,2)
            self.assertEqual(report['suite']['status'],'FAIL')

    def test_missing_adaptation_case(self):self.invalid_case(lambda d:d['cases'].pop())
    def test_duplicate_adaptation_id(self):self.invalid_case(lambda d:d['cases'][1].update(id='M01'))
    def test_audio_id_cannot_be_used_for_adaptation(self):self.invalid_case(lambda d:d['cases'][0].update(id='A01'))
    def test_context_is_required(self):self.invalid_case(lambda d:d['cases'][0].update(context=''))

    def response(self,value):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);write_minimal_suite(root);add_adaptation(root)
            response=root/'responses.json';response.write_text(json.dumps({'M01':value}),encoding='utf-8')
            proc,report=run_runner(root,response)
            return proc,report,next((r for r in report['results'] if r['test_case']=='M01'),None)

    def test_text_pass_does_not_pass_submission_or_video(self):
        proc,report,item=self.response({'adaptation':'PASS','text_review_status':'PASS','submission_compatibility':'UNVERIFIED'})
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(item['status'],'PASS')
        self.assertEqual(item['submission_compatibility'],'UNVERIFIED')
        self.assertEqual(item['video'],'PENDING_VIDEO')

    def test_text_failure_is_not_hidden_by_compatibility(self):
        proc,report,item=self.response({'adaptation':'PASS','text_review_status':'FAIL','submission_compatibility':'UNSUPPORTED'})
        self.assertEqual(proc.returncode,1)
        self.assertEqual(item['status'],'FAIL')
        self.assertEqual(item['video'],'PENDING_VIDEO')

    def test_compatible_requires_submission_evidence(self):
        proc,report,item=self.response({'adaptation':'PASS','submission_compatibility':'COMPATIBLE'})
        self.assertEqual(proc.returncode,2)
        self.assertEqual(item['status'],'FAIL')
        self.assertEqual(item['submission_compatibility'],'UNVERIFIED')
        self.assertEqual(item['submission_verdict_source'],'invalid_declaration')
        self.assertTrue(any('submission_evidence' in finding for finding in report['suite']['findings']))

    def test_compatible_evidence_source_wrong_type_returns_structured_error(self):
        for source in (['platform_measured'], {'name':'platform_measured'}, 7, None):
            with self.subTest(source=source):
                try:
                    proc,report,item=self.response({
                        'adaptation':'PASS','submission_compatibility':'COMPATIBLE',
                        'submission_evidence':{'source':source,'reference':'seedance-2.5 / 2026-11-05 / run-42'},
                    })
                except json.JSONDecodeError:
                    self.fail('Runner crashed without structured JSON for source %r' % (source,))
                self.assertEqual(proc.returncode,2)
                self.assertEqual(report['suite']['status'],'FAIL')
                self.assertEqual(item['status'],'FAIL')
                self.assertEqual(item['adaptation'],'FAIL')
                self.assertEqual(item['submission_compatibility'],'UNVERIFIED')
                self.assertEqual(item['submission_verdict_source'],'invalid_declaration')
                self.assertTrue(any('submission_evidence' in finding for finding in report['suite']['findings']))

    def test_compatible_with_platform_evidence_is_recorded(self):
        proc,report,item=self.response({
            'adaptation':'PASS','text_review_status':'PASS','submission_compatibility':'COMPATIBLE',
            'submission_evidence':{'source':'platform_measured','reference':'seedance-2.5 / 2026-11-05 / run-42'},
        })
        self.assertEqual(proc.returncode,0,proc.stderr)
        self.assertEqual(item['status'],'PASS')
        self.assertEqual(item['submission_compatibility'],'COMPATIBLE')
        self.assertEqual(item['submission_evidence_source'],'platform_measured')
        self.assertEqual(item['submission_evidence_reference'],'seedance-2.5 / 2026-11-05 / run-42')
        self.assertEqual(item['submission_verdict_source'],'external_declaration_with_evidence_reference')

    def test_documented_is_not_a_submission_compatibility_value(self):
        proc,report,item=self.response({'adaptation':'PASS','submission_compatibility':'documented'})
        self.assertEqual(proc.returncode,2)
        self.assertEqual(item['submission_compatibility'],'UNVERIFIED')
        self.assertEqual(item['submission_verdict_source'],'invalid_declaration')

    def test_invalid_adaptation_value_fails_the_item(self):
        proc,report,item=self.response({'adaptation':['PASS'],'submission_compatibility':'UNVERIFIED'})
        self.assertEqual(proc.returncode,2)
        self.assertEqual(item['status'],'FAIL')
        self.assertEqual(item['adaptation'],'FAIL')

    def test_invalid_compatibility_is_rejected(self):
        proc,report,item=self.response({'adaptation':'PASS','submission_compatibility':'READY'})
        self.assertEqual(proc.returncode,2)
        self.assertEqual(item['status'],'FAIL')
        self.assertEqual(item['adaptation'],'FAIL')

    def test_adaptation_suite_cannot_import_video_pass(self):
        proc,report,item=self.response({'adaptation':'PASS','video':'PASS'})
        self.assertEqual(proc.returncode,2)
        self.assertIsNotNone(item,'adaptation result must exist')
        self.assertEqual(item['video'],'PENDING_VIDEO')

    def test_malformed_review_fields_return_structured_error(self):
        for field,value in [('adaptation',['PASS']),('submission_compatibility',['COMPATIBLE']),('video',{'verdict':'PASS'})]:
            with self.subTest(field=field):
                try:proc,report,item=self.response({field:value})
                except json.JSONDecodeError:self.fail('Runner crashed without structured JSON')
                self.assertEqual(proc.returncode,2)
                self.assertEqual(report['suite']['status'],'FAIL')


class V375ToolingAndLibraryTests(unittest.TestCase):
    def test_rule_registry_sync_auto_repairs_digests(self):
        from rule_registry_check import check, sync
        with tempfile.TemporaryDirectory() as d:
            r = Path(d) / 'core'
            shutil.copytree(ROOT, r, ignore=shutil.ignore_patterns('__pycache__'))
            reg_path = r / 'rules/rule-registry.yaml'
            data = json.loads(reg_path.read_text(encoding='utf-8'))
            data['rules'][0]['authority_sha256'] = '0' * 64
            data['rules'][0]['summary_refs'][0]['summary_sha256'] = '0' * 64
            reg_path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            self.assertTrue(check(r))
            synced = sync(r)
            self.assertEqual(len(synced), 15)
            self.assertEqual(check(r), [])

    def test_consolidated_ability_and_style_libraries_validate(self):
        import ability_library
        import style_library
        ab_cat, ab_cards = ability_library.load_library()
        ab_res = ability_library.validate(ab_cat, ab_cards)
        self.assertEqual(ab_res['result'], 'PASS')
        self.assertEqual(ab_res['count'], 240)
        st_cat, st_cards = style_library.load_library()
        st_res = style_library.validate(st_cat, st_cards)
        self.assertEqual(st_res['result'], 'PASS')
        self.assertEqual(st_res['count'], 60)

    def test_v380_all_240_cards_and_index_lint_clean(self):
        import ability_library
        import block_lint
        ab_cat, ab_cards = ability_library.load_library()
        self.assertEqual(len(ab_cat['categories']), 24)
        for card in ab_cards:
            txt = "```\n分镜01：" + " ".join([card["mechanism"], card["action"], card["vfx"], card["counter_limit"], card["camera_sound"], card["residue"]]) + "\n```"
            rep = block_lint.inspect(txt, timing_policy="forbid")
            t_findings = [f for f in rep["groups"][0]["timing"]["findings"] if "没有可识别的时间区间" not in f and "未提供目标时长" not in f]
            self.assertEqual(t_findings, [], f"Card {card['id']} triggered timing findings: {t_findings}")
            self.assertEqual(rep["checks"]["timing_policy"]["findings"], [], f"Card {card['id']} triggered timing_policy")
            self.assertEqual(rep["checks"]["duplicated_or_internal_text"]["findings"], [], f"Card {card['id']} triggered purity findings")
        idx_text = (ROOT / "references/ability-library/index.md").read_text(encoding="utf-8")
        self.assertIn("共240种，24类，每类10种；ID为A001—A240", idx_text)
        for i in range(1, 25):
            self.assertIn(f"| C{i:02d} ", idx_text)
            self.assertIn(f"### C{i:02d} ", idx_text)

    def test_v381_a224_name_is_canonical_in_card_and_index(self):
        import ability_library
        _, cards = ability_library.load_library()
        a224 = next(card for card in cards if card['id'] == 'A224')
        self.assertEqual(a224['name'], '走廊重力翻转')
        idx_text = (ROOT / 'references/ability-library/index.md').read_text(encoding='utf-8')
        self.assertIn('A224 走廊重力翻转；', idx_text)


if __name__ == '__main__':
    unittest.main()
