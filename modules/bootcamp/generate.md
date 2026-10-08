# Bootcamp — Generator (Top-5 mistakes · 15 items/day ≈ 20 min)

Trigger: `/telc <level> bootcamp`. Tool prefix: `uv run $SKILL_DIR/tools/tutor.py` (written `tutor.py` below). All numbers come from `tutor.py`; never compute or estimate them yourself.

## Goal (what is measured, exactly)
Within the bootcamp length L (default 14 days, shorter when the exam is near), **≥ 60 % of targets (3 of 5, 2 of 3)** are **confirmed**. The exact `goal_needed` comes from `tutor.py`:
(a) ≥ 80 % correct in the last 10 drill items, on ≥ 3 different dates, spanning at least `min_span_days` calendar days; AND (b) the final check passes (first batch of hint-free items: ≥ 2/3 correct, or ≥ 4/5 with 5 items) on day L−2 or later.
This measures **drill accuracy on your top error patterns**, not exam points and not free-writing quality. The optional `transfer` measure (errors per 100 words, first vs last measurement) shows whether it carries over to writing.

## 0. Entry logic (follow in order)
1. Run `tutor.py status`.
2. `needs_exam_date` true and the user has never been asked: ask once "Wann ist deine Prüfung? (YYYY-MM-DD, or skip)". If given: `tutor.py exam-date set <date>`. If skipped, continue (14-day default). Past date: ask for a new one.
3. `bootcamp: inactive` or `done` → `tutor.py bootcamp-start`. If its output has `warning` or `bootcamp_viable` false, tell the user honestly and offer triage (top-3 errors + mocks, see `rules/exam_countdown.md`) instead.
   `active` → never restart (start refuses without `--force`; use `--force` only if the user explicitly wants to discard progress).
   Targets with `from_data=false` (fresh profile): day 1 is the diagnostic (3 items per target, mixed difficulty). The tool seeds their weights from the diagnostic accuracy. Tell the user the targets are priors until they submit graded tasks (suggest `/telc <level> correct schriftlich`).
4. `expired` or `goal_reached` → `next_step` says what to do: final check if pending, else `tutor.py bootcamp-close`.
5. Optional at the beginning: ask the user to write ~150 words (or reuse a graded text), then `tutor.py transfer first --words W --errors E`. At the end use `transfer last`.
6. Print a 3-line header: `Tag X/L · Phase · five targets with accuracy_last10 and band`. One Franz line.

## 1. Phases (day numbers scale with L; the tool returns `phase`)
| Phase | Days (L = 14) | Content |
| :-- | :-- | :-- |
| A: Diagnose & lock | 1–2 | Mixed items, 3 per target; mini-lesson per target (≤ 6 lines, forces logic + 1 mnemonic). |
| B: Drill | 3–9 | `todays_allocation` items. Mastered targets get 1 spaced-review item. |
| C: Transfer | 10–11 | Items embedded in exam-style micro-tasks (3-gap Sprachbausteine snippet, 3-sentence email paragraph, 2-item Lesen mini). |
| D: Final check | L−2 … L | `drill --final` items, 3 per target, no hints, fresh content (the tool's `todays_allocation` switches to this). |

## 2. Item design
Every item must have ONE defensible answer. Time target: ≤ 40 seconds per item; **exemption:** Phase C micro-tasks may take up to 2 minutes each, and the 15 items then shrink to what fits ≈ 20 min.
Rotate these formats within a category (≥ 2 per session):
1. **Fix it** — sentence with the error; the user rewrites it.
2. **Produce it** — prompt forcing the structure ("Combine with *obwohl*: …").
3. **Choose it** — 3 options, exactly one correct.
4. **Spot it** — which of 3 sentences is wrong, and why (one line).
Difficulty: accuracy < 60 % → single clause, hint allowed; 60–80 % → exam-like sentences; > 80 % → traps, longer sentences, exceptions from `rules/persona_franz.md`. Fresh vocabulary and topic every time.

Item recipes by category key (every key exists in `memory/error_profile.template.json`):
| Key | Typical item |
| :-- | :-- |
| `verb_position` | Fix: Nebensatz verb not at the end / inversion after position 1. Produce: combine with *weil, obwohl, dass, damit, nachdem*, starting with the second clause. |
| `middlefield_order` | Put 4–5 boxes in the frame (pronoun, time, place, *nicht*). |
| `case_prepositions` | Preposition + noun-phrase gaps incl. Wechselpräpositionen and fixed pairs (*warten auf + Akk*). |
| `adjective_endings` | Declined phrases after definite/indefinite/zero article; Franz hack + exceptions. |
| `article_gender_agreement` | Gender of 10 nouns via suffix patterns; noun–pronoun agreement. |
| `verb_forms_tense` | Perfekt vs Präteritum in writing, Partizip, Passiv, *wäre/hätte/würde*. |
| `relative_pronouns` | Pronoun by antecedent gender + own-clause case; build a relative clause. |
| `pronominaladverbien` | *darauf, daran, worüber, wofür*; person → *auf ihn*, thing → *darauf*. |
| `connectors_variety` | Replace *aber/weil/und* with B2 connectors with correct word order. |
| `register_formality` | Informal → semi-formal email phrasing; find the register break. |
| `word_choice_collocation` | Verb–noun collocations, Nomen-Verb-Verbindungen. |
| `spelling_caps_punctuation` | Capitals/commas in a 4-line text; compounds; *das/dass*. |
| `leitpunkte_coverage` | Given 4 Leitpunkte + skeleton, write the 2-sentence development of one. |
| `email_form_elements` | Betreff + Anrede + Schlussformel for a scenario. |
| `lesen_detail_trap`, `lesen_negation_trap`, `lesen_headline_trap`, `lesen_x_trap`, `lesen_other_trap` | 80–120-word mini-text + 2 questions isolating the trap in the key. |
| `sb_grammar_gap`, `sb_distractor_box` | 3-gap mini-cloze with the exam's trap; explain the rejected option. |
| `text_too_short`, `simple_structures_only`, `vocabulary_copied_from_prompt`, `thema_situierung_verfehlt` | Produce it: expand a 2-line stub to ≥ 150 words / upgrade 3 simple sentences to Satzgefüge / paraphrase 3 prompt phrases / write the Situierung sentence. |

## 3. Output template (format example only, never reuse content)
```
**Bootcamp · Tag 4/14 · Phase B (Drill)**
Verbstellung 62 % (near) · Mittelfeld 40 % (weak) · Adjektivendungen 55 % · Präpositionen 70 % · Relativpronomen – (neu)
Franz: Vier Tage, viermal Verbstellung. Heute drehen wir den Spieß um!

**Mini-Lektion: Nebensatz** (≤ 6 Zeilen) …

1. *(Fix it)* Ich bleibe zu Hause, weil ich habe Fieber.
2. *(Choose it)* Er wartet ___ den Bus. a) für  b) auf  c) an
…
15. …
⏱ Ziel: 20 Min. Antworte nummeriert (1: …, 2: …).
--- ENDE DER AUFGABE ---
```
Then save the slot with every `format`, `prompt` and any visible `options` needed to re-display the exercise (the answer and `accept` list stay hidden from the user):
`tutor.py task save` with JSON `{"level":"b2","module":"bootcamp","day":4,"items":[{"n":1,"category":"verb_position","format":"fix","prompt":"…","answer":"…","accept":["…"],"why":"…"}]}` (items need `category`; the tool does not require `answer` for bootcamp, but always include it for the evaluator).
Hide category labels from the user; shuffle category order.

## 4. Final check (from day L−2, `todays_allocation` = FINAL items)
3 fresh, hint-free items per pending target, saved in the bootcamp slot with the same layout; the evaluator records them with `drill --final`. Only the first batch of final items per target counts. After grading: copy `goal_needed` from the tool and report confirmed / provisional / weak targets, an honest verdict on the ≥60% goal, and a maintenance suggestion (2 items per confirmed target, full drill for the rest).

## 5. Common failure modes to avoid
- Computing accuracy/bands yourself, or calling a target "mastered" before the tool does.
- Starting a second bootcamp on top of an active one; skipping `bootcamp-start` and calling `drill` anyway.
- Items with two defensible answers; reusing content; showing the category or the answer in the prompt.
- Wrong key names (use only keys from the table); fewer than 2 formats per category.
- Final-check items with hints; mixing final items into a normal day's `drill` without `--final`.
- Free-form layout instead of the template.

## 6. Integrity
- Only real recorded attempts count; fewer than 10 attempts = "building", never "mastered".
- An ambiguous item is dropped, not recorded.
