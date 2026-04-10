import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
NEW_CHARACTER_SCRIPT = ROOT / ".agents" / "skills" / "last-epoch-offline-new-character" / "scripts" / "bootstrap_character.py"
RESET_SPECIALIZATIONS_SCRIPT = ROOT / ".agents" / "skills" / "last-epoch-specialization-reset" / "scripts" / "reset_specializations.py"


def load_epoch_json(path: Path):
    text = path.read_text(encoding="utf-8")
    if not text.startswith("EPOCH"):
        raise AssertionError(f"{path} does not start with the EPOCH prefix")
    return json.loads(text[5:])


def run_script(script_path: Path, *args: str):
    return subprocess.run(
        [sys.executable, str(script_path), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


class BootstrapCharacterTests(unittest.TestCase):
    def copy_fixture(self, temp_dir: Path, fixture_name: str, target_name: str):
        target = temp_dir / target_name
        shutil.copyfile(FIXTURES / fixture_name, target)
        return target

    def test_bootstrap_character_updates_requested_fields(self):
        temp_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        save_path = self.copy_fixture(temp_dir, "character_base.epoch", "character.epoch")
        stash_path = self.copy_fixture(temp_dir, "stash_base.epoch", "stash.epoch")

        result = run_script(
            NEW_CHARACTER_SCRIPT,
            "--save",
            str(save_path),
            "--stash",
            str(stash_path),
            "--name",
            "Shieldbearer",
            "--level",
            "75",
            "--class",
            "sentinel",
            "--mastery",
            "Forge Guard",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)

        summary = json.loads(result.stdout)
        self.assertEqual(
            summary,
            {
                "characterName": "Shieldbearer",
                "characterClass": 2,
                "chosenMastery": 1,
                "level": 75,
                "waypoints": 25,
                "quests": 15,
                "gold": 1000000,
                "dryRun": False,
            },
        )

        character = load_epoch_json(save_path)
        stash = load_epoch_json(stash_path)

        self.assertEqual(character["characterName"], "Shieldbearer")
        self.assertEqual(character["characterClass"], 2)
        self.assertEqual(character["chosenMastery"], 1)
        self.assertEqual(character["level"], 75)
        self.assertTrue(character["portalUnlocked"])
        self.assertTrue(character["reachedTown"])
        self.assertEqual(character["inventory"], {"items": [{"id": "amulet", "rarity": "rare"}]})
        self.assertEqual(character["savedMonolithQuests"], [{"id": 7, "echo": 3}])
        self.assertEqual(character["someOtherField"], {"untouched": True})
        self.assertIn("ArenaLobby", character["unlockedWaypointScenes"])
        self.assertEqual(stash["gold"], 1000000)
        self.assertEqual(stash["tabs"], [{"name": "Main", "items": [1, 2]}])
        self.assertEqual(stash["meta"], {"cycle": 7})

    def test_bootstrap_character_dry_run_leaves_inputs_unchanged(self):
        temp_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        save_path = self.copy_fixture(temp_dir, "character_base.epoch", "character.epoch")
        stash_path = self.copy_fixture(temp_dir, "stash_base.epoch", "stash.epoch")
        original_save = save_path.read_text(encoding="utf-8")
        original_stash = stash_path.read_text(encoding="utf-8")

        result = run_script(
            NEW_CHARACTER_SCRIPT,
            "--save",
            str(save_path),
            "--stash",
            str(stash_path),
            "--name",
            "Scout",
            "--level",
            "20",
            "--class",
            "rogue",
            "--mastery",
            "Falconer",
            "--dry-run",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        summary = json.loads(result.stdout)
        self.assertTrue(summary["dryRun"])
        self.assertEqual(save_path.read_text(encoding="utf-8"), original_save)
        self.assertEqual(stash_path.read_text(encoding="utf-8"), original_stash)

    def test_bootstrap_character_rejects_invalid_level(self):
        temp_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        save_path = self.copy_fixture(temp_dir, "character_base.epoch", "character.epoch")
        stash_path = self.copy_fixture(temp_dir, "stash_base.epoch", "stash.epoch")

        result = run_script(
            NEW_CHARACTER_SCRIPT,
            "--save",
            str(save_path),
            "--stash",
            str(stash_path),
            "--name",
            "TooHigh",
            "--level",
            "101",
            "--class",
            "mage",
            "--mastery",
            "Sorcerer",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Level must be between 1 and 100", result.stderr)


class ResetSpecializationsTests(unittest.TestCase):
    def copy_fixture(self, temp_dir: Path, fixture_name: str, target_name: str):
        target = temp_dir / target_name
        shutil.copyfile(FIXTURES / fixture_name, target)
        return target

    def test_reset_specializations_resets_existing_trees(self):
        temp_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        save_path = self.copy_fixture(temp_dir, "character_with_specs.epoch", "character.epoch")

        result = run_script(
            RESET_SPECIALIZATIONS_SCRIPT,
            "--save",
            str(save_path),
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)

        summary = json.loads(result.stdout)
        self.assertFalse(summary["dryRun"])
        self.assertEqual(
            summary["savedSkillTrees"],
            [
                {"treeID": 100, "slotNumber": 1, "xp": 5700000, "unspentPoints": 20},
                {"treeID": 200, "slotNumber": 2, "xp": 5700000, "unspentPoints": 20},
            ],
        )

        character = load_epoch_json(save_path)
        self.assertEqual(character["abilityBar"], [{"slot": 1, "skillId": "Fireball"}, {"slot": 2, "skillId": "Teleport"}])
        self.assertEqual(character["otherData"], {"keep": "yes"})
        for tree in character["savedSkillTrees"]:
            self.assertEqual(tree["xp"], 5700000)
            self.assertEqual(tree["nodeIDs"], [])
            self.assertEqual(tree["nodePoints"], [])
            self.assertEqual(tree["unspentPoints"], 20)
            self.assertEqual(tree["nodesTaken"], [])
            self.assertEqual(tree["abilityXP"], 0.0)

    def test_reset_specializations_dry_run_leaves_input_unchanged(self):
        temp_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        save_path = self.copy_fixture(temp_dir, "character_with_specs.epoch", "character.epoch")
        original_save = save_path.read_text(encoding="utf-8")

        result = run_script(
            RESET_SPECIALIZATIONS_SCRIPT,
            "--save",
            str(save_path),
            "--dry-run",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        summary = json.loads(result.stdout)
        self.assertTrue(summary["dryRun"])
        self.assertEqual(save_path.read_text(encoding="utf-8"), original_save)

    def test_reset_specializations_errors_when_no_skill_trees_exist(self):
        temp_dir = Path(self.enterContext(tempfile.TemporaryDirectory()))
        save_path = self.copy_fixture(temp_dir, "character_without_specs.epoch", "character.epoch")

        result = run_script(
            RESET_SPECIALIZATIONS_SCRIPT,
            "--save",
            str(save_path),
        )

        self.assertEqual(result.returncode, 1)
        self.assertIn("savedSkillTrees is empty; nothing to reset", result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
