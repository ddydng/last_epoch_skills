# Save Notes

## Main Stash File

- Offline stash saves are plaintext JSON prefixed with `EPOCH`.
- The main stash file lives at `AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/STASH_CYCLE_*`.
- The verified modern fields used by this skill are:
  - `tabsv2`
  - `categories`
  - `savedShards`
  - `savedResonances`
  - `materialsList`
  - `wovenEchoesList`
  - `keysList`
  - `tabs`
  - `savedStashItems`
  - `partitionKey`

## Per-Tab Files

- Each stash tab is stored as its own `STASH_CYCLE_*_TAB_*` file.
- Verified fields on the local save:
  - `displayOrder`
  - `tabId`
  - `categoryId`
  - `iconId`
  - `colorId`
  - `displayName`
  - `tabPriority`
  - `savedItems`
  - `id`
  - `partitionKey`
  - `seqNo`
  - `_etag`
  - `version`

## Item Wrapper Assumption

- Current character equipment uses `containerID`, but stash-tab items still appear to retain `tabID` in the game metadata.
- This skill writes stash items with:
  - `itemData = null`
  - `inventoryPosition`
  - `tabID`
  - `quantity = 1`
  - `formatVersion = 2`

## Item Payloads

- Community tooling still writes compact `data` arrays that start with `2`.
- The game may later normalize those arrays after loading and saving the stash again.
- This skill keeps normal affix slots empty and only encodes bounded unique or set identity bytes.

## Known Unsafe Groups

- A live test showed that placing the following groups directly into stash tabs can break character load:
  - blessings
  - lenses
  - affix shards
  - runes
  - glyphs
  - keys
  - resonances
  - woven echoes
  - bags
- Until their modern storage rules are understood, the skill must treat them as unsupported for stash-tab generation.

## Reset Scope

- The layout is fully regenerated.
- Existing tab files matching `STASH_CYCLE_*_TAB_*` are removed if they are no longer referenced.
- Special storage lists are cleared so the result is a clean, tab-first stash layout.
- Before writing, the script creates a timestamped Codex backup directory beside the stash files.
