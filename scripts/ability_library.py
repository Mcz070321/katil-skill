"""Read-only lookup and validation for KATIL-skill's bundled ability cards."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


LIBRARY = Path(__file__).resolve().parents[1] / "references" / "ability-library"
FIELDS = {"id", "name", "category", "world", "roles", "mechanism", "action", "vfx", "counter_limit", "camera_sound", "residue", "signature"}
LABELS = {
    "mechanism": "机制与用途", "action": "动作与应答", "vfx": "特效描写",
    "counter_limit": "限制与反制", "camera_sound": "镜头与声音", "residue": "残留与连续性",
}


def load_library() -> tuple[dict, list[dict]]:
    bundled = LIBRARY / "abilities.json"
    if bundled.is_file():
        data = json.loads(bundled.read_text(encoding="utf-8"))
        return data, list(data["abilities"])
    catalog = json.loads((LIBRARY / "catalog.json").read_text(encoding="utf-8"))
    cards = []
    for category in catalog["categories"]:
        shard = json.loads((LIBRARY / category["file"]).read_text(encoding="utf-8"))
        assert shard["category"] == category["id"], "Category metadata mismatch"
        cards.extend(shard["abilities"])
    return catalog, cards


def validate(catalog: dict, cards: list[dict]) -> dict:
    assert len(cards) == catalog["count"], "Wrong card count"
    expected_ids = [f"A{i:03d}" for i in range(1, catalog["count"] + 1)]
    assert [x["id"] for x in cards] == expected_ids, "IDs must be continuous and ordered"
    assert len({x["name"] for x in cards}) == len(cards), "Duplicate names"
    assert len({x["signature"] for x in cards}) == len(cards), "Duplicate mechanism signatures"
    categories = {x["id"]: x for x in catalog["categories"]}
    for card in cards:
        assert set(card) == FIELDS, f"Wrong fields: {card.get('id')}"
        assert all(isinstance(card[k], str) and card[k].strip() for k in FIELDS - {"roles"}), card["id"]
        assert card["world"] in catalog["worlds"], card["id"]
        assert card["category"] in categories, card["id"]
        category = categories[card["category"]]
        number = int(card["id"][1:])
        assert category["start"] <= number <= category["end"], card["id"]
        assert card["world"] in category["worlds"], card["id"]
        assert isinstance(card["roles"], list) and 1 <= len(card["roles"]) <= 3, card["id"]
        assert len(set(card["roles"])) == len(card["roles"]), card["id"]
        assert all(role in catalog["roles"] for role in card["roles"]), card["id"]
        assert len(card["signature"].split("|")) == 4 and all(x.strip() for x in card["signature"].split("|")), card["id"]
        assert not any(token in str(card) for token in ("TODO", "TBD", "待补", "{LOOK}")), card["id"]
    counts = Counter(x["category"] for x in cards)
    for category in catalog["categories"]:
        assert counts[category["id"]] == category["end"] - category["start"] + 1, category["id"]
    return {
        "result": "PASS", "version": catalog["version"], "count": len(cards),
        "categories": len(categories), "worlds": dict(Counter(x["world"] for x in cards)),
        "category_counts": dict(counts),
    }


def render(card: dict, category_names: dict[str, str]) -> str:
    lines = [f"## {card['id']} {card['name']}",
             f"适用：{card['world']}｜{category_names[card['category']]}｜{'、'.join(card['roles'])}"]
    lines.extend(f"- {label}：{card[key]}" for key, label in LABELS.items())
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="KATIL-skill：只读查询200种角色技能与配套特效。")
    parser.add_argument("--id", nargs="+", help="One or more exact stable IDs, e.g. A051 A081")
    parser.add_argument("--category", nargs="+", help="Category IDs, e.g. C06 C09")
    parser.add_argument("--world", choices=("现实", "科幻", "奇幻"))
    parser.add_argument("--role", nargs="+", help="Required role labels; all supplied roles must match")
    parser.add_argument("--query", help="Whitespace-separated keywords; all must occur in a card")
    parser.add_argument("--limit", type=int, help="Maximum returned cards, 1–200; defaults to 5 unless exact IDs supplied")
    parser.add_argument("--list", action="store_true", help="Print compact ID/name lines")
    parser.add_argument("--json", action="store_true", help="Return JSON instead of Markdown")
    parser.add_argument("--validate", action="store_true", help="Validate bundled cards and print counts")
    args = parser.parse_args(argv)
    try:
        catalog, cards = load_library()
        if args.validate:
            print(json.dumps(validate(catalog, cards), ensure_ascii=False, indent=2))
            return 0
        category_names = {x["id"]: x["name"] for x in catalog["categories"]}
        if args.limit is not None and not 1 <= args.limit <= catalog["count"]:
            parser.error(f"--limit must be 1–{catalog['count']}")
        if args.category and set(args.category) - set(category_names):
            parser.error("Unknown category: " + ", ".join(sorted(set(args.category) - set(category_names))))
        if args.role and set(args.role) - set(catalog["roles"]):
            parser.error("Unknown role: " + ", ".join(sorted(set(args.role) - set(catalog["roles"]))))
        if args.id:
            by_id = {x["id"]: x for x in cards}
            ids = list(dict.fromkeys(x.upper() for x in args.id))
            if set(ids) - set(by_id):
                parser.error("Unknown ability ID: " + ", ".join(sorted(set(ids) - set(by_id))))
            cards = [by_id[x] for x in ids]
        has_filter = any((args.id, args.category, args.world, args.role, args.query))
        if not has_filter and args.limit is None and not args.list and not args.json:
            print(f"能力库 v{catalog['version']}｜{catalog['count']}种｜{len(category_names)}类")
            for category in catalog["categories"]:
                print(f"{category['id']} A{category['start']:03d}—A{category['end']:03d} {category['name']}")
            return 0
        words = args.query.casefold().split() if args.query else []
        selected = [card for card in cards
                    if (not args.category or card["category"] in args.category)
                    and (not args.world or card["world"] == args.world)
                    and (not args.role or all(role in card["roles"] for role in args.role))
                    and all(word in json.dumps({**card, "category_name": category_names[card["category"]]}, ensure_ascii=False).casefold() for word in words)]
        limit = args.limit if args.limit is not None else (len(cards) if args.id else 5)
        selected = selected[:limit]
        if args.json:
            print(json.dumps(selected, ensure_ascii=False, indent=2))
        elif not selected:
            print("没有满足当前筛选条件的条目。请调整条件；不要把未找到的编号或能力当作已存在。")
        elif args.list:
            for card in selected:
                print(f"{card['id']} {card['name']}｜{card['world']}｜{'、'.join(card['roles'])}")
        else:
            print("\n\n".join(render(card, category_names) for card in selected))
        return 0
    except (OSError, ValueError, KeyError, AssertionError) as exc:
        print(f"Ability library error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
