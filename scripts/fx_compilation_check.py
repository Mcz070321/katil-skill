#!/usr/bin/env python3
"""Check manually annotated literal spans and ordering, never semantic quality.

Input can be either one JSON case object (with source_text, compiled_text,
requirements and optional required_order edges) or a suite object containing a
nonempty "cases" list (such as tests/fx_compilation_cases.json).
"""
import argparse
import json
from pathlib import Path


def check_case(case):
    """Return diagnostics; a clean result always needs human semantic review."""
    if not isinstance(case, dict):
        raise ValueError('case must be an object')
    source = case.get('source_text')
    compiled = case.get('compiled_text')
    reqs = case.get('requirements')
    edges = case.get('required_order', [])
    if not isinstance(source, str) or not source.strip():
        raise ValueError('source_text must be nonempty')
    if not isinstance(compiled, str) or not compiled.strip():
        raise ValueError('compiled_text must be nonempty')
    if not isinstance(reqs, list) or not reqs:
        raise ValueError('requirements must be a nonempty list')
    if not isinstance(edges, list):
        raise ValueError('required_order must be a list')

    issues = []
    positions = {}
    ids = set()
    for req in reqs:
        if not isinstance(req, dict):
            raise ValueError('each requirement must be an object')
        rid = req.get('id')
        src_span = req.get('source_span')
        dst_span = req.get('compiled_span')
        if not all(isinstance(value, str) and value.strip() for value in (rid, src_span, dst_span)):
            raise ValueError('each requirement needs nonempty id, source_span and compiled_span')
        if rid in ids:
            raise ValueError(f'duplicate requirement id: {rid}')
        ids.add(rid)
        source_count, compiled_count = source.count(src_span), compiled.count(dst_span)
        if source_count != 1:
            issues.append({'id': rid, 'kind': 'source_span_missing_or_ambiguous', 'count': source_count})
        if compiled_count != 1:
            issues.append({'id': rid, 'kind': 'compiled_span_missing_or_ambiguous', 'count': compiled_count})
        if source_count == compiled_count == 1:
            positions[rid] = (source.index(src_span), compiled.index(dst_span))

    for edge in edges:
        if (not isinstance(edge, list) or len(edge) != 2 or
                not all(isinstance(rid, str) and rid in ids for rid in edge) or edge[0] == edge[1]):
            raise ValueError('each required_order edge must identify two distinct requirements')
        before, after = edge
        if before in positions and after in positions:
            if positions[before][0] >= positions[after][0]:
                issues.append({'id': f'{before}->{after}', 'kind': 'source_order_invalid'})
            if positions[before][1] >= positions[after][1]:
                issues.append({'id': f'{before}->{after}', 'kind': 'compiled_order_changed'})

    count = lambda s: len(''.join(s.split()))
    return {
        'status': 'MISSING_OR_ORDER_VIOLATION' if issues else 'ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED',
        'issues': issues,
        'source_characters_without_whitespace': count(source),
        'compiled_characters_without_whitespace': count(compiled),
        'evidence_boundary': 'EV1_LITERAL_ONLY',
        'warning': '字面片段与先后顺序不能证明语义、否定、完整性或视频效果；必须人工对照原始需求。',
    }


def check_payload(payload):
    """Check either a single case dict or a multi-case suite dict with 'cases'."""
    if isinstance(payload, dict) and 'cases' in payload and 'source_text' not in payload:
        cases = payload.get('cases')
        if not isinstance(cases, list) or not cases:
            raise ValueError('cases must be a nonempty list')
        case_reports = []
        aggregated_issues = []
        seen_case_ids = set()
        for idx, item in enumerate(cases):
            if not isinstance(item, dict):
                raise ValueError('each case in cases must be an object')
            cid = item.get('id') or f'case_{idx + 1}'
            if not isinstance(cid, str) or not cid.strip():
                raise ValueError('each case id must be a nonempty string')
            if cid in seen_case_ids:
                raise ValueError(f'duplicate case id: {cid}')
            seen_case_ids.add(cid)
            report = check_case(item)
            case_reports.append({'id': cid, **report})
            for issue in report['issues']:
                aggregated_issues.append({'case_id': cid, **issue})
        return {
            'status': 'MISSING_OR_ORDER_VIOLATION' if aggregated_issues else 'ANNOTATED_SPANS_PRESENT_REVIEW_REQUIRED',
            'case_count': len(case_reports),
            'cases': case_reports,
            'issues': aggregated_issues,
            'evidence_boundary': 'EV1_LITERAL_ONLY',
            'warning': '字面片段与先后顺序不能证明语义、否定、完整性或视频效果；必须人工对照原始需求。',
        }
    return check_case(payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('json_file', type=Path, help='one manually annotated JSON case or a suite with "cases"')
    args = parser.parse_args()
    try:
        payload = json.loads(args.json_file.read_text(encoding='utf-8'))
        result = check_payload(payload)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({'status': 'INVALID_ANNOTATION', 'error': str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['issues'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
