"""Structural contracts for the document-level Seedance 2.5 adapter.

These tests do not authenticate the meaning of source web pages. Numeric
fixtures deliberately differ from the published maxima to keep the data file
as the single source for those values.
"""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "model_profile_check.py"
PROFILE = ROOT / "references" / "model-capabilities" / "seedance-2.5.json"
if SCRIPT.is_file():
    SPEC = importlib.util.spec_from_file_location("model_profile_check", SCRIPT)
    MODULE = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(MODULE)
    check = MODULE.check
else:
    # A missing implementation is a behavioral failure in the first RED run.
    def check(_path):
        return [{"code": "CHECKER_NOT_IMPLEMENTED", "location": "$"}]


def capability(value, unit, direction="input", source="S2", scope="provider_surface", **extra):
    return {
        "value": value,
        "unit": unit,
        "direction": direction,
        "scope": scope,
        "source_id": source if value is not None else None,
        "checked_on": "2026-11-05",
        "evidence_status": "documented" if value is not None else "unknown",
        "observed_status": "not_tested",
        **extra,
    }


def fixture():
    sources = {
        "S1": {
            "canonical_url": "https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5",
            "provider": "bytedance_seed", "surface": "public_model_documentation",
            "publisher": "bytedance_seed", "kind": "official_model_documentation",
            "scope": "model", "checked_on": "2026-11-05",
            "model_family": "seedance", "model_version": "2.5",
        },
        "S1-JIMENG": {
            "canonical_url": "https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5",
            "provider": "jimeng", "surface": "web", "publisher": "bytedance_seed",
            "kind": "official_model_availability", "scope": "provider_surface",
            "checked_on": "2026-11-05", "model_family": "seedance", "model_version": "2.5",
        },
        "S2": {
            "canonical_url": "https://help.runwayml.com/hc/en-us/articles/53542207042323-Creating-with-Seedance-2-5",
            "provider": "runway", "surface": "tools", "publisher": "runway",
            "kind": "official_provider_documentation", "scope": "provider_surface",
            "checked_on": "2026-11-05", "model_family": "seedance", "model_version": "2.5",
        },
    }
    profiles = []
    base = {
        "output_duration": capability({"max": 20}, "seconds", "output", "S1", "model"),
        "prompt_length": capability(None, "characters", scope="model"),
        "reference_images": capability({"max": 8}, "count", source="S1", scope="model"),
        "reference_videos": capability({"max": 3}, "count", source="S1", scope="model"),
        "reference_audio": capability({"max": 2}, "count", source="S1", scope="model"),
        "timestamp_editing": capability(True, "boolean", source="S1", scope="model"),
        "multi_round_extension": capability(True, "boolean", source="S1", scope="model"),
    }
    profiles.append({"id": "seedance-2.5-public-baseline", "provider": "bytedance_seed",
                     "surface": "public_model_documentation", "mode": "baseline", "capabilities": base})
    for mode in ("reference", "keyframe", "edit", "extend"):
        caps = {
            "output_duration": capability({"min": 4, "max": 20, "auto": True}, "seconds", "output", configurable=True),
            "prompt_length": capability({"max": 10000}, "characters"),
            "references_total": capability({"max": 13}, "count"),
            "reference_images": capability({"max": 8}, "count"),
            "reference_videos": capability({"max": 3}, "count"),
            "reference_audio": capability({"max": 2}, "count"),
            "reference_video_duration_per_file": capability({"max": 20}, "seconds"),
            "reference_video_total_duration": capability(None, "seconds"),
            "aspect_ratio": capability({"choices": ["Auto", "16:9", "9:16"]}, "ratio", "output", configurable=True),
            "output_resolution": capability({"choices": [480, 720]}, "vertical_pixels", "output", configurable=True),
            "resolution_control": capability(True, "boolean"),
        }
        if mode == "keyframe":
            caps["first_last_frames"] = capability(True, "boolean")
            caps["keyframes_with_references"] = capability(True, "boolean")
        if mode in ("edit", "extend"):
            caps["source_video_required"] = capability(True, "boolean")
            caps["aspect_ratio"] = capability({"matches": "source_video_aspect_ratio"}, "ratio", "output", configurable=False)
            caps["output_resolution"] = capability(None, "vertical_pixels", "output")
            caps["resolution_control"] = capability(False, "boolean")
        if mode == "edit":
            caps["output_duration"] = capability({"matches": "source_video_duration"}, "seconds", "output", configurable=False)
        if mode == "extend":
            caps["extension_directions"] = capability(["forward", "backward"], "enum")
            caps["output_extent"] = capability("new_footage_only", "enum", "output")
        profiles.append({"id": "runway-tools-" + mode, "provider": "runway", "surface": "tools",
                         "mode": mode, "capabilities": caps})
    profiles.append({"id": "jimeng-web-unverified", "provider": "jimeng", "surface": "web",
                     "mode": "unverified", "capabilities": {
                         "model_selection_available": capability(True, "boolean", source="S1-JIMENG"),
                         "available_modes": capability(None, "enum"),
                         "output_duration": capability(None, "seconds", "output"),
                         "prompt_length": capability(None, "characters"),
                         "references_total": capability(None, "count"),
                     }})
    for profile in profiles:
        profile.update(model_family="seedance", model_version="2.5", backend_model_revision=None, observed_status="not_tested")
        for name,cap in profile['capabilities'].items():
            if name=='reference_video_duration_per_file':cap['scope']='per_file'
            elif name in {'references_total','reference_images','reference_videos','reference_audio','reference_video_total_duration'}:cap['scope']='per_request_total'
            elif cap['direction']=='output':cap['scope']='per_output'
            else:cap['scope']='per_request'
    return {"schema_version": "1.0.0", "model_family": "seedance", "model_version": "2.5",
            "adapter_revision": "0.1.0", "artifact_kind": "document_level_natural_language_adapter",
            "submission_ready": False, "sources": sources, "profiles": profiles}


class ModelProfileCheckTests(unittest.TestCase):
    def setUp(self):
        self.document = fixture()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "profile.json"

    def errors(self, document=None):
        self.path.write_text(json.dumps(self.document if document is None else document), encoding="utf-8")
        return check(self.path)

    def assert_code(self, code):
        errors = self.errors()
        self.assertIn(code, {item["code"] for item in errors}, errors)
        self.assertTrue(all(set(item) == {"code", "location"} for item in errors))

    def cap(self, index=1, name="output_duration"):
        return self.document["profiles"][index]["capabilities"][name]

    def test_complete_document_is_valid(self):
        self.assertEqual([], self.errors())

    def test_packaged_profile_is_valid(self):
        self.assertTrue(PROFILE.is_file(), "The embedded capability profile is missing")
        self.assertEqual([], check(PROFILE))

    def test_dynamic_edit_duration_and_aspect_are_known_values(self):
        self.assertEqual("documented", self.cap(3)["evidence_status"])
        self.assertEqual([], self.errors())

    def test_numeric_values_are_data_not_validator_constants(self):
        self.cap()["value"] = {"min": 2.5, "max": 25, "auto": False}
        self.assertEqual([], self.errors())

    def test_documented_capability_requires_resolvable_source(self):
        self.cap()["source_id"] = "missing"
        self.assert_code("SOURCE_NOT_FOUND")

    def test_source_cannot_be_missing_for_documented_value(self):
        self.cap()["source_id"] = None
        self.assert_code("SOURCE_NOT_FOUND")

    def test_wrong_unit_is_rejected(self):
        self.cap()["unit"] = "characters"
        self.assert_code("UNIT_MISMATCH")

    def test_wrong_direction_is_rejected(self):
        self.cap()["direction"] = "input"
        self.assert_code("DIRECTION_MISMATCH")

    def test_wrong_scope_is_rejected(self):
        self.cap()["scope"] = "model"
        self.assert_code("SCOPE_MISMATCH")

    def test_packaged_limit_scopes_are_separate_from_provenance(self):
        data=json.loads(PROFILE.read_text(encoding='utf-8'))
        caps=data['profiles'][1]['capabilities']
        self.assertEqual(caps['output_duration']['scope'],'per_output')
        self.assertEqual(caps['reference_video_duration_per_file']['scope'],'per_file')
        self.assertEqual(caps['reference_video_total_duration']['scope'],'per_request_total')
        self.assertEqual(data['sources']['S2']['scope'],'provider_surface')

    def test_complete_application_scopes_are_valid(self):
        for profile in self.document['profiles']:
            for name,cap in profile['capabilities'].items():
                if name=='reference_video_duration_per_file':scope='per_file'
                elif name in {'references_total','reference_images','reference_videos','reference_audio','reference_video_total_duration'}:scope='per_request_total'
                elif cap['direction']=='output':scope='per_output'
                else:scope='per_request'
                cap['scope']=scope
        self.assertEqual([],self.errors())

    def test_per_file_limit_cannot_be_total_scope(self):
        self.cap(name='reference_video_duration_per_file')['scope']='per_request_total'
        self.assert_code('SCOPE_MISMATCH')

    def test_model_source_does_not_authorize_provider_surface_value(self):
        self.cap()["source_id"] = "S1"
        self.assert_code("SOURCE_PROVENANCE_MISMATCH")

    def test_runway_source_does_not_authorize_jimeng_value(self):
        self.cap(5, "model_selection_available")["source_id"] = "S2"
        self.assert_code("SOURCE_PROVENANCE_MISMATCH")

    def test_source_date_is_preserved(self):
        self.cap()["checked_on"] = "2026-11-04"
        self.assert_code("SOURCE_DATE_MISMATCH")

    def test_source_url_must_be_canonical_https_url(self):
        self.document["sources"]["S2"]["canonical_url"] = "not a url"
        self.assert_code("INVALID_SOURCE")

    def test_model_documentation_source_cannot_claim_provider_surface_scope(self):
        self.document["sources"]["S1"]["scope"] = "provider_surface"
        self.assert_code("INVALID_SOURCE")

    def test_invalid_checked_on_is_rejected(self):
        self.cap()["checked_on"] = "yesterday"
        self.assert_code("INVALID_DATE")

    def test_profile_version_mixing_is_rejected(self):
        self.document["profiles"][1]["model_version"] = "2.0"
        self.assert_code("VERSION_MISMATCH")

    def test_source_version_mixing_is_rejected(self):
        self.document["sources"]["S2"]["model_version"] = "2.0"
        self.assert_code("VERSION_MISMATCH")

    def test_unsupported_schema_version_is_rejected(self):
        self.document["schema_version"] = "2.0.0"
        self.assert_code("VERSION_MISMATCH")

    def test_missing_identity_field_is_rejected(self):
        del self.document["profiles"][1]["surface"]
        self.assert_code("PROFILE_IDENTITY_MISMATCH")

    def test_missing_profile_is_rejected(self):
        self.document["profiles"].pop()
        self.assert_code("MISSING_PROFILE")

    def test_duplicate_profile_is_rejected(self):
        self.document["profiles"].append(copy.deepcopy(self.document["profiles"][1]))
        self.assert_code("DUPLICATE_PROFILE")

    def test_duplicate_mode_identity_is_rejected(self):
        self.document["profiles"][2]["mode"] = "reference"
        self.assert_code("DUPLICATE_MODE")

    def test_invalid_mode_is_rejected(self):
        self.document["profiles"][1]["mode"] = "turbo"
        self.assert_code("INVALID_MODE")

    def test_invalid_mode_type_is_reported_without_exception(self):
        self.document["profiles"][1]["mode"] = ["reference"]
        self.assert_code("INVALID_MODE")

    def test_invalid_source_kind_type_is_reported_without_exception(self):
        self.document["sources"]["S2"]["kind"] = ["official_provider_documentation"]
        self.assert_code("INVALID_SOURCE")

    def test_invalid_source_scope_type_is_reported_without_exception(self):
        self.document["sources"]["S2"]["scope"] = {"model": True}
        self.assert_code("INVALID_SOURCE")

    def test_invalid_unit_type_is_reported_without_exception(self):
        self.cap()["unit"] = ["seconds"]
        self.assert_code("UNIT_MISMATCH")

    def test_large_finite_integers_do_not_crash_value_validation(self):
        self.cap(1, "prompt_length")["value"] = {"max": 10 ** 400}
        self.assertEqual([], self.errors())

    def test_unknown_is_not_a_numeric_infinity(self):
        self.cap(0, "prompt_length")["value"] = "unlimited"
        self.assert_code("UNKNOWN_VALUE_MUST_BE_NULL")

    def test_unknown_is_not_supported_boolean(self):
        self.cap(5, "available_modes")["value"] = True
        self.assert_code("UNKNOWN_VALUE_MUST_BE_NULL")

    def test_unknown_does_not_enable_control(self):
        self.cap(5, "output_duration")["configurable"] = True
        self.assert_code("UNKNOWN_CONTROL")

    def test_unknown_cannot_have_supported_alias(self):
        self.cap(5, "available_modes")["supported"] = True
        self.assert_code("UNEXPECTED_CAPABILITY_FIELD")

    def test_null_is_not_documented_support(self):
        self.cap()["value"] = None
        self.assert_code("DOCUMENTED_VALUE_REQUIRED")

    def test_unobserved_data_cannot_be_marked_tested(self):
        self.cap()["observed_status"] = "tested"
        self.assert_code("OBSERVED_STATUS_MUST_BE_NOT_TESTED")

    def test_profile_cannot_be_marked_observed(self):
        self.document["profiles"][1]["observed_status"] = "tested"
        self.assert_code("OBSERVED_STATUS_MUST_BE_NOT_TESTED")

    def test_backend_revision_must_not_be_invented(self):
        self.document["profiles"][1]["backend_model_revision"] = "seedance-2.5-2026"
        self.assert_code("BACKEND_REVISION_MUST_BE_NULL")

    def test_adapter_is_not_submission_ready(self):
        self.document["submission_ready"] = True
        self.assert_code("SUBMISSION_CLAIM_NOT_ALLOWED")

    def test_relation_cannot_mix_with_range(self):
        self.cap(3)["value"]["max"] = 30
        self.assert_code("INVALID_RELATION")

    def test_relation_requires_nonconfigurable_control(self):
        self.cap(3)["configurable"] = True
        self.assert_code("INVALID_RELATION")

    def test_relation_target_matches_capability(self):
        self.cap(3)["value"] = {"matches": "source_video_aspect_ratio"}
        self.assert_code("INVALID_RELATION")

    def test_edit_duration_cannot_be_a_free_range(self):
        self.cap(3)["value"] = {"min": 4, "max": 20}
        self.assert_code("MODE_CONFLICT")

    def test_reference_cannot_match_source_aspect(self):
        self.cap(1, "aspect_ratio").update(value={"matches": "source_video_aspect_ratio"}, configurable=False)
        self.assert_code("INVALID_RELATION")

    def test_edit_cannot_offer_resolution_control(self):
        self.cap(3, "resolution_control")["value"] = True
        self.assert_code("MODE_CONFLICT")

    def test_edit_does_not_infer_output_resolution(self):
        self.cap(3, "output_resolution").update(value={"choices": [1080]}, evidence_status="documented", source_id="S2")
        self.assert_code("MODE_CONFLICT")

    def test_keyframes_cannot_be_added_to_reference_mode(self):
        self.document["profiles"][1]["capabilities"]["first_last_frames"] = capability(True, "boolean")
        self.assert_code("MODE_CONFLICT")

    def test_extend_does_not_return_original_plus_new_footage(self):
        self.cap(4, "output_extent")["value"] = "source_plus_extension"
        self.assert_code("INVALID_VALUE")

    def test_extension_direction_must_be_forward_or_backward(self):
        self.cap(4, "extension_directions")["value"] = ["sideways"]
        self.assert_code("INVALID_VALUE")

    def test_jimeng_does_not_copy_runway_limits(self):
        self.cap(5, "output_duration").update(value={"max": 30}, evidence_status="documented", source_id="S1-JIMENG")
        self.assert_code("UNVERIFIED_SURFACE_CLAIM")

    def test_numeric_ranges_are_ordered(self):
        self.cap()["value"] = {"min": 30, "max": 4}
        self.assert_code("INVALID_RANGE")

    def test_reference_counts_are_integers(self):
        self.cap(1, "reference_images")["value"] = {"max": 3.5}
        self.assert_code("INVALID_RANGE")

    def test_total_count_cannot_contradict_per_modality_maximum(self):
        self.cap(1, "references_total")["value"] = {"max": 1}
        self.assert_code("COUNT_CONFLICT")

    def test_nan_cannot_pass_python_json_parser(self):
        self.cap()["value"] = {"max": float("nan")}
        self.assert_code("NON_FINITE_VALUE")

    def test_infinity_anywhere_is_rejected(self):
        self.document["unexpected_metadata"] = float("inf")
        self.assert_code("NON_FINITE_VALUE")

    def test_missing_required_capability_is_rejected(self):
        del self.document["profiles"][3]["capabilities"]["output_duration"]
        self.assert_code("MISSING_CAPABILITY")

    def test_unrecognized_capability_does_not_silently_pass(self):
        self.document["profiles"][1]["capabilities"]["unlimited_video"] = capability(True, "boolean")
        self.assert_code("UNKNOWN_CAPABILITY")

    def test_boolean_is_not_a_numeric_limit(self):
        self.cap()["value"] = {"max": True}
        self.assert_code("INVALID_RANGE")

    def test_malformed_json_is_reported(self):
        self.path.write_text("{", encoding="utf-8")
        self.assertIn("INVALID_JSON", {item["code"] for item in check(self.path)})

    def test_missing_file_is_reported(self):
        self.assertIn("PROFILE_READ_ERROR", {item["code"] for item in check(self.path)})

    def test_cli_default_claims_structure_only(self):
        self.assertTrue(SCRIPT.is_file(), "The checker is not implemented")
        result = subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual("PASS", output["status"])
        self.assertEqual("STRUCTURE_ONLY", output["claim_scope"])
        self.assertEqual("UNKNOWN", output["semantic_support"])
        self.assertEqual([], output["errors"])

    def test_cli_invalid_profile_exits_one(self):
        self.assertTrue(SCRIPT.is_file(), "The checker is not implemented")
        self.document["profiles"].pop()
        self.errors()
        result = subprocess.run([sys.executable, str(SCRIPT), "--profile", str(self.path)], capture_output=True, text=True)
        self.assertEqual(1, result.returncode)
        output = json.loads(result.stdout)
        self.assertEqual("FAIL", output["status"])
        self.assertEqual("STRUCTURE_ONLY", output["claim_scope"])
        self.assertEqual("UNKNOWN", output["semantic_support"])
        self.assertIn("MISSING_PROFILE", {item["code"] for item in output["errors"]})


if __name__ == "__main__":
    unittest.main()
