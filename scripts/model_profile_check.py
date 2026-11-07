#!/usr/bin/env python3
"""Check document-level capability profile structure using the standard library.

PASS covers schema, provenance links, finite values and mode contracts only.
This program cannot authenticate that a web source supports a capability claim;
semantic_support is therefore always UNKNOWN. It does not check a provider UI,
submit a generation, or establish API/submission readiness.
"""

import argparse
from datetime import date
import json
import math
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_PROFILE = Path(__file__).resolve().parents[1] / "references" / "model-capabilities" / "seedance-2.5.json"
VERSIONS = {"schema_version": "1.0.0", "model_family": "seedance", "model_version": "2.5", "adapter_revision": "0.1.0"}
IDENTITIES = {
    "seedance-2.5-public-baseline": ("bytedance_seed", "public_model_documentation", "baseline"),
    "runway-tools-reference": ("runway", "tools", "reference"),
    "runway-tools-keyframe": ("runway", "tools", "keyframe"),
    "runway-tools-edit": ("runway", "tools", "edit"),
    "runway-tools-extend": ("runway", "tools", "extend"),
    "jimeng-web-unverified": ("jimeng", "web", "unverified"),
}
# Capability metadata are structural contracts, not copies of published maxima.
# Values such as the duration and reference limits live only in the data file.
CONTRACTS = {
    "output_duration": ("seconds", "output", "range_or_relation"),
    "prompt_length": ("characters", "input", "range"),
    "references_total": ("count", "input", "range"),
    "reference_images": ("count", "input", "range"),
    "reference_videos": ("count", "input", "range"),
    "reference_audio": ("count", "input", "range"),
    "reference_video_duration_per_file": ("seconds", "input", "range"),
    "reference_video_total_duration": ("seconds", "input", "range"),
    "timestamp_editing": ("boolean", "input", "boolean"),
    "multi_round_extension": ("boolean", "input", "boolean"),
    "aspect_ratio": ("ratio", "output", "choices_or_relation"),
    "output_resolution": ("vertical_pixels", "output", "choices"),
    "resolution_control": ("boolean", "input", "boolean"),
    "first_last_frames": ("boolean", "input", "boolean"),
    "keyframes_with_references": ("boolean", "input", "boolean"),
    "source_video_required": ("boolean", "input", "boolean"),
    "extension_directions": ("enum", "input", "directions"),
    "output_extent": ("enum", "output", "extent"),
    "audio_generation": ("boolean", "output", "boolean"),
    "output_format": ("format", "output", "choices"),
    "timestamp_guidance": ("enum", "input", "timestamp_guidance"),
    "model_selection_available": ("boolean", "input", "boolean"),
    "available_modes": ("enum", "input", "modes"),
}
BASELINE_REQUIRED = {"output_duration", "prompt_length", "reference_images", "reference_videos",
                     "reference_audio", "timestamp_editing", "multi_round_extension"}
RUNWAY_REQUIRED = {"output_duration", "prompt_length", "references_total", "reference_images",
                   "reference_videos", "reference_audio", "reference_video_duration_per_file",
                   "reference_video_total_duration", "aspect_ratio", "output_resolution", "resolution_control"}
JIMENG_REQUIRED = {"model_selection_available", "available_modes", "output_duration", "prompt_length", "references_total"}
CAP_REQUIRED = {"value", "unit", "direction", "scope", "source_id", "checked_on", "evidence_status", "observed_status"}
CAP_OPTIONAL = {"configurable", "notes"}
SOURCE_REQUIRED = {"canonical_url", "provider", "surface", "publisher", "kind", "scope", "checked_on", "model_family", "model_version"}
SOURCE_KINDS = ("official_model_documentation", "official_provider_documentation", "official_model_availability")

def application_scope(name):
    """Where a limit applies is separate from its source's model/provider scope."""
    if name == "reference_video_duration_per_file":
        return "per_file"
    if name in {"references_total", "reference_images", "reference_videos", "reference_audio", "reference_video_total_duration"}:
        return "per_request_total"
    return "per_output" if CONTRACTS[name][1] == "output" else "per_request"


def _date_valid(value):
    try:
        return isinstance(value, str) and date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


def _numeric(value, integer=False):
    if type(value) is int:
        return True
    return not integer and type(value) is float and math.isfinite(value)


def _check_range(value, unit):
    if not isinstance(value, dict) or not value or not set(value) <= {"min", "max", "auto"}:
        return False
    if not {"min", "max"} & set(value):
        return False
    for key in ("min", "max"):
        if key in value:
            number = value[key]
            if not _numeric(number, unit in {"count", "characters"}):
                return False
            if number < 0 or (unit in {"seconds", "characters"} and number == 0):
                return False
    if "auto" in value and (type(value["auto"]) is not bool or unit != "seconds"):
        return False
    return not ("min" in value and "max" in value and value["min"] > value["max"])


def _check_choices(value, unit):
    if not isinstance(value, dict) or set(value) != {"choices"}:
        return False
    choices = value["choices"]
    if not isinstance(choices, list) or not choices:
        return False
    if unit == "vertical_pixels":
        valid = all(_numeric(item, integer=True) and item > 0 for item in choices)
    elif unit == "ratio":
        def ratio_valid(item):
            if item == "Auto":
                return True
            if not isinstance(item, str):
                return False
            parts = item.split(":")
            return len(parts) == 2 and all(part.isdigit() and int(part) > 0 for part in parts)
        valid = all(ratio_valid(item) for item in choices)
    else:
        valid = all(isinstance(item, str) and bool(item.strip()) for item in choices)
    return valid and len({json.dumps(item, sort_keys=True) for item in choices}) == len(choices)


def _check_value(name, cap, mode, add, loc):
    value, unit = cap.get("value"), CONTRACTS[name][0]
    shape = CONTRACTS[name][2]
    if isinstance(value, dict) and "matches" in value:
        target = value["matches"]
        expected = None
        if name == "output_duration" and mode == "edit":
            expected = "source_video_duration"
        if name == "aspect_ratio" and mode in ("edit", "extend"):
            expected = "source_video_aspect_ratio"
        if set(value) != {"matches"} or expected is None or target != expected or cap.get("configurable") is not False:
            add("INVALID_RELATION", loc + ".value")
        return
    if shape in {"range", "range_or_relation"}:
        if not _check_range(value, unit):
            add("INVALID_RANGE", loc + ".value")
    elif shape in {"choices", "choices_or_relation"}:
        if not _check_choices(value, unit):
            add("INVALID_VALUE", loc + ".value")
    elif shape == "boolean":
        if type(value) is not bool:
            add("INVALID_VALUE", loc + ".value")
    elif shape == "directions":
        if (not isinstance(value, list) or not value or
                any(item not in ("forward", "backward") for item in value) or
                len(set(value)) != len(value)):
            add("INVALID_VALUE", loc + ".value")
    elif shape == "extent":
        if value != "new_footage_only":
            add("INVALID_VALUE", loc + ".value")
    elif shape == "timestamp_guidance":
        if value != "approximate_pacing_not_frame_accurate":
            add("INVALID_VALUE", loc + ".value")
    elif shape == "modes":
        if not isinstance(value, list) or not value or any(item not in ("reference", "keyframe", "edit", "extend") for item in value):
            add("INVALID_VALUE", loc + ".value")


def _mode_contract(profile, caps, add, loc):
    mode, provider = profile.get("mode"), profile.get("provider")
    required = BASELINE_REQUIRED if mode == "baseline" else JIMENG_REQUIRED if mode == "unverified" else RUNWAY_REQUIRED
    if mode == "keyframe":
        required = required | {"first_last_frames", "keyframes_with_references"}
    if mode in ("edit", "extend"):
        required = required | {"source_video_required"}
    if mode == "extend":
        required = required | {"extension_directions", "output_extent"}
    for name in sorted(required - set(caps)):
        add("MISSING_CAPABILITY", loc + "." + name)

    def known(name):
        cap = caps.get(name)
        return cap.get("value") if isinstance(cap, dict) and cap.get("evidence_status") == "documented" else None

    def require_value(name, value):
        if name in caps and known(name) != value:
            add("MODE_CONFLICT", loc + "." + name + ".value")

    if provider == "runway":
        if mode in ("edit", "extend"):
            require_value("aspect_ratio", {"matches": "source_video_aspect_ratio"})
            require_value("source_video_required", True)
            require_value("resolution_control", False)
            if isinstance(caps.get("output_resolution"), dict) and caps["output_resolution"].get("evidence_status") != "unknown":
                add("MODE_CONFLICT", loc + ".output_resolution")
        else:
            require_value("resolution_control", True)
        if mode == "edit":
            require_value("output_duration", {"matches": "source_video_duration"})
        if mode == "keyframe":
            require_value("first_last_frames", True)
            require_value("keyframes_with_references", True)
        for name in ("first_last_frames", "keyframes_with_references"):
            if name in caps and mode != "keyframe":
                add("MODE_CONFLICT", loc + "." + name)
        for name in ("extension_directions", "output_extent"):
            if name in caps and mode != "extend":
                add("MODE_CONFLICT", loc + "." + name)
        if "source_video_required" in caps and mode not in ("edit", "extend"):
            add("MODE_CONFLICT", loc + ".source_video_required")
    if mode == "unverified":
        require_value("model_selection_available", True)
        for name, cap in caps.items():
            if name != "model_selection_available" and isinstance(cap, dict) and cap.get("evidence_status") != "unknown":
                add("UNVERIFIED_SURFACE_CLAIM", loc + "." + name)

    total = known("references_total")
    if isinstance(total, dict) and _numeric(total.get("max"), integer=True):
        for name in ("reference_images", "reference_videos", "reference_audio"):
            part = known(name)
            if isinstance(part, dict) and _numeric(part.get("max"), integer=True) and part["max"] > total["max"]:
                add("COUNT_CONFLICT", loc + "." + name + ".value.max")


def check(profile_path):
    """Return [{code, location}] without claiming semantic or runtime support."""
    errors = []

    def add(code, location):
        item = {"code": code, "location": location}
        if item not in errors:
            errors.append(item)

    try:
        data = json.loads(Path(profile_path).read_text(encoding="utf-8-sig"))
    except OSError:
        return [{"code": "PROFILE_READ_ERROR", "location": "$"}]
    except (ValueError, UnicodeError):
        return [{"code": "INVALID_JSON", "location": "$"}]

    def finite(value, loc):
        if type(value) is float and not math.isfinite(value):
            add("NON_FINITE_VALUE", loc)
        elif isinstance(value, dict):
            for key, child in value.items():
                finite(child, loc + "." + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                finite(child, loc + "[" + str(index) + "]")

    finite(data, "$")
    if not isinstance(data, dict):
        return errors + [{"code": "INVALID_DOCUMENT", "location": "$"}]
    for key, expected in VERSIONS.items():
        if data.get(key) != expected:
            add("VERSION_MISMATCH", "$." + key)
    if data.get("artifact_kind") != "document_level_natural_language_adapter":
        add("INVALID_ARTIFACT_KIND", "$.artifact_kind")
    if data.get("submission_ready") is not False:
        add("SUBMISSION_CLAIM_NOT_ALLOWED", "$.submission_ready")

    sources = data.get("sources")
    if not isinstance(sources, dict):
        add("INVALID_SOURCES", "$.sources")
        sources = {}
    for source_id, source in sources.items():
        loc = "$.sources." + source_id
        if not isinstance(source, dict):
            add("INVALID_SOURCE", loc)
            continue
        if not SOURCE_REQUIRED <= set(source):
            add("INVALID_SOURCE", loc)
        for key in ("provider", "surface", "publisher"):
            if not isinstance(source.get(key), str) or not source[key].strip():
                add("INVALID_SOURCE", loc + "." + key)
        if source.get("kind") not in SOURCE_KINDS or source.get("scope") not in ("model", "provider_surface"):
            add("INVALID_SOURCE", loc)
        elif (source["kind"] == "official_model_documentation") != (source["scope"] == "model"):
            add("INVALID_SOURCE", loc + ".scope")
        try:
            url = urlparse(source.get("canonical_url", ""))
            valid_url = url.scheme == "https" and bool(url.netloc) and not url.username and not url.password
        except (ValueError, TypeError, AttributeError):
            valid_url = False
        if not valid_url:
            add("INVALID_SOURCE", loc + ".canonical_url")
        if not _date_valid(source.get("checked_on")):
            add("INVALID_DATE", loc + ".checked_on")
        for key in ("model_family", "model_version"):
            if source.get(key) != VERSIONS[key]:
                add("VERSION_MISMATCH", loc + "." + key)

    profiles = data.get("profiles")
    if not isinstance(profiles, list):
        add("INVALID_PROFILES", "$.profiles")
        profiles = []
    seen_ids, seen_modes = set(), set()
    for index, profile in enumerate(profiles):
        loc = "$.profiles[" + str(index) + "]"
        if not isinstance(profile, dict):
            add("INVALID_PROFILE", loc)
            continue
        profile_id = profile.get("id")
        if not isinstance(profile_id, str) or profile_id not in IDENTITIES:
            add("UNKNOWN_PROFILE", loc + ".id")
        elif profile_id in seen_ids:
            add("DUPLICATE_PROFILE", loc + ".id")
        if isinstance(profile_id, str):
            seen_ids.add(profile_id)
        identity = tuple(profile.get(key) for key in ("provider", "surface", "mode"))
        if all(isinstance(value, str) for value in identity):
            if identity in seen_modes:
                add("DUPLICATE_MODE", loc + ".mode")
            seen_modes.add(identity)
        mode = profile.get("mode")
        if mode not in ("baseline", "reference", "keyframe", "edit", "extend", "unverified"):
            add("INVALID_MODE", loc + ".mode")
        if isinstance(profile_id, str) and profile_id in IDENTITIES and identity != IDENTITIES[profile_id]:
            add("PROFILE_IDENTITY_MISMATCH", loc)
        for key in ("model_family", "model_version"):
            if profile.get(key) != VERSIONS[key]:
                add("VERSION_MISMATCH", loc + "." + key)
        if "backend_model_revision" not in profile or profile["backend_model_revision"] is not None:
            add("BACKEND_REVISION_MUST_BE_NULL", loc + ".backend_model_revision")
        if profile.get("observed_status") != "not_tested":
            add("OBSERVED_STATUS_MUST_BE_NOT_TESTED", loc + ".observed_status")
        caps = profile.get("capabilities")
        if not isinstance(caps, dict):
            add("INVALID_CAPABILITIES", loc + ".capabilities")
            continue
        _mode_contract(profile, caps, add, loc + ".capabilities")
        expected_source_scope = "model" if mode == "baseline" else "provider_surface"
        for name, cap in caps.items():
            caploc = loc + ".capabilities." + name
            if name not in CONTRACTS:
                add("UNKNOWN_CAPABILITY", caploc)
                continue
            if not isinstance(cap, dict):
                add("INVALID_CAPABILITY", caploc)
                continue
            for key in sorted(CAP_REQUIRED - set(cap)):
                add("MISSING_CAPABILITY_FIELD", caploc + "." + key)
            for key in sorted(set(cap) - CAP_REQUIRED - CAP_OPTIONAL):
                add("UNEXPECTED_CAPABILITY_FIELD", caploc + "." + key)
            unit, direction, _ = CONTRACTS[name]
            if cap.get("unit") != unit:
                add("UNIT_MISMATCH", caploc + ".unit")
            if cap.get("direction") != direction:
                add("DIRECTION_MISMATCH", caploc + ".direction")
            if cap.get("scope") != application_scope(name):
                add("SCOPE_MISMATCH", caploc + ".scope")
            if cap.get("observed_status") != "not_tested":
                add("OBSERVED_STATUS_MUST_BE_NOT_TESTED", caploc + ".observed_status")
            if not _date_valid(cap.get("checked_on")):
                add("INVALID_DATE", caploc + ".checked_on")
            if "configurable" in cap and type(cap["configurable"]) is not bool:
                add("INVALID_CONTROL", caploc + ".configurable")
            if "notes" in cap and not isinstance(cap["notes"], str):
                add("INVALID_CAPABILITY", caploc + ".notes")
            evidence = cap.get("evidence_status")
            if evidence == "unknown":
                if cap.get("value") is not None:
                    add("UNKNOWN_VALUE_MUST_BE_NULL", caploc + ".value")
                if "configurable" in cap:
                    add("UNKNOWN_CONTROL", caploc + ".configurable")
            elif evidence == "documented":
                if cap.get("value") is None:
                    add("DOCUMENTED_VALUE_REQUIRED", caploc + ".value")
                else:
                    _check_value(name, cap, mode, add, caploc)
            else:
                add("INVALID_EVIDENCE_STATUS", caploc + ".evidence_status")
            source_id = cap.get("source_id")
            if source_id is None and evidence == "unknown":
                continue
            source = sources.get(source_id) if isinstance(source_id, str) else None
            if not isinstance(source, dict):
                add("SOURCE_NOT_FOUND", caploc + ".source_id")
                continue
            if (source.get("provider") != profile.get("provider") or source.get("surface") != profile.get("surface") or
                    source.get("scope") != expected_source_scope):
                add("SOURCE_PROVENANCE_MISMATCH", caploc + ".source_id")
            if source.get("checked_on") != cap.get("checked_on"):
                add("SOURCE_DATE_MISMATCH", caploc + ".checked_on")
    for profile_id in sorted(set(IDENTITIES) - seen_ids):
        add("MISSING_PROFILE", "$.profiles." + profile_id)
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    args = parser.parse_args(argv)
    errors = check(args.profile)
    print(json.dumps({"status": "FAIL" if errors else "PASS", "errors": errors,
                      "claim_scope": "STRUCTURE_ONLY", "semantic_support": "UNKNOWN"}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
