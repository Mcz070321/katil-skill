"""Local media integrity and external-review checks; never automatic artistic judging."""

from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_video(path):
    """Return (status, metadata, explanation). Missing tools/timeouts remain unverified."""
    probe = shutil.which('ffprobe')
    if not probe:
        return 'PENDING_VIDEO', {}, '未找到 ffprobe，媒体内容尚未验证'
    command = [probe, '-v', 'error', '-protocol_whitelist', 'file,pipe',
               '-select_streams', 'v:0', '-count_frames', '-show_entries',
               'stream=codec_name,width,height,nb_read_frames,duration:stream_disposition=attached_pic:format=duration,format_name',
               '-of', 'json', str(path)]
    try:
        process = subprocess.run(command, capture_output=True, text=True,
                                 encoding='utf-8', errors='replace', timeout=30)
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return 'PENDING_VIDEO', {}, f'媒体探测不可用或超时，尚未验证：{type(exc).__name__}'
    except OSError as exc:
        return 'PENDING_VIDEO', {}, f'无法执行媒体探测：{exc}'
    if process.returncode:
        return 'FAIL', {}, '媒体流检查失败：不是有效视频，或视频存在读取／解码错误'
    warnings = process.stderr.strip()
    try:
        data = json.loads(process.stdout)
        stream = data['streams'][0]
        container = data.get('format', {})
        frames = int(stream.get('nb_read_frames', 0))
        width, height = int(stream.get('width', 0)), int(stream.get('height', 0))
        raw_duration = stream.get('duration') or container.get('duration')
        duration = float(raw_duration)
        attached = stream.get('disposition', {}).get('attached_pic', 0)
        if (frames < 2 or width <= 0 or height <= 0 or attached or
                not math.isfinite(duration) or duration <= 0 or
                not stream.get('codec_name')):
            raise ValueError('not a timed multi-frame video')
    except (KeyError, IndexError, TypeError, ValueError, AttributeError):
        return 'FAIL', {}, '媒体缺少有效的多帧视频流、尺寸或有限正时长；音频／封面／单帧图片不能充当视频证据'
    try:
        digest = sha256_file(path)
    except OSError:
        return 'FAIL', {}, '媒体检查期间文件变得不可读'
    metadata = {'sha256': digest, 'duration_seconds': duration,
                'decoded_frames': frames, 'width': width, 'height': height,
                'codec': stream['codec_name']}
    if warnings:
        metadata['probe_warnings'] = warnings
        return 'PASS', metadata, '媒体流与帧读取检查通过；ffprobe 有非致命提示，已记录'
    return 'PASS', metadata, '媒体流与帧读取检查通过'


def read_review(raw, base, case_id, records, notes, audit, runs_min=2, review_criteria=None):
    """Import a separately stored, hash-bound, per-clip review; identity is not authenticated."""
    required_criteria = set(review_criteria or ())
    audit['review_record_valid'] = False
    audit.update(review_mode='open', independence='shared', blind_protocol=None,
                 sample_size=None, ev3_supported=False)
    if not isinstance(raw, str) or not raw.strip():
        notes.append('缺少独立评审文件 review_file；reviewed=true 不能代替逐条评审')
        return 'PENDING_VIDEO'
    path = Path(raw)
    if not path.is_absolute():
        path = base / path
    try:
        review = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(review, dict) or review.get('case_id') != case_id:
            raise ValueError('评审 case_id 与用例不符')
        reviewer = review.get('reviewer')
        if (not isinstance(reviewer, dict) or not isinstance(reviewer.get('id'), str)
                or not reviewer['id'].strip() or reviewer.get('kind') not in ('human', 'model')):
            raise ValueError('缺少评审者 id 或 kind（human／model）')
        date = datetime.fromisoformat(str(review.get('reviewed_at', '')).replace('Z', '+00:00'))
        if date.tzinfo is None:
            raise ValueError('reviewed_at 须为带时区的 ISO 时间')
        review_mode = review.get('review_mode', 'open')
        if review_mode not in ('blind', 'open'):
            raise ValueError('review_mode 须为 blind 或 open')
        independence = review.get('independence', 'shared')
        if independence not in ('independent', 'shared'):
            raise ValueError('independence 须为 independent 或 shared')
        protocol = review.get('blind_protocol')
        if protocol is not None and not isinstance(protocol, str):
            raise ValueError('blind_protocol 须为字符串')
        sample_size = review.get('sample_size')
        if sample_size is not None and (isinstance(sample_size, bool) or not isinstance(sample_size, int) or sample_size < 1):
            raise ValueError('sample_size 须为不小于 1 的整数')
        min_sample = max(2, runs_min if type(runs_min) is int else 2)
        if review_mode == 'blind':
            if not isinstance(protocol, str) or not protocol.strip():
                raise ValueError('blind 评审必须写明 blind_protocol')
            if not isinstance(sample_size, int) or sample_size < min_sample:
                raise ValueError(f'blind 评审的 sample_size 须不小于 {min_sample}（对应用例 runs_min）')
            if independence != 'independent':
                raise ValueError('blind 评审必须声明 independence=independent')
        clips = review.get('clips')
        if not isinstance(clips, list) or len(clips) != len(records):
            raise ValueError('逐条评审数与视频证据数不符')
        expected = {(item['version'], item['index']): item for item in records}
        seen, verdicts = set(), []
        partial = False
        for clip in clips:
            if not isinstance(clip, dict):
                raise ValueError('评审 clip 必须是对象')
            index = clip.get('index')
            if type(index) is not int or not isinstance(clip.get('version'), str):
                raise ValueError('评审 version／index 类型错误')
            key = (clip['version'], index)
            if key in seen or key not in expected:
                raise ValueError('评审证据条目重复或不属于当前版本／序号')
            seen.add(key)
            record = expected[key]
            if clip.get('sha256') != record['sha256']:
                raise ValueError('评审 SHA-256 与实际视频不符，不能沿用旧评审')
            if clip.get('viewing') not in ('full_video', 'frames', 'partial_video'):
                raise ValueError('缺少合法观看范围 viewing')
            partial = partial or clip['viewing'] != 'full_video'
            if clip.get('verdict') not in ('PASS', 'WARN', 'FAIL'):
                raise ValueError('缺少合法外部评审 verdict')
            observations = clip.get('observations')
            if not isinstance(observations, list) or not observations:
                raise ValueError('缺少逐条观察 observations')
            observed_criteria = set()
            for observation in observations:
                if not isinstance(observation, dict):
                    raise ValueError('观察必须是对象')
                for field in ('criterion', 'observation'):
                    if not isinstance(observation.get(field), str) or not observation[field].strip():
                        raise ValueError('观察缺少判据或画面描述')
                time = observation.get('time_seconds')
                if (isinstance(time, bool) or not isinstance(time, (int, float)) or
                        not math.isfinite(time) or not 0 <= time <= record['duration_seconds']):
                    raise ValueError('观察时间无效或超出对应视频时长')
                observed_criteria.add(observation['criterion'])
            if clip['viewing'] == 'full_video':
                missing = required_criteria - observed_criteria
                if missing:
                    raise ValueError(f'{key[0]} 第 {key[1]} 条视频缺少评审判据：{", ".join(sorted(missing))}')
            verdicts.append(clip['verdict'])
    except (OSError, UnicodeError, ValueError, TypeError, OverflowError) as exc:
        notes.append(f'独立评审记录无效：{exc}')
        return 'FAIL'
    ev3_supported = (review_mode == 'blind' and independence == 'independent'
                     and isinstance(protocol, str) and bool(protocol.strip())
                     and isinstance(sample_size, int) and sample_size >= min_sample
                     and not partial)
    audit.update(review_record_valid=True, reviewer=reviewer, reviewed_at=review['reviewed_at'],
                 review_mode=review_mode, independence=independence,
                 blind_protocol=protocol.strip() if isinstance(protocol, str) else None,
                 sample_size=sample_size, ev3_supported=ev3_supported)
    notes.append(f'导入外部评审：{reviewer["id"]}（{reviewer["kind"]}）；评审方式 {review_mode}／{independence}；身份与实际观看声明未认证')
    if ev3_supported:
        notes.append('EV3 盲评记录字段齐备；程序仍不认证评审者独立性与实际盲法执行')
    elif review_mode == 'blind':
        notes.append('声明 blind 但观看范围或字段不足，不能记为 EV3')
    if 'FAIL' in verdicts:
        return 'FAIL'
    if partial:
        notes.append('只有抽帧／局部观看记录，不能作为全片评审通过')
        return 'PENDING_VIDEO'
    return 'WARN' if 'WARN' in verdicts else 'PASS'


def validate_generation(case, response, base, versions, notes, audit):
    """Validate evidence separately from importing the quality verdict."""
    audit.update(evidence_status='UNKNOWN', review_status='UNKNOWN', evidence_records=[],
                 quality_verdict_source='unverified')
    value = response.get('video', 'PENDING_VIDEO')
    if value != 'PASS':
        return value
    if len(versions) != 2:
        notes.append('用例比较版本不是两版，无法核查 A/B')
        return 'FAIL'
    evidence = response.get('evidence')
    if not isinstance(evidence, dict):
        notes.append('视频 PASS 必须提供按比较版本分组的证据（evidence）；单一路径不足以证明 A/B')
        audit['evidence_status'] = 'FAIL'
        return 'FAIL'
    problems, records = [], []
    paths_seen, inodes_seen, hashes_seen = set(), set(), set()
    pending = False
    runs = response.get('runs')
    for version in versions:
        paths = evidence.get(version)
        if not isinstance(paths, list) or not paths:
            problems.append(f'缺少 {version} 版视频证据')
            continue
        count = runs.get(version) if isinstance(runs, dict) else None
        minimum = case.get('runs_min', 2)
        if type(count) is not int or count < minimum:
            problems.append(f'{version} 版生成次数不足：{count!r} < {minimum}')
        elif len(paths) != count:
            problems.append(f'{version} 版证据数必须等于声明的 {count} 次生成')
        for index, raw in enumerate(paths, 1):
            if not isinstance(raw, str) or not raw.strip():
                problems.append('证据路径不是非空字符串')
                continue
            path = Path(raw)
            if not path.is_absolute():
                path = base / path
            try:
                path = path.resolve(strict=True)
                stat = path.stat()
                if not path.is_file() or stat.st_size == 0:
                    raise ValueError('为空或不是普通文件')
                digest = sha256_file(path)
            except (OSError, ValueError, RuntimeError) as exc:
                problems.append(f'证据文件不存在、为空或不可读：{path}（{exc}）')
                continue
            inode = (stat.st_dev, stat.st_ino)
            if path in paths_seen or (stat.st_ino and inode in inodes_seen) or digest in hashes_seen:
                problems.append(f'重复证据：同一路径、文件实体或 SHA-256 不能在组内或跨版本重复计数：{path}')
                continue
            paths_seen.add(path)
            if stat.st_ino:
                inodes_seen.add(inode)
            hashes_seen.add(digest)
            status, metadata, explanation = inspect_video(path)
            if status == 'FAIL':
                problems.append(f'{path}：{explanation}')
                continue
            if status == 'PENDING_VIDEO':
                notes.append(f'{path}：{explanation}')
                pending = True
                continue
            if metadata['sha256'] != digest:
                problems.append(f'检查期间视频内容发生变化：{path}')
                continue
            records.append(dict(metadata, version=version, index=index, path=str(path)))
    for field, label in (('model', '模型'), ('model_version', '模型版本'), ('parameters', '生成参数')):
        if not isinstance(response.get(field), str) or not response[field].strip():
            problems.append(f'缺少{label}记录')
    audit['evidence_records'] = records
    if problems:
        notes.extend(problems)
        audit['evidence_status'] = 'FAIL'
        return 'FAIL'
    if pending:
        audit['evidence_status'] = 'PENDING_VIDEO'
        return 'PENDING_VIDEO'
    audit['evidence_status'] = 'PASS'
    review_status = read_review(
        response.get('review_file'), base, str(case.get('id')), records, notes, audit,
        runs_min=case.get('runs_min', 2), review_criteria=case.get('review_criteria'),
    )
    audit['review_status'] = review_status
    if audit.get('review_record_valid') and review_status in ('PASS', 'WARN', 'FAIL'):
        audit['quality_verdict_source'] = 'external_review_record_unverified_identity'
    notes.append('证据完整性与外部质量结论分开；程序不认证生成来源、评审身份或艺术质量')
    return review_status
