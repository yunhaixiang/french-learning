#!/usr/bin/env python3
"""Create a separate, unused learner folder. Never reset the source project."""

import argparse
import json
import shutil
from pathlib import Path


def create_learner(source: Path, destination: Path) -> None:
    source = source.resolve()
    # Reject even dangling symlinks; mkdir below also refuses existing targets.
    if destination.exists() or destination.is_symlink():
        raise ValueError("Destination already exists. Choose a new folder name.")
    destination = destination.resolve()
    if destination == source or source in destination.parents:
        raise ValueError("Choose a destination outside the source project.")
    if not destination.parent.is_dir():
        raise ValueError("The destination's parent folder must already exist.")

    # An explicit allowlist avoids copying transcripts, backups, environments,
    # navigation pointers, Git history, or other personal files.
    files = ["AGENTS.md", "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md",
             "requirements.txt", ".gitignore", "scripts/kokoro_french.py",
             "scripts/check_contract.py", "scripts/new_learner.py", "scripts/browse_bank.py"]
    for name in files:
        if not (source / name).is_file():
            raise ValueError(f"Missing template file: {name}")
    vocabulary = json.loads((source / "assessments/vocabulary.json").read_text(encoding="utf-8"))
    grammar = json.loads((source / "assessments/grammar.json").read_text(encoding="utf-8"))
    vocabulary["title"] = "French vocabulary bank"
    grammar["title"] = "French grammar bank"
    for item in vocabulary["entries"]:
        item["familiarity"] = 0
    for category in grammar["categories"]:
        for rule in category["rules"]:
            rule["familiarity"] = 0

    # Replace only the new copy's personal profile, preserving the contract.
    contract = (source / "AGENTS.md").read_text(encoding="utf-8")
    before, marker, remainder = contract.partition("## Learner Information\n")
    _, end_marker, after = remainder.partition("## Assessments\n")
    if not marker or not end_marker:
        raise ValueError("Cannot locate the learner profile in AGENTS.md.")
    profile = """
- Name: The user
- Gender: Not specified; ask when relevant to French agreement.
- Languages: Not specified; English is the default instruction language.
- Goal: Preparing for TEF Canada, aiming for NCLC 7 within three years by default.
- Starting point: A1 beginner material (a learning placement, not a certified level).
- Time commitment: Roughly one hour a day; adapt to the user's availability.
- Preferred learning style: Exposure-based learning.
- Setup: Ask the user to confirm their language background, goal, and preferences.

"""
    contract = before + marker + profile + end_marker + after

    destination.mkdir()  # No exist_ok: never merge with or overwrite a learner.
    (destination / "scripts").mkdir()
    (destination / "assessments").mkdir()
    (destination / "lessons").mkdir()
    for name in files:
        if name != "AGENTS.md":
            shutil.copy2(source / name, destination / name)
    (destination / "AGENTS.md").write_text(contract, encoding="utf-8")
    for name, data in (("vocabulary", vocabulary), ("grammar", grammar),
                       ("level", {"cefr_level": "A1", "unlocked_levels": ["A1"], "unlocks": []})):
        (destination / "assessments" / f"{name}.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    # No state.json: the assistant creates a real-mode checkpoint on first use.


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path, help="New folder outside this project; must not exist.")
    args = parser.parse_args()
    try:
        create_learner(Path(__file__).resolve().parents[1], args.destination)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"Could not create learner: {exc}\nSource records were not changed.\n")
    print(f"Created fresh A1 learner: {args.destination.resolve()}")
    print("All familiarity starts at 0. No lesson history, state, or Git history was copied.")
    print("Next: install requirements in that folder and open it in your assistant.")


if __name__ == "__main__":
    main()
