"""Browser sorting, pagination, metadata, and navigation compatibility tests."""

import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from browse_bank import (DEFAULT_DIRECTIONS, identity, identity_key, load_records,
                         make_page, selected_row, update_metadata, validate_browser,
                         validate_library)
from check_contract import templates, validate_navigation
from new_learner import create_learner


ROOT = Path(__file__).resolve().parents[1]


def row(name, *, bank="vocabulary", level="A1", familiarity=0, favorite=False, visited=None, pos="noun"):
    return {"bank": bank, "word": name if bank == "vocabulary" else None,
            "part_of_speech": pos if bank == "vocabulary" else None,
            "grammar_id": name if bank == "grammar" else None, "name": name,
            "level": level, "familiarity": familiarity, "favorite": favorite,
            "last_visited_at": visited}


def browser(page):
    return {key: page[key] for key in ("bank", "sort", "direction", "page_size", "page_number")} | {
        "rows": [dict(identity(item), number=item["number"]) for item in page["items"]],
        "selected_item": None}


class BrowserTests(unittest.TestCase):
    def test_paging_boundaries_and_empty_bank(self):
        rows = [row(f"mot-{number:03}") for number in range(43)]
        pages = [make_page(rows, "vocabulary", page=number) for number in (1, 2, 3)]
        self.assertEqual([len(page["items"]) for page in pages], [20, 20, 3])
        self.assertEqual([item["number"] for page in pages for item in page["items"]], list(range(1, 44)))
        self.assertEqual(len({identity_key(item) for page in pages for item in page["items"]}), 43)
        for invalid in (0, 4, True, 1.5):
            with self.assertRaises(ValueError):
                make_page(rows, "vocabulary", page=invalid)
        empty = make_page(rows, "grammar")
        self.assertEqual((empty["total_pages"], empty["total_items"], empty["items"]), (1, 0, []))

    def test_alphabetical_normalization_and_grammar_rule_sort(self):
        rows = [row("zèbre"), row("école"), row("avion"), row("École"), row("œuf")]
        names = lambda result: [item["name"] for item in result["items"]]
        self.assertEqual(names(make_page(rows, "vocabulary")), ["avion", "École", "école", "œuf", "zèbre"])
        self.assertEqual(names(make_page(rows, "vocabulary", direction="desc")),
                         ["zèbre", "œuf", "École", "école", "avion"])
        grammar = [row("Z99", bank="grammar"), row("A01", bank="grammar")]
        grammar[0]["name"], grammar[1]["name"] = "Articles", "Verbs"
        self.assertEqual(make_page(grammar, "grammar")["items"][0]["grammar_id"], "Z99")

    def test_all_sorts_and_both_directions(self):
        rows = [row("alpha", level="B2", familiarity=4, visited="2026-09-09T08:00:00-04:00"),
                row("beta", level="A1", familiarity=0, favorite=True, visited="2026-09-09T13:00:00+02:00"),
                row("gamma", level="Unknown", familiarity=2)]
        expected = {"alphabetical": ("alpha", "gamma"), "level": ("beta", "alpha"),
                    "familiarity": ("beta", "alpha"), "favorite": ("alpha", "beta"),
                    "recently_visited": ("beta", "alpha")}
        for sort, first in expected.items():
            for index, direction in enumerate(("asc", "desc")):
                result = make_page(rows, "vocabulary", sort, direction)
                self.assertEqual(result["items"][0]["name"], first[index], (sort, direction))
                if sort in ("level", "recently_visited"):
                    self.assertEqual(result["items"][-1]["name"], "gamma")
            self.assertEqual(make_page(rows, "vocabulary", sort)["direction"], DEFAULT_DIRECTIONS[sort])
        self.assertEqual(len(make_page(rows, "vocabulary", "favorite")["items"]), 3)

    def test_metadata_idempotence_and_independence(self):
        rows = [row("livre"), row("livre", pos="adjective"), row("F01", bank="grammar")]
        original = {"schema_version": 1, "items": []}
        target = identity(rows[0])
        starred = update_metadata(original, target, favorite=True, records=rows)
        self.assertEqual(original["items"], [])
        self.assertEqual(starred, update_metadata(starred, target, favorite=True, records=rows))
        self.assertIsNone(starred["items"][0]["last_visited_at"])
        visited = update_metadata(starred, target, visited_at="2026-09-09T10:00:00-04:00", records=rows)
        unstarred = update_metadata(visited, target, favorite=False, records=rows)
        self.assertEqual(unstarred["items"][0]["last_visited_at"], "2026-09-09T10:00:00-04:00")
        other = update_metadata(unstarred, identity(rows[1]), favorite=True, records=rows)
        other = update_metadata(other, identity(rows[2]), favorite=True, records=rows)
        self.assertEqual(len(other["items"]), 3)
        self.assertFalse(other["items"][0]["favorite"])
        self.assertTrue(other["items"][1]["favorite"])
        self.assertEqual(rows[0]["familiarity"], 0)

    def test_invalid_metadata_is_not_silently_repaired(self):
        rows = [row("livre")]
        data = update_metadata({"schema_version": 1, "items": []}, identity(rows[0]), favorite=True, records=rows)
        mutations = [lambda d: d["items"][0].update(favorite=1),
                     lambda d: d["items"][0].update(last_visited_at="2026-09-09T10:00:00"),
                     lambda d: d["items"][0].update(word="unknown"),
                     lambda d: d["items"][0].update(familiarity=5),
                     lambda d: d["items"].append(copy.deepcopy(d["items"][0])),
                     lambda d: d.update(schema_version=True)]
        for mutation in mutations:
            invalid = copy.deepcopy(data)
            mutation(invalid)
            with self.assertRaises(ValueError):
                validate_library(invalid, rows)

    def test_checkpoint_selection_survives_sort_changing_metadata(self):
        rows = [row("alpha"), row("beta")]
        checkpoint = browser(make_page(rows, "vocabulary", "favorite"))
        rows[1]["favorite"] = True
        self.assertEqual(make_page(rows, "vocabulary", "favorite")["items"][0]["name"], "beta")
        self.assertEqual(selected_row(checkpoint, 1)["word"], "alpha")
        with self.assertRaises(ValueError):
            selected_row(checkpoint, 21)
        checkpoint["selected_item"] = identity(rows[1])
        validate_browser(checkpoint, rows)
        for mutation in (lambda b: b.update(page_size=21),
                         lambda b: b["rows"][0].update(number=0),
                         lambda b: b.update(selected_item=identity(row("missing")))):
            invalid = copy.deepcopy(checkpoint)
            mutation(invalid)
            with self.assertRaises(ValueError):
                validate_browser(invalid, rows)

    def test_navigation_versions_and_bank_page_rules(self):
        shape = templates(ROOT)["state"]
        legacy = dict(shape, schema_version=1)
        legacy.pop("browser")
        validate_navigation(legacy, shape)
        rows = [row("livre")]
        current = dict(shape, page="bank_list", pending_action="bank_command",
                       browser=browser(make_page(rows, "vocabulary")))
        validate_navigation(current, shape, rows)
        current["page"] = "bank_item"
        with self.assertRaises(ValueError):
            validate_navigation(current, shape, rows)
        current["browser"]["selected_item"] = identity(rows[0])
        validate_navigation(current, shape, rows)
        current["page_number"] = 2
        with self.assertRaises(ValueError):
            validate_navigation(current, shape, rows)

    def test_real_bank_totals_read_only_and_persisted_preferences(self):
        paths = [ROOT / "state.json", *list((ROOT / "assessments").rglob("*.json")),
                 *list((ROOT / "lessons").rglob("*.json"))]
        before = {path: hashlib.sha256(path.read_bytes()).digest() for path in paths if path.exists()}
        rows = load_records(ROOT)
        for bank in ("vocabulary", "grammar"):
            total = sum(row["bank"] == bank for row in rows)
            first = make_page(rows, bank)
            self.assertEqual(first["total_items"], total)
            last = make_page(rows, bank, page=first["total_pages"])
            self.assertEqual(last["items"][-1]["number"], total)
        with tempfile.TemporaryDirectory(prefix="french-browser-test-") as temp:
            dest = Path(temp) / "learner"
            create_learner(ROOT, dest)
            fresh = load_records(dest)
            self.assertFalse((dest / "assessments/library.json").exists())
            target = identity(fresh[0])
            metadata = update_metadata({"schema_version": 1, "items": []}, target,
                                       favorite=True, visited_at="2026-09-09T12:00:00-04:00", records=fresh)
            (dest / "assessments/library.json").write_text(json.dumps(metadata))
            reloaded = load_records(dest)
            self.assertTrue(reloaded[0]["favorite"])
            self.assertEqual(reloaded[0]["last_visited_at"], "2026-09-09T12:00:00-04:00")
            self.assertEqual(reloaded[0]["familiarity"], 0)
            second = Path(temp) / "new-copy"
            create_learner(dest, second)
            self.assertFalse((second / "assessments/library.json").exists())
        self.assertEqual(before, {path: hashlib.sha256(path.read_bytes()).digest() for path in before})


if __name__ == "__main__":
    unittest.main()
