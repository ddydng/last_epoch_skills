---
name: last-epoch-offline-level-50
description: Create or patch a fresh offline Last Epoch character save to level 50 with a requested name, base class, and mastery. Use when Codex needs to bootstrap a brand-new offline character, unlock campaign progress through chapter 3, unlock the story plus arena and dungeon waypoint network, and grant 1 million gold in the stash for that character.
---

# Last Epoch Offline Level 50

Use this skill to bootstrap a fresh offline Last Epoch character from the local save files.

## Inputs

Ask for:
- character name
- class
- mastery
- whether overwriting an existing offline slot is explicitly allowed

Default behavior is to create a brand-new offline character slot. If the user does not specify a slot, detect the next unused `1CHARACTERSLOT_BETA_*` index and write there. Only reuse or overwrite an existing offline slot when the user explicitly asks for that.

## Workflow

1. Confirm the game is closed before writing save files.
2. Confirm whether the user wants a new slot or an overwrite. Treat overwrite as opt-in only.
3. If creating a new slot, detect the next unused `1CHARACTERSLOT_BETA_*` index and clone from a compatible offline template save without modifying the source slot.
4. Read the target character file in `AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/1CHARACTERSLOT_BETA_*`.
5. Read the cycle stash file that matches the character cycle, for example `STASH_CYCLE_7_0`.
6. Map the requested class/mastery to the save integers.
7. Patch the character save so it represents a level-50 offline character with:
   - requested `characterName`
   - requested `characterClass`
   - requested `chosenMastery`
   - `currentExp = 0`
   - `portalUnlocked = true`
   - `reachedTown = true`
   - internally consistent early campaign progression through chapter 3
   - story waypoint network unlocked
   - dungeon and arena travel nodes unlocked
8. Patch the matching stash save so it contains exactly `1000000` gold.
9. Re-read both files and report the final values, including the newly created slot path when applicable.

## Save Rules

- Preserve unrelated inventory and stash tab structures unless the user explicitly asks to replace them.
- Keep writes scoped to:
  - character identity fields
  - mastery/class fields
  - chapter-3 progression fields
  - waypoint fields
  - stash gold
- Do not touch online saves.
- Do not assume older reference save formats match the current save format. Convert scene progress entries to the current key shape when needed.

## References

Read [references/save-notes.md](references/save-notes.md) before patching.

## Scripts

Use [scripts/bootstrap_character.py](scripts/bootstrap_character.py) to perform the patch.

Example:

```bash
python3 scripts/bootstrap_character.py \
  --save "/mnt/c/Users/<user>/AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/1CHARACTERSLOT_BETA_0" \
  --stash "/mnt/c/Users/<user>/AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/STASH_CYCLE_7_0" \
  --name "MyCharacter" \
  --class primalist \
  --mastery shaman
```
