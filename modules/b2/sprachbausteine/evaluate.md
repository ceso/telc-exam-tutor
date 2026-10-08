# Sprachbausteine — Evaluator

Trigger: `/telc b2 correct sprachbausteine [part]`. Load slot `sb<part>` (`uv run $SKILL_DIR/tools/tutor.py task show --slot sb1`), the user's answers, `rules/feedback_format.md`.

## Steps (follow in order)
1. Mark each gap against the key. Blank = wrong. Count correct gaps.
2. `uv run $SKILL_DIR/tools/tutor.py score sb<part> --correct N --record` (10 × 1.5 P). Copy its numbers.
3. For each wrong gap quote the deciding sentence from saved `material.gap_text`, show the correct word, and explain WHY the user's choice fails *in that sentence* (case, agreement, word order, collocation, meaning). Word-order gaps: Franz's forces/boxes logic. Lexis: name the collocation or near-synonym trap.
4. Record, grouping wrong gaps by their saved `category`: `uv run $SKILL_DIR/tools/tutor.py errors <category>=<n> …`. Then `tutor.py task graded --slot sb<part>` (do not clear).
5. Tips only if relevant: T1 — official [Tipps p. 9]: if you know the answer at once, fill the gap before reading the options, then compare; otherwise check which option fits in Genus/Numerus/Kasus (skill tip: test all three options in the sentence). T2 — official [Tipps p. 10]: read the text first without the box, five words are left over, never leave a gap empty (an empty gap cannot score; the manuals do not say whether wrong answers are penalised, so guess); skill tip: cross out used words, fill sure gaps first.
6. If the user disputes a gap and a second answer is genuinely defensible: concede, say the item was flawed, and do not count it against them (re-run `score` only if the first run was not yet recorded; otherwise tell the user the corrected count and do NOT record again).

## Output template (format example only, never reuse content)
```
**Sprachbausteine · Teil 1: 7 / 10 richtig = 10,5 von 15 Punkten (70 %)** — Gut, die Präpositionen haben dich erwischt.

| Lücke | Du | Lösung | Grund |
| :-- | :-- | :-- | :-- |
| 1 | b | a | „Ich freue mich **auf** Ihr Angebot“ (sich freuen auf + Akk, Zukunft) |
| 6 | c | b | `deshalb` steht in Position 1, `weil` schickt das Verb ans Ende |

**Top-3 Lektionen**
1. ~~freue mich über~~ → **freue mich auf** · Warum: *über* = schon passiert, *auf* = noch nicht. Bild: ein Geschenk, das man schon schüttelt, aber noch nicht auspackt. `case_prepositions`
2. …

**Nächster Schritt:** Sprachbausteine 2 (≈ 20 Min.).
```
Tool calls: `score sb1 --correct 7 --record` → `errors case_prepositions=2 connectors_variety=1` → `task graded --slot sb1`.

## Common failure modes to avoid
- Own arithmetic for points; forgetting `--record`; recording twice after a dispute.
- Explaining the right word without saying why the user's word fails in THAT sentence.
- Wrong or invented category keys; more than 3 lessons; free-form layout.
- Revealing the key before the user answered; grading against the wrong slot (sb1 vs sb2).
