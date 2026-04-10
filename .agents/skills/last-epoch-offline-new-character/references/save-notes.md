# Save Notes

## Character Save

- Files are plaintext JSON prefixed with `EPOCH`.
- Offline character saves live in `AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/1CHARACTERSLOT_BETA_*`.
- Relevant fields for the requested-level bootstrap:
  - `characterName`
  - `characterClass`
  - `chosenMastery`
  - `clickedUnlockMasteriesButton`
  - `level`
  - `currentExp`
  - `reachedTown`
  - `portalUnlocked`
  - `focusedQuest`
  - `savedQuests`
  - `sceneProgresses`
  - `unlockedWaypointScenes`
  - `oneTimeEvents`
  - `savedMonolithQuests`
  - `dungeonCompletion`

## Stash Save

- Gold is stored in the stash save, not the character save.
- The relevant field is the top-level `gold` key in `STASH_CYCLE_*`.

## Class Mapping

- `0 = primalist`
- `1 = mage`
- `2 = sentinel`
- `3 = acolyte`
- `4 = rogue`

## Mastery Mapping

Each class uses the same ordinal pattern in `chosenMastery`:

- `1 = left mastery`
- `2 = middle mastery`
- `3 = right mastery`

Supported class/mastery names in the script:

- `primalist`: `beastmaster`, `shaman`, `druid`
- `mage`: `spellblade`, `sorcerer`, `runemaster`
- `sentinel`: `forge guard`, `paladin`, `void knight`
- `acolyte`: `necromancer`, `lich`, `warlock`
- `rogue`: `bladedancer`, `marksman`, `falconer`

## Chapter-3 Progression

Use the following chapter-3 progression template for a Primalist bootstrap:

- `savedQuests`
- `sceneProgresses`
- `unlockedWaypointScenes`
- `oneTimeEvents`
- `dungeonCompletion`
- arena travel flags

The script contains the normalized embedded template so the skill does not depend on ad hoc local temp files.
