#!/usr/bin/env python3
"""Read-only vocabulary/grammar pages and browser-metadata validation.

Prints one JSON page for the assistant to render. Does not record a visit,
favorite, navigation change, or learning evidence merely by running this tool.
"""

import argparse
import copy
from datetime import datetime
import json
from pathlib import Path
import unicodedata


BANKS = ("vocabulary", "grammar")
LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
DEFAULT_DIRECTIONS = {"recently_visited": "desc", "level": "asc",
                      "alphabetical": "asc", "familiarity": "asc", "favorite": "desc"}
PAGE_SIZE = 20
IDENTITY_FIELDS = {"bank", "word", "part_of_speech", "grammar_id"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique,
                      parse_constant=lambda value: require(False, f"Invalid number: {value}"))


def identity_key(item):
    require(isinstance(item, dict) and IDENTITY_FIELDS <= item.keys(), "Missing bank identity")
    bank, word, pos, grammar_id = (item[k] for k in ("bank", "word", "part_of_speech", "grammar_id"))
    if bank == "vocabulary":
        require(isinstance(word, str) and bool(word) and isinstance(pos, str) and bool(pos)
                and grammar_id is None, "Invalid vocabulary identity")
        return bank, word, pos
    require(bank == "grammar" and word is None and pos is None
            and isinstance(grammar_id, str) and bool(grammar_id), "Invalid grammar identity")
    return bank, grammar_id


def identity(item):
    identity_key(item)
    return {key: item[key] for key in ("bank", "word", "part_of_speech", "grammar_id")}


def timestamp(value):
    require(isinstance(value, str), "Visit time must be an ISO 8601 string")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    require(result.tzinfo is not None and result.utcoffset() is not None,
            "Visit time requires a timezone offset")
    return result.timestamp()


def validate_library(data, records=None):
    require(isinstance(data, dict) and set(data) == {"schema_version", "items"},
            "Invalid library root fields")
    require(type(data["schema_version"]) is int and data["schema_version"] == 1
            and isinstance(data["items"], list), "Unsupported library format")
    known = None if records is None else {identity_key(row) for row in records}
    seen = set()
    for item in data["items"]:
        require(isinstance(item, dict) and set(item) == IDENTITY_FIELDS | {"favorite", "last_visited_at"},
                "Invalid library item fields")
        key = identity_key(item)
        require(key not in seen, "Duplicate library identity")
        require(known is None or key in known, f"Library identity no longer exists in banks: {key}")
        seen.add(key)
        require(type(item["favorite"]) is bool, "Favorite must be a boolean")
        if item["last_visited_at"] is not None:
            timestamp(item["last_visited_at"])


def validate_browser(browser, records=None):
    require(isinstance(browser, dict) and set(browser) == {
        "bank", "sort", "direction", "page_size", "page_number", "rows", "selected_item"},
        "Invalid browser checkpoint fields")
    require(browser["bank"] in BANKS and browser["sort"] in DEFAULT_DIRECTIONS
            and browser["direction"] in ("asc", "desc"), "Invalid browser bank/sort/direction")
    require(type(browser["page_size"]) is int and browser["page_size"] == PAGE_SIZE,
            "Browser page size must be 20")
    page = browser["page_number"]
    require(type(page) is int and page >= 1, "Invalid browser page number")
    rows = browser["rows"]
    require(isinstance(rows, list) and len(rows) <= PAGE_SIZE, "Invalid browser rows")
    known = None if records is None else {identity_key(row) for row in records}
    seen = set()
    for number, row in enumerate(rows, (page - 1) * PAGE_SIZE + 1):
        require(isinstance(row, dict) and set(row) == IDENTITY_FIELDS | {"number"},
                "Invalid browser row fields")
        require(type(row["number"]) is int and row["number"] == number, "Invalid browser row number")
        key = identity_key(row)
        require(row["bank"] == browser["bank"] and key not in seen, "Wrong/duplicate browser identity")
        require(known is None or key in known, "Browser identity no longer exists")
        seen.add(key)
    selected = browser["selected_item"]
    if selected is not None:
        require(isinstance(selected, dict) and set(selected) == IDENTITY_FIELDS,
                "Invalid selected-item fields")
        require(identity_key(selected) in seen, "Selected item is not on the saved page")


def update_metadata(data, target, *, favorite=None, visited_at=None, records):
    """Return a validated proposed update; the caller must save/verify it explicitly.

    Set, never toggle. Call only for a user favorite request or actual detail
    opening. This function does not infer visits, change bank scores, or write.
    """
    validate_library(data, records)
    require(isinstance(target, dict) and set(target) == IDENTITY_FIELDS, "Invalid target fields")
    key = identity_key(target)
    require(key in {identity_key(row) for row in records}, "Target is not in the banks")
    require(favorite is None or type(favorite) is bool, "Favorite must be a boolean")
    if visited_at is not None:
        timestamp(visited_at)
    result = copy.deepcopy(data)
    if favorite is None and visited_at is None:
        return result
    item = next((item for item in result["items"] if identity_key(item) == key), None)
    if item is None:
        item = dict(target, favorite=False, last_visited_at=None)
        result["items"].append(item)
    if favorite is not None:
        item["favorite"] = favorite
    if visited_at is not None:
        require(item["last_visited_at"] is None or timestamp(visited_at) >= timestamp(item["last_visited_at"]),
                "Do not replace a visit with an older timestamp")
        item["last_visited_at"] = visited_at
    validate_library(result, records)
    return result


def selected_row(browser, number):
    """Resolve against the displayed checkpoint, never a freshly sorted page."""
    validate_browser(browser)
    require(type(number) is int, "Use a displayed row number")
    matches = [row for row in browser["rows"] if row["number"] == number]
    require(len(matches) == 1, "That row is not on the displayed page")
    return identity(matches[0])


def load_records(root):
    for relative in ("assessments", "assessments/vocabulary.json",
                     "assessments/grammar.json", "assessments/library.json"):
        require(not (root / relative).is_symlink(), "Symlinked bank/browser storage is not supported")
    vocabulary = read_json(root / "assessments/vocabulary.json")
    grammar = read_json(root / "assessments/grammar.json")
    records = []
    for entry in vocabulary["entries"]:
        records.append({"bank": "vocabulary", "word": entry["word"],
                        "part_of_speech": entry["part_of_speech"], "grammar_id": None,
                        "name": entry["word"], "english_meaning": entry["english_meaning"],
                        "gender": entry.get("gender"), "category": None,
                        "level": entry["cefr_level"], "familiarity": entry["familiarity"]})
    for category in grammar["categories"]:
        for rule in category["rules"]:
            records.append({"bank": "grammar", "word": None, "part_of_speech": None,
                            "grammar_id": rule["id"], "name": rule["rule"],
                            "english_meaning": None, "gender": None, "category": category["name"],
                            "level": rule["level"], "familiarity": rule["familiarity"]})
    require(len({identity_key(row) for row in records}) == len(records), "Duplicate bank identities")
    for row in records:
        require(type(row["familiarity"]) is int and 0 <= row["familiarity"] <= 5,
                "Invalid familiarity; do not replace missing scores with zero")
        require(row["level"] in (*LEVELS, "Unknown"), "Invalid bank level")
    path = root / "assessments/library.json"
    library = read_json(path) if path.exists() else {"schema_version": 1, "items": []}
    validate_library(library, records)
    preferences = {identity_key(item): item for item in library["items"]}
    for row in records:
        prefs = preferences.get(identity_key(row), {})
        row["favorite"] = prefs.get("favorite", False)
        row["last_visited_at"] = prefs.get("last_visited_at")
    return records


def alphabetical(text):
    text = unicodedata.normalize("NFKD", text.casefold().replace("œ", "oe").replace("æ", "ae"))
    return "".join(char for char in text if not unicodedata.combining(char))


def make_page(records, bank, sort="alphabetical", direction=None, page=1):
    require(bank in BANKS and sort in DEFAULT_DIRECTIONS, "Invalid bank or sort")
    direction = DEFAULT_DIRECTIONS[sort] if direction is None else direction
    require(direction in ("asc", "desc"), "Direction must be asc or desc")
    rows = [row for row in records if row["bank"] == bank]
    # Stable ascending tie-breakers apply even to descending primary sorts.
    rows.sort(key=lambda row: (alphabetical(row["name"]), row["name"], identity_key(row)))
    missing = []
    if sort == "recently_visited":
        missing = [row for row in rows if row["last_visited_at"] is None]
        rows = [row for row in rows if row["last_visited_at"] is not None]
        key = lambda row: timestamp(row["last_visited_at"])
    elif sort == "level":
        missing = [row for row in rows if row["level"] == "Unknown"]
        rows = [row for row in rows if row["level"] != "Unknown"]
        key = lambda row: LEVELS.index(row["level"])
    elif sort == "alphabetical":
        key = lambda row: alphabetical(row["name"])
    else:
        key = lambda row: row[sort]
    rows.sort(key=key, reverse=direction == "desc")
    rows += missing  # Never visited / unknown level always last, in either direction.
    pages = max(1, (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE)
    require(type(page) is int and 1 <= page <= pages, f"Choose a page between 1 and {pages}")
    start = (page - 1) * PAGE_SIZE
    return {"bank": bank, "sort": sort, "direction": direction, "page_number": page,
            "page_size": PAGE_SIZE, "total_items": len(rows), "total_pages": pages,
            "items": [dict(row, number=n) for n, row in enumerate(rows[start:start + PAGE_SIZE], start + 1)]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True, help="Explicit verified active data root.")
    parser.add_argument("--bank", choices=BANKS, required=True)
    parser.add_argument("--sort", choices=DEFAULT_DIRECTIONS, default="alphabetical")
    parser.add_argument("--direction", choices=("asc", "desc"))
    parser.add_argument("--page", type=int, default=1)
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        result = make_page(load_records(root), args.bank, args.sort, args.direction, args.page)
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f"BROWSER FAILED: {exc}\nNo records were changed.\n")


if __name__ == "__main__":
    main()
