#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


CLASS_MAP = {
    "primalist": 0,
    "mage": 1,
    "sentinel": 2,
    "acolyte": 3,
    "rogue": 4,
}

MASTERY_MAP = {
    "primalist": {
        "beastmaster": 1,
        "shaman": 2,
        "druid": 3,
    },
    "mage": {
        "spellblade": 1,
        "sorcerer": 2,
        "runemaster": 3,
    },
    "sentinel": {
        "forgeguard": 1,
        "paladin": 2,
        "voidknight": 3,
    },
    "acolyte": {
        "necromancer": 1,
        "lich": 2,
        "warlock": 3,
    },
    "rogue": {
        "bladedancer": 1,
        "marksman": 2,
        "falconer": 3,
    },
}

CHAPTER3_QUESTS = [
    {"questID": 18, "questStepID": 93, "state": 0, "questBranch": 0, "completeObjectives": [64, 66, 67, 65, 70, 72, 73, 136, 74, 137, 138, 148], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 48, "questStepID": 281, "state": 0, "questBranch": 0, "completeObjectives": [247, 248, 249, 250, 251, 252, 253], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 1, "questStepID": 4, "state": 0, "questBranch": 0, "completeObjectives": [1, 2, 3, 48], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 49, "questStepID": 284, "state": 0, "questBranch": 0, "completeObjectives": [254, 255, 256, 257], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 2, "questStepID": 24, "state": 0, "questBranch": 0, "completeObjectives": [4, 5, 6, 7, 20], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 3, "questStepID": 12, "state": 0, "questBranch": 0, "completeObjectives": [8, 9], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 11, "questStepID": 44, "state": 0, "questBranch": 0, "completeObjectives": [32, 33, 34], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 5, "questStepID": 14, "state": 0, "questBranch": 0, "completeObjectives": [22, 24, 25, 26, 62, 10], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 34, "questStepID": 197, "state": 0, "questBranch": 0, "completeObjectives": [175, 177, 178, 179], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 6, "questStepID": 22, "state": 0, "questBranch": 0, "completeObjectives": [11, 15, 16], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 9, "questStepID": 38, "state": 0, "questBranch": 0, "completeObjectives": [29, 30, 31], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 35, "questStepID": 199, "state": 0, "questBranch": 0, "completeObjectives": [180], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 10, "questStepID": 41, "state": 0, "questBranch": 0, "completeObjectives": [], "failedObjectives": [28], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 8, "questStepID": 33, "state": 0, "questBranch": 0, "completeObjectives": [27], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
    {"questID": 94, "questStepID": 493, "state": 0, "questBranch": 0, "completeObjectives": [404, 405, 406, 407, 408], "failedObjectives": [], "nolongerRelevantObjectives": [], "objectiveProgress": [], "trackStatus": 0},
]

CHAPTER3_SCENE_PROGRESS = [
    {"scene": "Z10", "savedProgress": 64357367807, "version": 1},
    {"scene": "Z20", "savedProgress": 31, "version": 1},
    {"scene": "Z30", "savedProgress": 286537109991325695, "version": 1},
    {"scene": "Z40", "savedProgress": 0, "version": 1},
    {"scene": "A10", "savedProgress": 0, "version": 1},
    {"scene": "A40", "savedProgress": 0, "version": 1},
    {"scene": "A60TR", "savedProgress": 0, "version": 2},
    {"scene": "A4S10", "savedProgress": 0, "version": 1},
    {"scene": "A80", "savedProgress": 0, "version": 1},
    {"scene": "A70", "savedProgress": 0, "version": 1},
    {"scene": "A5S10", "savedProgress": 0, "version": 1},
    {"scene": "A60", "savedProgress": 0, "version": 1},
    {"scene": "A50", "savedProgress": 0, "version": 1},
    {"scene": "A3S10", "savedProgress": 0, "version": 1},
    {"scene": "A90", "savedProgress": 0, "version": 1},
    {"scene": "B10", "savedProgress": 0, "version": 1},
    {"scene": "B1S10", "savedProgress": 0, "version": 1},
    {"scene": "B1S30", "savedProgress": 0, "version": 1},
    {"scene": "B1S40", "savedProgress": 0, "version": 1},
    {"scene": "B20", "savedProgress": 0, "version": 1},
    {"scene": "B2S10", "savedProgress": 0, "version": 1},
    {"scene": "B30", "savedProgress": 0, "version": 1},
    {"scene": "B1S20", "savedProgress": 0, "version": 1},
    {"scene": "B40", "savedProgress": 0, "version": 2},
    {"scene": "B50", "savedProgress": 0, "version": 1},
    {"scene": "A30", "savedProgress": 0, "version": 1},
]

CHAPTER3_WAYPOINTS = [
    "Z20", "Z30", "Z40", "A04", "Z50", "A10", "A30", "A40", "A60TR", "A60",
    "A70", "A80", "A50", "A90", "B10", "B20", "B1S10", "B30", "B40", "B50",
]

CHAPTER3_EVENTS = [
    "captain ring",
    "A30CinematicEvent",
    "A60-70Door",
    "A30SavingLastRefugeIdols",
    "A30RuneDoorOneTime",
    "A30VAActivate",
]

EXTRA_TRAVEL_WAYPOINTS = [
    "Dun1Q10",
    "Dun2Q10",
    "Dun3Q10",
    "ArenaLobby",
    "Arena_1_Forest",
]

ARENA_SCENE_PROGRESS = [
    {"scene": "Arena_5_TOE", "savedProgress": 0, "version": 1},
    {"scene": "Arena_6_Leaves", "savedProgress": 0, "version": 1},
    {"scene": "Arena_6_VoidPit", "savedProgress": 0, "version": 1},
    {"scene": "Arena_4_Lagon", "savedProgress": 0, "version": 1},
    {"scene": "ArenaLobby", "savedProgress": 0, "version": 1},
]

DUNGEON_COMPLETION = [
    {"dungeonID": 0, "tiersCompleted": [0]},
    {"dungeonID": 1, "tiersCompleted": [0]},
    {"dungeonID": 2, "tiersCompleted": [0]},
]


def load_epoch_json(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("EPOCH"):
        raise ValueError(f"{path} is not a Last Epoch save file")
    return json.loads(text[5:])


def save_epoch_json(path: Path, payload):
    path.write_text("EPOCH" + json.dumps(payload, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def normalize_key(value: str) -> str:
    return "".join(ch for ch in value.lower() if ch.isalnum())


def resolve_mastery(class_name: str, mastery_name: str) -> int:
    mastery_lookup = MASTERY_MAP[class_name]
    normalized = normalize_key(mastery_name)
    if normalized not in mastery_lookup:
        supported = ", ".join(sorted(mastery_lookup))
        raise ValueError(f"Unsupported {class_name} mastery: {mastery_name}. Supported: {supported}")
    return mastery_lookup[normalized]


def merge_waypoints(*groups):
    merged = []
    seen = set()
    for group in groups:
        for waypoint in group:
            if waypoint not in seen:
                seen.add(waypoint)
                merged.append(waypoint)
    return merged


def merge_scene_progress(*groups):
    merged = {}
    for group in groups:
        for entry in group:
            merged[entry["scene"]] = entry
    return list(merged.values())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", required=True)
    parser.add_argument("--stash", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--class", dest="class_name", required=True, choices=sorted(CLASS_MAP))
    parser.add_argument("--mastery", required=True)
    args = parser.parse_args()

    class_name = normalize_key(args.class_name)
    mastery_name = args.mastery

    character = load_epoch_json(Path(args.save))
    stash = load_epoch_json(Path(args.stash))

    character["characterName"] = args.name
    character["characterClass"] = CLASS_MAP[class_name]
    character["chosenMastery"] = resolve_mastery(class_name, mastery_name)
    character["clickedUnlockMasteriesButton"] = False
    character["level"] = 50
    character["currentExp"] = 0
    character["reachedTown"] = True
    character["portalUnlocked"] = True
    character["focusedQuest"] = -1
    character["savedQuests"] = CHAPTER3_QUESTS
    character["sceneProgresses"] = merge_scene_progress(CHAPTER3_SCENE_PROGRESS, ARENA_SCENE_PROGRESS)
    character["unlockedWaypointScenes"] = merge_waypoints(CHAPTER3_WAYPOINTS, EXTRA_TRAVEL_WAYPOINTS)
    character["oneTimeEvents"] = CHAPTER3_EVENTS
    character["dungeonCompletion"] = DUNGEON_COMPLETION
    character["previousArenaRunWaves"] = 1
    character["maxWave"] = 1

    stash["gold"] = 1_000_000

    save_epoch_json(Path(args.save), character)
    save_epoch_json(Path(args.stash), stash)

    print(json.dumps({
        "characterName": character["characterName"],
        "characterClass": character["characterClass"],
        "chosenMastery": character["chosenMastery"],
        "level": character["level"],
        "waypoints": len(character["unlockedWaypointScenes"]),
        "quests": len(character["savedQuests"]),
        "gold": stash["gold"],
    }, indent=2))


if __name__ == "__main__":
    main()
