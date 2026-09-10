"""Non-destructive tests for fresh-learner setup; all outputs stay in temp dirs."""

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from new_learner import create_learner


SOURCE = Path(__file__).resolve().parents[1]


class NewLearnerTests(unittest.TestCase):
    def test_clean_copy_preserves_source(self):
        protected = list((SOURCE / "assessments").rglob("*.json"))
        protected += list((SOURCE / "lessons").rglob("*"))
        protected += [SOURCE / "AGENTS.md", SOURCE / "state.json"]
        protected = [path for path in protected if path.is_file()]
        before = {path: hashlib.sha256(path.read_bytes()).digest() for path in protected}
        with tempfile.TemporaryDirectory(prefix="french-learner-test-") as temp:
            dest = Path(temp) / "learner"
            create_learner(SOURCE, dest)
            vocab = json.loads((dest / "assessments/vocabulary.json").read_text())
            grammar = json.loads((dest / "assessments/grammar.json").read_text())
            source_vocab = json.loads((SOURCE / "assessments/vocabulary.json").read_text())
            source_grammar = json.loads((SOURCE / "assessments/grammar.json").read_text())
            self.assertEqual(vocab["source"], source_vocab["source"])
            pairs = list(zip(vocab["entries"], source_vocab["entries"], strict=True))
            for a, b in zip(grammar["categories"], source_grammar["categories"], strict=True):
                pairs.extend(zip(a["rules"], b["rules"], strict=True))
            for new, original in pairs:
                self.assertEqual(new["familiarity"], 0)
                self.assertEqual({k: v for k, v in new.items() if k != "familiarity"},
                                 {k: v for k, v in original.items() if k != "familiarity"})
            level = json.loads((dest / "assessments/level.json").read_text())
            self.assertEqual(level, {"cefr_level": "A1", "unlocked_levels": ["A1"], "unlocks": []})
            self.assertEqual(list((dest / "lessons").iterdir()), [])
            for name in ("state.json", ".git", ".kokoro-env", "assessments/backups", "assessments/log"):
                self.assertFalse((dest / name).exists(), name)
            self.assertIn("Gender: Not specified", (dest / "AGENTS.md").read_text())
            subprocess.run([sys.executable, str(dest / "scripts/check_contract.py"),
                            "--root", str(dest), "--self-test"], check=True, capture_output=True)
            # The fresh copy remains usable as a template for another learner.
            create_learner(dest, Path(temp) / "second-learner")
        self.assertEqual(before, {path: hashlib.sha256(path.read_bytes()).digest() for path in protected})

    def test_refuses_existing_and_symlink_destinations(self):
        with tempfile.TemporaryDirectory(prefix="french-learner-test-") as temp:
            existing = Path(temp) / "existing"
            existing.mkdir()
            sentinel = existing / "keep.txt"
            sentinel.write_text("Keep my progress")
            with self.assertRaises(ValueError):
                create_learner(SOURCE, existing)
            self.assertEqual(sentinel.read_text(), "Keep my progress")
            link = Path(temp) / "link"
            link.symlink_to(Path(temp) / "missing")
            with self.assertRaises(ValueError):
                create_learner(SOURCE, link)

    def test_refuses_source_and_nested_destination(self):
        with self.assertRaises(ValueError):
            create_learner(SOURCE, SOURCE)
        with self.assertRaises(ValueError):
            create_learner(SOURCE, SOURCE / "new-learner-test-must-not-exist")


if __name__ == "__main__":
    unittest.main()
