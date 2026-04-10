---
name: last-epoch-specialization-reset
description: Reset a Last Epoch offline character's currently specialized skills to empty trees with 20 free points each using the XP-backed save fields. Use when Codex needs to read the active specialization trees from a local offline save, clear any allocated nodes, and preserve the current specialized skill set while restoring the full unallocated point budget.
---

# Last Epoch Specialization Reset

Use this skill to reset the currently specialized skills on an offline Last Epoch character without changing the chosen skills themselves.

## Workflow

1. Confirm the game is closed before writing save files.
2. Read the target character save from `AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/1CHARACTERSLOT_BETA_*`.
3. Read the current `abilityBar` and `savedSkillTrees`.
4. Reset every existing specialized skill tree in `savedSkillTrees` to:
   - `xp = 5700000`
   - `nodeIDs = []`
   - `nodePoints = []`
   - `unspentPoints = 20`
   - `nodesTaken = []`
   - `abilityXP = 0.0`
5. Preserve the current skill identities, slot numbers, versions, and the rest of the character save.
6. Re-read the file and report the resulting specialized trees.

## Important Notes

- Use the XP-backed approach. Do not only bump `unspentPoints` without setting high tree XP.
- Operate on `savedSkillTrees`, not on passive tree data.
- Preserve the current specialized skills already in the save. Do not replace them with guessed tree IDs.
- If `savedSkillTrees` is empty, stop and report that the character has no specialization records yet.

## Scripts

Use [scripts/reset_specializations.py](scripts/reset_specializations.py).

During development, add `--dry-run` to inspect the resulting summary without writing the target file.

Example:

```bash
python3 scripts/reset_specializations.py \
  --save "/mnt/c/Users/<user>/AppData/LocalLow/Eleventh Hour Games/Last Epoch/Saves/1CHARACTERSLOT_BETA_0"
```
