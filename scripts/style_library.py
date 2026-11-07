"""Read-only lookup for KATIL-skill's visual-style recipes."""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

LIBRARY = Path(__file__).resolve().parents[1] / 'references' / 'style-library'
TEXT_FIELDS = {
    'id', 'name', 'name_en', 'family', 'medium', 'shape_motion', 'texture',
    'light_color', 'camera_edit', 'vfx_sound', 'limits',
}
PAIR_FIELDS = {'character_style', 'scene_style', 'video_style'}
LABELS = {
    'medium': '媒介', 'shape_motion': '造型与动作', 'texture': '表面材质',
    'light_color': '光色', 'camera_edit': '摄影与剪辑',
    'vfx_sound': '效果与声音', 'limits': '适用边界',
}


def load_library() -> tuple[dict, list[dict]]:
    bundled = LIBRARY / 'styles.json'
    if bundled.is_file():
        data = json.loads(bundled.read_text(encoding='utf-8'))
        return data, list(data['styles'])
    catalog = json.loads((LIBRARY / 'catalog.json').read_text(encoding='utf-8'))
    cards = []
    for family in catalog['families']:
        file = Path(family['file'])
        if file.name != str(file) or file.suffix != '.json':
            raise ValueError('Family file must be a local JSON filename')
        shard = json.loads((LIBRARY / file).read_text(encoding='utf-8'))
        if shard['family'] != family['id']:
            raise ValueError('Family metadata mismatch')
        cards.extend(shard['styles'])
    return catalog, cards


def validate(catalog: dict, cards: list[dict]) -> dict:
    if catalog['count'] != 60 or len(cards) != 60:
        raise ValueError('Expected 60 style cards')
    if [c['id'] for c in cards] != [f'S{i:03d}' for i in range(1, 61)]:
        raise ValueError('Style IDs must be continuous and ordered S001-S060')
    families = {f['id']: f for f in catalog['families']}
    if list(families) != [f'F{i:02d}' for i in range(1, 11)]:
        raise ValueError('Expected ten ordered families F01-F10')
    if len({c['name'] for c in cards}) != len(cards):
        raise ValueError('Duplicate style names')
    if len({c['name_en'].casefold() for c in cards}) != len(cards):
        raise ValueError('Duplicate English style names')
    for card in cards:
        if set(card) != TEXT_FIELDS | PAIR_FIELDS:
            raise ValueError(f'Wrong fields: {card.get("id")}')
        if not all(isinstance(card[k], str) and card[k].strip() for k in TEXT_FIELDS):
            raise ValueError(f'Missing text: {card["id"]}')
        family = families.get(card['family'])
        if not family or not family['start'] <= int(card['id'][1:]) <= family['end']:
            raise ValueError(f'Wrong family: {card["id"]}')
        for field in PAIR_FIELDS:
            pair = card[field]
            if not isinstance(pair, dict) or set(pair) != {'zh', 'en'}:
                raise ValueError(f'Wrong bilingual field: {card["id"]}/{field}')
            if not all(isinstance(v, str) and v.strip() for v in pair.values()):
                raise ValueError(f'Missing language: {card["id"]}/{field}')
            if not re.search(r'[\u4e00-\u9fff]', pair['zh']) or not re.search(r'[A-Za-z]', pair['en']):
                raise ValueError(f'Wrong language: {card["id"]}/{field}')
        if any(t in str(card) for t in ('TODO', 'TBD', '待补', '{LOOK}', '<placeholder>')):
            raise ValueError(f'Unfinished card: {card["id"]}')
    counts = Counter(c['family'] for c in cards)
    if any(counts[f['id']] != f['end'] - f['start'] + 1 or counts[f['id']] != 6 for f in families.values()):
        raise ValueError('Each family must contain six cards')
    # Exact duplicates here are a data error; useful creative diversity needs human review too.
    for field in ('shape_motion', 'texture', 'camera_edit', 'video_style'):
        signatures = [json.dumps(c[field], ensure_ascii=False, sort_keys=True) for c in cards]
        if len(set(signatures)) != len(cards):
            raise ValueError(f'Duplicate recipe field: {field}')
    return {'result': 'PASS', 'version': catalog['version'], 'count': len(cards),
            'families': len(families), 'family_counts': dict(counts)}


def render(card: dict, names: dict[str, str]) -> str:
    lines = [f'## {card["id"]} {card["name"]} | {card["name_en"]}',
             f'分类：{card["family"]} {names[card["family"]]}']
    lines.extend(f'- {label}：{card[key]}' for key, label in LABELS.items())
    for key, label in [('character_style', '角色图风格片段'), ('scene_style', '场景图风格片段'), ('video_style', '视频风格片段')]:
        lines.extend([f'【{label}｜中文】', card[key]['zh'],
                      f'【{label}｜English】', card[key]['en']])
    return '\n'.join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='KATIL-skill: read-only lookup of 60 visual-style recipes.')
    parser.add_argument('--id', nargs='+', help='Exact IDs, e.g. S031 S050')
    parser.add_argument('--family', nargs='+', help='Exact family IDs, e.g. F06 F09')
    parser.add_argument('--query', help='Case-insensitive keywords; all terms must match')
    parser.add_argument('--limit', type=int, help='1-60; default 5 except exact ID lookup')
    parser.add_argument('--list-families', action='store_true')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--validate', action='store_true')
    args = parser.parse_args(argv)
    try:
        catalog, cards = load_library()
        if args.validate:
            print(json.dumps(validate(catalog, cards), ensure_ascii=False, indent=2))
            return 0
        if args.limit is not None and not 1 <= args.limit <= 60:
            parser.error('--limit must be between 1 and 60')
        families = {f['id']: f for f in catalog['families']}
        all_ids = {c['id'] for c in cards}
        for field, supplied, choices in [('id', args.id, all_ids), ('family', args.family, families)]:
            if supplied and set(supplied) - set(choices):
                parser.error(f'Unknown {field}: {", ".join(sorted(set(supplied) - set(choices)))}')
        if args.list_families:
            result = catalog['families']
            print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else '\n'.join(
                f'{f["id"]} {f["name"]}: S{f["start"]:03d}-S{f["end"]:03d}' for f in result))
            return 0
        if args.id:
            cards = [c for c in cards if c['id'] in args.id]
        if args.family:
            cards = [c for c in cards if c['family'] in args.family]
        if args.query:
            terms = args.query.casefold().split()
            cards = [c for c in cards if all(term in (
                json.dumps(c, ensure_ascii=False) + families[c['family']]['name']
            ).casefold() for term in terms)]
        total = len(cards)
        cards = cards[:args.limit or (60 if args.id else 5)]
        if args.json:
            print(json.dumps({'matched': total, 'returned': len(cards), 'styles': cards}, ensure_ascii=False, indent=2))
        elif cards:
            names = {k: v['name'] for k, v in families.items()}
            print(f'匹配{total}项，显示{len(cards)}项；风格片段需融入实际设计。\n\n' + '\n\n'.join(render(c, names) for c in cards))
        else:
            print('没有匹配的风格；请调整关键词或分类。')
        return 0 if total else 1
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f'Style library error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
