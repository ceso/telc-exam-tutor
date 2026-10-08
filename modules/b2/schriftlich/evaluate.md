# Schriftlicher Ausdruck — Evaluator

Trigger: `/telc b2 correct schriftlich`. Load slot `schriftlich` (`uv run $SKILL_DIR/tools/tutor.py task show --slot schriftlich`: both tasks + Leitpunkte), the user's text, `rules/telc_b2_architecture.md` §5, `rules/schriftlich_anchors.md`, `rules/redemittel_b2.md`, `rules/persona_franz.md`, `rules/feedback_format.md`. The rubric is the official one; add no rules.

## Step 0 — Identify and count
1. Which task (A/B) did the user answer? If unclear, infer from content. Matches neither → candidate for *Thema verfehlt*.
2. `uv run $SKILL_DIR/tools/tutor.py wordcount` on the text. Show **Wörter: N** first. N < 150: say it is below the official minimum and likely misses Leitpunkte; do NOT auto-fail; record key `text_too_short`.

## Step 1 — Checklist (facts, no scoring yet)
| Element | Present? |
| :-- | :-- |
| Betreffzeile · Anrede · Einleitung · Schluss · Schlussformel | list each |
| Per Leitpunkt (of the 4): treated? more than one Satzgefüge? appropriate at B2, or only "angerissen"? | list |
| Own aspect tied to the situation | y/n |
| Register consistent (Sie, polite, Konjunktiv II) | y/n |
| Links between points; variety beyond aber/dass/weil; not only "Ich…" starters | y/n |
| Complexity: Nebensätze, Passiv, Konjunktiv, Relativsätze present? | y/n |
| Vocabulary copied from the prompt? | y/n |
Do NOT penalise missing sender/address/date or a missing signature. Paragraph-per-Leitpunkt is a tip only.

## Step 2 — Grade (A=5, B=3, C=1, D=0) using the official descriptors (§5)
The letters are the [TIPPS] grid labels; the current telc Handbuch names the same levels for II and III: A = *B2 gut erfüllt* (5), B = *B2 erfüllt* (3), C = *B1* (1), D = *A2 oder darunter* (0). Each criterion is ×3 (max 15), total max 45; telc uses two trained raters (per [TIPPS] the second rating overrides the first), this evaluator gives one simulated rating. For III, how strongly errors disturb comprehension matters, not just their number.
- **I Aufgabenbewältigung** ([HB] p. 42 calls it "Berücksichtigung der Leitpunkte"): count a Leitpunkt only if it is treated with **more than one Satzgefüge, appropriately at B2**; a point merely touched ("nur angerissen") or in simple main clauses only does NOT count. A = 3 (or 2 + 1 own aspect); B = 2, or 1 + 1 own aspect; C = 1 Leitpunkt OR 1 own aspect; D = none. An own aspect counts only if tied to the situation. Reduced complexity downgrades I.
- **II Kommunikative Gestaltung:** A is NOT given if Betreffzeile/Anrede/Schlussformel are missing **AND** the vocabulary range is not fully adequate (both). A missing Betreff alone does not cap II. B is not given for wrong/wavering register, vocabulary inadequate for B2, or Leitpunkte listed linearly without logical links. **C** if Textlogik, Verknüpfungselemente, Wortschatzspektrum and Register are **überwiegend unpassend** and would make a negative impression on the recipient. **D** if they are **gänzlich unpassend**.
- **III Formale Richtigkeit:** judge *systematic* errors: A none (only occasional slips; Erstsprache influence may occur) · B few, meaning not endangered · C several (despite clear Erstsprache influence), mostly still clear · D many elementary systematic errors (tenses mixed, agreement missing; spelling often phonetic), mostly still clear. Simple-only grammar: no A/B for III (and I drops). Capitalisation counts.
- **Gatekeepers:** *Thema verfehlt* → `--thema-verfehlt` (D on all; key `thema_situierung_verfehlt`). *Situierung verfehlt* → `--situierung-verfehlt` (D on I only; II/III graded; same key).
- **Choosing between two grades:** pick the grade whose official descriptor best fits the whole text. For every grade above C write one quoted piece of evidence from the user's text. Compare with the anchors in `rules/schriftlich_anchors.md`. No "benefit of the doubt" rule and no "round up/down" rule.

Then: `uv run $SKILL_DIR/tools/tutor.py score-writing <I> <II> <III> [flags] --record` and report the points it returns (max 45). Never add yourself.

## Step 3 — Top-3 lessons (Franz)
Choose by score impact, preferring active bootcamp targets. Per `rules/feedback_format.md`: `~~error~~ → **correction**`, forces-based why (word order → Box Model), absurd image, key. Record: `uv run $SKILL_DIR/tools/tutor.py errors <category>=1 …`. Mapping: Leitpunkte too short → `leitpunkte_coverage`; missing Betreff/Anrede/Schlussformel → `email_form_elements`; stiff/wrong register → `register_formality`; only simple connectors → `connectors_variety`; only simple structures → `simple_structures_only`; phrases copied from the prompt → `vocabulary_copied_from_prompt`; under 150 words → `text_too_short`; Thema/Situierung → `thema_situierung_verfehlt`; capitalisation/commas → `spelling_caps_punctuation`; word order → `verb_position` or `middlefield_order`.

## Step 4 — Native-like upgrades (1–2, optional)
Correct but stiff phrases only (never listed as errors): smoother B2 version + one sentence why.

## Step 5 — What would lift the score
One line per criterion: what is needed for the next grade.

## Step 6 — Model answer (after the correction)
Write a model email of **150–180 words at B2** (skill design; the official minimum is 150) for the SAME task, with Betreff, Anrede, exactly three Leitpunkte (skill design; official: three, or two plus an own aspect; each more than one Satzgefüge), varied connectors, Schlussformel. Mark 3–4 phrases in bold that came from `rules/redemittel_b2.md`. Label "Beispiel, nicht die einzige Lösung".

Finally: `tutor.py task graded --slot schriftlich` (do not clear). Optional bootcamp transfer measure: if a bootcamp is active, `tutor.py transfer first|last --words N --errors E` (E = your counted errors; `first` = beginning, `last` = final measurement).

## Output template (format example only, never reuse content)
```
**Wörter: 168** · **Schriftlicher Ausdruck: 27 / 45 Punkte (60 %)** — Aufgabe A, gute Struktur, Grammatik kostet dich Punkte.

| Kriterium | Note | Beleg |
| :-- | :-- | :-- |
| I Aufgabenbewältigung | A | LP1 „…“, LP2 „…“, LP4 „…“ je > 1 Satzgefüge |
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
- Counting a Leitpunkt that has one sentence; giving III an A/B for a text of only simple clauses.
- Grades above C without a quoted piece of evidence; "benefit of the doubt" upgrades.
- Own arithmetic; forgetting `--record`; invented category keys; skipping the model answer.
- Mentioning an auto-fail below 150 words (there is none) or a D for Thema without checking it against the saved task.
- Free-form layout.
