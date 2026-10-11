# Schriftlicher Ausdruck — Evaluator

Trigger: `/telc b2 correct schriftlich`. **Every correction obeys the Correction safety protocol in `rules/feedback_format.md`.** Load slot `schriftlich` (`uv run $SKILL_DIR/tools/tutor.py task show --slot schriftlich`: both tasks + Leitpunkte), the user's text, `rules/telc_b2_architecture.md` §5, `rules/schriftlich_anchors.md`, `rules/redemittel_b2.md`, `rules/persona_franz.md`, `rules/feedback_format.md`. The rubric is the official one; add no rules.

## Step 0 — Identify and count
1. Which task (A/B) did the user answer? If unclear, infer from content. Matches neither → candidate for *Thema verfehlt*.
2. `uv run $SKILL_DIR/tools/tutor.py wordcount` on the text. Show **Wörter: N** first. N < 150: say it is below the official minimum and likely misses Leitpunkte; do NOT auto-fail; record key `text_too_short`.

## Step 1 — Checklist (facts, no scoring yet)
| Element | Present? |
| :-- | :-- |
| Betreffzeile · Anrede · Einleitung · Schluss · Schlussformel | list each |
| Per CHOSEN Leitpunkt (3 of 4, or 2 + own): understandable and fitting the task? | list |
| Own aspect tied to the situation | y/n |
| Register consistent (Sie, polite, Konjunktiv II) | y/n |
| Links between points; variety beyond aber/dass/weil; not only "Ich…" starters | y/n |
| Complexity: Nebensätze, Passiv, Konjunktiv, Relativsätze present? | y/n |
| Vocabulary copied from the prompt? | y/n |
Do NOT penalise missing sender/address/date or a missing signature. Paragraph-per-Leitpunkt is a tip only.

## Step 2 — Grade (A=5, B=3, C=1, D=0) using the official descriptors (§5)
The letters are the [TIPPS] grid labels; the current telc Handbuch names the same levels for II and III: A = *B2 gut erfüllt* (5), B = *B2 erfüllt* (3), C = *B1* (1), D = *A2 oder darunter* (0). Each criterion is ×3 (max 15), total max 45; telc uses two trained raters (per [TIPPS] the second rating overrides the first), this evaluator gives one simulated rating. For III, how strongly errors disturb comprehension matters, not just their number.
- **I Aufgabenbewältigung** ([HB-neu] ground truth): count a Leitpunkt (or an own aspect tied to the situation) when it is written **verständlich und passend** to the task. Do NOT withhold credit because it is one sentence or one Satzgefüge (that is only the older [TIPPS] wording, a depth tip). Not credited: unintelligible, off-task, or not tied to the situation. A = 3 Leitpunkte, or 2 + 1 own aspect; B = 2, or 1 + 1 own aspect; C = 1 Leitpunkt OR 1 own aspect; D = none. Never penalise or list as "missing" a Leitpunkt the candidate was free to skip (3 of 4, or 2 + own).
- **II Kommunikative Gestaltung:** A is NOT given if Betreffzeile/Anrede/Schlussformel are missing **AND** the vocabulary range is not fully adequate (both). A missing Betreff alone does not cap II. B is not given for wrong/wavering register, vocabulary inadequate for B2, or Leitpunkte listed linearly without logical links. **C** if Textlogik, Verknüpfungselemente, Wortschatzspektrum and Register are **überwiegend unpassend** and would make a negative impression on the recipient. **D** if they are **gänzlich unpassend**.
- **III Formale Richtigkeit:** judge *systematic* errors: A none (only occasional slips; Erstsprache influence may occur) · B few, meaning not endangered · C several (despite clear Erstsprache influence), mostly still clear · D many elementary systematic errors (tenses mixed, agreement missing; spelling often phonetic), mostly still clear. Simple-only grammar: no A/B for III. Capitalisation counts. Count only errors that passed the Correctness guard below.
- **Gatekeepers:** *Thema verfehlt* → `--thema-verfehlt` (D on all; key `thema_situierung_verfehlt`). *Situierung verfehlt* → `--situierung-verfehlt` (D on I only; II/III graded; same key).
- **Choosing between two grades:** pick the grade whose official descriptor best fits the whole text. For every grade above C write one quoted piece of evidence from the user's text. Compare with the anchors in `rules/schriftlich_anchors.md`. No "benefit of the doubt" for the grade itself and no "round up/down" rule (benefit of the doubt applies only to whether a single form is an error, see the guard).

Then: `uv run $SKILL_DIR/tools/tutor.py score-writing <I> <II> <III> [flags] --record` and report the points it returns (max 45). Never add yourself.

## Correctness guard (run BEFORE Step 2 III and Step 3)
Apply the **Correction safety protocol** of `rules/feedback_format.md` to every candidate error (true one-line rule, Stilfrage if doubtful, slips not counted, re-read the corrected sentence, minimal change, record only confirmed errors, disputes). Schriftlich specifics:
- **Typed transcription of a handwritten text:** doubled/missing letters, stray commas or a one-off wrong ending are likely typing slips: not counted for III, not recorded. Only recurring patterns count as *systematic*.
- **III is about systematic errors:** one-off slips ("Ausrutscher") and Stilfragen do not lower III; never count the same pattern twice as two systems.
- **Known past mistakes of this evaluator (never repeat):** a correct Perfekt flagged as a tense error (Perfekt is normal in emails); `sollte … saubere Umkleiden … gibt` "corrected" to `sollten … geben` with a false "plural agreement" reason (right: `sollte es … saubere Umkleiden geben`; `es` is the subject, the Umkleiden are Akkusativ; the only error was `gibt` after the modal); a correct `entsprach der Beschreibung` (Dativ) changed; typing slips counted; the older [TIPPS] "more than one Satzgefüge" used to refuse a Leitpunkt; an unchosen Leitpunkt listed as missing.

## Step 3 — Top-3 lessons (Franz)
Choose by score impact, preferring active bootcamp targets. Per `rules/feedback_format.md`: `~~error~~ → **correction**` (only confirmed errors, minimal change), the true rule + forces-based why (word order → Box Model), absurd image, key. Record: `uv run $SKILL_DIR/tools/tutor.py errors <category>=1 …`. Mapping: a chosen Leitpunkt not credited (not understandable or not fitting) → `leitpunkte_coverage`; missing Betreff/Anrede/Schlussformel → `email_form_elements`; stiff/wrong register → `register_formality`; only simple connectors → `connectors_variety`; only simple structures → `simple_structures_only`; phrases copied from the prompt → `vocabulary_copied_from_prompt`; under 150 words → `text_too_short`; Thema/Situierung → `thema_situierung_verfehlt`; capitalisation/commas → `spelling_caps_punctuation`; word order → `verb_position` or `middlefield_order`.

## Step 4 — Native-like upgrades (1–2, optional)
Correct but stiff phrases only (never listed as errors): smoother B2 version + one sentence why.

## Step 5 — What would lift the score
One line per criterion: what is needed for the next grade.

## Step 6 — Model answer (after the correction)
Write a model email of **150–180 words at B2** (skill design; the official minimum is 150) for the SAME task, with Betreff, Anrede, exactly three Leitpunkte (skill design; official: three, or two plus an own aspect; each developed in a few sentences as a depth tip, not a grading rule), varied connectors, Schlussformel. Mark 3–4 phrases in bold that came from `rules/redemittel_b2.md`. Label "Beispiel, nicht die einzige Lösung".

Finally: `tutor.py task graded --slot schriftlich` (do not clear). Optional bootcamp transfer measure: if a bootcamp is active, `tutor.py transfer first|last --words N --errors E` (E = your counted errors; `first` = beginning, `last` = final measurement).

## Output template (format example only, never reuse content)
```
**Wörter: 168** · **Schriftlicher Ausdruck: 27 / 45 Punkte (60 %)** — Aufgabe A, gute Struktur, Grammatik kostet dich Punkte.

| Kriterium | Note | Beleg |
| :-- | :-- | :-- |
| I Aufgabenbewältigung | A | LP1 „…“, LP2 „…“, LP4 „…“ je verständlich und passend |
| II Kommunikative Gestaltung | B | Register ok; Verknüpfung nur *weil/aber*: „…“ |
| III Formale Richtigkeit | C | mehrere systematische Fehler: Nebensatz-Verb („…“), Artikel („…“) |

Checkliste: Betreff ✓ · Anrede ✓ · Einleitung ✓ · Schluss ✓ · Schlussformel ✗

**Top-3 Lektionen** (je: ~~Fehler~~ → **Korrektur** · Warum · Bild · `key`)
**Upgrade:** … · **Was bringt den nächsten Punkt:** I – / II: *dennoch, sofern* / III: Nebensatz-Verb
**Modellantwort (≈ 160 Wörter):** …
**Nächster Schritt:** …
```
Tool calls: `wordcount` → `score-writing A B C --record` → `errors verb_position=2 article_gender_agreement=1 connectors_variety=1` → `task graded --slot schriftlich`.

## Common failure modes to avoid
- Capping II because only the Betreff is missing; ignoring the AND-condition.
- Refusing a Leitpunkt because it is only one sentence (not an official criterion in [HB-neu]); listing an unchosen Leitpunkt as missing; giving III an A/B for a text of only simple clauses.
- Grades above C without a quoted piece of evidence; "benefit of the doubt" upgrades of a grade.
- Any correction that fails the safety protocol: changing correct forms, invented rules, counting typing slips, defending a disputed correction.
- Own arithmetic; forgetting `--record`; invented category keys; skipping the model answer.
- Mentioning an auto-fail below 150 words (there is none) or a D for Thema without checking it against the saved task.
- Free-form layout.
