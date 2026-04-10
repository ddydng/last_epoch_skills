#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def load_epoch_json(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("EPOCH"):
        raise ValueError(f"{path} is not a Last Epoch save file")
    return json.loads(text[5:])


def save_epoch_json(path: Path, payload):
    path.write_text("EPOCH" + json.dumps(payload, separators=(",", ":"), ensure_ascii=False), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--save", required=True)
    args = parser.parse_args()

    path = Path(args.save)
    data = load_epoch_json(path)
    trees = data.get("savedSkillTrees", [])
    if not trees:
        raise SystemExit("savedSkillTrees is empty; nothing to reset")

    for tree in trees:
        tree["xp"] = 5_700_000
        tree["nodeIDs"] = []
        tree["nodePoints"] = []
        tree["unspentPoints"] = 20
        tree["nodesTaken"] = []
        tree["abilityXP"] = 0.0

    data["savedSkillTrees"] = trees
    save_epoch_json(path, data)

    print(json.dumps({
        "abilityBar": data.get("abilityBar"),
        "savedSkillTrees": [
            {
                "treeID": tree.get("treeID"),
                "slotNumber": tree.get("slotNumber"),
                "xp": tree.get("xp"),
                "unspentPoints": tree.get("unspentPoints"),
            }
            for tree in trees
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
