#!/usr/bin/env python3
"""Read-only structural checks. Does not teach, grade, migrate, or write records."""
import argparse
import copy
import json
import re
from pathlib import Path

SECTIONS = ("Reading", "Listening", "Writing", "Speaking")
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def score(value):
    require(integer(value, 0, 5), "familiarity must be an integer 0–5")


def load(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: require(False, f"invalid number: {value}"))


def keys(value, example, context):
    require(isinstance(value, dict), f"{context}: expected an object")
    require(set(value) == set(example), f"{context}: key mismatch; missing "
            f"{set(example) - set(value)}, unexpected {set(value) - set(example)}")


def templates(root):
    text = (root / "AGENTS.md").read_text(encoding="utf-8")
    require(sum(bool(re.match(r"\s*```", line)) for line in text.splitlines()) % 2 == 0,
            "AGENTS.md has an unmatched code fence")
    objects = [json.loads(block) for block in re.findall(
        r"^```json\n(.*?)^```", text, re.M | re.S)]
    selectors = {
        "lesson": lambda obj: "Focus" in obj,
        "state": lambda obj: "pending_action" in obj,
        "vocab": lambda obj: "headword" in obj,
        "grammar": lambda obj: "assessment_id" in obj,
        "question": lambda obj: "attempts" in obj,
        "attempt": lambda obj: "response_audio_path" in obj,
        "clarification": lambda obj: "clarification_number" in obj,
    }
    result = {}
    for name, selector in selectors.items():
        matches = [obj for obj in objects if selector(obj)]
        require(len(matches) == 1, f"expected one canonical {name} JSON example")
        result[name] = matches[0]
    require(result["lesson"]["schema_version"] == 9, "checker expects lesson schema 9")
    return result


def validate_evaluation(evaluation, lesson_id):
    fields = """schema_version lesson_id familiarity_policy progress_policy status created_at applied_at
        source_lesson_ids historical_lesson_ids exception_authorization lesson_start progress_before
        progress_after unlocked_levels_before unlocked_levels_after new_unlocks selected_level_at_evaluation
        items review_questions uncertain_questions skipped_questions summary""".split()
    keys(evaluation, dict.fromkeys(fields), "embedded evaluation")
    require(evaluation["schema_version"] == 6, "expected embedded evaluation schema 6")
    require(evaluation["lesson_id"] == lesson_id, "embedded evaluation belongs to another lesson")
    require(evaluation["status"] in ("pending", "applied"), "invalid evaluation status")
    require((evaluation["status"] == "pending" and evaluation["applied_at"] is None) or
            (evaluation["status"] == "applied" and isinstance(evaluation["applied_at"], str)
             and evaluation["applied_at"]), "invalid evaluation application timestamp")
    sources = evaluation["source_lesson_ids"]
    require(isinstance(sources, list) and 1 <= len(sources) <= 3 and
            all(isinstance(s, str) for s in sources) and len(set(sources)) == len(sources)
            and sources[-1] == lesson_id, "invalid embedded evaluation window")
    require(evaluation["historical_lesson_ids"] == sources[:-1], "historical window mismatch")
    require(isinstance(evaluation["new_unlocks"], list), "new_unlocks must be an array")
    for event in evaluation["new_unlocks"]:
        keys(event, dict.fromkeys(("level", "source_level", "source_progress_percent", "lesson_id",
                                  "evaluation_lesson_path", "recorded_at")), "unlock event")
        require(event["lesson_id"] == lesson_id and
                event["evaluation_lesson_path"] == f"lessons/{lesson_id}/lesson.json",
                "unlock must point to its lesson, not an external log")
    require(isinstance(evaluation["items"], list), "evaluation items must be an array")
    seen = set()
    for item in evaluation["items"]:
        fields = """bank word part_of_speech grammar_id old_familiarity new_familiarity S E accuracy
            current_S current_E current_accuracy reason observations""".split()
        keys(item, dict.fromkeys(fields), "evaluation item")
        score(item["old_familiarity"])
        score(item["new_familiarity"])
        require(abs(item["new_familiarity"] - item["old_familiarity"]) <= 1,
                "familiarity delta exceeds one point")
        require((item["bank"] == "vocabulary" and isinstance(item["word"], str)
                 and isinstance(item["part_of_speech"], str) and item["grammar_id"] is None)
                or (item["bank"] == "grammar" and isinstance(item["grammar_id"], str)
                    and item["word"] is None and item["part_of_speech"] is None),
                "invalid changed-item identity")
        identity = (item["bank"], item["word"], item["part_of_speech"], item["grammar_id"])
        require(identity not in seen, "duplicate evaluation item")
        seen.add(identity)
        require(isinstance(item["reason"], str) and item["reason"], "missing change reason")
        require(isinstance(item["observations"], list), "observations must be an array")
        for s, e, accuracy in (("S", "E", "accuracy"), ("current_S", "current_E", "current_accuracy")):
            require(all(type(item[k]) is int and item[k] >= 0 for k in (s, e)), "invalid evidence count")
            total = item[s] + item[e]
            value = item[accuracy]
            require((total == 0 and value is None) or
                    (total > 0 and type(value) in (int, float) and abs(value - item[s] / total) < 1e-12),
                    "accuracy disagrees with evidence counts")


def validate_lesson(data, shape):
    keys(data, shape["lesson"], "lesson")
    require(data["schema_version"] == 9, "expected schema 9")
    if data["evaluation"] is not None:
        validate_evaluation(data["evaluation"], data["lesson_id"])
        require((data["type"] == "lesson" and data["completed"]) or
                bool(data["evaluation"]["exception_authorization"]),
                "incomplete lesson/trial evaluated without explicit exception")
    require(data["type"] in ("lesson", "trial"), "invalid lesson type")
    require(data["cefr_level"] in LEVELS, "invalid new lesson CEFR band")
    require(data["status"] in ("in_progress", "stopped", "completed"), "invalid root status")
    require(type(data["completed"]) is bool and
            data["completed"] == (data["status"] == "completed"), "completion mismatch")
    require(data["current_section"] in ("Focus", *SECTIONS, None), "invalid section cursor")
    require(data["status"] == "completed" or data["current_section"] is not None,
            "unfinished lesson needs a saved position")
    require(data["status"] != "in_progress" or data["ended_at"] is None,
            "active lesson cannot have an end timestamp")
    require(data["active_sections"] and len(set(data["active_sections"])) == len(data["active_sections"])
            and all(s in SECTIONS for s in data["active_sections"]), "invalid active sections")
    if data["type"] == "lesson":
        require(data["active_sections"] == list(SECTIONS), "full lesson section order/count")
    for field in ("cefr_progress_percent", "vocabulary_progress_percent", "grammar_progress_percent"):
        value = data[field]
        require(value is None or (type(value) in (int, float) and 0 <= value <= 100),
                f"invalid {field}")
    require(data["cefr_progress_percent"] is None or
            type(data["cefr_progress_percent"]) is int, "combined progress must be integer")
    if data["cefr_level"] == "C2":
        require(data["cefr_progress_percent"] is None, "C2 has no combined percentage")
    require(data["policy_history"], "missing policy snapshot history")
    for policy in data["policy_history"]:
        keys(policy, shape["lesson"]["policy_history"][0], "policy history")
    keys(data["Focus"], shape["lesson"]["Focus"], "Focus")
    focus_ids = {}
    for bank in ("vocabulary", "grammar"):
        ids = []
        for item in data["Focus"][bank]:
            keys(item, shape["vocab" if bank == "vocabulary" else "grammar"], f"Focus {bank}")
            score(item["familiarity_at_start"])
            ids.append(item["id"])
        require(len(set(ids)) == len(ids), f"duplicate Focus {bank} ID")
        focus_ids[bank] = set(ids)
    generation = data["current_section"] == "Focus"
    if not generation:
        require(len(focus_ids["vocabulary"]) == 8 and len(focus_ids["grammar"]) == 4,
                "ready lesson requires eight vocabulary and four grammar targets")
    for section in SECTIONS:
        part = data[section]
        keys(part, shape["lesson"][section], section)
        require(part["status"] in ("not_started", "in_progress", "completed", "stopped"),
                f"{section}: invalid status")
        if section not in data["active_sections"]:
            require(part == {"status": "not_started", "current_item": None, "items": []},
                    "unused trial section must stay empty")
            continue
        if not generation:
            require(len(part["items"]) == 4, f"{section}: expected four questions")
        ids = [q["id"] for q in part["items"]]
        require(len(set(ids)) == len(ids), f"{section}: duplicate question IDs")
        require(part["current_item"] is None or part["current_item"] in ids, "invalid item cursor")
        for q in part["items"]:
            keys(q, shape["question"], "question")
            require(q["status"] in ("not_started", "awaiting_answer", "retry", "correct", "skipped"),
                    "invalid question status")
            for bank in ("vocabulary", "grammar"):
                require(set(q[f"focus_{bank}_ids"]) <= focus_ids[bank], "unknown Focus reference")
            keys(q["audio"], shape["question"]["audio"], "audio")
            for speed_name, speed in (("normal", 1), ("slow", .75), ("very_slow", .5)):
                audio = q["audio"][speed_name]
                expected = section in ("Listening", "Speaking") or (section == "Reading" and speed_name == "normal")
                if not generation:
                    require((audio is not None) == expected, "missing or unexpected audio version")
                if audio is not None:
                    keys(audio, {"path": None, "speed": None}, "audio version")
                    require(type(audio["speed"]) in (int, float) and audio["speed"] == speed,
                            "incorrect audio speed")
                    require(isinstance(audio["path"], str) and audio["path"].startswith("audio/")
                            and ".." not in Path(audio["path"]).parts, "unsafe generated audio path")
            if not generation:
                require(all(isinstance(q[k], str) and q[k] for k in ("french", "english")),
                        "missing source/reference text")
                require(q["target_words"]["min"] <= len(q["french"].split()) <= q["target_words"]["max"],
                        "French word count outside saved target range")
            for number, attempt in enumerate(q["attempts"], 1):
                keys(attempt, shape["attempt"], "attempt")
                require(attempt["attempt_number"] == number, "attempt numbering mismatch")
                require(attempt["verdict"] in ("Correct", "Almost correct", "Needs revision", "Skipped"),
                        "invalid verdict")
                require(isinstance(attempt["corrections"], list) and
                        all(isinstance(s, str) for s in attempt["corrections"]), "invalid corrections")
                require(type(attempt["reference_revealed"]) is bool and
                        type(attempt["reference_shown_before_attempt"]) is bool, "invalid reveal flags")
                require(not attempt["reference_revealed"] or attempt["verdict"] == "Correct",
                        "reference revealed before Correct")
            if q["status"] in ("awaiting_answer", "retry"):
                require(data["current_section"] == section and part["current_item"] == q["id"],
                        "pending question does not match the saved cursor")
            if q["status"] in ("correct", "skipped", "retry"):
                require(q["attempts"], "answered/retry question has no attempt")
                expected_verdicts = {"correct": ("Correct",), "skipped": ("Skipped",),
                                     "retry": ("Almost correct", "Needs revision")}
                require(q["attempts"][-1]["verdict"] in expected_verdicts[q["status"]],
                        "question status disagrees with latest verdict")
        if part["status"] == "completed":
            require(part["current_item"] is None and part["items"] and
                    all(q["status"] in ("correct", "skipped") for q in part["items"]),
                    "section completion mismatch")
    if data["completed"]:
        require(data["current_section"] is None and data["ended_at"] is not None and
                all(data[s]["status"] == "completed" for s in data["active_sections"]),
                "root completion mismatch")
    for number, entry in enumerate(data["clarifications"], 1):
        keys(entry, shape["clarification"], "clarification")
        require(entry["clarification_number"] == number, "clarification numbering mismatch")
        require(entry["explanation"] and all(isinstance(s, str) for s in entry["explanation"]),
                "missing clarification text")
        require(type(entry["full_reference_revealed"]) is bool, "invalid clarification reference flag")
        for target in entry["assistance_targets"]:
            keys(target, {"bank": None, "word": None, "part_of_speech": None, "grammar_id": None},
                 "assistance target")
            require((target["bank"] == "vocabulary" and isinstance(target["word"], str)
                     and isinstance(target["part_of_speech"], str) and target["grammar_id"] is None)
                    or (target["bank"] == "grammar" and isinstance(target["grammar_id"], str)
                        and target["word"] is None and target["part_of_speech"] is None),
                    "invalid assistance target identity")
        if entry["section"] == "Focus":
            require(entry["item_id"] is None and entry["after_attempt_number"] == 0,
                    "invalid Focus clarification position")
        else:
            require(entry["section"] in data["active_sections"], "invalid clarification section")
            matches = [q for q in data[entry["section"]]["items"] if q["id"] == entry["item_id"]]
            require(len(matches) == 1 and integer(entry["after_attempt_number"], 0, len(matches[0]["attempts"])),
                    "invalid clarification question/attempt reference")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    shape = templates(root)
    if args.self_test:
        validate_lesson(copy.deepcopy(shape["lesson"]), shape)
        for mutate in (lambda d: d.update(completed=True),
                       lambda d: d.update(cefr_progress_percent=1.5),
                       lambda d: d.update(policy_history=[]),
                       lambda d: d.update(user_answer="wrong key")):
            data = copy.deepcopy(shape["lesson"])
            mutate(data)
            try:
                validate_lesson(data, shape)
            except ValueError:
                continue
            raise ValueError("self-test accepted an invalid lesson")
        for value in (-1, 6, True, 2.5):
            try:
                score(value)
            except ValueError:
                continue
            raise ValueError("self-test accepted invalid familiarity")
        print("Self-tests passed: canonical skeleton and eight invalid-data checks.")
        evaluation = {
            "schema_version": 6, "lesson_id": "test", "familiarity_policy": "familiarity-v2",
            "progress_policy": "progress-v5", "status": "pending",
            "created_at": "2026-09-09T09:00:00-04:00", "applied_at": None,
            "source_lesson_ids": ["test"], "historical_lesson_ids": [],
            "exception_authorization": None, "lesson_start": {}, "progress_before": [],
            "progress_after": [], "unlocked_levels_before": ["A1"], "unlocked_levels_after": ["A1"],
            "new_unlocks": [], "selected_level_at_evaluation": "A1", "items": [],
            "review_questions": [], "uncertain_questions": [], "skipped_questions": [], "summary": [],
        }
        validate_evaluation(evaluation, "test")
        evaluation.update(status="applied", applied_at="2026-09-09T09:01:00-04:00")
        validate_evaluation(evaluation, "test")  # Applied with zero changes is valid, not null.
        evaluation["items"] = [{
            "bank": "vocabulary", "word": "test", "part_of_speech": "noun", "grammar_id": None,
            "old_familiarity": 1, "new_familiarity": 2, "S": 1, "E": 0, "accuracy": 1,
            "current_S": 1, "current_E": 0, "current_accuracy": 1,
            "reason": "Synthetic structural test; not a learner assessment.", "observations": [],
        }]
        validate_evaluation(evaluation, "test")
        for mutate in (lambda e: e.update(lesson_id="another"),
                       lambda e: e.update(applied_at=None),
                       lambda e: e.update(source_lesson_ids=["test", "test"]),
                       lambda e: e["items"][0].update(new_familiarity=4),
                       lambda e: e["items"][0].update(accuracy=100),
                       lambda e: e["items"].append(copy.deepcopy(e["items"][0])),
                       lambda e: e["items"][0].update(reason="")):
            invalid = copy.deepcopy(evaluation)
            mutate(invalid)
            try:
                validate_evaluation(invalid, "test")
            except ValueError:
                continue
            raise ValueError("self-test accepted an invalid embedded evaluation")
        print("Embedded-evaluation tests passed: pending, no-change, changed-item, and seven invalid cases.")
        # A self-contained stopped trial is a valid exceptional evaluation fixture;
        # no log directory, journal file, or filesystem access is needed here.
        standalone = copy.deepcopy(shape["lesson"])
        standalone.update(lesson_id="test", type="trial", status="stopped",
                          ended_at="2026-09-09T09:02:00-04:00")
        standalone["evaluation"] = copy.deepcopy(evaluation)
        standalone["evaluation"]["exception_authorization"] = "Synthetic test authorization."
        validate_lesson(standalone, shape)
        for obsolete in ("assessment_log_path", "evaluation_log_path"):
            invalid = copy.deepcopy(standalone)
            invalid[obsolete] = None
            try:
                validate_lesson(invalid, shape)
            except ValueError:
                continue
            raise ValueError("self-test accepted an obsolete external-log field")
        unlock = {"level": "A2", "source_level": "A1", "source_progress_percent": 80,
                  "lesson_id": "test", "evaluation_lesson_path": "lessons/test/lesson.json",
                  "recorded_at": "2026-09-09T09:02:00-04:00"}
        standalone["evaluation"]["new_unlocks"] = [unlock]
        validate_lesson(standalone, shape)
        unlock["evaluation_lesson_path"] = "assessments/log/test.json"
        try:
            validate_lesson(standalone, shape)
        except ValueError:
            pass
        else:
            raise ValueError("self-test accepted an external-log unlock reference")
        print("Lesson-only tests passed: standalone evaluation, obsolete-field rejection, and unlock reference.")
    vocab = load(root / "assessments/vocabulary.json")
    grammar = load(root / "assessments/grammar.json")
    entries = vocab["entries"]
    rules = [r for category in grammar["categories"] for r in category["rules"]]
    require(len({(e["word"], e["part_of_speech"]) for e in entries}) == len(entries),
            "duplicate vocabulary identities")
    require(len({r["id"] for r in rules}) == len(rules), "duplicate grammar IDs")
    for item in entries + rules:
        score(item["familiarity"])
    level = load(root / "assessments/level.json")
    require(level["cefr_level"] in level["unlocked_levels"], "selected band is locked")
    require(level["unlocked_levels"] == [s for s in LEVELS if s in level["unlocked_levels"]],
            "unlocked levels have invalid values, order, or duplicates")
    if (root / "state.json").exists():
        state = load(root / "state.json")
        keys(state, shape["state"], "state")
        require(state["schema_version"] == 1 and state["mode"] in ("real", "isolated_test"),
                "unsupported state format/mode")
        require(state["page"] in ("welcome", "begin", "resume", "stats", "level", "archive_list",
                                  "archive", "help", "lesson", "review"), "invalid navigation page")
        require(state["pending_action"] in ("menu_choice", "new_lesson_confirmation", "resume_choice",
                    "level_choice", "archive_choice", "archive_continue", "lesson_answer", None),
                "invalid navigation action")
        require(type(state["page_number"]) is int and state["page_number"] >= 1, "invalid page number")
        require((state["mode"] == "real" and state["test_root"] is None) or
                (state["mode"] == "isolated_test" and isinstance(state["test_root"], str)
                 and Path(state["test_root"]).is_absolute()), "invalid test-root pointer")
    count = 0
    for path in sorted((root / "lessons").glob("*/lesson.json")):
        data = load(path)
        if data.get("schema_version", 0) < 9:
            print(f"Legacy record preserved; not checked against schema 9: {path.parent.name}")
        else:
            validate_lesson(data, shape)
            require(data["lesson_id"] == path.parent.name, "lesson ID/folder mismatch")
            for policy in data["policy_history"]:
                target = (path.parent / policy["rules_path"]).resolve()
                require(target.is_relative_to(path.parent.resolve()) and target.is_file(),
                        "policy snapshot missing or outside lesson")
        count += 1
    print(f"Read-only checks passed: contract examples, {len(entries)} vocabulary entries, "
          f"{len(rules)} grammar rules, level selection, and {count} lesson records.")
    print("These structural checks do not replace semantic grading, full policy review, or audio QA.")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, TypeError, OSError) as exc:
        raise SystemExit(f"CHECK FAILED: {exc}")
