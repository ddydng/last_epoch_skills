---
name: last-epoch-offline-stash-all-items
description: Reset a Last Epoch offline stash and repopulate it with one copy of every stash-safe equippable base plus every bounded unique or set variant, organized into stash categories and tabs by item family and class requirement. Use when Codex needs to rebuild `STASH_CYCLE_*` and `STASH_CYCLE_*_TAB_*` save files for an offline stash showcase or item reference layout without touching unsupported special-storage item formats.
---

# Last Epoch Offline Stash All Items

Use this skill to wipe an offline stash layout and rebuild it as a categorized item museum.

## Workflow

1. Confirm the game is closed before writing save files.
2. Read the target stash file from `AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/STASH_CYCLE_*`.
3. Rebuild the stash from scratch using the bundled `assets/items_catalog.json`.
4. Create one item entry per stash-safe equippable base subtype.
5. Create one additional item entry for each bounded unique or set variant attached to a stash-safe base subtype.
6. Leave normal affix slots empty. Only keep the intrinsic unique or set identity data that belongs to the item itself.
7. Organize the stash into category tabs such as armor, weapons, accessories, idols, materials, utility, and endgame items.
8. Split class-mixed item families into separate tabs like `Helmet - Mage` or `Relic - Primalist`.
9. Write a Codex backup copy of the current stash files before modifying them.
10. Clear legacy stash arrays and special storage lists, then write a fresh `tabsv2` list plus one `STASH_CYCLE_*_TAB_*` file per generated tab.
11. Re-read or summarize the resulting layout.

## Important Notes

- This skill targets the modern stash format:
  - main stash file: `STASH_CYCLE_*`
  - per-tab files: `STASH_CYCLE_*_TAB_*`
- The script uses `tabID` on stash items and `formatVersion = 2`.
- Regular affix slots are intentionally empty per the current request.
- The bundled `assets/items_catalog.json` is sourced from the live TunkLab item bundle on `2026-04-10` and is tagged with game data version `1.4.2.1`.
- The catalog currently includes `legendaryType` entries, so the generated stash can include purple legendary-only records when they exist in the live item data.
- Some same-name uniques are intentionally preserved more than once when the live data exposes separate unique IDs for different variants, such as alternate `Scales of Eterra` or `Pearls of the Swine` records.
- The script currently excludes unsupported special-storage item groups such as blessings, lenses, shards, runes, glyphs, keys, resonances, woven echoes, and bags. A previous attempt to place those directly into stash tabs corrupted the live stash load path.
- The script clears special storage lists such as `savedShards`, `savedResonances`, `materialsList`, `wovenEchoesList`, and `keysList`.
- The generated layout is currently limited to stash-safe equippables and idols until the modern special-storage schemas are understood well enough to rebuild them safely.

## Scripts

Use [scripts/populate_stash_all_items.py](scripts/populate_stash_all_items.py).

During development, add `--dry-run` to inspect the generated category and tab counts without writing the save files.

Example:

```bash
python3 scripts/populate_stash_all_items.py \
  --stash "/mnt/c/Users/<user>/AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/STASH_CYCLE_7_0" \
  --dry-run
```
