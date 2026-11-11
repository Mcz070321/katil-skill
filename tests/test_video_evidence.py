"""Negative evidence checks and external-review import tests, using synthetic fixtures."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from test_run_regression import ROOT, generation_response, run_runner, write_evidence, write_minimal_suite

SPEC = importlib.util.spec_from_file_location('video_evidence', ROOT / 'scripts/video_evidence.py')
MEDIA = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MEDIA)


class VideoEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        write_minimal_suite(self.root)

    def evaluate(self, response):
        responses = self.root / 'responses.json'
        responses.write_text(json.dumps({'G01': response}), encoding='utf-8')
        proc, report = run_runner(self.root, responses=responses)
        return proc, next(item for item in report['results'] if item['test_case'] == 'G01')

    def valid(self):
        evidence = write_evidence(self.root)
        return evidence, generation_response(evidence)

    def change_review(self, response, mutate):
        path = Path(response['review_file'])
        data = json.loads(path.read_text())
        mutate(data)
        path.write_text(json.dumps(data), encoding='utf-8')

    def test_text_named_mp4_repeated_across_versions_is_rejected(self):
        fake = self.root / 'fake.mp4'
        fake.write_text('NOT A VIDEO')
        evidence = {v: [str(fake)] * 3 for v in ('3.6.1', '3.6.2')}
        proc, item = self.evaluate(generation_response(evidence))
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(item['evidence_status'], 'FAIL')

    def test_different_fake_video_files_are_rejected(self):
        evidence = {}
        for v in ('3.6.1', '3.6.2'):
            evidence[v] = []
            for index in range(3):
                p = self.root / ('%s_%d.mp4' % (v, index))
                p.write_text('NOT A VIDEO %s %d' % (v, index))
                evidence[v].append(str(p))
        _, item = self.evaluate(generation_response(evidence))
        self.assertEqual(item['status'], 'FAIL')

    def test_nonfatal_ffprobe_stderr_does_not_reject_valid_video(self):
        path = self.root / 'valid.mp4'
        path.write_bytes(b'probe is mocked; bytes are not decoded here')
        stdout = json.dumps({
            'streams': [{'codec_name': 'h264', 'width': 16, 'height': 16,
                         'nb_read_frames': '2', 'duration': '0.5',
                         'disposition': {'attached_pic': 0}}],
            'format': {'duration': '0.5', 'format_name': 'mov,mp4,m4a,3gp,3g2,mj2'},
        })
        completed = subprocess.CompletedProcess(
            ['ffprobe'], 0, stdout=stdout,
            stderr='[mov,mp4] non-fatal probe warning retained for review')
        with patch.object(MEDIA.shutil, 'which', return_value='ffprobe'), \
                patch.object(MEDIA.subprocess, 'run', return_value=completed):
            status, metadata, explanation = MEDIA.inspect_video(path)
        self.assertEqual(status, 'PASS')
        self.assertEqual(metadata['decoded_frames'], 2)
        self.assertIn('probe_warnings', metadata)
        self.assertIn('非致命', explanation)

    def test_same_path_and_relative_alias_within_version_are_rejected(self):
        evidence, response = self.valid()
        evidence['3.6.1'][1] = 'videos/../videos/' + Path(evidence['3.6.1'][0]).name
        _, item = self.evaluate(response)
        self.assertEqual(item['evidence_status'], 'FAIL')
        self.assertTrue(any('重复证据' in n for n in item['notes']))

    def test_same_video_across_versions_is_rejected(self):
        evidence, response = self.valid()
        evidence['3.6.2'][0] = evidence['3.6.1'][0]
        _, item = self.evaluate(response)
        self.assertEqual(item['evidence_status'], 'FAIL')

    def test_copied_bytes_under_different_names_are_rejected(self):
        evidence, response = self.valid()
        shutil.copyfile(evidence['3.6.1'][0], evidence['3.6.2'][0])
        _, item = self.evaluate(response)
        self.assertEqual(item['evidence_status'], 'FAIL')
        self.assertTrue(any('SHA-256' in n for n in item['notes']))

    def test_symlink_alias_is_rejected(self):
        evidence, response = self.valid()
        alias = self.root / 'alias.mp4'
        try:
            alias.symlink_to(evidence['3.6.1'][0])
        except OSError:
            self.skipTest('symlinks unsupported')
        evidence['3.6.2'][0] = str(alias)
        _, item = self.evaluate(response)
        self.assertEqual(item['evidence_status'], 'FAIL')

    def test_media_tools_missing_remains_unverified(self):
        with patch.object(MEDIA.shutil, 'which', return_value=None):
            status, _, _ = MEDIA.inspect_video(self.root / 'not-read.mp4')
        self.assertEqual(status, 'PENDING_VIDEO')

    def test_probe_timeout_remains_unverified(self):
        with patch.object(MEDIA.shutil, 'which', return_value='ffprobe'), patch.object(
                MEDIA.subprocess, 'run', side_effect=subprocess.TimeoutExpired('ffprobe', 30)):
            status, _, _ = MEDIA.inspect_video(self.root / 'clip.mp4')
        self.assertEqual(status, 'PENDING_VIDEO')

    def test_audio_only_and_single_frame_are_not_video_evidence(self):
        if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):
            self.skipTest('media tools unavailable')
        audio = self.root / 'audio.mp4'
        still = self.root / 'still.mp4'
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                        'anullsrc=r=8000:cl=mono', '-t', '0.5', '-c:a', 'aac', str(audio)], check=True)
        subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i',
                        'color=s=16x16:r=4', '-frames:v', '1', '-c:v', 'mpeg4',
                        '-threads', '1', str(still)], check=True)
        for path in (audio, still):
            with self.subTest(path=path.name):
                self.assertEqual(MEDIA.inspect_video(path)[0], 'FAIL')

    def test_reviewed_boolean_without_review_file_cannot_pass(self):
        _, response = self.valid()
        response.pop('review_file')
        _, item = self.evaluate(response)
        self.assertEqual(item['evidence_status'], 'PASS')
        self.assertEqual(item['status'], 'PENDING_VIDEO')

    def test_review_hash_mismatch_is_rejected(self):
        _, response = self.valid()
        self.change_review(response, lambda data: data['clips'][0].update(sha256='0' * 64))
        _, item = self.evaluate(response)
        self.assertEqual(item['evidence_status'], 'PASS')
        self.assertEqual(item['review_status'], 'FAIL')
        self.assertFalse(item['review_record_valid'])

    def test_missing_or_duplicate_review_items_are_rejected(self):
        for mode in ('missing', 'duplicate'):
            with self.subTest(mode=mode):
                _, response = self.valid()
                def mutate(data):
                    if mode == 'missing':
                        data['clips'].pop()
                    else:
                        data['clips'][1] = data['clips'][0]
                self.change_review(response, mutate)
                _, item = self.evaluate(response)
                self.assertEqual(item['review_status'], 'FAIL')

    def test_wrong_case_and_malformed_review_are_rejected(self):
        for mode in ('wrong_case', 'not_json', 'list'):
            with self.subTest(mode=mode):
                _, response = self.valid()
                path = Path(response['review_file'])
                if mode == 'wrong_case':
                    self.change_review(response, lambda data: data.update(case_id='G99'))
                else:
                    path.write_text('NOT JSON' if mode == 'not_json' else '[]')
                _, item = self.evaluate(response)
                self.assertEqual(item['review_status'], 'FAIL')

    def test_frame_only_review_remains_pending(self):
        _, response = self.valid()
        self.change_review(response, lambda data: data['clips'][0].update(viewing='frames'))
        _, item = self.evaluate(response)
        self.assertEqual(item['evidence_status'], 'PASS')
        self.assertEqual(item['review_status'], 'PENDING_VIDEO')

    def test_external_failure_is_not_overridden_by_response_pass(self):
        _, response = self.valid()
        self.change_review(response, lambda data: data['clips'][0].update(verdict='FAIL'))
        proc, item = self.evaluate(response)
        self.assertEqual(proc.returncode, 1)
        self.assertEqual(item['review_status'], 'FAIL')
        self.assertTrue(item['review_record_valid'])

    def test_invalid_observation_time_is_rejected(self):
        _, response = self.valid()
        self.change_review(response, lambda data: data['clips'][0]['observations'][0].update(time_seconds=999))
        _, item = self.evaluate(response)
        self.assertEqual(item['review_status'], 'FAIL')

    def test_valid_review_import_explicitly_is_not_quality_authentication(self):
        _, response = self.valid()
        _, item = self.evaluate(response)
        self.assertEqual(item['status'], 'PASS')
        self.assertEqual(len(item['evidence_records']), 6)
        self.assertEqual(item['quality_verdict_source'], 'external_review_record_unverified_identity')
        self.assertTrue(any('未认证' in n for n in item['notes']))
        self.assertEqual(item['review_mode'], 'open')
        self.assertEqual(item['independence'], 'shared')
        self.assertFalse(item['ev3_supported'])

    def test_blind_review_requires_protocol_sample_and_independence(self):
        cases = {
            'missing_protocol': {'review_mode': 'blind', 'independence': 'independent', 'sample_size': 3},
            'small_sample': {'review_mode': 'blind', 'independence': 'independent', 'blind_protocol': '随机盲测', 'sample_size': 1},
            'below_runs_min': {'review_mode': 'blind', 'independence': 'independent', 'blind_protocol': '随机盲测', 'sample_size': 2},
            'shared_reviewer': {'review_mode': 'blind', 'independence': 'shared', 'blind_protocol': '随机盲测', 'sample_size': 3},
        }
        for mode, fields in cases.items():
            with self.subTest(mode=mode):
                _, response = self.valid()
                self.change_review(response, lambda data: data.update(fields))
                _, item = self.evaluate(response)
                self.assertEqual(item['review_status'], 'FAIL')
                self.assertFalse(item['review_record_valid'])
                self.assertFalse(item['ev3_supported'])

    def test_valid_blind_review_records_ev3_support_but_not_authentication(self):
        _, response = self.valid()
        self.change_review(response, lambda data: data.update(
            review_mode='blind', independence='independent',
            blind_protocol='评审者未见版本标签，按随机顺序逐条观看全片',
            sample_size=3))
        _, item = self.evaluate(response)
        self.assertEqual(item['status'], 'PASS')
        self.assertEqual(item['review_mode'], 'blind')
        self.assertEqual(item['independence'], 'independent')
        self.assertEqual(item['sample_size'], 3)
        self.assertTrue(item['ev3_supported'])
        self.assertTrue(any('EV3' in n for n in item['notes']))
        self.assertTrue(any('未认证' in n for n in item['notes']))

    def test_required_criteria_are_checked_for_each_full_clip(self):
        path = self.root / 'generation_cases.json'
        suite = json.loads(path.read_text(encoding='utf-8'))
        suite['cases'][0]['review_criteria'] = {
            'right_arm_and_blade': '右臂带刀离体',
            'head_separation': '头身分离',
        }
        path.write_text(json.dumps(suite), encoding='utf-8')
        _, response = self.valid()

        def set_review(data, mode):
            data.update(review_mode='blind', independence='independent',
                        blind_protocol='synthetic fixture', sample_size=3)
            for clip in data['clips']:
                clip['viewing'] = 'full_video'
                clip['observations'] = [
                    {'criterion': key, 'time_seconds': 0.0, 'observation': 'synthetic test'}
                    for key in ('right_arm_and_blade', 'head_separation')
                ]
            if mode != 'complete':
                data['clips'][0]['observations'][1]['criterion'] = 'lighting'
            if mode == 'partial':
                data['clips'][0]['viewing'] = 'frames'

        for mode, expected in [('missing', 'FAIL'), ('complete', 'PASS'), ('partial', 'PENDING_VIDEO')]:
            with self.subTest(mode=mode):
                self.change_review(response, lambda data: set_review(data, mode))
                _, item = self.evaluate(response)
                self.assertEqual(item['evidence_status'], 'PASS')
                self.assertEqual(item['review_status'], expected)
                self.assertIs(item['ev3_supported'], mode == 'complete')

    def test_blind_frame_only_review_is_not_ev3(self):
        _, response = self.valid()
        self.change_review(response, lambda data: data.update(
            review_mode='blind', independence='independent',
            blind_protocol='随机盲测', sample_size=3))
        self.change_review(response, lambda data: data['clips'][0].update(viewing='frames'))
        _, item = self.evaluate(response)
        self.assertEqual(item['review_status'], 'PENDING_VIDEO')
        self.assertFalse(item['ev3_supported'])


if __name__ == '__main__':
    unittest.main()
