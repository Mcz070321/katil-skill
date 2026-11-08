#!/usr/bin/env python3
"""KATIL 回归运行器：校验用例结构，汇总已有判定，输出结构化报告。

只做确定性检查：用例字段、预期枚举、响应值合法性、音频判定是否符合预期、
生成用例的 A/B 媒体流、证据唯一性与独立存放的逐条评审记录、提示词文件里的已知规则残留。
不调用任何大模型 API，也不把文本通过当成成片通过。
"""

import argparse
import json
import re
import sys
from pathlib import Path

from video_evidence import validate_generation
from block_lint import copy_block_purity_findings, event_timing_findings

VERSION = "3.9.0"
STATUSES = {"PASS", "WARN", "FAIL", "UNKNOWN", "PENDING_VIDEO"}
AUDIO_DECISIONS = {
    "music_led",
    "sound_design_led",
    "information_led",
    "unspecified_no_conflict",
}
# 3.9.0 起，这些高密度/连续性用例必须把正反断言分开写，避免拒绝项只藏在 criteria 里。
STRUCTURED_IDS = {f"T{i}" for i in range(34, 44)} | {"C04"}

# 文件名, 类别, 最少条数, 必有字段
SPECS = [
    ("routing_cases.json", "routing", 20, ["id", "request", "expected_load", "prohibited_or_caution"]),
    ("execution_cases.json", "execution", 1, ["id", "request", "criteria"]),
    ("continuity_cases.json", "continuity", 1, ["id", "initial", "next", "expected"]),
    ("style_cases.json", "style", 1, ["id", "request", "expected"]),
    ("audio_cases.json", "audio", 4, ["id", "request", "expected_decision", "required_behavior", "forbidden_behavior"]),
    ("generation_cases.json", "generation", 3, ["id", "request", "focus", "comparison", "runs_min", "evidence_required"]),
    ("model_adaptation_cases.json", "adaptation", 36, ["id", "request", "context", "material_conditions"]),
]

FIELD_BY_CATEGORY = {
    "routing": "routing",
    "execution": "key_action_visibility",
    "continuity": "continuity",
    "style": "style_material",
    "audio": "audio_decision",
    "generation": "video",
    "adaptation": "adaptation",
}

LIMITS = [
    "本报告只证明用例结构与已提供判定的一致性，不证明模型路由正确、提示词可生成或成片改善。",
    "未提供模型输出时，路由、连续性、关键动作可见性与风格材质一律 UNKNOWN。",
    "未提供实际视频与参数时，生成用例保持 PENDING_VIDEO，不接受无证据的 PASS。",
    "媒体证据须有有效多帧视频流、有限正时长，路径／文件实体／SHA-256在组内和跨版本均不重复；工具缺失或探测超时保持待验证。",
    "evidence_status 只表示媒体与记录检查；video／review_status 的 PASS 只能来自按哈希绑定的逐条外部全片评审，reviewed=true 本身不再有效。",
    "程序不能认证生成来源、独立生成次数、评审者身份或实际观看行为，也不能发现全部重编码重复；结构化评审记录不等于可信认证。",
    "艺术质量、声音判断与风格辨识度需要人工或独立模型评审，运行器不自动判优。",
    "小样本、单条优秀成片或一次重测都不能推断稳定提升。",
    "adaptation只汇总外部文字判定；submission_compatibility独立保留外部声明，未提供时UNVERIFIED，不是提交认证。该文字套件不导入视频PASS。",
]


def fail_errors(errors, message):
    errors.append(message)


def load_cases(cases_dir, errors):
    loaded = []
    for filename, category, min_count, required in SPECS:
        path = cases_dir / filename
        if not path.is_file():
            fail_errors(errors, f"缺少用例文件：{path}")
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            fail_errors(errors, f"{filename} 无法解析：{exc}")
            continue
        cases = data.get("cases") if isinstance(data, dict) else None
        if not isinstance(cases, list):
            fail_errors(errors, f"{filename} 缺少 cases 数组")
            continue
        if len(cases) < min_count:
            fail_errors(errors, f"{filename} 用例不足：{len(cases)} < {min_count}")
        if category == "routing" and len(cases) != 20:
            fail_errors(errors, f"{filename} 应保持 20 条，实际 {len(cases)}")
        if category == "adaptation" and (len(cases) != 36 or {str(c.get('id')) for c in cases if isinstance(c,dict)} != {f'M{i:02}' for i in range(1,37)}):
            fail_errors(errors, f"{filename} 应独立覆盖 M01–M36")
        seen = set()
        for index, case in enumerate(cases, 1):
            label = f"{filename} 第 {index} 条"
            if not isinstance(case, dict):
                fail_errors(errors, f"{label} 不是对象")
                continue
            cid = case.get("id")
            if cid is None:
                fail_errors(errors, f"{label} 缺少 id")
                continue
            if str(cid) in seen:
                fail_errors(errors, f"{filename} 重复 id：{cid}")
            seen.add(str(cid))
            for field in required:
                if field not in case or case[field] in (None, "", []):
                    fail_errors(errors, f"{label} 缺少字段 {field}")
            if category in ("execution", "continuity") and str(cid) in STRUCTURED_IDS:
                for field in ("must_hold", "must_reject"):
                    values = case.get(field)
                    if (not isinstance(values, list) or not values
                            or not all(isinstance(v, str) and v.strip() for v in values)):
                        fail_errors(errors, f"{label}（{cid}）{field} 必须是非空字符串数组")
                        continue
                    if len(values) != len(set(values)):
                        fail_errors(errors, f"{label}（{cid}）{field} 含重复断言")
                hold = case.get("must_hold")
                reject = case.get("must_reject")
                if isinstance(hold, list) and isinstance(reject, list):
                    overlap = {v.strip() for v in hold if isinstance(v, str)} & {
                        v.strip() for v in reject if isinstance(v, str)}
                    if overlap:
                        fail_errors(errors, f"{label}（{cid}）must_hold 与 must_reject 互相矛盾：{sorted(overlap)}")
            if 'timing_mode' in case and case['timing_mode'] not in ('event_driven', 'timecoded', 'local_anchor'):
                fail_errors(errors, f"{label} timing_mode 不在枚举内")
            if category == "routing":
                for field in ("id", "request", "expected_load", "prohibited_or_caution"):
                    if field in case and not isinstance(case[field], (str, int)):
                        fail_errors(errors, f"{label} 字段 {field} 类型异常")
                if index >= 13 and case.get("concept_mode") not in {"作者型", "约束型", "极简型"}:
                    fail_errors(errors, f"{label} 缺少合法 concept_mode")
            if category == "audio":
                if case.get("expected_decision") not in AUDIO_DECISIONS:
                    fail_errors(errors, f"{label} expected_decision 不在枚举内")
            if category == "adaptation":
                for field in ("id", "request", "context", "material_conditions"):
                    if field in case and not isinstance(case[field],str):
                        fail_errors(errors, f"{label} 字段 {field} 必须为字符串")
            if category == "generation":
                if not isinstance(case.get("focus"), list) or not case.get("focus"):
                    fail_errors(errors, f"{label} focus 必须是非空数组")
                if case.get("evidence_required") is not True:
                    fail_errors(errors, f"{label} evidence_required 必须为 true")
                versions = comparison_versions(case)
                if len(versions) != 2:
                    fail_errors(errors, f"{label} comparison 必须写明两个不同的三段版本号")
                runs = case.get("runs_min")
                if not isinstance(runs, int) or runs < 2:
                    fail_errors(errors, f"{label} runs_min 必须是不小于 2 的整数")
            loaded.append((category, case))
    return loaded


def case_key(category, case):
    cid = str(case.get("id"))
    if category == "routing":
        try:
            return "R%02d" % int(cid)
        except (TypeError, ValueError):
            return "R-" + cid
    return cid


def comparison_versions(case):
    text = str(case.get("comparison", ""))
    return list(dict.fromkeys(re.findall(r"\d+\.\d+\.\d+", text)))


def evaluate_generation(case, response, evidence_base, notes, audit=None):
    """Verify media and uniqueness, then import a separately recorded quality review."""
    if audit is None:
        audit = {}
    return validate_generation(case, response, evidence_base, comparison_versions(case), notes, audit)


def check_prompts(prompts_dir, key, notes, timing_mode=None):
    if not prompts_dir:
        return None
    for suffix in (".txt", ".md"):
        path = prompts_dir / (key + suffix)
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            return "FAIL", [f"提示词文件无法读取：{exc}"]
        text = text.strip()
        if not text:
            return "FAIL", ["提示词文件为空"]
        flags = copy_block_purity_findings(text)
        ranges = re.findall(r"\d+(?:\.\d+)?\s*[—–-]\s*\d+(?:\.\d+)?\s*(?:秒|s\b)", text)
        if ranges:
            notes.append(f"提示词含 {len(ranges)} 个可识别时间区间；仅记录，未证明节奏成立")
        if timing_mode == 'event_driven':
            flags.extend(event_timing_findings(text))
        return ("WARN" if flags else None), flags
    return None


def build_results(loaded, responses, prompts_dir, evidence_base, errors):
    results = []
    unknown_keys = set(responses) - {case_key(c, x) for c, x in loaded}
    for key in sorted(unknown_keys):
        fail_errors(errors, f"响应中有未知用例：{key}")
    for category, case in loaded:
        key = case_key(category, case)
        response = responses.get(key)
        notes = []
        if response is None:
            notes.append("未提供模型输出或判定，保持待执行")
        elif not isinstance(response, dict):
            fail_errors(errors, f"{key} 的响应必须是对象")
            response = None
        for field in ("routing", "reference_contract", "timeline", "key_action_visibility", "style_material", "video", "continuity", "audio_decision", "adaptation"):
            value = (response or {}).get(field)
            if value is not None and (not isinstance(value,str) or value not in STATUSES):
                if field == "audio_decision" and isinstance(value,str) and value in AUDIO_DECISIONS:
                    pass
                else:
                    fail_errors(errors, f"{key} 的 {field} 值非法：{value}")
        if category == "adaptation" and response:
            adaptation=response.get('adaptation','UNKNOWN')
            compatibility=response.get('submission_compatibility','UNVERIFIED')
            video=response.get('video','PENDING_VIDEO')
            if not isinstance(adaptation,str) or adaptation not in {'PASS','WARN','FAIL','UNKNOWN'}:
                fail_errors(errors, f"{key} 的 adaptation 必须是文字判定")
            if not isinstance(compatibility,str) or compatibility not in {'UNVERIFIED','UNSUPPORTED','DEGRADED','COMPATIBLE'}:
                fail_errors(errors, f"{key} 的 submission_compatibility 值非法")
            if not isinstance(video,str) or video not in {'UNKNOWN','PENDING_VIDEO'}:
                fail_errors(errors, f"{key} 的适配文字套件不能导入视频结论")
        if response:
            for note in response.get("notes", []) if isinstance(response.get("notes"), list) else [response.get("notes")] if response.get("notes") else []:
                notes.append(str(note))

        field = FIELD_BY_CATEGORY[category]
        value = (response or {}).get(field, "UNKNOWN")
        audit = {}
        if category == "generation":
            value = evaluate_generation(case, response or {}, evidence_base, notes, audit)
        if category == "audio" and response:
            decision = response.get("audio_decision")
            expected = case.get("expected_decision")
            if decision is None:
                value = "UNKNOWN"
            elif decision == expected:
                value = "PASS"
            elif isinstance(decision,str) and decision in AUDIO_DECISIONS:
                value = "FAIL"
                notes.append(f"声音判断 {decision} 与预期 {expected} 不一致")
        if category == "routing" and response and response.get("routing") is None:
            value = "UNKNOWN"

        # Decision-enum matches do not erase the actual output review (e.g. missing song audio).
        if category != "generation" and response and "text_review_status" in response:
            review = response["text_review_status"]
            if review not in ("PASS", "FAIL", "WARN", "UNKNOWN", "NOT_RUN"):
                fail_errors(errors, f"{key} 的 text_review_status 值非法：{review}")
                review = "UNKNOWN"
            if review == "FAIL" or value == "FAIL":
                value = "FAIL"
            elif review in ("UNKNOWN", "NOT_RUN"):
                value = "UNKNOWN"
            elif review == "WARN" and value == "PASS":
                value = "WARN"

        prompt_status, flags = None, []
        checked = check_prompts(prompts_dir, key, notes, case.get('timing_mode'))
        if checked:
            prompt_status, flags = checked
            notes.extend(flags)
        if prompt_status == "FAIL":
            value = "FAIL"
        elif prompt_status == "WARN" and value in ("PASS", "UNKNOWN"):
            value = "WARN"

        if value in ("PASS", "FAIL", "WARN"):
            status = value
        elif category == "generation" and value == "PENDING_VIDEO":
            status = "PENDING_VIDEO"
        else:
            status = "UNKNOWN"

        result = {
            "test_case": key,
            "category": category,
            "routing": "UNKNOWN",
            "reference_contract": "UNKNOWN",
            "timeline": "UNKNOWN",
            "key_action_visibility": "UNKNOWN",
            "style_material": "UNKNOWN",
            "continuity": "UNKNOWN",
            "audio_decision": "UNKNOWN",
            "video": "PENDING_VIDEO" if category == "generation" else "UNKNOWN",
            "status": status,
            "notes": notes,
        }
        if category == "generation":
            result.update(audit)
        result[field] = value
        if category != "generation" and field != "video":
            result["video"] = "UNKNOWN"
        if category == "adaptation":
            result['submission_compatibility']=(response or {}).get('submission_compatibility','UNVERIFIED')
            result['submission_verdict_source']='external_declaration' if response and 'submission_compatibility' in response else 'not_provided'
            result['video']='PENDING_VIDEO'
        results.append(result)
    return results


def main(argv=None):
    # 管道输出固定为 UTF-8：Windows 下 stdout 默认按本地代码页编码，
    # 父进程或 CI 以 UTF-8 解码时会失败，导致报告变成 None。
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="KATIL 回归结构检查与结果汇总")
    parser.add_argument("--cases", default="tests", help="用例目录，默认 tests")
    parser.add_argument("--responses", help="已有判定的 JSON 文件")
    parser.add_argument("--prompts", help="按用例编号命名的提示词目录（R01.txt 等）")
    parser.add_argument("--out", help="报告输出路径；省略时打印到 stdout")
    parser.add_argument("--version", default=VERSION, help="报告中的版本号")
    args = parser.parse_args(argv)

    cases_dir = Path(args.cases)
    errors = []
    responses = {}
    evidence_base = Path.cwd()
    if not cases_dir.is_dir():
        errors.append(f"用例目录不存在：{cases_dir}")
        loaded = []
    else:
        loaded = load_cases(cases_dir, errors)
    if args.responses:
        path = Path(args.responses)
        evidence_base = path.resolve().parent
        try:
            responses = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(responses, dict):
                errors.append("responses 必须是对象：键为用例编号")
                responses = {}
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"responses 无法解析：{exc}")
            responses = {}
    prompts_dir = Path(args.prompts) if args.prompts else None

    results = build_results(loaded, responses, prompts_dir, evidence_base, errors)
    summary = {name: 0 for name in ("PASS", "WARN", "FAIL", "UNKNOWN", "PENDING_VIDEO")}
    for item in results:
        summary[item["status"]] = summary.get(item["status"], 0) + 1

    report = {
        "version": args.version,
        "suite": {
            "status": "FAIL" if errors else "PASS",
            "counts": {category: sum(1 for c, _ in loaded if c == category) for _, category, _, _ in SPECS},
            "findings": errors,
        },
        "results": results,
        "summary": summary,
        "limits": LIMITS,
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    print(text)

    if errors:
        return 2
    if summary["FAIL"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
