import hashlib
import json
from pathlib import Path
import re
import tempfile
import unittest

from test_run_regression import run_runner, write_minimal_suite

ROOT = Path(__file__).resolve().parents[1]
FX_CLASSES = {'FX%02d' % i for i in range(1, 16)}
FX_LAYERS = {'Primary', 'Secondary', 'Impact', 'Environment', 'Optical', 'Audio'}
FX_DOCS = {
    'FX_DIRECTOR': ('references/fx-director.md', 'katil-fx-director'),
    'FX_PROCEDURAL': ('references/procedural-fx-grammar.md', 'katil-procedural-fx'),
    'FX_ENGINE': ('references/engine-fx-visual-mapping.md', 'katil-engine-fx'),
    'FX_OPTICAL': ('references/optical-and-compositing-grammar.md', 'katil-optical-compositing'),
    'FX_SYNC': ('references/fx-synchronization.md', 'katil-fx-sync'),
}
FX_DEPS = {
    'FX_DIRECTOR': {'TIME', 'WITNESS', 'DELIVERY'},
    'FX_PROCEDURAL': {'FX_DIRECTOR', 'WITNESS', 'CONTINUITY', 'TIME'},
    'FX_ENGINE': {'FX_DIRECTOR', 'ADAPTER', 'SEEDANCE'},
    'FX_OPTICAL': {'FX_DIRECTOR', 'SPACE', 'CONTINUITY'},
    'FX_SYNC': {'FX_DIRECTOR', 'SOUND', 'WITNESS', 'CONTINUITY', 'TIME'},
}


def load_fx_cases():
    return json.loads((ROOT / 'tests' / 'fx_cases.json').read_text(encoding='utf-8'))['cases']


class FxCaseStructureTests(unittest.TestCase):
    def test_fx_cases_cover_ids_classes_and_layers(self):
        cases = load_fx_cases()
        self.assertEqual(len(cases), 21)
        self.assertEqual({case['id'] for case in cases}, {'FXT%02d' % i for i in range(1, 22)})
        seen = set()
        primary_seen = set()
        layers = set()
        for case in cases:
            self.assertEqual(case['evidence_boundary'], 'PENDING_VIDEO')
            self.assertTrue(case['criteria'])
            self.assertTrue(case['must_hold'])
            self.assertTrue(case['must_reject'])
            self.assertFalse(set(case['must_hold']) & set(case['must_reject']))
            self.assertEqual(len(case['must_hold']), len(set(case['must_hold'])))
            self.assertEqual(len(case['must_reject']), len(set(case['must_reject'])))
            if case['primary_fx'] != 'NONE':
                seen.add(case['primary_fx'])
                primary_seen.add(case['primary_fx'])
            seen.update(case['secondary_fx'])
            layers.update(case['layers'])
            self.assertTrue(set(case['layers']) <= FX_LAYERS)
        self.assertEqual(seen, FX_CLASSES)
        self.assertEqual(primary_seen, FX_CLASSES)
        self.assertEqual(layers, FX_LAYERS)

    def test_new_primary_cases_and_reclassified_semantics(self):
        cases = {case['id']: case for case in load_fx_cases()}
        expected = {'FXT07': 'FX08', 'FXT14': 'FX10', 'FXT15': 'FX05',
                    'FXT16': 'FX05', 'FXT17': 'FX07', 'FXT18': 'FX11',
                    'FXT19': 'FX15', 'FXT20': 'FX14', 'FXT21': 'FX04'}
        for cid, primary in expected.items():
            self.assertEqual(cases[cid]['primary_fx'], primary, cid)
        self.assertIn('扫描线', cases['FXT19']['request'])
        self.assertIn('几何', cases['FXT20']['request'])

    def test_secondary_labels_and_no_fx_case_do_not_add_unrequested_effects(self):
        cases = {case['id']: case for case in load_fx_cases()}
        self.assertEqual(cases['FXT02']['secondary_fx'], ['FX04', 'FX09'])
        self.assertEqual(cases['FXT11']['secondary_fx'], ['FX06', 'FX01'])
        self.assertEqual(cases['FXT13']['secondary_fx'], ['FX04'])
        self.assertEqual(cases['FXT15']['secondary_fx'], ['FX03', 'FX06', 'FX07'])
        self.assertEqual(cases['FXT10']['layers'], ['Environment', 'Audio'])

    def test_only_fxt10_is_no_fx(self):
        cases = {case['id']: case for case in load_fx_cases()}
        self.assertEqual(cases['FXT10']['primary_fx'], 'NONE')
        self.assertEqual(cases['FXT10']['secondary_fx'], [])
        for cid, case in cases.items():
            if cid != 'FXT10':
                self.assertNotEqual(case['primary_fx'], 'NONE')

    def test_runner_counts_fx_without_promoting_video(self):
        proc, report = run_runner(ROOT / 'tests')
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(report['suite']['counts']['fx'], 21)
        self.assertEqual(len(report['results']), 162)
        self.assertEqual(report['summary']['UNKNOWN'], 151)
        self.assertEqual(report['summary']['PENDING_VIDEO'], 11)
        fx_results = [item for item in report['results'] if item['category'] == 'fx']
        self.assertEqual(len(fx_results), 21)
        for item in fx_results:
            self.assertEqual(item['status'], 'UNKNOWN')
            self.assertEqual(item['fx_result'], 'UNKNOWN')
            self.assertEqual(item['video'], 'UNKNOWN')


class FxAuthorityTests(unittest.TestCase):
    def test_five_documents_have_anchors_and_authority_scope(self):
        for rule_id, (relative, anchor) in FX_DOCS.items():
            text = (ROOT / relative).read_text(encoding='utf-8')
            self.assertIn('<a id="%s"></a>' % anchor, text)
            self.assertIn('权威范围', text)
            if rule_id != 'FX_DIRECTOR':
                self.assertIn('fx-director.md', text)

    def test_taxonomy_has_all_fifteen_classes_and_six_layers(self):
        text = (ROOT / 'references/fx-director.md').read_text(encoding='utf-8')
        for code in FX_CLASSES:
            self.assertIn('| %s |' % code, text)
        for layer in FX_LAYERS:
            self.assertIn(layer, text)
        self.assertIn('主导', text)
        self.assertIn('辅助', text)

    def test_procedural_lifecycle_is_complete(self):
        text = (ROOT / 'references/procedural-fx-grammar.md').read_text(encoding='utf-8')
        for stage in ('Trigger', 'Spawn', 'Initial State', 'Motion', 'Interaction', 'Event Response', 'Decay', 'Residue'):
            self.assertIn(stage, text)
        self.assertIn('碰撞', text)
        self.assertIn('残留', text)

    def test_engine_mapping_does_not_claim_real_engine_execution(self):
        text = (ROOT / 'references/engine-fx-visual-mapping.md').read_text(encoding='utf-8')
        self.assertIn('Niagara Fluids', text)
        self.assertIn('Chaos', text)
        self.assertIn('Lumen', text)
        self.assertIn('不得声称', text)
        self.assertIn('视觉', text)

    def test_optical_and_sync_documents_cover_required_checks(self):
        optical = (ROOT / 'references/optical-and-compositing-grammar.md').read_text(encoding='utf-8')
        for term in ('Bloom', 'Lens Flare', 'Refraction', 'Chromatic Aberration', 'Exposure', 'Depth of Field', 'Motion Blur'):
            self.assertIn(term, optical)
        self.assertIn('光源', optical)
        self.assertIn('遮挡', optical)
        sync = (ROOT / 'references/fx-synchronization.md').read_text(encoding='utf-8')
        for track in ('Action', 'Primary FX', 'Secondary FX', 'Impact', 'Environment', 'Optical', 'Camera', 'Audio'):
            self.assertIn(track, sync)
        self.assertIn('接触', sync)

    def test_registry_has_five_fx_rules_with_expected_dependencies(self):
        registry = json.loads((ROOT / 'rules/rule-registry.yaml').read_text(encoding='utf-8'))
        rules = {rule['rule_id']: rule for rule in registry['rules']}
        for rule_id, (relative, anchor) in FX_DOCS.items():
            self.assertIn(rule_id, rules)
            rule = rules[rule_id]
            self.assertEqual(rule['rule_revision'], '1.0.0')
            self.assertEqual(rule['authority'], {'path': relative, 'anchor': anchor})
            self.assertEqual(set(rule['depends_on']), FX_DEPS[rule_id])
            self.assertEqual(rule['review_status'], 'reviewed')
            self.assertTrue(rule['summary_refs'])
            self.assertEqual(rule['summary_refs'][0]['marker'], 'SUMMARY of %s@1.0.0' % rule_id)

    def test_skill_routes_and_summaries_are_present(self):
        skill = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        for relative, _ in FX_DOCS.values():
            self.assertIn(relative, skill)
        for rule_id in FX_DOCS:
            self.assertIn('SUMMARY of %s@1.0.0' % rule_id, skill)
        self.assertIn('integration-version: "3.10.5"', skill)
        self.assertIn('FX Director 2.0', skill)

    def test_old_authorities_link_to_new_topics_without_transferring_power(self):
        expectations = {
            'references/effects-and-damage.md': ('fx-director.md', '机制'),
            'references/visual-material-grammar.md': ('fx-director.md', '材质'),
            'references/camera-direction.md': ('optical-and-compositing-grammar.md', '机位'),
            'references/sound-and-rhythm.md': ('fx-synchronization.md', '声音'),
            'references/model-adaptation.md': ('engine-fx-visual-mapping.md', '模型'),
            'references/seedance-2.5.md': ('fx-director.md', '模型'),
            'references/ability-library.md': ('fx-director.md', '240'),
        }
        for relative, (link, boundary) in expectations.items():
            text = (ROOT / relative).read_text(encoding='utf-8')
            self.assertIn(link, text, relative)
            self.assertIn(boundary, text, relative)

    def test_version_files_are_in_sync(self):
        manifest = (ROOT / 'manifest.yaml').read_text(encoding='utf-8')
        self.assertIn('version: 3.10.5', manifest)
        self.assertNotIn('version: 3.10.3', manifest)
        self.assertIn('fx_director', manifest)
        for relative in ('SKILL.md', 'agents/openai.yaml'):
            text = (ROOT / relative).read_text(encoding='utf-8')
            self.assertIn('3.10.5', text, relative)
            self.assertNotIn('3.10.3', text, relative)
        adapter = ROOT.parent / 'direct-cinematic-fights'
        if not adapter.is_dir():
            adapter = ROOT / 'compatibility' / 'direct-cinematic-fights'
        entry = adapter / ('SKILL.md' if (adapter / 'SKILL.md').exists() else 'entry.md')
        for path in (entry, adapter / 'agents/openai.yaml'):
            self.assertIn('3.10.5', path.read_text(encoding='utf-8'), str(path))
            self.assertNotIn('3.10.3', path.read_text(encoding='utf-8'), str(path))
        for path in sorted(adapter.rglob('*.md')):
            self.assertNotIn('3.10.2', path.read_text(encoding='utf-8'), str(path))
        for relative in ('references/action-and-shot-compiler.md',
                         'references/high-speed-combat-generation.md'):
            text = (adapter / relative).read_text(encoding='utf-8')
            self.assertIn('V3.10.5', text, relative)
            self.assertNotIn('V3.10.3', text, relative)
            self.assertNotIn('../entry.md', text, relative)

    def test_package_file_budget_and_no_stale_releases(self):
        # Repository checkout also carries README/docs/CI/hero assets. The 95-file
        # budget applies to the distributed skill package, so exclude repo-only paths.
        repo_only_dirs = {'.git', '.github', 'docs', '.pytest_cache'}
        repo_only_files = {'README.md', 'README.en.md', 'LICENSE', '.gitattributes', '.gitignore',
                           'assets/hero-zh.jpg', 'assets/hero-en.jpg'}
        skill_files = [
            p for p in ROOT.rglob('*')
            if p.is_file()
            and '__pycache__' not in p.parts
            and not (set(p.relative_to(ROOT).parts) & repo_only_dirs)
            and p.relative_to(ROOT).as_posix() not in repo_only_files
        ]
        self.assertLessEqual(len(skill_files), 95, len(skill_files))
        self.assertTrue((ROOT / 'references' / 'release-history.md').is_file())
        history = (ROOT / 'references' / 'release-history.md').read_text(encoding='utf-8')

        expected = {
            '3.10.2': 'a35690384b30e6ccec438c9cd76eff445ce1ad53b7fbae4ad04f24b6b021e8a9',
            '3.10.1': '5b8513217b359cafd34fbf0e8b0c996190b3039ad9b881a0a3811ebbcacd225f',
            '3.10.0': 'd812fab40cf145c63554280661b1160f4ac7831ff460dc79f424fc52c9efa6fe',
            '3.9.5': '3dc616893a36ba539d5348601f3740b81cd7697dfcc4b450c0efe919aab86e5d',
            '3.9.4': 'dcbdd06bb918111b4c521e2673027320df7b6a338a6fe0ba861c0898242e57f3',
            '3.9.3': '0e0715e04459a52d0ea86ebe0c25592a9e139a539bedf62493b5887627bb6a1d',
        }
        sections = {}
        current = None
        body = []
        for line in history.splitlines():
            match = re.fullmatch(
                r'<!-- source: katil-skill/references/release-v([0-9.]+)\.md -->',
                line,
            )
            if match:
                if current is not None:
                    sections[current] = '\n'.join(body).rstrip()
                current = match.group(1)
                body = []
                continue
            if current is None:
                continue
            if line == '---':
                sections[current] = '\n'.join(body).rstrip()
                current = None
                body = []
            elif body or line:
                body.append(line)
        if current is not None:
            sections[current] = '\n'.join(body).rstrip()

        self.assertEqual(set(sections), set(expected))
        for version, digest in expected.items():
            actual = hashlib.sha256(sections[version].encode('utf-8')).hexdigest()
            self.assertEqual(actual, digest, version)

        new_marker = '<!-- source: V3.10.3 CHANGELOG + KATIL_Core_V3.10.3_修正报告.md -->'
        old_marker = '<!-- source: katil-skill/references/release-v3.10.2.md -->'
        self.assertIn(new_marker, history)
        self.assertLess(history.index(new_marker), history.index(old_marker))
        new_section = history[history.index(new_marker):history.index(old_marker)]
        self.assertIn('# KATIL Core V3.10.3 · 候选修正 · 2026-11-10', new_section)
        for phrase in ('P1', 'P2', 'P3', '243', '242', '162', 'PENDING_VIDEO'):
            self.assertIn(phrase, new_section)

        self.assertIn('## 变更映射', history)
        self.assertIn('15.88', history)
        self.assertIn('239 项', history)
        self.assertEqual(list((ROOT / 'references').glob('release-v*.md')), [])
        self.assertFalse((ROOT / 'baseline_regression.json').exists())
        adapter = ROOT.parent / 'direct-cinematic-fights'
        if adapter.is_dir():
            adapter_files = [p for p in adapter.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
            self.assertLessEqual(len(skill_files) + len(adapter_files), 100)


class FxRunnerValidationTests(unittest.TestCase):
    def invalid_fx_suite(self, mutate):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_minimal_suite(root)
            path = root / 'fx_cases.json'
            data = json.loads(path.read_text(encoding='utf-8'))
            mutate(data['cases'])
            path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
            proc, report = run_runner(root)
            self.assertEqual(proc.returncode, 2)
            self.assertEqual(report['suite']['status'], 'FAIL')
            return report['suite']['findings']

    def test_fxt10_must_remain_no_fx(self):
        findings = self.invalid_fx_suite(lambda cases: cases[9].update(primary_fx='FX10'))
        self.assertTrue(any('FXT10' in finding and 'NONE' in finding for finding in findings), findings)

    def test_auxiliary_coverage_cannot_mask_missing_primary(self):
        def mutate(cases):
            for case in cases:
                if case['primary_fx'] == 'FX07':
                    case.update(primary_fx='FX01', secondary_fx=['FX07'])
        findings = self.invalid_fx_suite(mutate)
        self.assertTrue(any('主导类别' in finding for finding in findings), findings)

    def test_duplicate_secondary_class_is_rejected(self):
        findings = self.invalid_fx_suite(lambda cases: cases[0].update(secondary_fx=['FX09', 'FX09']))
        self.assertTrue(any('secondary_fx' in finding and '重复' in finding for finding in findings), findings)

    def test_missing_layer_coverage_is_rejected(self):
        findings = self.invalid_fx_suite(lambda cases: [case.update(layers=['Primary']) for case in cases])
        self.assertTrue(any('六层' in finding for finding in findings), findings)


if __name__ == '__main__':
    unittest.main()
