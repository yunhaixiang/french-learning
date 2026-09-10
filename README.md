# French learning buddy

A daily French-learning project, starting with beginner A1 material and working toward NCLC 7 on
TEF Canada within three years. The aim is to learn through meaningful exposure,
practice, feedback, and review—not to rush through a fixed calendar.

## Start here

Open a chat in this project and say **“Menu”** to see the starting page:

1. Begin a new lesson
2. Resume an incomplete lesson
3. View my stats
4. Set my level
5. View a completed lesson
6. Help

Reply with the option number or name. You can also ask directly, for example
“Begin today's lesson” or “Continue my unfinished lesson.” If several unfinished
lessons exist, you will be asked which one to resume. An unfinished trial is
labelled separately from a full lesson.

Every menu page has a fixed layout: the same headings, labels, tables, and
navigation prompts on each visit, including when there are no saved records.
Only your data and the relevant state change. These formats are defined in
AGENTS.md. Lesson openings, questions, feedback, and closing reviews also follow
their established templates.

**View my stats** shows your selected level, that level's vocabulary and grammar
progress, unlocked levels, completed lessons, and saved unfinished sessions.
**Set my level** shows available and locked CEFR bands. Type an unlocked band's
name to select it for subsequent lessons; just opening the page changes nothing.
Your scores and any unfinished lesson stay unchanged.
**View a completed lesson** lets you choose a completed full lesson by date or
ID and see its entire saved content: the focus preview, all four sections,
source passages, reference translations, **every attempt and its feedback**,
and the saved evaluation. Longer lessons are shown in parts without omitting
attempts. This explicit archive view includes references for skipped questions;
it does not change what was recorded during the lesson or reassess your scores.
Deleted audio can be regenerated on request; all text remains available.
New lesson.json files also contain the full evaluation, including every vocabulary
and grammar item's old and new familiarity, the reason, and supporting answers.
The evaluation is stored only inside that lesson.json—there is no separate log
folder or duplicate evaluation file. Its pending/applied status supports safe
recovery without awarding changes twice. An unevaluated lesson has no evaluation yet; this is
distinct from a completed evaluation that made no score changes.
**Help** explains the lesson workflow and available commands. These views do
not change your scores or start a lesson. You can ask for **“Menu”** during a
lesson without losing your place; menu choices are not recorded as answers.

The assistant prepares the material, presents questions, and saves your answers.
You do not need to edit the project files yourself. Audio preparation may take
a little time before the lesson starts.

If you start a new chat, say:

> Read AGENTS.md and my latest lesson and assessment records, then continue
> from where I left off.

Saved files provide continuity; the project does not rely only on chat history.

AGENTS.md includes a recovery checklist for every new conversation. A small
`state.json` checkpoint records the open page, pending choice, active lesson, and
whether you are in an isolated test. Browsing never changes your learning scores.
Each new lesson also saves an immutable `rules.md` snapshot, so later instruction
changes do not silently change an unfinished lesson. Existing historical records
are preserved rather than automatically rewritten into the latest format.

The assistant also has a read-only consistency checker for the saved format,
bank identities, and score bounds. It does not grade answers or change records.
Backups are preserved before score updates; they are not counted as extra lessons.

## Your daily lesson

Allow roughly one hour: four sections of about 15 minutes. Retries may make a
section longer, and you can stop when you need to.

At the beginning, you see your current progress, such as **35% A1** (an example,
not your actual score), plus your vocabulary and grammar percentages for that
same CEFR band. These cover all bank items in that band—not the whole database
or only today's focus. Then comes a short focus preview: **eight vocabulary items** (four new, four
review) and **four grammar targets** (two new, two review). It includes meanings,
useful forms, examples, and vocabulary audio. This is an introduction, not a quiz.

| Section | What you do | Material |
|---|---|---|
| Reading | Translate French into natural English. | Four passages, each 30–50 French words, with audio. |
| Listening | Listen and type what you hear in French. | Four passages, each 30–50 French words. Replay at 100%, 75%, or 50% speed. |
| Writing | Translate English passages into natural French. | Four passages; length depends on level. At A1, the reference translations are about 25–45 French words each. |
| Speaking | Translate English passages aloud into French, then submit the dictated text. | Four passages, with the same level-based lengths as Writing. After a correct answer, hear the French reference at 100%, 75%, or 50% speed. |

Questions arrive one at a time. For translations, natural alternatives are
accepted—you do not need to match one exact wording. Writing and Speaking length is a guide
for preparing material, not a word-count test for your answer.

Lesson material can use vocabulary and grammar from your selected CEFR band
and any lower band, including items you have never encountered. For example,
B1 lessons may include unseen A1 or A2 items. Unseen focus items are still
labelled new, and appearing in a passage does not automatically raise familiarity.
Lower-band items contribute to their own band's progress, not your selected band's.

These are our learning activities, not a full mock exam. Completing the project
or receiving high familiarity scores does not guarantee a TEF result.

## Feedback and retries

Feedback shows a verdict, your answer, and brief corrections in this format:

- *étudie* → *étudier*: after *voulons*, use the infinitive (*to study*).

- **Correct:** see a reference answer, then move to the next question.
- **Almost correct:** use the corrections and try the same question again.
- **Needs revision:** use the hints or local corrections and retry.
- **Skip:** move on without revealing the reference answer.

The full reference answer is revealed **only after a correct response**.
Individual corrections can be given before then.

Every submitted answer, retry, skip, and its feedback is saved. A successful
retry does not erase the earlier mistake.

Ask questions at any point. Explanations are saved separately from quiz attempts
inside new lessons' `lesson.json`, along with the targets that received help.
This keeps a later retry from being mistaken for unaided understanding after a
new conversation. Asking a question does not move you to the next passage.

## Speaking with dictation

Use the app's voice-to-text input for your French answer, then send the text.
Try to build the answer aloud rather than type a draft first. For a retry,
say it again using dictation. No Voice Memos attachments are needed.

After a correct response, the French reference answer comes with three playable
audio versions: normal (100%), slow (75%), and very slow (50%). You can listen
and repeat along if you wish. These answer recordings stay hidden during
attempts and retries, and are not revealed when you skip.
Generated audio is temporary: it is removed when the full lesson and its
evaluation are complete. Completion cleanup takes precedence over replaying
the last answer's audio in the closing review; audio can be regenerated on request.

Feedback is based on the transcript's meaning, vocabulary, and grammar—not
pronunciation, rhythm, or speaking speed. Dictation can mishear or normalize
what you say. If it gets a word wrong, tell the assistant rather than treating
the transcription as proof of a French mistake. Garbled phrases may be flagged
as possible pronunciation unclearness, with a request to say them again clearly;
this is a practice cue, not a confirmed pronunciation diagnosis. There is no
pronunciation score.

## Useful requests

- “Skip this question.”
- “Explain that correction more simply.”
- “This is too easy” or “This is too difficult.”
- “Set my lesson level to A2.” (Once A2 is unlocked.)
- “Stop the lesson here.”
- “Show my recent progress and recurring mistakes.”
- “Let's test just the listening section.”
- “Menu” or “Help.”

Stopping preserves your position and answers without marking the lesson complete.
Starting a different lesson while one is unfinished requires confirmation.
Section trials are saved separately from full lessons and do not count toward
your completed daily lessons.

## Your progress records

- [AGENTS.md](/Users/yunhai/Home/Repositories/french-learning/AGENTS.md): the assistant's detailed teaching instructions and lesson-file format.
- [lessons/](/Users/yunhai/Home/Repositories/french-learning/lessons): dated lesson folders. Each `lesson.json` contains material, focus, answers, feedback, and progress; its `audio/` folder holds temporary generated clips. An `audio-cleanup.json` audit records completed-lesson audio removal.
- [Vocabulary](/Users/yunhai/Home/Repositories/french-learning/assessments/vocabulary.json) and [grammar](/Users/yunhai/Home/Repositories/french-learning/assessments/grammar.json): familiarity records on a **0–5 scale**, from untested/unfamiliar to consistently reliable.
- `lesson.json` → `evaluation`: the sole record of that lesson's vocabulary and
  grammar changes, evidence, and before/after progress.
- `assessments/level.json`: your selected lesson level and permanently unlocked levels.

Lesson folder names use the local Toronto start time: year, month, day, hour,
minute, second. Tests are identified as trials inside their lesson records.

Review selection prioritizes weak or recently incorrect items. Difficulty follows
your demonstrated progress; familiarity scores and CEFR estimates are learning
guides, not official exam scores.

The review schedule uses intervals of 1, 2, 4, 8, and 16 completed full lessons
for familiarity scores 1–5. Recent errors are due immediately; time alone never
lowers a score. If a requested new/review category is short of items, the preview
explains its replacement instead of mislabelling a known word as new.

Your selected learning band and its progress are displayed as **70% A2**, for
example—not 70% correct on a quiz. A1 is available from the start. A displayed
percentage **of 80% or higher** unlocks the next band: A1 unlocks A2,
A2 unlocks B1, and so on. Exactly 80% qualifies; 79% does not.

You choose when to switch and may select any unlocked band, including an easier
one for review. There is no automatic switch, even at 100%, and earned unlocks
remain available if scores later decrease. A level choice applies to subsequent
lessons; your current lesson and historical snapshots stay unchanged. Each band
keeps its own progress, so switching neither resets familiarity nor transfers
the previous band's percentage. These are curriculum choices, not certified levels.

At the end of a lesson, the assistant considers **the lesson you just completed
plus the two previous completed full lessons**. If fewer exist, it uses those
available. Trials and incomplete lessons do not fill the historical window.
Earlier answers provide evidence of consistency; their old score changes are
not applied again. Each new evaluation is applied once, and an item must have
fresh evidence in the current lesson to change. Merely appearing in an earlier
lesson cannot produce another increase or decrease.

Each item's familiarity can rise or fall by at most one point per completed
lesson. Promotions use independent evidence across the three-lesson window and,
at higher scores, different sections including French production. They also
require a fresh independent success and at least 80% independent accuracy for
that item in the current lesson. A decrease requires at least two confirmed
errors in different questions across the window, with more errors than successes,
plus a fresh error and more errors than successes in the current lesson.
Assisted retries are
recorded as learning, not extra independent successes; uncertain dictation errors
and unassessed items receive no penalty. A new item's move from 0 to 1 means
newly encountered, not mastered.

At the end, your **Lesson Review** shows:

- Starting → ending progress in the same band, with separate before → after
  arrows for that band's vocabulary and grammar percentages.
- Every vocabulary item and grammar target that improved or regressed, with
  its old → new familiarity and a short reason. Newly encountered items are labelled.
- Every question from the just-completed lesson with a confirmed error, including ones you later corrected:
  the original question, **Your best answer**, any remaining corrections, earlier
  mistakes, and final outcome. The best answer is your highest-verdict attempt
  (latest if tied), not a rewritten reference; assisted improvement is labelled.
- Any newly unlocked level.
- A **Summary**: a short bullet list of the most important vocabulary and grammar
  to review, ordered by priority, with a key reminder for each. It is not an extra
  quiz you must complete immediately.

Uncertain dictation and skips without errors are listed separately, not treated
as wrong answers. After audio cleanup, listening questions are identified without
broken audio players; you can request regenerated audio. Hidden reference answers
remain hidden for skipped questions, including in the final review.

## Saving space

After a full lesson is completed and its evaluation is saved, its generated
audio files are automatically removed. **All lesson text, generated materials
other than audio, your dictation transcripts, answers, retries, corrections, and
progress records are kept.** Unfinished lessons and trials retain their audio;
user-supplied recordings and shared TTS models are not deleted.

Old audio players will stop working after cleanup. Ask to regenerate a clip
from the saved text when you want to listen again. The assistant reports what
was removed and how much space was freed when known.

## Progress calculation

It then calculates your **progress percentage**: the average of vocabulary
progress and grammar progress in your
current band, giving each bank 50% weight. Each bank's progress is its average
familiarity divided by 5, expressed as a percentage; untested items count as 0.
The final percentage is rounded down to a whole number. For example, 60%
vocabulary progress and 80% grammar progress give 70% overall.

This is an internal curriculum indicator, not a precise measurement of CEFR
ability. It can stay unchanged or decrease as evidence changes. Familiarity 5
means consistently reliable in varied practice, not measured automaticity or a
guaranteed TEF result. If either bank lacks items
for your band, the percentage remains unassessed; this currently affects C1
because its grammar pool is empty; C1 can be unlocked from B2, but cannot yet
unlock C2 through this calculation. C2 has no next band here and is displayed
without a percentage. Progress summaries and calculation details are saved in
each lesson.json's evaluation; historical lesson snapshots are preserved.

Avoid opening `lesson.json` during a question if you want an unaided attempt:
it contains the hidden reference answers. Keep backups of this folder to protect
your long-term record.

This README is your quick guide. AGENTS.md is the detailed source of truth for
the current lesson rules.
