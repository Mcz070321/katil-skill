#!/usr/bin/env python3
"""Conservative timing inspector for KATIL prompt text. No semantic or video validation."""
import argparse
import json
import math
import re
import sys
from pathlib import Path

NUMBER = r'\d+(?:\.\d+)?'
CLOCK = rf'(?:\d+:\d{{2}}(?::\d{{2}})?(?:\.\d+)?|{NUMBER})'
RANGE = re.compile(rf'^\s*(?:[-*]\s+)?[【\[(（]?\s*(?P<a>{CLOCK})\s*(?:秒|s|sec(?:onds?)?)?\s*(?:—|–|~|～|至|到|-)\s*(?P<b>{CLOCK})\s*(?:秒|s|sec(?:onds?)?)?\s*[】\])）]?(?=\s|[:：]|$)', re.I)
TRACK = re.compile(r'^\s*\[(?:track|轨道)\s*[:：]\s*([^\]]+)\]\s*$',re.I)
LABEL = re.compile(r'^\s*(?:#{1,6}\s*)?(中文|Chinese|英文|English)\s*[:：]?\s*$',re.I)
TIME_LIKE = re.compile(r'^\s*(?:[-*]\s+)?[【\[(（]?(?:第\s*\d+\s*帧|\d+(?:[.:]\d+)*(?:\s*(?:秒|s|帧)|\s*[—–~～至到-]))',re.I)
CLOCK_POINT = re.compile(r'^\s*(?:[-*]\s+)?[【\[(（]?\d+:\d{2}(?::\d{2})?(?:\.\d+)?\s*(?:[:：]|$)')
INLINE_RANGE = re.compile(rf'(?<![\d:.]){CLOCK}\s*(?:秒|seconds?|secs?|s)?\s*[—–~～至到-]\s*{CLOCK}(?![\d:.])',re.I)
DISTANCE_UNIT = re.compile(r'^\s*(?:毫米|厘米|千米|公里|米|英尺|mm\b|cm\b|km\b|m\b|feet\b|ft\b)',re.I)
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
SHOT_LABEL = re.compile(r'^\s*(?:[-*]\s+)?(?:分镜|镜内阶段|Shot\b|Phase\b)\s*\d+\s*', re.I)
TIME_UNIT = r'(?:秒|seconds?\b|secs?\b|s\b)'
CLOCK_VALUE = r'\d+:\d{2}(?::\d{2})?(?:\.\d+)?(?![\d.]|:\d)'
EDITORIAL_RANGE = re.compile(
    rf'^(?:{CLOCK}\s*{TIME_UNIT}?\s*[—–~～至到-]\s*{CLOCK}\s*{TIME_UNIT}|'
    rf'{CLOCK_VALUE}\s*[—–~～至到-]\s*{CLOCK_VALUE})', re.I)
EDITORIAL_POINT = re.compile(
    rf'^(?:at\s+)?(?:(?:第\s*{NUMBER}\s*秒)|{CLOCK_VALUE}|'
    rf'(?:{NUMBER}\s*{TIME_UNIT}))(?=\s*[：:，,）)\]】]|\s*$)', re.I)
EDITORIAL_DURATION = re.compile(
    rf'^(?:(?:时长|镜长|持续时间|持续|duration)\s*[:：]?\s*)?{NUMBER}\s*{TIME_UNIT}'
    r'(?=\s*[：:，,）)\]】]|\s*$)', re.I)
RELATIVE_DELAY = re.compile(r'\s*(?:钟?后|之后|later\b)', re.I)



INTERNAL_MAINT_ID = re.compile(r'\bSD25-\d{2}\b')
FORM_TRANSITION = re.compile(r'入段转场\s*[｜|]|前段\s*→\s*本段')
SELF_EXPLAIN_TIMING = re.compile(r'以无时间码分镜推进|无分镜秒数|其余按事件自然推进')


def copy_block_purity_findings(text):
    """Check prompt text and copy blocks for legacy rule remnants and leaked internal tags."""
    flags = []
    if '如有参考图' in text or 'If reference images are present' in text:
        flags.append('仍含「如有参考图」条件句；无参考图时不应生成该声明')
    if '默认无BGM' in text or '默认无 BGM' in text:
        flags.append('仍含全局「默认无BGM」表述；应按声音目的判断')
    groups = groups_from(text)
    if any(FENCE.match(line) for line in text.splitlines()):
        groups = [group for group in groups if group['source'] != 'plain']
    block_text = '\n'.join(g['text'] for g in groups) if groups else text
    if INTERNAL_MAINT_ID.search(block_text):
        flags.append('复制块内含内部维护编号（如 SD25-01），应留在块外')
    if FORM_TRANSITION.search(block_text):
        flags.append('复制块内含表单式转场标题，跨段承接应自然融入首句起态')
    if SELF_EXPLAIN_TIMING.search(block_text):
        flags.append('复制块内含无时间码写作方式自解释赘语，应留在块外')
    return flags


def event_timing_findings(text):
    """Find clearly labelled editorial timing in copy blocks, conservatively."""
    groups = groups_from(text)
    if any(FENCE.match(line) for line in text.splitlines()):
        groups = [group for group in groups if group['source'] != 'plain']
    findings = []
    for index, group in enumerate(groups, 1):
        for lineno, raw in enumerate(group['text'].splitlines(), 1):
            line = raw.strip().replace('**', '')
            label = SHOT_LABEL.match(line)
            body = line[label.end():] if label else line
            body = body.lstrip(' \t：:（([【|｜')
            marker = (EDITORIAL_RANGE.match(body) or EDITORIAL_POINT.match(body)
                      or (EDITORIAL_DURATION.match(body) if label else None))
            if marker and not RELATIVE_DELAY.match(body[marker.end():]):
                findings.append(f'复制块 {index} 第 {lineno} 行含明确镜头／阶段时间标记，需核对授权范围')
    return findings


def seconds(raw):
    parts=raw.split(':')
    if len(parts)==1: return float(parts[0])
    if len(parts)>3: raise ValueError('unsupported clock format')
    nums=[float(x) for x in parts]
    if nums[-1]>=60 or (len(nums)==3 and nums[-2]>=60): raise ValueError('clock component >= 60')
    return sum(v*60**i for i,v in enumerate(reversed(nums)))


def has_inline_range(line):
    # Numbers carrying an explicit distance unit are not timestamps. Ambiguous
    # unitless ranges are UNKNOWN, not a hard error.
    for match in INLINE_RANGE.finditer(line):
        if not DISTANCE_UNIT.match(line[match.end():]):
            return True
    return False


def groups_from(text):
    """Keep explicitly labelled plain text and fenced copy blocks independent."""
    lines=text.splitlines(); groups=[]; outside=[]; inside=None; pending=None
    def lang(line):
        m=LABEL.match(line)
        if not m:return None
        return 'zh' if m.group(1).lower() in ('中文','chinese') else 'en'
    def append(buf,label,source):
        if any(x.strip() for x in buf):groups.append({'language':label,'source':source,'text':'\n'.join(buf)})
    def flush_outside(force=False):
        nonlocal outside
        timed=any(RANGE.match(x) or TIME_LIKE.match(x) or CLOCK_POINT.match(x) or has_inline_range(x) for x in outside)
        if force or timed or pending is not None:append(outside,pending,'plain')
        outside=[]
    saw_fence=any(FENCE.match(line) for line in lines)
    if saw_fence:
        for line in lines:
            m=FENCE.match(line)
            if m:
                if inside is None:
                    flush_outside();inside=[]
                else:
                    append(inside,pending,'fenced');inside=None;pending=None
                continue
            if inside is not None:
                inside.append(line);continue
            label=lang(line)
            if label:
                flush_outside();pending=label
            else:outside.append(line)
        if inside is not None:append(inside,pending,'unclosed-fence')
        else:flush_outside(force=not groups)
    else:
        for line in lines:
            label=lang(line)
            if label:
                flush_outside(force=True);pending=label
            else:outside.append(line)
        flush_outside(force=True)
    return groups


def inspect_group(group,duration,allow_overlap,ignore_relative=False):
    tracks={};all_ranges=[];findings=[];unparsed=[];track='default'
    for lineno,line in enumerate(group['text'].splitlines(),1):
        line=re.sub(r'^(\s*(?:[-*]\s+)?)\*\*(.*?)\*\*',r'\1\2',line,count=1)
        tm=TRACK.match(line)
        if tm:
            track=tm.group(1).strip();continue
        m=RANGE.match(line)
        if m:
            if ignore_relative and RELATIVE_DELAY.match(line[m.end():]):
                continue
            try:a,b=seconds(m.group('a')),seconds(m.group('b'))
            except ValueError:
                unparsed.append(f'第 {lineno} 行时间格式不合法或无法识别');continue
            if not math.isfinite(a) or not math.isfinite(b):
                unparsed.append(f'第 {lineno} 行时间数值超出范围，无法可靠解析');continue
            all_ranges.append([a,b]);tracks.setdefault(track,[]).append((a,b,lineno))
            if has_inline_range(line[m.end():]):
                unparsed.append(f'第 {lineno} 行存在多个时间区间，无法可靠区分，请每行写一个区间')
        elif TIME_LIKE.match(line) or CLOCK_POINT.match(line) or has_inline_range(line):
            unparsed.append(f'第 {lineno} 行时间点或格式无法作为区间识别')
    for track,spans in tracks.items():
        last_start=None;max_end=None
        for start,end,line in spans:
            if end<=start:findings.append(f'轨道 {track} 第 {line} 行结束时间不晚于开始时间')
            if duration is not None and (start>duration or end>duration):findings.append(f'轨道 {track} 第 {line} 行超出目标时长 {duration:g} 秒')
            if last_start is not None and start<last_start:findings.append(f'轨道 {track} 第 {line} 行开始时间倒序')
            if max_end is not None and start<max_end and not allow_overlap:findings.append(f'轨道 {track} 第 {line} 行与前一区间重叠，可能为有意并行')
            if max_end is not None and start>max_end:findings.append(f'轨道 {track} 第 {line} 行与前一区间存在间隙，可能为有意留白')
            last_start=start;max_end=end if max_end is None else max(max_end,end)
    findings.extend(unparsed)
    if findings and any(x not in unparsed for x in findings):status='WARN'
    elif unparsed or not all_ranges or duration is None or group['source']=='unclosed-fence':status='UNKNOWN'
    else:status='PASS'
    if not all_ranges:findings.append('没有可识别的时间区间，不能判断时间轴')
    if duration is None:findings.append('未提供目标时长，不能核对是否超时')
    if group['source']=='unclosed-fence':findings.append('复制块未闭合，分组可能不完整')
    return {'language':group['language'],'source':group['source'],'ranges_seconds':all_ranges,'timing':{'status':status,'findings':findings},'coverage':{'status':'UNKNOWN','detail':'只检查已识别区间；用户未声明完整覆盖时，不推断开头、结尾是否需要填满。'},'tracks':list(tracks)}


def inspect(text,duration=None,language=None,task_type=None,reference_mode=None,previous_state=None,allow_overlap=False,timing_policy='auto'):
    if timing_policy not in ('auto', 'forbid'):
        raise ValueError('timing_policy must be auto or forbid')
    source_groups = groups_from(text)
    if timing_policy == 'forbid' and any(FENCE.match(line) for line in text.splitlines()):
        source_groups = [group for group in source_groups if group['source'] != 'plain']
    groups=[inspect_group(g,duration,allow_overlap,ignore_relative=timing_policy=='forbid') for g in source_groups]
    if not groups:groups=[inspect_group({'text':'','language':None,'source':'plain'},duration,allow_overlap)]
    labels={g['language'] for g in groups if g['language']}
    language_status='WARN' if language and labels and any(x!=language for x in labels) else 'UNKNOWN'
    checks={
      'output_language':{'status':language_status,'detail':'仅识别显式块标签；专有名词、台词、双语内容须人工核对。'},
      'reference_mode':{'status':'UNKNOWN','detail':'已接收参考模式，但不推断图片是否实际绑定或首尾帧是否锁定。'},
      'semantic_content':{'status':'UNKNOWN','detail':'人物、物品、手别、换手、声音、空间、动作、风格与硬约束需要语义核验。'},
      'continuity':{'status':'UNKNOWN','detail':'可接收上一段尾态文件，但不推断内容或跨段承接是否一致。'},
      'duplicated_or_internal_text':{
          'status': 'WARN' if copy_block_purity_findings(text) else 'UNKNOWN',
          'findings': copy_block_purity_findings(text),
          'detail':'已检查已知规则残留、维护编号与表单标题；其他重复片段仍需人工核对。'
      },
      'actual_video':{'status':'UNKNOWN','detail':'此脚本只读取提示词文本，不能验证视频或音轨。'}
    }
    if timing_policy == 'forbid':
        findings = event_timing_findings(text)
        checks['timing_policy'] = {
            'status': 'WARN' if findings else 'UNKNOWN',
            'findings': findings,
            'detail': '只警示明确的镜头时间标记；未检出时仍需核对语义与局部授权。',
        }
    statuses=[g['timing']['status'] for g in groups]+[x['status'] for x in checks.values()]
    overall='WARN' if 'WARN' in statuses else 'UNKNOWN' if 'UNKNOWN' in statuses else 'PASS'
    return {'status':overall,'groups':groups,'checks':checks,'parameters':{'target_duration_seconds':duration,'language':language,'task_type':task_type,'reference_mode':reference_mode,'previous_state_supplied':previous_state is not None,'allow_overlap':allow_overlap},'scope':'只检查识别到的区间；PASS 不表示语义、生成视频或模型性能通过。'}


def main():
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('path',type=Path,help='UTF-8 提示词文件')
    p.add_argument('--duration',type=float,help='目标总时长（秒）')
    p.add_argument('--language',choices=('zh','en'),help='指定输出语言')
    p.add_argument('--task-type',help='任务类型，仅记录，不做语义推断')
    p.add_argument('--reference-mode',choices=('none','reference','locked','unknown'),help='参考图模式，仅记录')
    p.add_argument('--previous-state',type=Path,help='上一段尾态 UTF-8 文件，仅记录存在，不自动对照')
    p.add_argument('--allow-overlap',action='store_true',help='明确允许同一轨道重叠；此选项不证明动作可执行')
    p.add_argument('--timing-policy',choices=('auto','forbid'),default='auto',help='auto 沿用区间检查；forbid 另警示复制块中的明确镜头时间标记')
    args=p.parse_args()
    if args.duration is not None and (args.duration<=0 or args.duration!=args.duration or args.duration==float('inf')):p.error('--duration 必须为有限的正数')
    try:
        text=args.path.read_text(encoding='utf-8-sig')
        prev=args.previous_state.read_text(encoding='utf-8-sig') if args.previous_state else None
    except (OSError,UnicodeError) as e:p.error(str(e))
    report=inspect(text,args.duration,args.language,args.task_type,args.reference_mode,prev,args.allow_overlap,args.timing_policy)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))

if __name__=='__main__':main()
