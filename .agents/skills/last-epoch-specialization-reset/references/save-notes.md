# Save Notes

## Specialized Skills

- Specialized skills are stored in `savedSkillTrees`.
- The active hotbar lives in `abilityBar`, but the reset must use the existing `savedSkillTrees` records rather than guessing IDs from the bar.

## Reset Shape

For each specialized tree:

- preserve `treeID`
- preserve `slotNumber`
- preserve `version`
- set `xp` high enough that the game grants the full point budget
- clear `nodeIDs`
- clear `nodePoints`
- set `unspentPoints = 20`
- clear `nodesTaken`
- set `abilityXP = 0.0`

This is the XP-backed approach that worked on the local offline save.
