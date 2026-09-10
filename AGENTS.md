# French-learning project

This is a long term project for the user to learn French. Read this file for a guide to create and teach lessons, quiz the user, update progress, and more. 

## Continuity: read this at every new conversation or context recovery

This file is the authoritative current project contract, not a reminder of a
conversation. Read it completely before teaching, presenting project pages, or
editing learning records. If a tool truncates it, continue reading to the end.
Do not depend on remembered examples, previous replies, or a summary to supply
missing rules. The current contract revision is `2026-09-09.4`; its teaching
policy is `lesson-v1`, lesson schema is 9, embedded evaluation schema is 6,
familiarity policy is `familiarity-v2`, and progress policy is `progress-v5`.
Navigation schema is 2 and the bank-browser policy is `library-v1`; these do not
change lesson/evaluation schemas or learning-score policies.

### Sources of truth and recovery order

1. Read this AGENTS.md, then `state.json` if it exists, to resolve the current
   mode, data root, navigation prompt, and active lesson. Never assume a temporary
   test folder is the real project or vice versa.
2. Read the resolved data root's `assessments/level.json`, bank metadata, lesson
   metadata, and each lesson's embedded evaluation status. Read whole banks only when calculations
   or selection require them. For bank browsing also read `assessments/library.json`
   if present and the saved browser checkpoint. Do not load every historical
   transcript each turn.
3. For teaching, read the selected lesson's saved policy snapshot, Focus, current
   question, all its attempts, and relevant `clarifications`. For evaluation,
   read the three eligible source lessons and their relevant clarifications;
   source attempts, not old aggregate evaluations, supply the evidence.
4. Reconcile the saved UI pointer against the actual lesson. Lesson status and
   attempts are authoritative for teaching position; state.json is authoritative
   only for navigation context. A stale pointer must not reset a question.
5. Check for a completed full lesson without an applied evaluation, a pending
   evaluation, or interrupted cleanup. A legacy lesson with missing/deleted
   external history is not automatically a pending evaluation: show its evaluation
   as unavailable, never infer or reapply old changes from current bank scores.
   Read-only views only flag these. Before
   another lesson or assessment, finish the authorized pending work safely using
   its original ID; never award an extra update. Do not assess a stopped trial.
6. Follow the user's explicit request. If a bare number/Yes/Continue cannot be
   resolved from the saved prompt, ask which action they mean; never guess, grade
   it as French, or start a lesson on that basis.

Current banks own current familiarity; level.json owns level selection/unlocks;
lesson.json owns material, position, attempts, explanations, and its sole evaluation
record. Its `evaluation` object is also the transaction record for applying changes
exactly once. There is no separate assessment-log file or synchronized copy.
Do not recreate `assessments/log/`, including during recovery or isolated tests.
This storage-location rule overrides older lesson policy snapshots that requested
external logs; it does not change their scoring rules. README.md explains these
rules but does not override them.
Examples contain placeholders, not the user's actual data. If required data is
missing, report it as unavailable rather than rebuilding it from assumptions.

### Rule changes and historical compatibility

Implement an explicit permanent user preference in this file and update README.md
when user-facing behavior changes. Replace the superseded rule wherever repeated;
do not merely append a contradictory instruction. Never treat a quiz response or
an explanation request as a rule change. Mention any unresolved conflict instead
of choosing a new scoring heuristic silently.

For every new lesson/trial, save an immutable plain-text `rules.md` copy of this
complete contract in its lesson folder before generating material. Record its
path and revision in the current root object. That snapshot defines the lesson's
generation, teaching, and evaluation behavior when resumed. Current menu layouts
and safety/data-preservation safeguards still apply. Later rule changes apply to
future lessons by default. If the user explicitly changes an active lesson's
rules, preserve the old snapshot, save `rules-02.md` (then 03, etc.), and append a
policy-history event; do not rewrite existing questions, attempts, or snapshots.
Never rerun an applied evaluation under a newer policy.

Increment the affected schema for structural changes; increment the relevant
policy label for behavioral changes. Update the revision, all affected examples,
validation instructions, and compatibility notes together. Never put a new shape
under an existing schema number. Historical schemas remain readable; do not mass
migrate, relabel A0 records, backfill unknown evidence, or reset scores. A legacy
lesson without a policy snapshot uses the current compatible teaching rules, with
that limitation stated when relevant. Its saved counts/material remain intact.

### Durable navigation and test isolation (`state.json`, version 2)

Keep one small `state.json` at the real project root for continuity. Create it
when navigation/lesson work next needs a checkpoint, not with invented history.
All keys below are required; it contains pointers only, never duplicate scores or
reference answers. Stats, Help, and archives may save this UI checkpoint but must
not mutate lessons, banks, evaluations, unlocks, or audio as a browsing side effect.
The bank browser may additionally save favorites and explicit item-detail visits
in `assessments/library.json`. Neither kind of navigation write changes scores.

```json
{
  "schema_version": 2,
  "updated_at": "2026-09-09T09:00:00-04:00",
  "mode": "real",
  "test_root": null,
  "active_lesson_id": null,
  "page": "welcome",
  "pending_action": "menu_choice",
  "choices": [],
  "page_number": 1,
  "archive_lesson_id": null,
  "archive_position": null,
  "browser": null
}
```

- `mode`: `real` or `isolated_test`. `test_root` is null in real mode, otherwise
  the verified absolute path to the explicitly created test copy. This pointer is
  the exception to lesson-relative paths. Do not follow a missing, symlinked, or
  unverified test root; ask how to recover it without falling back to real writes.
- `page`: `welcome`, `begin`, `resume`, `stats`, `level`, `archive_list`,
  `archive`, `help`, `lesson`, `review`, `library`, `bank_list`, or `bank_item`.
- `pending_action`: `menu_choice`, `new_lesson_confirmation`, `resume_choice`,
  `level_choice`, `archive_choice`, `archive_continue`, `lesson_answer`,
  `bank_choice`, `bank_command`, or null.
- `choices`: ordered objects `{ "number": 1, "lesson_id": "..." }` only for
  displayed lesson/trial lists; otherwise `[]`. Preserve this mapping until the
  page is refreshed. Welcome numbers always use the seven fixed menu options.
  Bank-table numbers are stored separately in `browser.rows`, never in `choices`.
- `page_number`: positive integer. `archive_position`: null or an object with
  `section` (Focus/Reading/Listening/Writing/Speaking/Evaluation), `item_id`
  (string or null), and `attempt_number` (integer or null), identifying the next
  undisplayed block. Archive and active lesson IDs are separate nullable strings.
- `browser`: null until a bank has been displayed; otherwise use the exact
  bank-browser checkpoint below. Retain it when returning to Menu so its last
  bank, sort, and page can be recovered without storing the entire bank in state.
  On `bank_list`/`bank_item`, root `page_number` matches `browser.page_number`;
  other pages retain their own pagination conventions.
- Save after presenting a navigable prompt or changing the teaching cursor, and
  before yielding. Menu/Help/stats do not clear the active lesson pointer. Lesson
  changes commit before their navigation checkpoint; on recovery reconcile both.

Existing version-1 navigation remains readable and is not migrated by checks or
this rule edit. On the next navigation write, this feature authorizes a one-time
navigation-only upgrade: preserve the exact original as `state.json.pre-v1.bak`
without overwriting an existing backup, add `browser: null`, and set version 2.
Preserve every existing field, especially mode, test_root, and active lesson;
then apply only the requested navigation. New checkpoints use version 2.
Never migrate lessons or banks as part of this upgrade. If an existing backup
conflicts, preserve both files and resolve the conflict before writing.

An explicitly requested dry run uses a separate copied data root, labelled as an
isolated test on pages; all lesson/bank/evaluation/audio writes stay inside that root.
Persist its pointer before proceeding. Shared installed TTS assets may be read,
but do not merge test scores into real banks. Explicit permanent rule edits still
update the real AGENTS.md/README.md; they do not authorize changes to real scores.
When the user ends a test, preserve its records and test-mode pointer until they
explicitly return to real mode. Do not rely on a temporary directory for long-term
retention: identify temporary test storage as disposable, never as a backup.

### Storage and write discipline

Use UTF-8 JSON, two-space indentation, a final newline, valid JSON numbers (no
NaN/Infinity), and the documented key types. Empty arrays are `[]`; unknown values
are null, never empty strings or zero substitutes. Save actual ISO 8601 timestamps
with timezone offsets; do not invent historical timestamps. Paths in records are
relative to their documented root; reject path traversal and symlink escapes.
Resolve absolute paths only for display/playback. Avoid hard-coded home paths in
instructions; resolve the project root from the actual workspace.

Read the latest file before editing, preserve unrelated fields and existing order,
validate the intended result, write, and parse it again. Keep a recoverable backup
before a bank update: copy the exact pre-update vocabulary.json, grammar.json,
and level.json to `assessments/backups/<lesson_id>/` within the active data root.
Create this backup once before applying the pending evaluation; never overwrite it with
partially updated files during recovery. Backups are not active banks, lessons,
or evaluation records and must be excluded from lookup/calculation. Before any
separately authorized schema migration, preserve the original file as
`<filename>.pre-v<old-version>.bak` without overwriting an existing backup.
No migration is authorized by routine teaching.
Never infer a successful save from a planned edit or continue advancing after a
failed save. Report the failure and preserve the response for retry. Do not merge
parallel writers or deduplicate genuine retries merely because their text matches.
If delivery/save history is ambiguous, reconcile actual evidence or ask rather than
appending a guessed duplicate. No response or score is reconstructed from memory.

## Learner Information

- Name: The user
- Gender: Male
- Languages: Mandarin (Native), English (Very fluent)
- Goal: Preparing TEF and reach NCLC 7 on TEF Canada within three years
- Starting point: A1 beginner material (a learning placement, not a certified level).
- Time committment: Roughly 1hr a day, sometimes more and sometimes less
- Preferred learning style: Exposure based learning

## Assessments

### Bank storage contract (existing unversioned bank format)

Keep the current bank shapes; do not convert them into a new array/dictionary or
add a separate familiarity file. Both banks store familiarity directly as an
integer 0–5. Do not create a pronunciation bank. Do not invent missing entries or
change their level/meaning/gender to make a lesson or assessment easier to score.

- Vocabulary root keys: `title` (string), `source` (object with string `name`,
  `url`, `license`, `selection`), `familiarity_scale` (object with string keys
  `"0"`–`"5"` and descriptions), `gender_note` (string), `entries` (array).
  Each entry has `word`, `part_of_speech`, `cefr_level`, `english_meaning` (strings)
  and `familiarity` (integer). Noun entries may additionally have `gender`:
  `m`, `f`, `m/f`, or null. Absence is unknown/not applicable, not masculine.
  Preserve the exact `(word, part_of_speech)` identity; source POS `nom` means
  noun but is not silently renamed to `noun`. Levels are A1–C2 or `Unknown`.
  Map bank genders `m`, `f`, `m/f` to lesson `masculine`, `feminine`, `both`,
  respectively, without changing bank metadata.
- Grammar root keys: `title`, `scope` (strings), `familiarity_scale` (as above),
  `categories` (array). Categories have `name` and `rules`. Rules have `id`,
  `rule`, `level` (strings), and `familiarity` (integer). IDs are unique across
  all categories. Keep existing category/rule order; levels for new rules are
  A1–C2. No rule-level summaries substitute for actual rule records.
- Preserve all existing source metadata and unknown legacy fields. Missing or
  malformed required fields and duplicate identities require repair, not a
  score update against an arbitrary match. Future bank structural changes need
  an explicitly versioned migration; this audit does not migrate these banks.

- `assessments/vocabulary.json` tracks vocabulary familiarity on the `0`–`5`
  scale defined in Step 12. Each item is a word family.
- `assessments/grammar.json` tracks grammar familiarity on the same `0`–`5`
  scale. Each item is a grammar target. A score of 5 means consistently reliable
  in varied practice, not measured automaticity, speaking fluency, or exam readiness.
- `lessons/<lesson_id>/lesson.json` stores that lesson's evaluation and all
  vocabulary/grammar changes in its root `evaluation` object. No separate log
  folder is used or required.
- `assessments/level.json` stores the user's selected lesson band, unlocked bands,
  and the evidence for each unlock. Changing the selected band does not change
  vocabulary or grammar familiarity.

## Level and progress notation

Display an assessed learning level as `n% CEFR`, for example `70% A2`.
The CEFR label is the current learning band; the percentage measures progress
from that band toward the next: `70% A2` means 70% of the way from A2 toward B1.
It is not quiz accuracy, a confidence percentage, or an official exam score.

Use the sequence A1 → A2 → B1 → B2 → C1 → C2. Store the band and percentage
separately as `cefr_level` and `cefr_progress_percent`; do not put `70% A2`
inside `cefr_level`. Percentages are integers from 0 to 100. The user chooses
the lesson band from their unlocked levels; A1 is unlocked initially.
A displayed progress percentage of at least 80 (80–100) in a band
unlocks the next band. Exactly 80 qualifies; 79 does not. Unlocking does not switch
the selected band automatically, even at 100%. The user may stay at the current
band or select any previously unlocked band for review. Unlocks remain available
if familiarity later decreases. These are curriculum permissions, not certified
CEFR placements. Do not rescale the percentage to make the unlock threshold 100%.

When the user selects an unlocked band, save that choice in
`assessments/level.json` and use it for subsequent lessons. Calculate the selected
band's percentage from its own bank entries using Step 12; never carry another
band's percentage over or reset existing familiarity. Do not rewrite a current
lesson's materials or starting snapshot for a level-selection request. If the
requested band is locked, explain the prerequisite rather than silently unlocking
it. Never discard familiarity already earned in the next band. C2 has no next band in this project, so its
progress percentage is null and it is displayed simply as `C2`.

Use the progress percentage algorithm in Step 12. Do not invent a percentage,
derive it from lesson completion, or treat the example `70% A2`
as the user's actual level. Until calculated, use null for the percentage and
display, for example, `A1 — progress not yet assessed`. An explicitly assigned
beginner baseline of `0% A1` is a starting convention, not evidence of mastery.
Record assessed changes and their supporting evidence in the embedded evaluation.
Each new lesson snapshots the user-selected band and its latest calculated percentage; never
rewrite previous lesson snapshots when the estimate changes.

Keep `assessments/level.json` in this format:

```json
{
  "cefr_level": "A1",
  "unlocked_levels": ["A1"],
  "unlocks": []
}
```

`cefr_level` must be a member of `unlocked_levels`; keep that list unique and in
CEFR order. Each earned unlock appends an object to `unlocks` with `level`,
`source_level`, `source_progress_percent`, `lesson_id`, `evaluation_lesson_path`,
and `recorded_at` (ISO 8601 with timezone). A1 is the starting permission and
needs no earned-unlock event. Never duplicate an unlock on a repeated update.
For new unlock events, evaluation_lesson_path is the project-relative path
`lessons/<lesson_id>/lesson.json`; its evaluation is the supporting record.
Historical events with assessment_log_path remain unchanged; a missing legacy
log does not revoke an earned unlock or justify recreating the log folder.
This file records selection and access, not an independent familiarity score.

## Welcome / starting page

The starting page is a menu in this conversation, not a separate website or
application. Show it when the user asks for the welcome page, starting page,
home, or menu, or greets the assistant without requesting a specific action.
In a new conversation, follow an explicit task directly; do not force the menu
before a request to begin/resume a lesson, view a completed lesson, view stats,
set a level, browse vocabulary/grammar, get help, or edit rules.
Render the following as Markdown, not a code block:

```text
# Welcome to your French learning buddy

1. Begin a new lesson
2. Resume an incomplete lesson
3. View my stats
4. Set my level
5. View a completed lesson
6. Help
7. View vocabulary and grammar

Choose an option by number or name.
```

Accept either the option number or a natural-language equivalent. Interpret a
bare number as a menu choice only when this menu is the current unanswered
prompt, never while the user is answering a lesson question or another numbered
choice. Explicit menu commands can be used during a lesson without recording
them as attempts or changing the saved question/status. Showing the menu alone
does not create, stop, complete, or assess a lesson and does not generate audio.

### Fixed page format contract

All seven welcome-menu destinations and their navigation states use the canonical
templates below. Keep page titles, heading order, field labels, table columns,
and closing prompts fixed across conversations. Substitute actual saved values;
do not redesign, rename, reorder, or add optional dashboard sections on each visit.
Render templates as Markdown, never as code blocks. Include proper table separator
rows and blank lines before headings, lists, and tables. Learning material remains
italicized; navigation labels and instructions remain in regular type.

The welcome menu itself stays exactly as shown above. All other navigation pages
end with `Type Menu to return to the starting page.` Active lesson questions use
their existing section templates instead of adding this navigation footer. Starting,
resuming, Focus, feedback, and Lesson Review reuse the Lesson Procedure templates;
do not invent another lesson format for entry from the menu.

Use Toronto date/time as `YYYY-MM-DD HH:mm:ss`, combined progress as an integer,
and vocabulary/grammar percentages to one decimal place. Preserve the C2 and
unavailable-progress exceptions above. Never fill missing records with invented
values. Keep an empty section's heading and use its defined empty-state message.
For unavailable data use `Unavailable — [specific reason]` in the affected field.
If an evaluation is pending, put `Status: Evaluation pending — scores may be
partially applied.` directly below the page title; do not display mixed values as
final progress. An isolated test uses `Mode: Isolated test — real progress is
unchanged.` directly below the title, before any status line. These are conditional
lines, not extra sections. Editing these instructions does not assess any lesson.

For invalid navigation input, redisplay the same page and put
`Selection: Not recognized — [valid input required].` immediately before its
closing choice prompt. Resolve ambiguous dates/selections on that same page with
only the matching records and `Selection: More than one match — choose a lesson
by number or lesson ID.` Do not interpret these inputs as lesson attempts.
The conditional mode/status/selection lines are the only exceptions to literal
template wording; in an isolated test the welcome page also includes its mode
line. Preserve blank-line field separation in rendered pages, not just source
newlines that Markdown would collapse. Use the saved UI checkpoint for numbered
choices after a context reset; do not reconstruct the list from a new sort order.

### Menu actions

1. **Begin a new lesson:** follow the Lesson Procedure below, including the
   existing confirmation if a lesson is unfinished. Do not generate material
   or create a new lesson folder until that confirmation is resolved. A declined
   confirmation leaves the existing lesson unchanged.
2. **Resume an incomplete lesson:** inspect saved lesson metadata for incomplete
   records (`completed: false`, with `in_progress` or `stopped` status). Prefer
   full lessons; offer an unfinished trial separately, clearly labelled, if
   there is no incomplete full lesson. If more than one full lesson qualifies,
   show their Toronto start dates, levels, and saved sections/passage positions
   and ask the user to choose rather than guessing. If none exists, say so and
   offer option 1 without starting automatically. Resume the selected record
   from its saved cursor, preserving its ID, materials, audio, starting progress,
   and all attempts. For a stopped record, set the root and active section back
   to `in_progress`, clear root `ended_at`, update `updated_at`, and leave
   `completed: false`; completed sections stay completed. Present the pending
   question with its established answer-hiding rules; do not restart the lesson
   or require already completed questions again. If generation was incomplete,
   finish/validate missing material before teaching. Reconcile a missing or
   inconsistent cursor from saved evidence before continuing; never invent work.
3. **View my stats:** read the current banks, level selection/unlocks, lesson
   metadata, and applied lesson evaluations. Show the selected band and calculated
   progress, vocabulary and grammar percentages for that CEFR band only,
   unlocked bands, completed full-lesson count, and any saved unfinished
   lesson/trial positions. Include a concise account of changes from the latest
   applied evaluation if available; otherwise say no evaluation has been logged.
   Count only completed full lessons, never trials or stopped lessons, and do
   not invent study hours from the intended one-hour duration. This is read-only:
   no familiarity changes, regrading, unlock awards, or lesson-snapshot updates.
   If an evaluation is pending, flag that its scores may be partially applied
   and do not present a mixed state as final progress. Use unavailable labels
   for missing components instead of zero. Keep hidden question answers hidden.
4. **Set my level:** read `assessments/level.json` and show the level-selection
   page below. Merely opening the page changes nothing. Accept the name of an
   unlocked CEFR band; update only the saved selection after an explicit choice.
   A locked choice explains its prerequisite without changing the level or
   awarding an unlock. Selecting the current band is a no-op. Follow the Level
   and progress notation rules: the choice affects subsequent lessons, preserves
   familiarity and earned unlocks, and never rewrites an existing lesson.
5. **View a completed lesson:** follow the archive browser below. List completed
   full lessons, let the user select one, and show its complete saved content,
   including every attempt—not just the best answer or final summary. This is
   read-only browsing, not restarting, reassessing, or resuming the lesson.
6. **Help:** briefly explain the four lesson sections, dictation input, audio
   speeds, feedback/retries/skipping, saved progress, and how unlocked level
   selection works. Include the commands `Begin a new lesson`, `Resume my lesson`,
   `View my stats`, `Set my level`, `View a completed lesson`,
   `View vocabulary and grammar`, `Skip`,
   `Stop the lesson`, and `Menu`. Explain that scores
   are learning indicators rather than official CEFR/TEF results. Keep this a
   concise user guide; link to README.md for detail. Do not start or alter a
   lesson as a side effect of help.
7. **View vocabulary and grammar:** show the bank chooser below, then a paginated
   table of the chosen bank. Accept direct `View vocabulary` / `View grammar`
   requests without forcing the chooser. Support all five sorts, explicit item
   visits, and favorites using `library-v1`. Never start a lesson or change scores
   merely because the user browses, sorts, or favorites an item.

### View vocabulary and grammar (`library-v1`)

Keep welcome options 1–6 unchanged and append this as option 7. Use this chooser:

```text
# View vocabulary and grammar

1. Vocabulary
2. Grammar

Choose Vocabulary or Grammar by name or number.
Type Menu to return to the starting page.
```

Use page `library`, pending_action `bank_choice`, and empty `choices`. Here 1/2
select a bank, not a welcome action. Direct bank requests skip the chooser.
Initially use Alphabetical (A–Z), page 1; reopening the same bank preserves its
saved sort/direction/page. Switching banks starts at page 1, Alphabetical (A–Z).
All levels are browsable, including locked lesson bands and Unknown; this awards
no unlock. Use these fixed list templates:

```text
# Vocabulary

Sort: [name] — [direction label]
Page [p] of [pages] — [total] items — 20 per page.

| # | Favorite | Word | Part of speech | Gender | English meaning | Level | Familiarity | Last visited (Toronto) |
|---|---|---|---|---|---|---|---|---|
| [number] | [★ / ☆] | *[stored word]* | [stored POS] | [gender] | *[stored meaning]* | [level] | [n]/5 | [date/time / Never] |

Sort by: Recently visited / Level / Alphabetical / Familiarity / Favorite.
Commands: Next; Previous; Page [n]; Sort [name] [asc/desc]; View [#]; Favorite [#]; Unfavorite [#]; Vocabulary; Grammar.
Type Menu to return to the starting page.
```

```text
# Grammar

Sort: [name] — [direction label]
Page [p] of [pages] — [total] items — 20 per page.

| # | Favorite | ID | Rule | Category | Level | Familiarity | Last visited (Toronto) |
|---|---|---|---|---|---|---|---|
| [number] | [★ / ☆] | [stored ID] | [stored rule] | [stored category] | [level] | [n]/5 | [date/time / Never] |

Sort by: Recently visited / Level / Alphabetical / Familiarity / Favorite.
Commands: Next; Previous; Page [n]; Sort [name] [asc/desc]; View [#]; Favorite [#]; Unfavorite [#]; Vocabulary; Grammar.
Type Menu to return to the starting page.
```

Use 20 rows per page, fewer on the last page. Numbers are positions in the current
ordering: 1–20, 21–40, etc.; they are not permanent IDs. Show full stored meanings
and rules, italicizing language material as usual. Escape table pipes/newlines
without editing bank text. Gender shows Masculine / Feminine / Both / Unknown
for nouns, and — for non-nouns; use stored data, not guessed articles. Grammar
alphabetical order uses full rule text, not ID/category. Missing/malformed banks
or scores are Unavailable with a reason, not zero or a fabricated empty bank.
For an actually empty bank, show Page 1 of 1 — 0 items — 20 per page, retain the
table headers with no data rows, and add `No items in this bank.` after the table.
Reject out-of-range pages/directions without changing the checkpoint.

| Sort | Default direction / label | Reverse direction / label |
|---|---|---|
| Recently visited | desc / Newest first | asc / Oldest first |
| Level | asc / A1 → C2 | desc / C2 → A1 |
| Alphabetical | asc / A–Z | desc / Z–A |
| Familiarity | asc / 0 → 5 | desc / 5 → 0 |
| Favorite | desc / Favorites first | asc / Favorites last |

Store sort names as `recently_visited`, `level`, `alphabetical`, `familiarity`,
or `favorite`. Unknown levels and never-visited items always go last in their
respective sorts, even when reversed. Favorite groups starred items first by
default; it does not hide unstarred entries. Break primary-key ties by normalized
alphabetical name ascending, then exact stored name ascending, then exact bank
identity ascending. Normalize with casefold, œ→oe and æ→ae, Unicode NFKD, and
removal of combining marks; never change stored French. Sort changes reset to
page 1. Pagination alone does not alter visit dates. Numbers may change when an
ordering refreshes; commands always refer to the currently displayed table.

Use the read-only helper to calculate a page without loading every entry into the
conversation (an available Python 3.9+ works; no audio dependencies are needed):

```sh
.kokoro-env/bin/python scripts/browse_bank.py --root [verified-active-data-root] --bank vocabulary --sort alphabetical --direction asc --page 1
```

Resolve mode/data root from state first. In isolated mode pass the verified test
root, never fall back to real data. The script itself neither presents a page
nor records a visit. Render its output with the templates above and checkpoint
only the displayed identities. Use its validators for library metadata and browser
rows; malformed, duplicate, or orphaned identities require repair, never guessing
or silently dropping favorites. It may read the banks, not historical transcripts,
for sorting. Never infer visits from saved familiarity or lesson dates.

#### Item visits and favorites

`View [#]` or a bare displayed row number opens that item. Resolve the number
against the LAST DISPLAYED `browser.rows` before updating metadata or sorting.
A unique exact word plus POS, or grammar ID, can also identify an item. Ask which
POS is intended if a word matches multiple entries; do not favorite all matches.
For a direct item request not on the saved page, calculate and checkpoint its
page in the chosen ordering before opening it. Never interpret a saved number
against a newly sorted list after context recovery.

Details use `# Vocabulary item — *[word]*` or `# Grammar item — [ID]`, then a
two-column `Field | Value` table. Vocabulary fields in order: Word, Part of speech,
Gender, English meaning, Level, Familiarity, Favorite, Last visited (Toronto).
Grammar fields: ID, Rule, Category, Level, Familiarity, Favorite, Last visited
(Toronto). Use the same stored values and formatting as the list. End with:

```text
Commands: Favorite; Unfavorite; Back.
Type Menu to return to the starting page.
```

An explicit detail opening records the actual ISO 8601 time with offset as
`last_visited_at`. Redisplaying that detail after a favorite change does not
count as a new visit. Tables, sorting, paging, favoriting, lessons, previews,
and archives do not update this browser-only timestamp. Missing metadata means
Favorite false and Last visited Never, not missing assessment evidence.

`Favorite [#]` sets true; `Unfavorite [#]` sets false. In details, bare Favorite /
Unfavorite applies to selected_item. These are idempotent set operations, not
toggles. Preserve last_visited_at when favoriting and favorite when visiting.
Use ★ / ☆ for true / false. After a list favorite change, redisplay the SAME
saved rows/order with updated stars. Back from details also restores those rows,
with the updated visit value. Do not renumber underneath a command. When a
favorite or visit has changed, add `Selection: Saved — ordering refreshes on your
next page or sort command.` above the commands. Explicit Sort, Page, Next,
Previous, or re-opening the bank recalculates ordering and saves new row mappings.
If bank identities changed, flag stale navigation and safely refresh before
accepting numbered mutations. Invalid commands do not alter metadata.

Browsing generates no audio, full lesson references, grades, or automatic focus
priority changes. Favorites are preferences, not mastery or a change to lesson
selection. Keep the active lesson, cursor, attempts, and starting snapshots intact.
If a lookup supplies answer-specific help for a pending question, record it under
the existing clarification rules and treat later relevant answers as assisted;
do not reveal a hidden full reference or award a point for viewing a table.
Unrelated browsing and navigation are not lesson attempts.

#### Persistent browser metadata and checkpoint

`assessments/library.json` is optional until the first explicit favorite/visit.
It is preferences only, NOT an assessment log or a copy of bank scores. An absent
file is equivalent to this empty object; do not create it merely for listing:

```json
{
  "schema_version": 1,
  "items": []
}
```

Each sparse items entry has exactly these six fields:

```json
{
  "bank": "vocabulary",
  "word": "être",
  "part_of_speech": "verb",
  "grammar_id": null,
  "favorite": true,
  "last_visited_at": null
}
```

Grammar uses bank `grammar`, word/part_of_speech null, and its exact ID in
grammar_id. Vocabulary uses exact (word, part_of_speech). Identities are unique
and must resolve to their corresponding bank. Favorite is a boolean, not 0/1;
last_visited_at is null or a real timezone-aware ISO 8601 timestamp. Preserve
array order; append an identity once, update in place, and leave others untouched.
Validate and verify saves; never claim success after a failed write. No meanings,
levels, familiarity, lesson changes, or evaluations are stored here. Write only
under the active data root. Fresh-learner copies omit this file, starting with
no visits/favorites. Bank shapes and existing learner data stay unchanged.

The non-null version-2 state.json.browser object has this exact shape:

```json
{
  "bank": "vocabulary",
  "sort": "alphabetical",
  "direction": "asc",
  "page_size": 20,
  "page_number": 1,
  "rows": [],
  "selected_item": null
}
```

Populate rows from the displayed page, at most 20. Each row has exactly number,
bank, word, part_of_speech, and grammar_id, with consecutive global page positions.
selected_item is null in list view, or those four identity fields (without number)
for the detail item on the saved page. Never store a sorted copy of the entire
bank or duplicate scores in state. Use page `bank_list` / `bank_item`, pending_action
`bank_command`, empty choices, and matching root/browser page numbers. Save
metadata before checkpointing; reconcile interruptions without replaying a toggle
or inventing a visit. This rule edit and validation runs do not create visits,
favorites, or a new prompt in the user's live data.

### Begin a new lesson page

With no unfinished session, an explicit request to begin proceeds directly to
generation and the Step 7 `# Lesson` opening, Focus, then the first Reading
question. Do not insert another confirmation or a redundant setup page.

When an unfinished session requires confirmation, use:

```text
# Begin a new lesson

## Unfinished sessions

| Started (Toronto) | Type | Level | Position | Lesson ID |
|---|---|---|---|---|
| [date/time] | [Lesson / Trial] | [saved band] | [section — passage n of count] | [ID] |

We haven't finished the current lesson, are you sure you want to begin a new lesson?
Your existing material and answers will be preserved.

Reply Yes to begin a new lesson, or No to keep the current session unchanged.
Type Menu to return to the starting page.
```

List the relevant unfinished sessions; do not silently choose among ambiguous
records to modify. Confirmation preserves all existing records and only stops the
active session being left, if identifiable. Other unfinished sessions stay as they
are. On No, keep the title and show `No new lesson started. Your existing session
is unchanged.` followed by the Menu footer. On Yes, follow the existing new-lesson
procedure and opening format; do not regenerate the old session.

### Resume an incomplete lesson page

When multiple unfinished full lessons exist, use:

```text
# Resume an incomplete lesson

## Unfinished lessons

| # | Started (Toronto) | Level | Position | Lesson ID |
|---|---|---|---|---|
| [index] | [date/time] | [saved band] | [section — passage n of count] | [ID] |

Choose a lesson by number or lesson ID.
Type Menu to return to the starting page.
```

Order newest start first, breaking ties by lesson ID. If no unfinished full lesson
exists, keep `## Unfinished lessons` and show `No incomplete full lessons.` instead
of an empty table. If trials exist in that case, append `## Unfinished trials`
with the same columns and `Choose a trial by number or lesson ID.` Never resume a
trial automatically, even when there is only one. If neither kind exists, end with
`Type Begin a new lesson to start.` and the Menu footer.

For one unambiguous full lesson, or after a selection, resume directly using:

```text
# Resume an incomplete lesson

Lesson ID: [ID]
Session type: [Lesson / Trial]
Started (Toronto): [date/time]
Level: [original band]
Resume at: [section — passage n of count]

Your saved material, starting progress, and previous attempts are unchanged.
Type Menu to return to the starting page.
```

Then present the pending question using its section's fixed teaching template.
Do not repeat the Focus or manufacture a new starting snapshot. Use `Material
preparation incomplete` for a genuinely unfinished generation position, finish
validation, then present the first pending question.

### View a completed lesson page

Read metadata first and list only records with `type: "lesson"`,
`status: "completed"`, and `completed: true`. Do not include trials, stopped
sessions, or incomplete lessons as completed full lessons. Display newest
completion first, with an index, Toronto date/time, original CEFR band, and
lesson ID so same-day lessons are distinguishable. Read-only browsing must
not complete a pending assessment. If no completed lesson exists, show
`No completed lessons yet.` and the Menu return command.

```text
# View a completed lesson

| # | Completed (Toronto) | Level | Lesson ID |
|---|---|---|---|
| [index] | [date and time] | [saved CEFR band] | [lesson ID] |

Choose a lesson by number, date, or lesson ID.
Type Menu to return to the starting page.
```

When empty, keep the page title, replace the table and choice prompt with
`No completed lessons yet.`, and retain the Menu footer. List ten records per
page with stable indices across pages. Before the choice prompt show
`Page [p] of [total].` and, only when another page exists,
`Type Next or Previous to change pages.` Accept only directions that exist.
If a date matches several lessons, ask which one. Never omit older lessons.
A number here selects from this
displayed list, not the welcome menu. On selection, show a read-only archive:

```text
# Completed lesson — [Toronto date/time]

Lesson ID: [ID]
Level: [original CEFR band]
Progress: [saved starting progress] → [saved ending progress]
Vocabulary progress ([band]): [saved start] → [saved end]
Grammar progress ([band]): [saved start] → [saved end]

## Focus
[All saved vocabulary and grammar cards, meanings, forms, examples, and translations]

## Reading
### Passage [n] of [saved count]
Instruction: [saved instruction]
French: [saved French text]
English: [saved English text]
Status: [saved question status]

#### Attempt [number] — [recorded time, when available]
Your answer: [verbatim saved response]
Verdict: [saved verdict]
Corrections: [all saved corrections, using the arrow format where recorded]
Reference shown before this attempt: [Yes/No]
Reference revealed in this feedback: [Yes/No]

[Repeat every attempt and every question; then Listening, Writing, and Speaking]

## Evaluation
[All saved item changes/reasons, progress, unlocks, and Summary bullets;
or Evaluation unavailable/pending, if no applied evaluation exists]
```

Show ALL attempts chronologically within each question, including mistakes,
retries, skips, and attempts preceding the best answer. Preserve original wording
and recorded verdicts; never regrade, silently correct, or invent missing content.
Show `No attempts recorded.` for empty attempt arrays and identify missing legacy
data honestly. Use actual saved question counts and fields for older schemas.
Ending progress comes from that lesson's applied `evaluation`, never today's
bank scores. Display every saved vocabulary/grammar change and reason from the
lesson itself. Existing version-8 embedded evaluations are also valid history;
ignore their obsolete external-log pointers. If a legacy record has no embedded
evaluation, show `Evaluation unavailable — no evaluation saved in this lesson.`
Do not infer historical changes or restore an external log during browsing.

This explicit full-archive view is an exception to answer hiding: show all saved
source texts and reference translations, including references for questions that
were skipped. Label them as archival references, not feedback newly awarded
Correct. Historical reference flags describe what happened DURING the lesson;
do not change them because the user views the archive later. This exception
does not apply to active lessons, ordinary Lesson Reviews, stats, or incomplete
session browsing. Italicize learning material and answers as usual.

Do not truncate attempts to fit a short response. If the complete lesson is too
long for one reply, show it in explicitly labelled parts in saved order (Focus,
Reading, Listening, Writing, Speaking, Evaluation), state what remains, and let
the user type `Continue` or name a section. Keep the viewing position separate
from the lesson's teaching cursor; browsing does not add attempts or mutate any
saved record. Provide a link to the existing lesson.json for the full raw record.

Show audio players only for files that actually exist. If generated clips were
cleaned up, state `Audio removed to save space; available to regenerate on request.`
All text, translations, and attempts remain viewable. Do not automatically
regenerate audio merely to browse history. Never delete further files, update
familiarity, change selected level, or rerun evaluations as a browsing side effect.
End the archive with `Type Menu to return to the starting page.`

### Set my level page

Render this layout with actual saved values, not the example placeholders:

```text
# Set my level

Current lesson level: [CEFR]

| Level | Status | Requirement |
|---|---|---|
| A1 | Current / Available | Available from the start |
| A2 | Current / Available / Locked | Reach 80% A1 to unlock |
| B1 | Current / Available / Locked | Reach 80% A2 to unlock |
| B2 | Current / Available / Locked | Reach 80% B1 to unlock |
| C1 | Current / Available / Locked | Reach 80% B2 to unlock |
| C2 | Current / Available / Locked | Reach 80% C1 to unlock |

Type an available level, such as A1, to select it for your next lesson.
Your scores and any unfinished lesson stay unchanged.

Type Menu to return to the starting page.
```

Use `Current` for the selected band, `Available` for other unlocked bands, and
`Locked` otherwise. For an already unlocked band, show `Already unlocked` as
its requirement; do not imply the user must meet a threshold again. Check the
actual banks before describing coverage gaps. If a band has no grammar entries,
explain why its progress cannot unlock its successor. Do not assume a temporary
coverage gap persists forever or impose prerequisites on starting A1.

After a level choice, redisplay this same page with one `Selection:` line between
the table and instructions. Use `Selection: [band] selected for your next lesson.`,
`Selection: [band] is already your current level.`, or
`Selection: [band] is locked — reach 80% [preceding band] to unlock it.` as
applicable. Never replace the page with a differently structured confirmation.

### View my stats page

Use this structure, populated from saved data and read-only calculations:

```text
# My stats

Current progress: [n]% [CEFR]
Vocabulary progress ([CEFR]): [V]%
Grammar progress ([CEFR]): [G]%

| Record | Count |
|---|---|
| Vocabulary encountered ([CEFR]) | [familiarity > 0] / [band total] |
| Grammar encountered ([CEFR]) | [familiarity > 0] / [band total] |
| Completed full lessons | [count] |

Unlocked levels: [saved unlocked levels]
Next unlock: [next locked band and prerequisite, or All levels unlocked]

## Saved sessions
[Unfinished full lessons and separately labelled trials, with date and position;
or None. Do not expose reference answers.]

## Latest evaluation
[Concise changes from the most recent applied evaluation, or No evaluation recordged yet.]

Type Menu to return to the starting page.
```

Encountered counts are bank entries with familiarity above zero, not a claim
of mastery. All component percentages and encountered counts use only the
selected band; the completed full-lesson count covers all bands. If no evaluation
evaluation exists, explain that percentages are calculated from existing bank scores,
not a newly evaluated lesson. Follow the read-only and pending-evaluation
safeguards above. Omit a numerical combined percentage when unavailable.

Use this fixed table under `## Saved sessions` when records exist, newest start
first; otherwise show `None.`:

```text
| Type | Started (Toronto) | Level | Position | Lesson ID |
|---|---|---|---|---|
| [Lesson / Trial] | [date/time] | [saved band] | [section — passage n of count] | [ID] |
```

Under `## Latest evaluation`, use these fields in order when an applied evaluation exists:

```text
Lesson ID: [ID]
Evaluated (Toronto): [date/time]
Progress ([evaluated band]): [saved before]% → [saved after]%
Vocabulary changes: [increased count] increased; [decreased count] decreased.
Grammar changes: [increased count] increased; [decreased count] decreased.
Unlocked: [newly unlocked bands / None]
```

Counts come from that evaluation, not a new evaluation; identify increases from 0 as
newly encountered in a brief parenthetical count. Preserve unavailable and C2
notation. Without an applied evaluation show `No evaluation recordged yet.` followed by
`The percentages above come from existing bank scores, not a new evaluation.`
If a pending evaluation prevents safe calculation, use the pending status line
and unavailable values instead, not this claim about calculated percentages.

### Help page

Render this fixed page verbatim, resolving the README link to the actual absolute
path of the active project's README.md. Do not generate audio or start a lesson.

```text
# Help

## Lesson sections

| Section | What you do |
|---|---|
| Reading | Translate four French passages into English. |
| Listening | Transcribe four audio passages into French. |
| Writing | Translate four English passages into French. |
| Speaking | Translate four English passages aloud and submit the dictated French text. |

## Answers and audio

- Questions arrive one at a time. Ask for explanations whenever you need them; questions are not quiz attempts.
- Correct answers reveal a reference and advance. Almost correct or Needs revision means retry; Skip advances without revealing the reference.
- Listening audio has 100%, 75%, and 50% speeds. Reading and vocabulary audio use 100%. Speaking reference audio is available after Correct, until completion cleanup.
- Speaking feedback uses your dictated text, not an audio-based pronunciation assessment. Tell me if dictation misheard you.

## Saved progress

- Answers, retries, and feedback are saved. Stop preserves an incomplete session; Resume continues where you left off.
- Completed full lessons update familiarity. Progress is specific to each CEFR band; reaching 80% unlocks the next band without switching automatically.
- Set my level lets you choose an unlocked band for future lessons. Scores are learning indicators, not official CEFR or TEF results.
- Generated audio is removed after a full lesson and its evaluation finish. Text and attempts remain; audio can be regenerated on request.

## Commands

| Command | Action |
|---|---|
| Begin a new lesson | Start a lesson; confirm first if one is unfinished. |
| Resume my lesson | Continue a saved incomplete session. |
| View my stats | See band-specific progress and saved sessions. |
| Set my level | Choose an unlocked band for future lessons. |
| View a completed lesson | Browse all saved material and attempts. |
| View vocabulary and grammar | Browse either bank in 20-item tables; sort, visit, and favorite items. |
| Skip | Move past the current question without revealing its answer. |
| Stop the lesson | Save your place and end the session without completing it. |
| Menu | Return to the starting page without losing your place. |

Full guide: [README.md]([absolute README path])

Type Menu to return to the starting page.
```

After stats or help, say `Type Menu to return to the starting page.` Do not
automatically launch a lesson. A menu request while a question is pending is
navigation, not a skip or a stop.

## Lesson Procedure

Presentation style: Italicize all French learning material in user-facing
messages: vocabulary headwords (including inside headings), useful forms,
French grammar patterns, example sentences, passages, and French text quoted
in feedback or reference answers. Also italicize English meanings, translations,
and equivalent phrases in the learning material. Use Markdown `*text*`, not
inline code. Keep instructions, labels, and explanatory prose in regular type.
The response following `Your answer:` or `Your best answer:` must always be
italicized, regardless of language; keep the label itself in regular type.
Keep audio players outside the italic span, immediately after
the relevant French material. Store plain text in `lesson.json` and apply
italics only when presenting it. This applies to all lesson sections and retries.

Each lesson is designed to take one hour and has four 15-minute sections: Reading, Listening, Writing, and Speaking. 

The lesson begins when the user asks anything such as "Begin today's lesson" or "I want to continue one more lesson today" or anything equivalent. If the user have not finished a lesson, ask "We haven't finished the current lesson, are you sure you want to begin a new lesson?". If the user says yes, then mark this lesson as incomplete in the `lesson.json` referred to in the next paragraph, and then continue starting a new lesson. The lesson follows the following steps. 

1. Create a folder under `lessons/` with name `YYMMDDhhmmss` i.e. the exact time the lesson starts (two digits each for year, month, day, hour, minute, and second), in the `America/Toronto` timezone. All lesson material for this lesson will be generated under this folder. We will henceforth refer to this folder as the "lesson folder". Create a `lesson.json` using the canonical format defined below, including its metadata and five sections: Reading, Listening, Writing, Speaking, and Focus. Never invent a different layout for a new lesson.

   Calculate the selected band's starting progress from the current banks using
   Step 12's formula, without changing familiarity or regrading old lessons.
   Save the resulting integer in `cefr_progress_percent` as the starting snapshot.
   Also save the unrounded band-specific components as
   `vocabulary_progress_percent` and `grammar_progress_percent` in `lesson.json`.
   Calculate vocabulary using only entries with `cefr_level` matching the lesson
   band and grammar using only rules whose `level` matches it. Include all items
   in that band, not just the lesson focus, and exclude other bands. An unavailable
   component is null; an available component can still be shown when the other
   component (and therefore the combined percentage) is unavailable.
   A first calculation is permitted even when no embedded evaluation exists; use null
   only when the calculation is unavailable (including C2). Do not apply a new
   assessment while a previous evaluation is pending; resolve it first.

2. Pick Lesson Focus: Pick exactly eight vocabulary items and four grammar targets, and log them in the Focus section:
   - four new vocabulary items (`familiarity: 0`)
   - four previously encountered vocabulary items for review: two fragile items
     (`familiarity: 1–2`) and two strengthening items (`familiarity: 3–4`)
   - two new grammar targets (`familiarity: 0`)
   - one fragile grammar target for review (`familiarity: 1–2`)
   - one strengthening grammar target for review (`familiarity: 3–4`)

   Choose material appropriate to the user-selected CEFR level saved in the
   lesson snapshot. All vocabulary and grammar assigned to that band or ANY
   lower CEFR band are fair game in material for all four sections, even when
   their familiarity is 0 or they have never appeared in a prior lesson. For
   example, B1 material may use any A1, A2, or B1 bank item; prior exposure is
   not a prerequisite for including a lower-band item. Unknown-level entries
   are not automatically lower-band items. Keep the overall complexity suited
   to the selected band and the passages natural, not overloaded with unknowns.
   Continue reviewing lower-band weaknesses where relevant. If an unseen
   lower-band item is selected as a focus item, classify it as new (0), not
   review; use the requested counts and the documented shortage fallback.
   Incidental lower-band material need not appear in the Focus Preview, but
   explain it when needed. Inclusion is not evidence of mastery: assess it only
   from actual answers, do not raise its score automatically, and do not penalize
   mere lack of prior exposure. These lower-band items keep their own CEFR labels
   and affect only their own band's progress, not the selected band's numerator.
   Prefer items that
   are recently incorrect or due for review within the stated familiarity
   ranges. For focus selection, items at familiarity 5 are maintenance items:
   select them only when due, never merely to fill a review slot. They may still
   appear naturally as incidental material. Apply the deterministic fallback and
   due-for-review rules below when a requested range has too few eligible items.

   For both Reading and Listening, generate exactly four self-contained
   passages using the lesson focus. Each passage must contain 30–50 French
   words, regardless of CEFR level. Aim to use about two vocabulary focus items and
   one grammar focus target per passage on average. This is a coverage guide,
   not a strict quota: natural, meaningful French takes priority.

### Focus selection and review scheduling (`lesson-v1`)

Select distinct bank identities, not multiple forms of one word/rule. Work within
the selected and lower bands. Fill new slots first, then fragile, then
strengthening. Within a requested range prioritize: confirmed errors in the last
completed lesson; then due items (most overdue first); then lower familiarity;
then existing bank order as a stable tie-breaker. For new items use bank order,
choosing a coherent situation around the selected targets. A preview is orientation,
not an additional source of familiarity points.

For scheduling only, an item's review interval is 1, 2, 4, 8, or 16 completed full
lessons for familiarity 1, 2, 3, 4, or 5 respectively. Its age for the upcoming
lesson is one plus the number of completed full lessons since its most recent
meaningful practice in a completed full lesson. Thus interval 1 is due in the
very next lesson. Errors in the last completed lesson make it immediately due.
Meaningful practice includes independent, assisted, and recognition evidence,
not preview-only exposure or skip-only/unassessed observations. If a familiar
item has no recoverable practice date, treat it as due with age unknown (highest
due priority), not as a fabricated date. This is a scheduling convention, not a
memory-decay score; passing time alone never lowers familiarity. Scheduling can
inspect older history, but evaluation still uses only its defined three lessons.

If a slot lacks eligible items, use the lowest familiarities among remaining
unused items at 0–4, then due maintenance items at 5. Record actual classification:
0 = new, 1–2 = review_fragile, 3–4 = review_strengthening, 5 = maintenance.
Never call an unseen item review or a known item new merely to satisfy a quota.
The eight vocabulary/four grammar total stays fixed whenever enough distinct
eligible entries exist; requested new/review counts are the explicit fallback
exception, not fictional score changes. Record each shortage and replacement in
`Focus.selection_notes`. This also handles a band with no unseen items remaining.
If even total counts cannot be met, explain the shortage and ask whether to use
a reduced-focus trial or select another unlocked band; do not silently duplicate
items, use an undued 5, unlock a band, or add bank entries. Trials otherwise use
the same Focus counts and four passages per active section as full lessons.

3. Generate Reading Material: Generate four Reading passages in a natural mix
of situations, appropriate to the CEFR level in `lesson.json`. Store each
French passage and its English reference translation in the `Reading` section
of that lesson's `lesson.json`. Generate one normal-speed (`1.0`) Kokoro audio
clip for each passage. Save them as `audio/reading-passage-01.wav` through
`audio/reading-passage-04.wav`, and store their relative paths in the matching
`Reading` items in `lesson.json`. Present these saved items during Step 8.

Every Reading and Listening passage must contain 30–50 French words at all
levels. Adapt difficulty through vocabulary, grammar, sentence complexity,
and context rather than passage length. At beginner A1, use short, simple sentences
with repeated familiar patterns to form a coherent passage. Count words
separated by whitespace; contractions such as `j’ai` count as one word.

### Reproducible local audio

Use the existing project `scripts/kokoro_french.py` with the installed
`.kokoro-env/bin/python`, French voice `ff_siwis`, language `fr`, WAV output,
and the saved speed. Resolve both paths from the actual project root; in an
isolated test the installed runtime may be read from the real project while
every output must resolve inside the test lesson folder. Read the script before
invoking it. Supply `--output` and `--speed` explicitly; pass exactly the saved
French text safely as one argument or standard input, not interpolated shell
code. Do not use its default output path, which is not lesson-specific.

Check the runtime, voice/model availability, output path, and generated WAV
readability. A model/permission failure is a generation problem, not an excuse to
claim audio exists, substitute another voice/speed silently, or reveal Listening
text. Explain the issue, retain generated text and the generation cursor, and ask
before changing the agreed audio workflow or installing/downloading alternatives.
A full lesson has 36 generated WAV files: 8 vocabulary, 4 Reading, 12 Listening,
12 Speaking. Reuse a loaded model for batching if available; the saved paths,
voice, speeds, and source text stay the same. Never fabricate exact speech duration.

4. Generate Listening Material: Generate four Listening passages using the
lesson focus in contexts different from Reading, each containing 30–50 French
words regardless of level. Store each French passage and English reference translation
in the `Listening` section of that lesson's `lesson.json`. Generate a
normal-speed (`1.0`), slow-speed (`0.75`), and very-slow-speed (`0.50`) Kokoro clip for each passage. Save
them as `audio/listening-passage-01-normal.wav` through
`audio/listening-passage-04-normal.wav`, with equivalent `-slow.wav` and
`-very-slow.wav` files. Record each version's speed with its relative audio path.
Store every relative audio path in the matching `Listening` items in
`lesson.json`. Present the audio during Step 9, with the French transcript and
English translation hidden until the feedback rules permit revealing them.

5. Generate Writing Material: Generate exactly four self-contained English
passages for the user to translate into French, using the lesson focus in
contexts different from Reading and Listening. There is no separate sentence
set or free-composition question. Store each English source passage and a
natural French reference translation in the `Writing` section of `lesson.json`.
Use the level-dependent French target lengths in the table below:
size the English source so its French reference fits that range. This is a
material-generation guide, not a strict word-count requirement for the user's
translation. Use simple, connected sentences at beginner A1. Aim for about two focus
vocabulary items and one grammar target per passage, without forcing coverage.
Do not generate answer audio for Writing. Present these items during Step 10.

6. Generate Speaking Material: Generate exactly four self-contained English
passages for the user to translate aloud into French using dictation. Follow
Writing's generation rules and level-dependent reference lengths, using the
lesson focus in contexts different from the other sections. Store each English
source, natural French reference translation, and target length in `Speaking`
in `lesson.json`. There is no separate sentence set or free-composition prompt.
Aim for about two focus vocabulary items and one grammar target per passage,
without forcing coverage. Generate three Kokoro WAV clips of each saved French
reference translation: normal (`1.0`), slow (`0.75`), and very slow (`0.50`).
Save them in the lesson folder as `audio/speaking-passage-01-normal.wav` through
`audio/speaking-passage-04-normal.wav`, with matching `-slow.wav` and
`-very-slow.wav` files. Store the relative paths and speeds in each Speaking
item's `audio` object. All three clips must speak the same saved reference text.
Keep answer audio hidden until Correct feedback in Step 11. Word counts guide
material generation, not grading the user's spoken answer.

Use the following French reference-translation target lengths for both Writing
and Speaking:

| CEFR Level | Target words |
|---|---:|
| A1 | 25–45 |
| A2 | 45–70 |
| B1 | 70–110 |
| B2 | 110–150 |
| C1 | 150–220 |
| C2 | 220–300 |


7. Start Lesson: Before the Focus Preview, show the saved starting percentages:

   ```text
   # Lesson

   Progress at start: [n]% [CEFR]
   Vocabulary progress ([CEFR]): [V]%
   Grammar progress ([CEFR]): [G]%
   ```

   For an unavailable percentage, show `[CEFR] — progress unavailable: [reason]`;
   show simply `C2` at C2. Never substitute zero for missing data. A resumed
   lesson keeps its original starting percentages; do not present a new baseline.
   Display vocabulary and grammar components to one decimal place, using the
   lesson's band only, never the entire database or only the focus items.
   Show `Unavailable — [reason]` for a missing component rather than zero.
   Then present a concise Focus Preview before the four lesson sections. It is
   an orientation, not a quiz: do not require an answer before continuing.
   Use exactly this compact structure:

   ```text
   # Focus: [saved practical situation]

   ## New Vocabulary
   ### *French headword* [clickable audio player]
   Part of speech: [part of speech; gender when a noun]
   Meaning: *English meaning*
   Useful form: *[form]*
   Example: *French example*
   English: *English translation*

   ## Review Vocabulary
   ### *French headword* [clickable audio player]
   Part of speech: [part of speech; gender when a noun]
   Meaning: *English meaning*
   Useful form: *[form]*
   Example: *French example*
   English: *English translation*

   ## New Grammar
   ### Rule name
   Pattern: *[French pattern]*
   Example: *French example*
   English: *English translation*

   ## Grammar Review
   ### Rule name
   Pattern: *[French pattern]*
   Example: *French example*
   English: *English translation*
   ```

   Use one compact multi-line card per focus item and no extra explanation.
   A new lesson must save a nonempty practical situation. If focus selection
   needed a fallback, show `Selection note: [saved selection note]` directly below
   the Focus heading, one line per note, before the four fixed category headings.
   Group cards by their actual New/Review classification, retaining saved order
   within each group. Keep empty category headings with `None this lesson.`
   Before displaying the Focus Preview, generate one normal-speed (`1.0`) Kokoro
   WAV clip for each vocabulary headword. For nouns, speak the displayed
   headword with its article; for all other parts of speech, speak the displayed
   headword itself. Save the clips as `audio/focus-vocab-01.wav` through
   `audio/focus-vocab-08.wav` in the lesson folder, and store each relative
   audio path in the corresponding vocabulary item in the `Focus` section of
   `lesson.json`.

   In the user-facing preview, render each card as Markdown, never inside a code
   block. Use a level-2 heading for every New/Review category and a level-3
   heading for every vocabulary or grammar item. Put the playable audio control
   immediately after the French headword using an absolute local audio path, for
   example: `### *un livre* ![Play](/absolute/path/to/lesson/audio/focus-vocab-01.wav)`.

   Include only one or two lesson-relevant forms: an article or plural for a
   noun, an agreement form for an adjective, the form(s) used in the lesson for
   a verb, or a useful fixed phrase. Do not list every variant or conjugation.
   Clearly label New and Review, but do not display numerical familiarity
   scores. Store all Focus Preview details in the `Focus` section of that
   lesson's `lesson.json`.

Next, we begin the four sections. 
Answer-reveal rule for all sections: Show the full reference answer only after
the user's response receives `Correct`. For `Almost correct` or `Needs revision`,
give targeted hints or local corrections and request a retry, without the full
answer or a piecemeal reconstruction of it. For `Skipped`, advance without
revealing the answer. Omit the entire `Correct answer` field unless the verdict
is `Correct`. Listening's English translation and Speaking's reference-answer
audio are also withheld until Correct.
This changes presentation only: keep all reference material saved in `lesson.json`.
The explicit View a completed lesson archive is the sole browsing exception:
it shows all saved references without altering historical reveal flags. Normal
teaching and the end-of-lesson review retain the answer-hiding rules above.

Standard correction format for all sections: Under `Corrections:`, use one
bullet per error, in the form `*[user's incorrect word or phrase]* →
*[correct word or phrase]*: [brief explanation].` Use the literal arrow `→`,
italicize both language fragments and any French forms or English equivalents
in the explanation, and keep explanatory prose in regular type. For example:

- *étudie* → *étudier*: after *voulons*, use the infinitive (*to study*).
- *frençais* → *français*: spell it with *a*, not *e*.
- *together* → *ensemble*: use the French word.

Quote only the relevant erroneous fragment, not an entire corrected passage.
Local corrected forms are allowed before Correct; the full reference answer
remains hidden. For omissions or unnecessary words, use `[missing]` or
`[remove]` on the appropriate side of the arrow. If a correction would reveal
an entire unanswered sentence or passage, use a short targeted hint after the
arrow instead of supplying that full text. Do not invent errors to fill this
format. Keep the section-specific `Corrections: None — ...` for correct answers;
use `Corrections: None — skipped.` when skipping without new corrections.

### Mid-lesson questions, interruptions, and cursor transitions

Requests such as `Explain libre and venir`, replay requests, navigation, and rule
edits are not answers. Keep the pending question unchanged. For a vocabulary
explanation use `## Explanation`, then a heading `### *[word]*`, `Meaning:`,
`Use:`, and `Example:` with the example and its translation italicized. For grammar
use `### [rule name]`, `Pattern:`, `Use:`, and `Example:`. Give only the relevant
forms/examples; do not reconstruct the whole pending reference. Close with
`We’re still on [section] — Passage [n] of [count]. Send your answer when ready.`
Do not attach a verdict, count a retry, or force the user to answer immediately.

Save substantive explanations and any additional hints in the root
`clarifications` array described in the canonical contract before waiting for the
next answer. A user can ask before the first attempt or between retries. Record
which exact targets received answer-specific help; later attempts on those targets
in the same question are assisted even if no full reference was shown. General
explanations with a genuinely different example need not contaminate unrelated
targets. Do not award familiarity simply for asking or reading an explanation.

When the user says stop/end, or `skip and show the end of lesson`, stop the
session: preserve the current question and all attempts; do not manufacture skips
for remaining questions. A plain `Skip` is an attempt on the current question and
advances one question. A rule edit changes neither cursor nor attempts.

Commit each answer and the resulting item/section/root cursor together before
presenting the next question. Correct/Skipped advances to the first unresolved
item; Almost correct/Needs revision keeps the same item at `retry`. After the last
item in a section, set its status completed and current_item null, announce
`[Section] section complete.`, and present the next active section's first question
in the same reply. After the last active section, set current_section null,
root completed true/status completed, and actual ended_at before evaluating a
full lesson. Completed trials are saved but not automatically evaluated.
Only the current active question may be awaiting_answer/retry. A generation-only
skeleton has current_section Focus and no pending question. Never reset completed
items on resume, replay, or clarification. Focus is presented once before the
first question; moving to Reading is its durable completion marker.

For every section, save the user's answers in the matching question's
`attempts` array in `lesson.json` as soon as feedback is given, before moving
on or waiting for a retry. Append every attempt; never overwrite an earlier
answer. Store plain text with the user's original wording and mistakes intact.
Each attempt must record:

- `recorded_at`: ISO 8601 timestamp with timezone.
- `response`: the user's verbatim answer or skip request.
- `verdict`: `Correct`, `Almost correct`, `Needs revision`, or `Skipped`.
- `corrections`: the specific corrections or hints given (an empty array if none).
- `reference_shown_before_attempt`: whether the full reference answer had
  already been revealed, so a retry is not mistaken for unaided recall.
- `reference_revealed`: whether this attempt's feedback reveals the reference.

Track each item's `status` as `not_started`, `awaiting_answer`, `retry`,
`correct`, or `skipped`, and save the section's `current_item`. Save section
status as `not_started`, `in_progress`, `completed`, or `stopped`. When the user ends a test
or lesson early, preserve all attempts, mark it `stopped`, and leave
`completed: false`; do not count unanswered items as skips or errors. An
instruction to stop is not an answer to the current question. Apply these
rules to all section trials as well as full lessons.

8. Conduct Reading Section: After the Focus Preview in Step 7, present the four
saved Reading passages from `lesson.json` one at a time. Use the following
format, rendered as Markdown rather than inside a code block:

   ```markdown
   # Reading

   ## Passage 1 of 4

   Please translate the following passage into natural English.

   *[French passage]* ![Play](/absolute/path/to/lesson/audio/reading-passage-01.wav)
   ```

   Show `# Reading` when the section begins, and update the passage number and
   audio path for each item. Place the playable audio control immediately after
   the French text. Do not show future passages or reference translations.
   Wait for the user's response.

   Give feedback using this standard format, also rendered as Markdown:

   ```markdown
   ## Feedback

   Verdict: Correct / Almost correct / Needs revision / Skipped
   Your answer: *[the user's response, or “Skipped”]*

   Corrections:

   - *[incorrect word or phrase]* → *[correct word or phrase]*: [brief explanation].

   Correct answer: *[natural reference translation, only when permitted]*
   ```

   Preserve line breaks between the feedback fields. Accept natural English
   equivalents; assess understanding of the French meaning and focus items.
   Do not invent errors because wording differs from the reference. Harmless
   English style/capitalization differences are Correct, not a French error.
   Almost correct requires an actual minor omission or meaning/usage problem;
   Needs revision indicates significant omissions or changed meaning. Grade the
   entire passage for the verdict, but attribute item evidence separately.

   - Correct: Write `Corrections: None — this is a natural translation.` Show
     the reference translation, then present the next passage in the same reply.
   - Almost correct: Explain the small remaining mistake with a targeted hint or
     local correction. Withhold the full translation and omit `Correct answer`.
     Ask the user to retry the same passage.
   - Needs revision: Give targeted corrections or hints, omit the entire
     `Correct answer` field, and withhold the full translation. Ask the user to
     retry the same passage.
   - Skipped: On any clear skip request, omit `Correct answer` and present the
     next passage without revealing the translation or requiring another attempt.

   For retries, write `Please try the passage again:` followed by the same
   French passage and its audio player. Wait for the user's next response.
   Advance only after a correct answer or an explicit skip; an Almost correct
   answer neither reveals the full reference nor advances the item.
   After the fourth passage is answered correctly or skipped, give feedback and
   state `Reading section complete.`

9. Conduct Listening Section: After Reading, present the four saved Listening
passages one at a time. The user transcribes the audio into French. Use this
format, rendered as Markdown rather than inside a code block:

   ```markdown
   # Listening

   ## Passage 1 of 4

   Please transcribe the following audio into French.

   Normal speed (100%): ![Play](/absolute/path/to/lesson/audio/listening-passage-01-normal.wav)

   Slow speed (75%): ![Play](/absolute/path/to/lesson/audio/listening-passage-01-slow.wav)

   Very slow speed (50%): ![Play](/absolute/path/to/lesson/audio/listening-passage-01-very-slow.wav)
   ```

   Show `# Listening` when the section begins. Update the passage number and
   audio paths for each item. Allow replays of any version. Do not display
   the French transcript, English translation, or future passages before the
   user answers. Wait for the user's transcription.

   Use the same Feedback format and retry/skip flow as Reading, with these
   adaptations:

   - `Your answer:` contains the user's French transcription in italics.
   - Check against the spoken wording. Point out missed, added, or misheard
     words and relevant spelling or grammar errors. Distinguish hearing errors
     from spelling errors; punctuation and capitalization alone do not make an
     otherwise accurate transcription incorrect. Accept genuinely ambiguous
     homophones when the audio and context cannot distinguish them.
   - Correct: Write `Corrections: None — this is an accurate transcription.`
     Show the full italicized French transcript under `Correct answer:`, then
     present the next passage in the same reply.
   - Almost correct: Give targeted hints or local corrections for the minor
     remaining errors. Omit `Correct answer` and withhold the full transcript
     and English translation. Ask for a retry.
   - Needs revision: Give targeted corrections or hints, omit the entire
     `Correct answer` field, and withhold the full transcript. Ask for a retry.
   - Skipped: On an explicit request to skip, omit `Correct answer` and advance
     without revealing the transcript or English translation.

   Only after Correct, when revealing the full transcript, also show its stored English translation
   in italics under `English:`. For retries, write `Please try the passage
   again:` and repeat all three audio players. Do not repeat the French text except
   when permitted by the feedback rules. Advance only after a correct
   transcription or an explicit skip. After the fourth passage is answered
   correctly or skipped, give feedback and state `Listening section complete.`

10. Conduct Writing Section: After Listening, present the four saved English
passages one at a time. Use this format, rendered as Markdown:

   ```markdown
   # Writing

   ## Passage 1 of 4

   Please translate the following passage into natural French.

   *[English passage]*
   ```

   Show `# Writing` when the section begins. Update the passage number for each
   item. Do not display future passages, the French reference, or answer audio
   before the user's attempt. Wait for the user's French translation.

   Use the same Feedback format as Reading: `Verdict`, italicized `Your answer`,
   `Corrections`, and `Correct answer` only when permitted. Assess preservation
   of meaning, vocabulary choice, verb forms, word order, articles, agreement,
   and spelling/accents. Accept natural alternative translations, not just the
   saved reference. Do not require a particular focus expression if another
   expression is correct. Accept either gender when the English/context leaves
   it unspecified and the French agreement is consistent. Do not mark a correct
   translation wrong merely for style, word count, or reference wording.

   - Correct: Write `Corrections: None — this is a natural translation.` Show
     the italicized French reference under `Correct answer:` (one valid version,
     not the only acceptable answer), then present the next passage immediately.
   - Almost correct: For a faithful translation with only minor remaining errors,
     identify the errors and give targeted hints or local corrections. Omit
     `Correct answer`, withhold the full French reference, and ask the user to
     retry the same passage.
   - Needs revision: For significant omissions, changed meaning, or substantial
     grammar problems, give a few targeted hints or local corrections. Omit
     `Correct answer` and withhold the full translation; do not reconstruct it
     piecemeal in the hints. Ask the user to retry the same passage.
   - Skipped: On any clear skip request, omit `Correct answer` and advance
     without revealing the French reference or requiring another attempt.

   For retries, write `Please try the passage again:` followed by the same
   italicized English passage. Do not repeat the French reference outside the
   permitted feedback. Advance only after Correct or an explicit skip; Almost
   correct still requires a retry. Save every answer, retry, skip, correction,
   and reference-reveal flag in `lesson.json` using the shared recording rules.
   After the fourth passage is correct or skipped, give feedback and state
   `Writing section complete.` If the user ends the section early, save the
   stopped state without marking remaining passages skipped or completed.

11. Conduct Speaking Section: After Writing, present the four saved English
passages one at a time, following Writing's feedback and retry flow. Use this
format, rendered as Markdown:

   ```markdown
   # Speaking

   ## Passage 1 of 4

   Please translate the following passage aloud into natural French using dictation, then send the text.

   *[English passage]*
   ```

   Show `# Speaking` when the section begins and update the passage number for
   each item. Keep future passages, French references, and reference-answer audio
   hidden. Assess the
   submitted text subject to the dictation limitations below; accept natural
   alternative translations as in Writing. Use the shared Feedback format and
   arrow corrections. Only Correct reveals the French reference and advances;
   Almost correct or Needs revision requires another attempt without the full
   answer. A skip advances without revealing it.

   On Correct, write `Corrections: None — this is a natural translation.`
   Then show the italicized French reference and its three audio players using
   the following format, before presenting the next passage in the same reply:

   ```markdown
   Correct answer: *[saved French reference translation]*

   Normal speed (100%): ![Play](/absolute/path/to/lesson/audio/speaking-passage-01-normal.wav)

   Slow speed (75%): ![Play](/absolute/path/to/lesson/audio/speaking-passage-01-slow.wav)

   Very slow speed (50%): ![Play](/absolute/path/to/lesson/audio/speaking-passage-01-very-slow.wav)
   ```

   Update the passage number in each path. The reference is one valid answer;
   accept correct alternatives even when they differ from the recorded version.
   Keep players outside italics and allow replay after revealing them while the
   lesson is active. Completed-lesson audio cleanup in Step 13 takes precedence
   over playback after completion. Do not
   show these players or audio links with the initial question, Almost correct,
   Needs revision, or Skipped feedback. Listening's pre-answer audio rule does
   not apply to Speaking.

   For retries, write `Please try the passage again aloud using dictation:` and
   repeat the same italicized English passage. Save each submitted attempt and
   the current position in `lesson.json`. After the fourth passage is correct
   or skipped, give feedback and state `Speaking section complete.` If the user
   stops early, preserve the position and mark it stopped, not completed.

### Speaking input: voice-to-text dictation

The user speaks their French answer using the app's voice-to-text input, then
submits the resulting text. This replaces the Voice Memos attachment workflow.
Do not require the user to supply audio files, use external recording apps, or
manage files manually. Generated reference-answer audio is separate from user input.
The user should formulate the answer aloud rather than type a draft first;
for a retry, ask them to say the answer again using dictation.

Assess the submitted transcript for meaning, vocabulary, and grammar using the
shared feedback, arrow-correction, retry, skip, and answer-reveal rules.
Dictation may misrecognize words or normalize errors: a correct transcript is
not proof of correct pronunciation or fully accurate spoken grammar. When a
phrase is garbled or implausible in context, flag it as `Possible pronunciation
unclearness` and ask the user to say the phrase again clearly. Use the standard
arrow format, for example: `*Mara froid et* → *Ma sœur est*: possible
pronunciation unclearness—try saying this phrase again clearly.` This is a
practice cue, not a confirmed diagnosis: dictation errors remain another
possible cause. Do not count such a fragment as a confirmed vocabulary/grammar
error or infer a particular mispronounced sound without audio evidence. Record
the uncertainty in the attempt's correction text. If ambiguity persists, ask
what the user intended to say instead of requiring endless recognition retries.
Do not treat
automatically supplied punctuation, accents, spelling, or homophone choices as
evidence of the user's writing or pronunciation ability.

This section practises spoken sentence-building, but transcript-only feedback
cannot reliably assess pronunciation, rhythm, pauses, or speaking speed. Do not assign
pronunciation scores from dictated text or claim to have heard audio.
Save the exact submitted text in the matching Speaking attempt's `response`,
with `response_audio_path: null`. Save every retry separately, preserve earlier
attempts, and update progress normally. Interpret these Speaking records as
transcript-based evidence, not audio assessments.

12. Update Progress: At the end of a full lesson, use an evidence window of
the lesson just completed PLUS the two most recent previously completed full
lessons (up to three lessons total). Select the two earlier lessons by actual
completion time (`ended_at`), strictly before the current lesson's completion;
exclude the current lesson from that selection. Require `type: "lesson"`,
`status: "completed"`, and `completed: true` for historical eligibility.
Exclude trials, in-progress lessons, and stopped/incomplete lessons regardless
of their recency. Use fewer historical lessons when fewer exist; do not delay
evaluation or fill the window with ineligible sessions. Do not filter earlier
lessons by CEFR band or whether they share focus targets. Resolve missing or
ambiguous legacy completion times from saved evidence, not invented timestamps.

Read relevant questions, actual responses, hints, corrections, retries, and
reference flags across this window, not just summaries or final verdicts. The
earlier lessons provide historical evidence of consistency or difficulty; do
not replay their old score changes. Apply one new evaluation for the current
lesson, starting from the existing bank scores.

After all four sections finish, save this lesson with `type: "lesson"`,
`status: "completed"`, and `completed: true` before updating progress. Do not
automatically assess an in-progress lesson, stopped lesson, or trial. A user
request to include one is an explicit exception, not a change to its completion
status. If resuming a pending end-of-lesson update, use that same lesson ID.

Update only items with fresh, clear evidence in the just-completed lesson;
historical evidence alone cannot change an item. Retain other items'
existing scores. Identify evidence by lesson ID, section, item ID, and attempt
number. Check its embedded evaluation before applying changes: each lesson is
evaluated once, and rerunning a completed update must not apply the same
familiarity changes again. Earlier answers may support the window calculations,
but are not new attempts or independent grounds for another score change.

### Familiarity-update algorithm (`familiarity-v2`)

Apply these rules to both banks. Preserve all entry metadata; only change an
entry's `familiarity`. Match vocabulary by exact `word` plus `part_of_speech`,
and grammar by `id`; verify each match is unique. Assess non-focus items too
when there is clear evidence, not just the eight vocabulary/four grammar focus
items. Do not infer success merely because a target occurs in generated text.

| Score | Meaning |
|---|---|
| 0 | Not yet meaningfully assessed. |
| 1 | Encountered or attempted, but not reliable. |
| 2 | Demonstrated some independent understanding or use in a familiar context. |
| 3 | Usually correct in straightforward practice. |
| 4 | Reliable across different contexts, including producing French. |
| 5 | Consistently reliable across varied contexts and relevant forms. |

These are practical assessment rules, not a validated proficiency measurement.
A word-family score does not certify every meaning or variant. Do not infer
automaticity or performance under time pressure without measuring it.

**Extract evidence per target per question:**

Read the root clarifications (and a legacy sidecar if present) in their saved
position before attributing independent evidence. An explanation given after an
attempt cannot retroactively invalidate that earlier answer; it affects later
responses to the assisted target. Use the policies pinned for the current
evaluation when interpreting earlier source evidence, without rewriting any
historical attempt verdict or applied evaluation.

- `independent_success`: a correct, meaningful demonstration without an
  answer-specific hint. Reading must demonstrate meaning or the grammatical
  contrast. Writing/Speaking must demonstrate appropriate production, subject
  to dictation limitations. Natural alternatives count for the targets actually
  demonstrated; an unused focus expression is not a failure.
- `confirmed_error`: a clear independent misunderstanding or incorrect use.
  Attribute the cause precisely. For example, `Nous voulons étudie` can show
  knowledge of the word's meaning but an error in infinitive use; do not
  automatically penalize both vocabulary and grammar. Minor English style,
  correct alternatives, and dictation-supplied spelling are not French errors.
- `assisted_success`: success after a relevant local hint, correction, full
  reference, or direct copying of a preview/reference example. Local assistance
  matters even when `reference_shown_before_attempt` is false. Preparation in
  the Focus Preview does not invalidate independent use in a new context.
- `recognition_only`: reproducing a form without demonstrating its meaning or
  grammatical use. Accurate listening transcription alone is normally this
  evidence, not proof of semantic understanding or productive grammar mastery.
- `uncertain_unassessed`: a skip without assessable evidence, an unanswered
  question, an untested target, ambiguous dictation, or evidence otherwise too
  unclear to attribute. This cannot cause a score decrease.

Use at most one independent outcome per target per question. Repeated occurrences
and retries are one learning episode. Assess the earliest usable unaided evidence;
do not replace an initial error with an assisted retry. If the target has both
correct and confirmed incorrect independent uses in that question, count one
`confirmed_error`, not several successes. Uncertainty alone is not a confirmed
error. Preserve later improvement as `assisted_recovery: true`, without another
independent success. Hints for one target do not invalidate unrelated targets.
Independent use in a genuinely new question/context can count again after learning
from an earlier question. A later skip does not erase earlier assessable evidence.

For each target with fresh evidence, let S be the number of distinct questions
across the selected window with `independent_success`, and E those with
`confirmed_error`. Identify questions by `(lesson_id, section, item_id)` so
identical item IDs in different lessons are not merged. Count each observation
once within the window, even when it also appears in several lesson evaluations;
use source lesson attempts rather than adding old evaluations' aggregate S/E totals.
Independent accuracy is `S / (S + E)`; if the denominator is zero it is
unavailable, not zero. Also calculate `current_S`, `current_E`, and
`current_accuracy` from the just-completed lesson alone.
Use exact comparisons (`5 * S >= 4 * (S + E)` for 80%), not rounded accuracy.
Assisted/recognition/uncertain observations are excluded from this denominator.

**Promotion: at most one point per completed lesson.**

| Change | Required evidence |
|---|---|
| 0 → 1 | At least one meaningful attempt involving the target (including a confirmed error), assisted success, or clear recognition in the just-completed lesson. Preview exposure alone does not count. |
| 1 → 2 | S ≥ 1 and independent accuracy ≥80%. |
| 2 → 3 | S ≥ 2 in different questions and independent accuracy ≥80%. |
| 3 → 4 | S ≥ 3 across at least two sections, including at least one independent Writing/Speaking success; accuracy ≥80%. |
| 4 → 5 | S ≥ 4 across at least two sections, including at least two independent Writing/Speaking successes; accuracy ≥80%, with varied contexts and relevant forms. |

For promotions from 1–4, S/E, section coverage, production successes, and varied
contexts refer to the three-lesson window. Additionally require `current_S >= 1`
and `current_accuracy >= 80%`: history cannot promote an untested item, an
assisted-only retry, or an item performed poorly in the current lesson.
Earlier observations can support a later promotion only alongside this new
independent evidence; they never earn a second standalone increment.

For the higher scores, repetition of one memorized phrase is insufficient.
Broad grammar targets need representative coverage: repeated `je suis` alone
cannot establish mastery of an entire broad être target. Record why coverage
qualifies or is insufficient. Existing scores carry earlier learning, while
the two historical lessons provide supporting evidence. Do not invent successes,
look beyond the selected window to fill thresholds, or recalculate old score deltas.
An increase from 0 to 1 marks encounter, not demonstrated mastery; label it
`Newly encountered` in the user-facing review.

**Regression:** decrease by exactly one point when window totals meet `E >= 2`
and `E > S`, AND the current lesson meets `current_E >= 1` and
`current_E > current_S`, with a minimum resulting score of 1. Historical errors
alone cannot cause another decrease, and current independent improvement is not
overridden by old errors. One confirmed error across the entire window does not
lower familiarity; one current error plus a distinct historical error can qualify
when both error-majority conditions hold. Separate retries on one question do
not meet the two-error requirement. For a starting score of 0, apply the encounter rule,
not regression. For scores 1–5, evaluate regression first, then the applicable
promotion threshold. Otherwise retain the old score. Never change by more
than one point or grant independent mastery for an assisted retry. All values
must remain integers 0–5; unassessed items remain unchanged. The proposed
thresholds are now the active rules; do not substitute a different heuristic.

### Percentage calculation and unlocks

After the familiarity updates, calculate the user's **progress percentage**
using the following deterministic policy, named `progress-v5` (user-selected
unlocked bands; the percentage formula is unchanged by the evidence window):

`progress-v5` changes the unlock threshold to at least 80%; it does not change
the separate 80% independent-accuracy requirement for familiarity promotion.
Preserve previously earned unlocks and historical policy labels.

   - Let L be the user's selected learning band in `assessments/level.json`.
     Select all vocabulary entries
     with `cefr_level == L` and all grammar targets with `level == L`.
     Include untested items at familiarity 0; never limit the denominator to
     this lesson's focus or previously tested items. Unknown-level entries
     are excluded. The window informs score changes anchored in fresh evidence;
     the percentage still summarizes the entire current-band curriculum,
     not just performance on this lesson.
   - Calculate vocabulary progress V and grammar progress G:

     ```text
     V = 100 × sum(vocabulary familiarity) / (5 × vocabulary item count)
     G = 100 × sum(grammar familiarity) / (5 × grammar target count)
     progress percentage = floor((V + G) / 2)
     ```

   - Every item has equal weight within its own bank; vocabulary and grammar
     each contribute 50% overall, regardless of their different item counts.
     Familiarity 0 contributes nothing and familiarity 5 contributes full credit.
     Do not round V or G before combining them. Store/display the final integer;
     use the resulting integer for the unlock threshold: at least 80 qualifies.
     An unrounded result of 79.9 displays 79 and does not unlock; 80.0 qualifies.
   - Example: vocabulary progress of 60% and grammar progress of 80% produce
     `70% A2` when the current band is A2. Under this project's convention,
     A2-labelled bank items measure curriculum progress from A2 toward B1.
   - Recalculate from the banks each time, not by adding a fixed percentage
     per lesson. The percentage can stay unchanged or decrease when familiarity
     decreases. Higher-band successes affect that band's future progress, not
     the current band's numerator. Lower-band gaps remain review priorities;
     this percentage does not represent them.
   - A band reaches 100% only when every included vocabulary and grammar item
     has familiarity 5, but 100% is no longer required to unlock the next band.
     After updating familiarity, calculate progress for unlocked bands using
     the same formula. If a band's displayed percentage is at least 80,
     unlock its immediate successor and record the supporting calculation.
     Proceed in CEFR order; any additional unlock needs its own qualifying
     predecessor calculation. This reads existing bank scores, not old lesson
     transcripts. Never change the selected band automatically or revoke an
     earned unlock because a score decreases. Announce newly unlocked bands
     and let the user choose whether to switch.
   - If either bank has no items for L, return null with an explanation; do not
     treat the missing component as 100% or silently give the other bank all
     the weight. Inspect the banks each time: if the C1 grammar pool is still
     empty, C1 cannot unlock C2 until coverage is supplied and a qualifying
     percentage is assessed. Do not assume this temporary data gap persists
     forever. C1 can still be unlocked by qualifying B2 progress. C2 is displayed
     without a percentage.
   - Validate familiarity values as integers 0–5. Missing or invalid values
     require clarification/repair, not silently assuming zero. If the bank
     contents change, identify the resulting denominator change in the evaluation;
     do not describe a data-maintenance change as learning or regression.

This is an internal vocabulary-and-grammar curriculum indicator, not a measured
fraction of real-world CEFR ability or a TEF score. Its accuracy depends on the
underlying familiarity assessments and the bank's coverage. It does not add a
separate pronunciation, speed, or fluency score.

Save the complete end-of-lesson evaluation ONLY in this lesson.json's root
`evaluation` field. Every vocabulary/grammar change is logged there, including
old/new familiarity, reasons, and supporting observations. Do not create another
file, duplicate the evaluation, or restore the deleted log folder. This storage
change does not alter the evidence window or scoring thresholds.
Record the policy name, calculation time, old and new band/percentage, each
changed item's old/new familiarity and evidence references, and V/G item counts
and familiarity sums so the percentage can be reproduced. Record the single
current lesson ID, all source lesson IDs in the evidence window, and which
evidence was processed, including evidence that
resulted in no score change. Include the selected band, unlocked bands before
and after, and the counts and sums behind every qualifying unlock calculation.
Save earned unlocks in `assessments/level.json` without changing its selected
band. Preserve the lesson's creation-time level snapshot; the next lesson uses
the saved user selection and that band's calculated percentage.
Reprocessing the same lesson must not apply its familiarity changes twice.
Trials remain practice records and do not update assessed progress automatically;
the user may explicitly ask to include them. For a stopped lesson, keep its
evidence without treating unattempted questions as failures.

### Saving the evaluation safely

Use one object at `lessons/<lesson_id>/lesson.json` → `evaluation`. Keep plain
text, two-space indentation, and the following fields for every evaluation:

- `schema_version`: 6; `lesson_id`; `familiarity_policy`: `familiarity-v2`;
  `progress_policy`: `progress-v5`; `status`: `pending` or `applied`;
  `created_at` and `applied_at` (ISO 8601 with timezone; applied_at null while pending).
  Evaluation schema 6 changes each new_unlocks event from assessment_log_path to
  evaluation_lesson_path, pointing at the enclosing lesson.json. Its other fields
  and scoring policies remain unchanged; historical schema-5 objects stay readable.
- `source_lesson_ids`: the selected evidence-window lesson IDs in chronological
  completion order, with the current `lesson_id` last; at most three unique IDs.
  `historical_lesson_ids`: the same list without the current lesson (at most two).
  Freeze the window when saving the pending evaluation so retries/recovery use the same
  evidence. Evaluation schema version 5 adds window provenance, per-observation lesson IDs,
  and separate current-lesson counts. Preserve older evaluations and their old policies;
  rereading their source answers as historical context does not rewrite those evaluations.
  Break equal historical completion-time ties by lesson ID in ascending order;
  the current lesson must still be strictly later than its historical sources.
- `exception_authorization`: null for a completed full lesson, otherwise the
  user's explicit request permitting evaluation of this trial/stopped session.
- `lesson_start`: the original `cefr_level`, `cefr_progress_percent`,
  `vocabulary_progress_percent`, and `grammar_progress_percent` snapshots.
  Evaluation schema version 3 adds these component snapshots and `best_attempt_number` below.
  Preserve older evaluations; missing historical component snapshots are unknown, not zero.
- `progress_before` and `progress_after`: arrays of calculations for the selected
  band, the lesson's band if different, and every band checked for an unlock.
  Each object has `cefr_level`, `vocabulary_count`, `vocabulary_sum`,
  `grammar_count`, `grammar_sum`, `vocabulary_percent`, `grammar_percent`,
  `cefr_progress_percent`, and `unavailable_reason` (null when available).
  Preserve exact counts/sums; do not round components used by the formula.
- `unlocked_levels_before`, `unlocked_levels_after`, and `new_unlocks` (the
  unlock objects defined for level.json); `selected_level_at_evaluation`.
- `items`: every assessed bank target, including unchanged ones. Each object
  has `bank` (`vocabulary` or `grammar`), `word`, `part_of_speech`, `grammar_id`
  (null for inapplicable identifiers), `old_familiarity`, `new_familiarity`,
  `S`, `E`, `accuracy` (window totals; accuracy null without independent evidence),
  `current_S`, `current_E`, `current_accuracy` (current lesson only), `reason`, and
  `observations`. Each observation has `lesson_id`, `section`, `item_id`, `attempt_number`,
  `outcome` (one of the five evidence labels above), `assisted_recovery`,
  `supporting_attempt_numbers`, and `note`. These refer to real saved attempts
  in the identified source lesson; the note explains target-specific attribution,
  assistance, and how historical evidence supports the current decision.
  `accuracy` and `current_accuracy` are fractions in 0–1, not 0–100 percentages,
  or null without an independent denominator. S/E counts are nonnegative integers.
  `assisted_recovery` is boolean; supporting attempt numbers are unique integers
  in chronological order. An unassessed observation without a submitted response
  uses attempt_number null and an empty supporting list; it counts as neither
  success nor error. Never invent a response to fill a required key.
- `review_questions`: one object per CURRENT-lesson question with a confirmed error, containing
  `section`, `item_id`, `error_attempt_numbers`, `best_attempt_number`, and
  `final_status`. Select the best attempt by the end-of-lesson rules below;
  use null only when there is no assessable answer. Include
  errors on retries as well as first attempts; deduplicate by section/item ID.
  Store `uncertain_questions` and `skipped_questions` separately using the same
  shape (an empty error-attempt list for skips without errors). A question may
  appear in multiple lists when it has both confirmed errors and uncertainty,
  or errors followed by a skip. Do not label uncertainty-only cases as wrong.
- `summary`: an array of plain-text strings, one per user-facing bullet, listing
  the most important items for the user to review in priority order. Evaluation schema version
  4 changes this from a recap string to a review-priority list; preserve older
  evaluations as recorded. This field replaced `review_priorities` in evaluation schema version 2.
  Future review selection still uses item evidence and familiarity.

Before writing the banks, save the complete intended evaluation inside lesson.json
with status `pending`, applied_at null, old/new values, and before/after
calculations. Validate referenced attempts, eligible source lessons, unique bank
identities/question observations, current/window S/E totals, fresh-evidence gates,
promotion requirements, and score bounds. Save the pre-update bank backups.
If saving/validating the pending object fails, do not touch the banks.

Apply only the saved item changes, preserving unrelated metadata and scores. Save
unlocks with evaluation_lesson_path pointing to this lesson.json, without changing
the selected band. Validate both banks, level.json, and the expected calculations.
Then, in one lesson.json save, mark evaluation.status `applied`, set its actual
applied_at timestamp, copy its summary into closing_summary, and update updated_at.
Only after that save is verified may closing review and audio cleanup proceed.
There is no external-log creation or synchronization step.

For recovery, an applied evaluation is read-only: display its review without
applying changes again. For a pending evaluation, resume its frozen intended
changes, never recompute increases from partially changed scores. Each current
target must equal its saved old or new value; apply old → new once, and leave
already-new values alone. If the banks have already reached all intended new
values but the lesson still says pending, validate the whole transaction before
marking it applied, without adding another point. Conflicting values or unrelated
bank changes require resolution, not overwriting outside edits. Never mark applied
until all intended files agree. Do not run concurrent evaluations.

Current-schema null means no evaluation was prepared; it is not an applied
zero-change evaluation. Legacy records with no embedded history remain unavailable
rather than triggering automatic reassessment. Existing embedded evaluations can
be read/recovered in place without needing any removed external file.

### End-of-lesson presentation

After applying the evaluation and completing Step 13's audio cleanup, render
this structure as Markdown (not a code block). Do not ask the user to retry
again as part of this summary. Do not embed players pointing to deleted files.

```text
# Lesson Review

Progress: [start n% CEFR] → [end n% same CEFR]
Vocabulary progress ([CEFR]): [start V]% → [end V]%
Grammar progress ([CEFR]): [start G]% → [end G]%
Unlocked: [new levels, or None]

## Vocabulary changes

| Item | Familiarity | Result | Reason |
|---|---|---|---|
| ... | old/5 → new/5 | Improved / Regressed / Newly encountered | ... |

## Grammar changes

| Item | Familiarity | Result | Reason |
|---|---|---|---|
| ... | old/5 → new/5 | Improved / Regressed / Newly encountered | ... |

## Questions to review

### [Section] — Passage [n] of 4
Question: [original prompt and source material, subject to answer hiding]
Your best answer: [best saved response, verbatim]
Corrections: [remaining errors in that response, or None in your best answer.]
Earlier mistakes: [only when errors occurred in other attempts]
- [incorrect] → [correct or hint]: [explanation]
Outcome: [Correct after retry / Skipped after errors]

## Uncertain answers

[Uncertainty-only cases, or None.]

## Skipped questions

[Skip-only cases, or None.]

## Summary

- [most important item to review and the key point to remember]
- [next most important item to review and the key point to remember]
```

Make `Summary` a short bulleted list of the most important things for the user
to review, not a general recap. Normally use two to four bullets, fewer when
the evidence warrants fewer. Prioritize recurring confirmed errors, regressed
items, and fragile or newly encountered knowledge that still needs independent
recall. Each bullet names a specific word, pattern, or distinction and gives a
concise reminder. Italicize French material and English equivalents as usual.
Distinguish uncertainty and assisted improvement from confirmed weakness; do not
invent problems or claim mastery from a corrected retry. If no particular review
need is supported, use one bullet saying so. These are review priorities, not an
extra quiz the user must complete now. Save each bullet as one plain-text string
without a bullet prefix or Markdown italics in the evaluation's `summary`.

List EVERY changed vocabulary and grammar item, not just counts or highlights.
Show `None — no familiarity changes.` for an empty changes section. Italicize
vocabulary headwords, French patterns, meanings, question material, and the
response following `Your best answer:`; keep scores, labels, and explanations regular.
Use the literal arrow `→` for every old/new item familiarity and for the combined,
vocabulary, and grammar progress comparisons, including unchanged percentages.

List EVERY question with a confirmed error at any point, even if a later retry
was correct, from the just-completed lesson only. The older two lessons inform
assessment but are not replayed as today's questions or mistakes. Explain when
an item change depends on evidence across lessons. Show each current question
once in section/question order, its original
source material, and `Your best answer:` instead of `Your answer:`. Select an
actual assessable, non-skip attempt using the saved verdict order Correct >
Almost correct > Needs revision; among attempts with the highest verdict,
choose the latest. Save its `attempt_number` as `best_attempt_number` in the
evaluation record. Do not replace the user's wording with a model correction or
reference answer. If no assessable answer exists, state that rather than treating
a skip request as an answer. This changes the final review only: ordinary
in-lesson feedback keeps `Your answer:` and assessment still uses all evidence,
not just the best attempt.

Under `Corrections:`, show only corrections relevant to the selected best
answer, using the standard italicized arrow format. If it was Correct, write
`Corrections: None in your best answer.` Show relevant errors from other attempts
under `Earlier mistakes:` with their attempt numbers and arrow corrections;
do not suggest those errors remain in the best answer. Include distinct confirmed
errors without repeating every full retry. Clearly identify when the best answer
followed hints or corrections: best does not mean unaided. Use saved evidence,
not a reconstructed answer. Questions can need review without a score decrease.

Reading review shows the French question; include its normal audio only if the
file still exists. Writing/Speaking review shows the English question. After
cleanup, Listening review shows its instruction, question ID, and
`Audio removed to save space; available to regenerate on request.` Do not reveal
a hidden transcript as a substitute for deleted audio. If audio has been
explicitly regenerated, show the original three speeds while those files exist.
Full references/translations and Speaking
answer audio may only be repeated if that question already reached Correct and
the reference was revealed. A summary must not reveal answers for skipped or
unresolved questions. Keep earlier corrections local; do not reconstruct the
whole hidden answer from fragments. List uncertainty-only dictation cases and
skip-only questions separately if present, not as confirmed mistakes. If there
were no confirmed errors, say `None — no confirmed errors this lesson.`

Compare progress at start and end in the SAME band, normally the lesson's
snapshot band. If the user selected another band during the lesson, show its
current percentage separately for the next lesson; never present a cross-band
subtraction as improvement. The start comes from the immutable lesson snapshot;
the end comes from the applied evaluation. Vocabulary and grammar comparisons likewise
use their immutable starting component snapshots and end calculations for this
same band. They summarize ALL bank items assigned to that CEFR level, not the
whole database and not just this lesson's selected items. For legacy lessons
without component snapshots, show the starting component as unavailable unless
it can be reliably reconstructed from saved evidence; never use the current bank
as an invented starting value. If external bank maintenance/intervening
learning changed the baseline, distinguish it from this lesson's effect using
`progress_before`. Components may be displayed to one decimal place, but the
overall integer is calculated from unrounded values. Show unchanged percentages
honestly, and explain unavailable values instead of inventing them.

Setting up these rules alone does not evaluate old trials, change familiarity
scores, assign a new percentage, or start/complete a lesson.

For uncertainty-only and skip-only cases, use `## Uncertain answers` and
`## Skipped questions` respectively, after Questions to review and before Summary;
keep both headings, using `None.` if empty. Each listed item uses
`[Section] — Passage [n] of [count]: [saved uncertainty / Skipped without an
assessable answer].` These lists do not classify uncertainty or silence as errors.

For an early stop or an unevaluated completed trial, reuse the same Lesson Review
headings, with `Status: Stopped — incomplete; no evaluation applied.` or
`Status: Trial completed — no evaluation applied.` directly below the title
(after the isolated-test mode line if applicable). Display the saved starting
progress and `End progress: Not evaluated.` instead of inventing assessed ending
values or suggesting an applied update. Vocabulary/grammar changes both say
`None — no familiarity changes.` Show only actually attempted questions with
confirmed errors; an unresolved best answer's outcome is `Unresolved when stopped.`
Preserve all unanswered item statuses, save Summary strings in closing_summary,
and retain audio. A request for a closing page alone is not authorization for an
exceptional assessment. A resumed session later closes under its actual status.

An explicitly authorized evaluation of an incomplete/trial session remains an
exception recorded in its evaluation and never changes its type/completion status.
It consumes that lesson ID's one evaluation; before later resuming such a record,
warn that it cannot receive a second update without a separately authorized,
versioned evaluation-policy change. Do not silently double-credit added attempts.

13. Clean Up Completed-Lesson Audio: Automatically remove generated audio files
once a full lesson is completed and its evaluation is safely saved as `applied`.
Do this before the closing Lesson Review. Do not delete audio from in-progress,
stopped/incomplete lessons, trials, or sessions with pending evaluations unless
the user explicitly requests that separate cleanup. Never mark a session completed
just to make it eligible. Do not run background cleanup when merely showing stats.

This permission covers ONLY the reproducible generated audio clips: Focus
vocabulary, Reading, Listening, and Speaking reference audio. Preserve ALL
generated text and other non-audio material, including French passages, English
sources/translations, examples, patterns, prompts, vocabulary/grammar targets,
and every reference answer. Preserve every user dictation transcript, attempt,
correction, reference flag, embedded evaluation, and familiarity score. Never delete
`lesson.json`, other lesson documents, user-supplied audio recordings, TTS scripts,
or shared model/voice assets. User recordings referenced by `response_audio_path`
are protected even if stored in the same audio folder.

Before deletion, validate the saved lesson and evaluation. Build an explicit
candidate list from non-null generated `audio` paths in Focus and question
objects; check it against the actual files. Each target must be a regular audio
file whose resolved path is inside this exact lesson's `audio/` directory, with
no symlink traversal, and must not be a protected user-recording path. Never use
a recursive folder delete, a broad wildcard, or an extension alone to authorize
deletion. Leave unreferenced/ambiguous files and all non-audio files untouched.
If a path's origin or scope is unclear, retain it and explain the issue.

Save an audit file `audio-cleanup.json` in the lesson folder with
`schema_version: 1`, `lesson_id`, `status` (`pending` or `completed`), `created_at`,
`completed_at` (null until done), `targeted_paths`, `removed_paths`,
`already_missing_paths`, and `bytes_removed`. Paths are lesson-relative; timestamps
are ISO 8601 with timezone. Save validated targets before deletion, append only
confirmed removals, and distinguish already missing files from newly removed
files. Retry an interrupted cleanup using the same audited targets; never reapply
familiarity changes. Mark completed only after eligible targets are absent and
all protected content remains intact. Report failures instead of claiming success.
Leave the empty audio directory in place if convenient.

Keep the original audio paths and speeds in `lesson.json` as historical generation
metadata; do not null them or erase their source text. The separate cleanup audit
lets historical lessons retain their original JSON schema and evidence unchanged.
Validation accepts intentionally absent files documented by that audit for a
completed lesson; missing audio in an active lesson still needs investigation.

At completion, briefly state that generated audio was removed, how many files
were removed (and space freed when known), and that all text and answers were
preserved. Old audio players will no longer work after removal. If the final
Speaking feedback is in the same closing reply, show the permitted correct text
but do not embed deleted audio; explicitly note the cleanup and regeneration
option. Completion cleanup overrides post-completion audio-player requirements.
On a later explicit request to replay/review audio, regenerate it from the saved
text at the saved speeds without rewriting the question, user responses, or
assessment evidence. Do not claim the regenerated waveform is the original.
Retain regenerated files for that requested review; clean them again when the
user finishes it, recording the new run as `audio-cleanup-<YYMMDDhhmmss>.json`
without overwriting the prior audit. Check all cleanup audit runs when resolving
historical missing paths; a regenerated file that currently exists is playable.

## Canonical `lesson.json` format (version 9)

Version 9 makes root `evaluation` the ONLY evaluation/change log and removes root
`assessment_log_path` and `evaluation_log_path`. All new lessons/trials use version
9. The nested evaluation uses schema 6: its evidence/change fields are unchanged,
but new level-unlock events point to evaluation_lesson_path instead of an
external assessment_log_path. Do not recreate the deleted log folder.

Version 8 introduced the embedded evaluation. Its existing contents remain valid
historical evidence without an external copy. Ignore obsolete log pointers for
lookup and recovery; do not delete historical fields or silently migrate records.
An explicitly approved migration may remove obsolete pointers while preserving
all content, but must not recompute or invent an evaluation. A legacy session
without embedded history is unavailable, not a reason to recreate an external log.

Version 7 adds root `policy_history`, `evaluation_log_path`, `clarifications`,
and `closing_summary`, plus `Focus.selection_notes`. These make rule snapshots,
mid-lesson assistance, fallback selection, and early-stop summaries recoverable
without chat history. Preserve existing
versions as historical records; missing new fields mean unavailable, not proof
that no assistance occurred. If resuming a legacy lesson requires newly stored
clarifications/policy fields, obtain approval for an explicit backed-up migration
first; do not write a version-7 shape while still labelling it version 6.
Existing legacy `clarifications.json` sidecars must be read alongside their
lesson's attempts when present, but are not the format for new lessons.

Version 6 adds root `vocabulary_progress_percent` and `grammar_progress_percent`
starting snapshots so the end-of-lesson arrows compare real starting and ending
values in the lesson's CEFR band. Preserve older lessons; missing historical
components are unknown, not zero. The evaluation schema is versioned separately.
Version 5 requires all three Speaking reference-audio versions in the existing
question `audio` object; the object shape is unchanged. Earlier records may
have null Speaking audio and remain valid historical records; do not backfill
completed questions or fabricate past audio playback. When resuming an older
lesson, generate and save missing reference clips for an unanswered Speaking
item before presenting its Correct feedback under the current rules.
Version 4 adds the root `cefr_progress_percent` field. Earlier versions do not
have an assessed percentage; interpret its absence as unknown, not zero.
Version 3 changes Speaking to four passage translations, matching Writing.
Version 2 changed Writing from four sentence translations plus a composition
prompt to four passage translations. Versions 2–3 kept object shapes unchanged. Preserve
older records: version 1 has five Writing items, and versions 1–2 have five
Speaking items. Do not rewrite them to match the new material counts.

This is the storage contract for all new lessons and section trials. Use valid
UTF-8 JSON, two-space indentation, the exact key names and capitalization below,
and plain text rather than presentation Markdown. Keep every defined key;
use `null` for an unavailable/not-applicable scalar and `[]` for an empty list.
Do not introduce alternative names such as `answer`, `user_answer`, or
`audio_normal`. Arrays are in presentation order. Examples below describe
reusable object shapes, not a complete generated lesson.

### Root object

```json
{
  "schema_version": 9,
  "lesson_id": "260907090000",
  "type": "lesson",
  "created_at": "2026-09-07T09:00:00-04:00",
  "updated_at": "2026-09-07T09:00:00-04:00",
  "ended_at": null,
  "timezone": "America/Toronto",
  "status": "in_progress",
  "completed": false,
  "cefr_level": "A1",
  "cefr_progress_percent": null,
  "vocabulary_progress_percent": null,
  "grammar_progress_percent": null,
  "evaluation": null,
  "policy_history": [
    {
      "recorded_at": "2026-09-07T09:00:00-04:00",
      "contract_revision": "2026-09-09.4",
      "teaching_policy": "lesson-v1",
      "familiarity_policy": "familiarity-v2",
      "progress_policy": "progress-v5",
      "rules_path": "rules.md",
      "reason": "Initial policy snapshot."
    }
  ],
  "clarifications": [],
  "closing_summary": [],
  "completed_lessons_today_at_start": 0,
  "active_sections": ["Reading", "Listening", "Writing", "Speaking"],
  "current_section": "Focus",
  "Focus": {
    "situation": null,
    "selection_notes": [],
    "vocabulary": [],
    "grammar": []
  },
  "Reading": {"status": "not_started", "current_item": null, "items": []},
  "Listening": {"status": "not_started", "current_item": null, "items": []},
  "Writing": {"status": "not_started", "current_item": null, "items": []},
  "Speaking": {"status": "not_started", "current_item": null, "items": []}
}
```

- `lesson_id` matches the lesson folder name and is never changed. Use actual
  start time, not the example date. `type` is `lesson` or `trial`; a trial lists
  only its tested sections in `active_sections`, but retains all five section keys.
  If a timestamp-named folder already exists (including a daylight-saving-time
  collision), do not overwrite or invent a suffix/date. Wait until an actual
  unused Toronto second and use that as the new start time.
- All timestamps are ISO 8601 with a timezone offset. `created_at` never changes;
  update `updated_at` whenever saving, and set `ended_at` on completion or stop.
- `status` at the root is `in_progress`, `completed`, or `stopped`.
  `completed` is true exactly when root status is `completed`. Completion means
  all active sections finished; a stopped session remains incomplete. Trials
  are never counted as completed daily lessons.
- `cefr_level`, `cefr_progress_percent`, `vocabulary_progress_percent`,
  `grammar_progress_percent`, and
  `completed_lessons_today_at_start` are snapshots at creation; do not update them
  as the user improves. Use the selected band in `assessments/level.json` and
  its freshly calculated starting percentage from Step 1, not a different band's
  latest evaluation percentage. Missing prior evaluations do not prevent calculation
  from valid banks; use a null percentage only
  when unavailable. The initial selected band is A1. Count prior completed full lessons on the same local
  date using completed full-lesson metadata and actual ended_at. An applied
  evaluation is not a prerequisite for counting completed full lessons.
- Use A1, A2, B1, B2, C1, or C2 for new CEFR placements; A1 is the beginner
  starting level. Older records labelled A0 remain unchanged as historical
  snapshots. When selecting new material from those records, use beginner A1;
  this label change is not evidence of a proficiency gain.
- `cefr_progress_percent` follows the Level and progress notation above: an
  integer 0–100 when assessed, or null when unknown or when the band is C2.
  This field describes the user, not the CEFR labels of individual vocabulary
  entries, grammar targets, or Focus objects.
- `vocabulary_progress_percent` and `grammar_progress_percent` are the starting
  component percentages for `cefr_level`, numbers in 0–100 or null if unavailable.
  Store them without display rounding; display to one decimal place. They use
  all items in the matching CEFR band and exclude every other band. Do not
  update these starting snapshots after evaluation; ending components belong
  in the embedded evaluation's `progress_after` calculations.
- `current_section` is `Focus`, `Reading`, `Listening`, `Writing`, `Speaking`,
  or null after completion. Each section's `current_item` is an item ID string,
  not an array index; it is null before starting or after completing that section.
  Preserve the position when stopped. Unused trial sections remain `not_started`
  with empty items. Stop the active section without altering finished sections.
- `policy_history` is nonempty, append-only, in time order. Each object has exactly
  the seven keys shown above; all are nonempty strings, with recorded_at an actual
  timestamp. Paths are lesson-relative and refer to immutable, complete rule
  snapshots. The initial event matches creation time. Subsequent events require
  an explicit user rule change and quote that authorization in `reason`. Use the
  latest applicable event; preserve policy labels in applied historical evaluations.
- `closing_summary` is an array of plain-text review-priority strings. Empty while
  active; set when stopping or completing. On a normally evaluated full lesson it
  copies the applied evaluation's summary for convenience; evaluation remains authoritative.
  Preserve a stopped summary until the next close, and do not interpret it as a
  completed evaluation or a new score. No hidden reference is stored in summary
  merely to evade answer hiding.

### Embedded evaluation and bank changes (version 9)

`evaluation` is null until an evaluation is actually prepared. A stopped lesson
or unevaluated trial retains null, not an empty successful evaluation. Once
prepared, it contains the COMPLETE evaluation schema-6 object defined under
Saving the evaluation safely, with all its fields, statuses, policy names,
timestamps, evidence-window IDs, progress calculations, item observations, and
summary. Do not introduce another evaluation schema or omit evidence to save space.

In particular, `evaluation.items` records each assessed vocabulary/grammar target:

- Identity: `bank`, `word`, `part_of_speech`, `grammar_id`, with null for the
  inapplicable identifiers. This includes clearly assessed non-focus items.
- Change: `old_familiarity` and `new_familiarity`, both integers 0–5, and `reason`.
  These values are the actual before/after of THIS evaluation, not necessarily
  the lesson's starting Focus scores if other learning happened in between.
- Evidence: `S`, `E`, `accuracy`, `current_S`, `current_E`, `current_accuracy`, and
  every supporting `observations` entry, using exactly the evaluation's defined shape.

Changed items are those with old_familiarity != new_familiarity; unchanged assessed
items remain in the array too. Group changes by bank for display, not by renaming
the stored fields. An applied evaluation with no changed items means evaluation
completed without score changes; it is different from evaluation null.

The embedded lesson_id must match the enclosing lesson. There are no external
log-path fields in version 9. Use lesson ID and this embedded object to index,
display, and recover an evaluation. Never create a second copy or reconstruct a
historical delta from today's banks. Applied evaluations remain immutable;
interrupted pending updates follow the recovery rules. This field survives audio
cleanup. For self-contained lookup, read `evaluation.items` for item changes and
`evaluation.progress_before`/`evaluation.progress_after` for their bank-level effect.

### Focus objects

Each `Focus.vocabulary` entry uses this shape:

```json
{
  "id": "vocab-01",
  "word": "être",
  "part_of_speech": "verb",
  "cefr_level": "A1",
  "gender": null,
  "selection": "review_fragile",
  "familiarity_at_start": 2,
  "headword": "être",
  "english_meaning": "to be",
  "useful_forms": ["je suis", "nous sommes"],
  "example_french": "Je suis à la maison.",
  "example_english": "I am at home.",
  "audio": {
    "normal": {"path": "audio/focus-vocab-01.wav", "speed": 1.0},
    "slow": null,
    "very_slow": null
  }
}
```

Each `Focus.grammar` entry uses this shape:

```json
{
  "id": "grammar-01",
  "assessment_id": "F03",
  "rule": "Present tense of être for identity, state, profession and location.",
  "cefr_level": "A1",
  "selection": "review_fragile",
  "familiarity_at_start": 1,
  "pattern": "subject + être + complement",
  "example_french": "Je suis à la maison.",
  "example_english": "I am at home."
}
```

- Assign local IDs `vocab-01`–`vocab-08` and `grammar-01`–`grammar-04` in full
  lessons. `word` and `part_of_speech` identify the vocabulary-bank entry;
  copy them exactly. `headword` is its displayed form, including a noun's article.
  Grammar `assessment_id` is the exact ID in the grammar bank, not a new ID.
- `selection` is `new`, `review_fragile`, `review_strengthening`, or
  `maintenance`; record the actual selection if a fallback was necessary.
  `familiarity_at_start` is an integer 0–5 and remains a historical snapshot.
- `gender` is `masculine`, `feminine`, `both`, or null when unknown/not applicable.
  Save lesson-relevant meanings, forms, and examples so the preview remains
  reconstructable even if the assessment banks later change.
- `Focus.selection_notes` is an array of plain-text strings explaining any
  requested-slot shortage and actual replacement; otherwise `[]`. Its exact keys
  are `situation`, `selection_notes`, `vocabulary`, and `grammar` in versions 7–9.

### Question object shared by all four sections

Every entry in a section's `items` array has exactly this shape:

```json
{
  "id": "listening-01",
  "kind": "passage",
  "task": "transcribe_french",
  "instruction": "Please transcribe the following audio into French.",
  "french": null,
  "english": null,
  "target_words": {"min": 30, "max": 50},
  "focus_vocabulary_ids": ["vocab-01"],
  "focus_grammar_ids": ["grammar-01"],
  "audio": {
    "normal": {"path": "audio/listening-passage-01-normal.wav", "speed": 1.0},
    "slow": {"path": "audio/listening-passage-01-slow.wav", "speed": 0.75},
    "very_slow": {"path": "audio/listening-passage-01-very-slow.wav", "speed": 0.5}
  },
  "status": "not_started",
  "attempts": []
}
```

- Item IDs are `reading-01`–`reading-04`, `listening-01`–`listening-04`,
  `writing-01`–`writing-04`, and `speaking-01`–`speaking-04`. Never renumber them
  during a session. An item is uniquely located by lesson ID, section, and item ID.
- Reading: all four items have `kind: "passage"`, `task: "translate_to_english"`;
  `french` is the source and `english` its reference translation.
- Listening: all four have `kind: "passage"`, `task: "transcribe_french"`;
  `french` is the exact spoken transcript and `english` its reference translation.
  Populate both fields before teaching; the nulls above are placeholders, not
  permission to omit the hidden answer. Hiding answers is a presentation rule.
- Writing: all four items have `kind: "passage"` and
  `task: "translate_to_french"`; `english` is the source passage and `french`
  its reference translation. Populate both before teaching. `instruction` is
  `Please translate the following passage into natural French.`
- Speaking: all four items have `kind: "passage"` and
  `task: "translate_to_french"`; `english` is the source passage and `french`
  its reference translation. Populate both before teaching. `instruction` is
  `Please translate the following passage aloud into natural French using dictation, then send the text.`
- `target_words` is `{ "min": 30, "max": 50 }` for Reading/Listening,
  and the level-dependent range from the Writing/Speaking table for each
  Writing and Speaking reference translation.
- Focus ID arrays list actual targets used in the question, referencing its
  saved Focus objects. Do not invent bank IDs or claim unused coverage.
- All `audio` objects have the same three keys. Use null for unused versions:
  Reading and vocabulary have normal only; Listening and Speaking have all three;
  Writing has all three null. Speaking audio reads the saved French reference,
  not the English prompt, and is revealed only with Correct feedback in Step 11.
  Its paths follow `audio/speaking-passage-NN-normal.wav`, `-slow.wav`, and
  `-very-slow.wav`, with speeds `1.0`, `0.75`, and `0.50` respectively.
  Non-null versions always contain
  `path` and numeric `speed`. Paths are relative to the lesson folder and must
  point to generated files before presenting the active question. After completed
  lesson cleanup, retain those paths as historical metadata; `audio-cleanup.json`
  records their intentional removal. Never render a player for a missing file.
  Resolve to absolute
  paths only for playback. Never store temporary absolute paths in a saved lesson.
- Item status follows the Recording answers rules above. Set `awaiting_answer`
  when first presenting it, `retry` after Almost correct/Needs revision, and
  `correct`/`skipped` only for their corresponding verdicts. A section becomes
  `completed` only when every item is correct or skipped.

### Attempt object

Append the following object to the current item's `attempts` after each answer:

```json
{
  "attempt_number": 1,
  "recorded_at": "2026-09-07T09:20:00-04:00",
  "response": "the user's exact answer",
  "response_audio_path": null,
  "verdict": "Needs revision",
  "corrections": ["The targeted correction or hint given to the user."],
  "reference_shown_before_attempt": false,
  "reference_revealed": false
}
```

Number attempts consecutively starting at 1 within each item. Preserve original
spelling, accents, capitalization, and wording in `response`, including skip
requests. `response_audio_path` is a lesson-relative path only if the user
actually supplied audio saved with the lesson; otherwise null. For audio-only
answers, use null for `response` unless an actual transcript is available.
Do not infer pronunciation evidence from typed French. Never fabricate an
answer or grade when no assessable response is available.

Use only the four verdict strings defined above. `corrections` is an array of
plain-text strings retaining the `incorrect → correct: explanation` format,
without Markdown italics or bullet prefixes; use `[]` if no correction was given.
Record what was actually
shown, not hidden model reasoning. The two reference flags track FULL reference
exposure only; false does not prove independence. Read prior corrections and
clarifications to identify local assistance. They are false for open-ended tasks with
no reference answer. Keep reference texts in the question, not duplicated in
each attempt. Do not fabricate timestamps for legacy attempts; use null when
the original recording time is unavailable.

Under the current answer-reveal rule, set `reference_revealed` to true only for
`Correct` feedback that shows a reference; it is false for Almost correct,
Needs revision, and Skipped. Preserve historical flags from earlier rules as
recorded, including past Almost correct or Skipped attempts that revealed answers.
Do not change the current question or record a new attempt for a rule-change request.

### Clarification object (version 7)

Append each substantive mid-lesson explanation to root `clarifications`, not to
an attempts array. This fixed shape stores the actual explanation in plain text:

```json
{
  "clarification_number": 1,
  "recorded_at": "2026-09-09T09:20:00-04:00",
  "section": "Reading",
  "item_id": "reading-02",
  "after_attempt_number": 1,
  "user_question": "Explain libre and venir.",
  "explanation": ["libre means free or available.", "venir means to come."],
  "assistance_targets": [
    {"bank": "vocabulary", "word": "libre", "part_of_speech": "adjective", "grammar_id": null}
  ],
  "full_reference_revealed": false
}
```

All nine keys are required. Numbers are consecutive across the lesson, starting
at 1. `section` is Focus or an active section name; `item_id` is null for Focus,
otherwise an existing question ID. `after_attempt_number` is 0 before an answer,
otherwise the number of attempts already saved for that item at explanation time.
`user_question` is verbatim. `explanation` is a nonempty string array of what was
actually taught, including example text and its translation. The abbreviated
example above illustrates shape, not permission to omit an actual explanation.
`assistance_targets` lists precisely the answer-specific bank targets helped:
vocabulary uses exact word/POS and grammar_id null; grammar uses its exact ID and
word/POS null. Use `[]` when no answer-specific target was helped; explain any
unmapped expression in the explanation rather than inventing a bank identity.
All target objects have the same four keys. Before Correct, full_reference_revealed
must be false; a clarification cannot reveal a still-hidden reference. Its true
value is allowed only when repeating a reference already earned with Correct.

During archive viewing, show clarifications in their saved positions: before
attempt 1 when after_attempt_number is 0, otherwise after the indicated attempt
and before its next retry. Use `#### Explanation [number] — [Toronto time]`,
`Your question:`, `Explanation:`, `Assistance targets:`, and
`Full reference repeated: Yes/No`. Italicize language material and the user's
quoted question as appropriate; preserve saved wording, not a fresh explanation.
Focus clarifications follow their saved Focus preview. Read these records during
evaluation; never mistake a helped retry for an independent success.

### Validation and looking up previous lessons

Run the read-only `scripts/check_contract.py --self-test` with an available
Python 3.9+ runtime after changing this contract or its checker; the installed
`.kokoro-env/bin/python` is suitable. Run `scripts/check_contract.py` after new
lesson/assessment writes, with `--root [active data root]` for isolated tests.
The checker parses canonical JSON examples, checks bank identities and score
bounds, selection, optional library metadata, navigation versions 1/2, and
version-9 structural invariants, including the embedded
evaluation's shape, identities, and score bounds; no external log is required. It reports legacy
records instead of migrating them. It is a guardrail, not a complete JSON Schema
validator, semantic grader, or replacement for the manual checks below. Update
the checker alongside schema changes and keep its tests passing. Never change a
record merely to silence a checker that is using the wrong historical schema.
After bank-browser changes also run `scripts/test_browse_bank.py` and
`scripts/test_new_learner.py`. Their fixtures must not change live scores,
favorites, visits, navigation, lessons, or test-mode pointers.

Before teaching and after updating a record, check valid JSON, required keys,
unique item/Focus IDs, valid references, status/cursor consistency, sequential
attempt numbers, and the agreed material counts, lengths, and audio speeds.
Check audio-file existence for active material; completed lessons with a cleanup
audit may intentionally lack generated clips. Do not regenerate deleted audio
just to evaluate historical transcripts or display text-only stats.
An empty skeleton is allowed during generation, not when starting a full lesson.
Save each response and progress update together; never discard earlier attempts.

For history lookup, read metadata first to select by date, level, type, and
completion. Then read `Focus` for covered targets and starting familiarities,
and the relevant section's `items[].attempts` and `clarifications` for evidence.
The earliest usable unaided response, earlier corrections, explanation targets,
and reference flags together distinguish independent from supported answers.
Do not treat skips, unanswered questions, or answer-assisted retries as unaided
mastery. Current familiarity remains in `assessments/`; never rewrite historical
Focus scores to match it.

Records without `schema_version` are legacy: inspect their actual keys rather
than assuming this layout, and preserve their evidence. Do not silently rewrite
old lessons. Any future format change must update this contract and increment
`schema_version`, rather than creating incompatible layouts under the same version.
