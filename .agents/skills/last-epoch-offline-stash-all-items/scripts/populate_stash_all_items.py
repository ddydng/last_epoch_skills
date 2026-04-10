#!/usr/bin/env python3
import argparse
import shutil
import json
from collections import defaultdict
from datetime import datetime
from pathlib import Path


GRID_WIDTH = 12
GRID_HEIGHT = 17

ARMOR_BASE_TYPES = {0, 1, 2, 3, 4}
WEAPON_BASE_TYPES = {5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 23, 24}
OFFHAND_BASE_TYPES = {17, 18, 19}
ACCESSORY_BASE_TYPES = {20, 21, 22}
IDOL_BASE_TYPES = set(range(25, 34))
ENDGAME_EQUIPPABLE_BASE_TYPES = {34, 35, 36, 37, 38, 39}
SAFE_STASH_EQUIPPABLE_BASE_TYPES = (
    ARMOR_BASE_TYPES
    | WEAPON_BASE_TYPES
    | OFFHAND_BASE_TYPES
    | ACCESSORY_BASE_TYPES
    | IDOL_BASE_TYPES
)

CATEGORY_ORDER = [
    "Armor",
    "Weapons",
    "Offhands",
    "Accessories",
    "Idols",
]

CLASS_ORDER = ["Any", "Primalist", "Mage", "Sentinel", "Acolyte", "Rogue"]

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "assets" / "items_catalog.json"


def load_epoch_json(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("EPOCH"):
        raise ValueError(f"{path} is not a Last Epoch save file")
    return json.loads(text[5:])


def save_epoch_json(path: Path, payload):
    path.write_text(
        "EPOCH" + json.dumps(payload, separators=(",", ":"), ensure_ascii=False),
        encoding="utf-8",
    )


def load_catalog():
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    if "equippable" not in catalog or "non_equippable" not in catalog:
        raise ValueError(f"{CATALOG_PATH} does not contain the expected catalog keys")
    return catalog


def create_codex_backup(stash_path: Path):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    backup_dir = stash_path.parent / f"codex-backup-{stash_path.name}-{timestamp}"
    backup_dir.mkdir(exist_ok=False)

    for path in sorted(stash_path.parent.glob(f"{stash_path.name}*")):
        if path.is_file():
            shutil.copy2(path, backup_dir / path.name)

    return backup_dir


def normalize_display(value: str) -> str:
    return value.strip() if value and value.strip() else "Unknown"


def ordered_bucket_names(buckets):
    ordered = [name for name in CLASS_ORDER if buckets.get(name)]
    remaining = sorted(name for name in buckets if name not in CLASS_ORDER and buckets.get(name))
    return ordered + remaining


def category_for_equippable(base_type: int) -> str:
    if base_type in ARMOR_BASE_TYPES:
        return "Armor"
    if base_type in WEAPON_BASE_TYPES:
        return "Weapons"
    if base_type in OFFHAND_BASE_TYPES:
        return "Offhands"
    if base_type in ACCESSORY_BASE_TYPES:
        return "Accessories"
    if base_type in IDOL_BASE_TYPES:
        return "Idols"
    if base_type in ENDGAME_EQUIPPABLE_BASE_TYPES:
        return "Endgame"
    return "Utility"


def category_for_non_equippable(base_type: int) -> str:
    if base_type in {101, 102, 103}:
        return "Materials"
    if base_type in {106, 107}:
        return "Endgame"
    return "Utility"


def item_kind(base_type: int, unique_id=None) -> str:
    if unique_id is not None:
        if base_type in IDOL_BASE_TYPES:
            return "unique_idol"
        return "unique_equipment"
    if base_type in IDOL_BASE_TYPES:
        return "idol"
    if base_type in ENDGAME_EQUIPPABLE_BASE_TYPES or base_type >= 100:
        return "simple_other"
    return "simple_equipment"


def build_item_data(entry):
    base_type = entry["base_type"]
    sub_type = entry["sub_type"]
    unique_id = entry.get("unique_id")
    kind = entry["kind"]

    if kind == "unique_equipment":
        rarity = 8 if entry.get("set_id") is not None else 7
        data = [
            2,
            base_type,
            sub_type,
            rarity,
            128,
            255,
            255,
            255,
            unique_id // 256,
            unique_id % 256,
        ]
        data.extend([255] * 8)
        data.append(0)
        return data

    if kind == "unique_idol":
        data = [
            2,
            base_type,
            sub_type,
            7,
            128,
            255,
            255,
            255,
            unique_id // 256,
            unique_id % 256,
        ]
        data.extend([255] * 8)
        data.append(4)
        return data

    if kind == "idol":
        return [
            2,
            base_type,
            sub_type,
            2,
            128,
            255,
            255,
            255,
            20,
            0,
            255,
            255,
            255,
            255,
            255,
            255,
            0,
        ]

    if kind == "simple_equipment":
        return [2, base_type, sub_type, 4, 128, 255, 255, 255, 255, 0, 0]

    return [2, base_type, sub_type, 0, 128, 255, 255, 255, 0, 0, 0]


def make_entry(base_type, sub_type, width, height, label, class_name="Any", unique_id=None, set_id=None):
    return {
        "base_type": base_type,
        "sub_type": sub_type,
        "width": width,
        "height": height,
        "label": label,
        "class_name": class_name,
        "unique_id": unique_id,
        "set_id": set_id,
        "kind": item_kind(base_type, unique_id),
    }


def make_title(group_name, class_name, split_by_class, unique=False, page_number=1):
    base = f"{group_name} Uniques" if unique else group_name
    if split_by_class:
        base = f"{base} - {class_name}"
    if page_number > 1:
        base = f"{base} {page_number}"
    return base


def new_grid():
    return [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def fits(grid, x, y, width, height):
    if x + width > GRID_WIDTH or y + height > GRID_HEIGHT:
        return False
    for row in range(y, y + height):
        for column in range(x, x + width):
            if grid[row][column]:
                return False
    return True


def mark(grid, x, y, width, height):
    for row in range(y, y + height):
        for column in range(x, x + width):
            grid[row][column] = True


def first_fit_slot(grid, width, height):
    if width > GRID_WIDTH or height > GRID_HEIGHT:
        raise ValueError(f"Item size {width}x{height} does not fit in the stash grid")
    for y in range(GRID_HEIGHT - height + 1):
        for x in range(GRID_WIDTH - width + 1):
            if fits(grid, x, y, width, height):
                return x, y
    return None


def pack_entries(entries):
    pages = []
    current_grid = new_grid()
    current_page = []

    for entry in entries:
        slot = first_fit_slot(current_grid, entry["width"], entry["height"])
        if slot is None:
            if not current_page:
                raise ValueError(
                    f"Item size {entry['width']}x{entry['height']} does not fit in the stash grid"
                )
            pages.append(current_page)
            current_grid = new_grid()
            current_page = []
            slot = first_fit_slot(current_grid, entry["width"], entry["height"])
            if slot is None:
                raise ValueError(
                    f"Item size {entry['width']}x{entry['height']} does not fit in the stash grid"
                )

        x, y = slot
        mark(current_grid, x, y, entry["width"], entry["height"])
        current_page.append({"entry": entry, "position": {"x": x, "y": y}})

    if current_page:
        pages.append(current_page)

    return pages


def create_tab_specs(category_name, group_name, buckets, unique=False):
    split_by_class = len([name for name in buckets if buckets[name]]) > 1
    specs = []
    for class_name in ordered_bucket_names(buckets):
        entries = buckets[class_name]
        if not entries:
            continue
        pages = pack_entries(entries)
        for index, page in enumerate(pages, start=1):
            specs.append(
                {
                    "category": category_name,
                    "title": make_title(group_name, class_name, split_by_class, unique=unique, page_number=index),
                    "placements": page,
                }
            )
    return specs


def build_tab_specs(catalog):
    specs = []
    skipped_groups = []

    for group in catalog["equippable"]:
        base_type = group["b"]
        if base_type not in SAFE_STASH_EQUIPPABLE_BASE_TYPES:
            skipped_groups.append(normalize_display(group["d"]))
            continue
        width, height = group["g"]
        group_name = normalize_display(group["d"])
        category_name = category_for_equippable(base_type)

        base_buckets = defaultdict(list)
        unique_buckets = defaultdict(list)

        for sub_type in group["s"]:
            class_name = sub_type.get("c") or "Any"
            label = normalize_display(sub_type["d"])
            base_buckets[class_name].append(
                make_entry(base_type, sub_type["i"], width, height, label, class_name=class_name)
            )

            for unique in sub_type.get("u", []):
                unique_buckets[class_name].append(
                    make_entry(
                        base_type,
                        sub_type["i"],
                        width,
                        height,
                        normalize_display(unique["d"]),
                        class_name=class_name,
                        unique_id=unique["i"],
                        set_id=unique.get("s"),
                    )
                )

        specs.extend(create_tab_specs(category_name, group_name, base_buckets, unique=False))
        specs.extend(create_tab_specs(category_name, group_name, unique_buckets, unique=True))

    for group in catalog["non_equippable"]:
        skipped_groups.append(normalize_display(group["d"]))

    return specs, sorted(dict.fromkeys(skipped_groups))


def place_items(placements, tab_id):
    return [
        {
            "itemData": None,
            "data": build_item_data(placement["entry"]),
            "inventoryPosition": placement["position"],
            "tabID": tab_id,
            "quantity": 1,
            "formatVersion": 2,
        }
        for placement in placements
    ]


def ordered_category_names(specs):
    present = {spec["category"] for spec in specs}
    ordered = [name for name in CATEGORY_ORDER if name in present]
    ordered.extend(sorted(name for name in present if name not in CATEGORY_ORDER))
    return ordered


def summarize_tabs(tab_specs):
    preview = []
    for spec in tab_specs[:10]:
        preview.append({"title": spec["title"], "items": len(spec["placements"])})
    return preview


def rebuild_stash(stash_path: Path, dry_run: bool):
    stash = load_epoch_json(stash_path)
    catalog = load_catalog()
    tab_specs, skipped_groups = build_tab_specs(catalog)
    category_names = ordered_category_names(tab_specs)
    category_lookup = {name: index for index, name in enumerate(category_names)}

    total_items = sum(len(spec["placements"]) for spec in tab_specs)
    unique_items = sum(
        1
        for spec in tab_specs
        for placement in spec["placements"]
        if placement["entry"].get("unique_id") is not None
    )
    base_items = total_items - unique_items

    summary = {
        "categories": len(category_names),
        "tabs": len(tab_specs),
        "base_items": base_items,
        "unique_or_set_items": unique_items,
        "total_items": total_items,
        "skipped_groups": skipped_groups,
        "preview_tabs": summarize_tabs(tab_specs),
    }
    if catalog.get("source"):
        summary["catalog_source"] = catalog["source"]

    if dry_run:
        return summary

    backup_dir = create_codex_backup(stash_path)

    partition_key = stash.get("partitionKey") or ""
    new_tab_names = []
    tab_payloads = []

    for tab_id, spec in enumerate(tab_specs):
        tab_name = f"{stash_path.name}_TAB_{tab_id}"
        new_tab_names.append(tab_name)
        tab_payloads.append(
            (
                stash_path.parent / tab_name,
                {
                    "displayOrder": tab_id,
                    "tabId": tab_id,
                    "categoryId": category_lookup[spec["category"]],
                    "iconId": 0,
                    "colorId": 0,
                    "displayName": spec["title"],
                    "tabPriority": None,
                    "savedItems": place_items(spec["placements"], tab_id),
                    "id": tab_name,
                    "partitionKey": partition_key,
                    "seqNo": 0,
                    "_etag": None,
                    "version": 0,
                },
            )
        )

    stash["tabsv2"] = new_tab_names
    stash["categories"] = [
        {
            "categoryId": category_lookup[name],
            "iconId": 0,
            "colorId": 0,
            "displayName": name,
            "displayOrder": category_lookup[name],
            "dirty": False,
        }
        for name in category_names
    ]
    stash["stashTabsCreated"] = True
    stash["savedShards"] = []
    stash["savedResonances"] = []
    stash["materialsList"] = []
    stash["wovenEchoesList"] = []
    stash["keysList"] = []
    stash["tabs"] = []
    stash["savedStashItems"] = []

    existing_tab_files = list(stash_path.parent.glob(f"{stash_path.name}_TAB_*"))
    for path in existing_tab_files:
        if path.name not in new_tab_names:
            path.unlink()

    for path, payload in tab_payloads:
        save_epoch_json(path, payload)

    save_epoch_json(stash_path, stash)
    summary["backup_dir"] = str(backup_dir)
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stash", required=True, help="Path to STASH_CYCLE_*")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Summarize the generated layout without writing files.",
    )
    args = parser.parse_args()

    stash_path = Path(args.stash)
    summary = rebuild_stash(stash_path, dry_run=args.dry_run)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
