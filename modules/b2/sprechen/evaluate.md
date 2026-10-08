# Sprechen — Evaluator (estimate only)

Trigger: `/telc <level> correct sprechen [1|2|3]`. Load slot `sprechen<part>` (`uv run $SKILL_DIR/tools/tutor.py task show --slot sprechen1`), the dialogue of this conversation (the user's turns), `rules/feedback_format.md`, `rules/redemittel_b2.md`.

## Honest scope (state it in the first lines)
Official scoring (Handbuch, Informationen zur Prüfung, newer edition): both examiners score each part on **1 Ausdrucksfähigkeit (7/5/3/0), 2 Aufgabenbewältigung (7/5/3/0), 3 Formale Richtigkeit (7/5/3/0), 4 Aussprache und Intonation (4/2/1/0)** = max 25 per part, 75 in total. "Einander kennenlernen" is not scored. What you produce here is only an **estimate from typed text**: criteria 1–3 on the official 7/5/3/0 scale (max **21** per part). **Aussprache/Intonation cannot be assessed from text and is excluded**, so the estimate is never out of 25 and never an exam score. Ask the user to paste a voice-to-text transcript if they have one (it shows intelligibility, not sound quality) and give general pronunciation tips only.

## Steps (follow in order)
1. If the user typed fewer than 3 turns: say the sample is too small and offer to continue; do not grade.
2. Rate three criteria A–D (letters and mapping A = 7 points, B = 5, C = 3, D = 0 are skill design; the official levels are 7/5/3/0), each with one quoted piece of evidence from the user's turns:
   - **I Ausdrucksfähigkeit:** range of vocabulary and structures; B2 expects more than "ausschließlich einfache Konstruktionen mit simplem Wortschatz"; fluency/spontaneity.
   - **II Aufgabenbewältigung:** T1 topic developed + questions asked/answered; T2 main points reproduced + own opinion + reasons + reaction to partner + compromise; T3 Leitfragen covered, proposals made and reacted to, decision reached.
   - **III Formale Richtigkeit:** errors in word order, cases, verb forms; "Fehler und Vereinfachungen sind in gewissem Maße erlaubt" if meaning stays clear.
   Choose the letter whose description fits best; no letter above C without evidence.
3. `uv run $SKILL_DIR/tools/tutor.py score-speaking <part> <I> <II> <III> --record` (positional order: Ausdrucksfähigkeit, Aufgabenbewältigung, Formale Richtigkeit). Copy the `estimate_points` it returns (out of 21: criteria 1–3 only, Aussprache excluded; not an exam score). It is stored in a separate "estimates" list: it never enters scores, module averages or `block-total`. If the slot is already graded the tool refuses unless `--recheck` is given (re-grade only on explicit request).
4. Error recording: `uv run $SKILL_DIR/tools/tutor.py errors sprechen_task_coverage=<n> sprechen_discourse_devices=<n> sprechen_range_complexity=<n>` (only keys that occurred; use grammar keys like `verb_position` for formal errors), then `tutor.py task graded --slot sprechen<part>`.
5. Feedback: max 3 lessons (`~~wrong~~ → **right**`, Franz why, key) + 3 usable Redemittel from `rules/redemittel_b2.md` the user did not use + pronunciation tips (general: stress, final -er, ch-sounds; say that they are tips).

## Output template (format example only, never reuse content)
```
**Sprechen · Teil 3 — Schätzung aus dem Text (Kriterien 1–3, Aussprache nicht bewertbar)**
| Kriterium | Stufe (Punkte) | Beleg |
| :-- | :-- | :-- |
| Ausdrucksfähigkeit | B (5) | „Ich schlage vor, dass wir …“ (gute Struktur), aber viele *und*-Ketten |
| Aufgabenbewältigung | C (3) | Kosten und Essen nicht besprochen |
| Formale Richtigkeit | B (5) | 2× Verbstellung im Nebensatz |
| Aussprache/Intonation | — | nicht bewertbar; schick mir ein Transkript deiner Aufnahme |
Schätzung: 13 / 21 (offiziell wären 25 pro Teil inkl. Aussprache; kein Prüfungsergebnis)

**Top-3 Lektionen**
1. ~~weil wir haben Zeit~~ → **weil wir Zeit haben** · Verb ans Ende. Bild: der Zug hält am Endbahnhof. `verb_position`
2. …

**Nützliche Redemittel:** *Habe ich das richtig verstanden, dass …?* · …
**Nächster Schritt:** Teil 3 noch einmal mit anderer Situation, diesmal alle Leitfragen abdecken.
```
Tool calls: `score-speaking 3 B C B --record` → `errors verb_position=1 sprechen_task_coverage=1` → `task graded --slot sprechen3`.

## Common failure modes to avoid
- Presenting the letters or the 21-point estimate as an exam score or as out of 25; grading Aussprache from text.
- Grading from fewer than 3 user turns; a letter above C without a quoted example.
- Correcting during the dialogue (do it only here); more than 3 lessons; free-form layout.
- Forgetting `--record`; own arithmetic for the index.
