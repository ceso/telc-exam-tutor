# Sprachbausteine — Evaluator

Trigger: `/telc b2 correct sprachbausteine [part]`. **Every correction obeys the Correction safety protocol in `rules/feedback_format.md`.** Load slot `sb<part>` (`uv run $SKILL_DIR/tools/tutor.py task show --slot sb1`), the user's answers, `rules/feedback_format.md`.

## Steps (follow in order)
0. **Verify the key first (silent, every gap, before scoring):** re-solve each gap by inserting every option into the full sentence. Exactly one option must be grammatical AND fit the context (T2: no unused box word may fit either). If the user's option also fits, or the saved key does not fit, the gap is flawed: count the user's answer as correct, say "Lücke N ist mehrdeutig/fehlerhaft, das zählt für dich", and record no error for it. Never "explain" a key that fails this check.
1. Mark each gap against the (verified) key. Blank = wrong. Count correct gaps.
2. `uv run $SKILL_DIR/tools/tutor.py score sb<part> --correct N --record` (10 × 1.5 P). Copy its numbers.
3. For each wrong gap quote the deciding sentence from saved `material.gap_text`, show the correct word, and explain WHY the user's choice fails *in that sentence* (case, agreement, word order, collocation, meaning) with the true rule (protocol (h); e.g. the verb's real government, not a guessed one). Word-order gaps: Franz's forces/boxes logic. Lexis: name the collocation or near-synonym trap.
4. Record, grouping wrong gaps by their saved `category`: `uv run $SKILL_DIR/tools/tutor.py errors <category>=<n> …`. Then `tutor.py task graded --slot sb<part>` (do not clear).
5. Tips only if relevant: T1 — official [Tipps p. 9]: if you know the answer at once, fill the gap before reading the options, then compare; otherwise check which option fits in Genus/Numerus/Kasus (skill tip: test all three options in the sentence). T2 — official [Tipps p. 10]: read the text first without the box, five words are left over, never leave a gap empty (an empty gap cannot score; the manuals do not say whether wrong answers are penalised, so guess); skill tip: cross out used words, fill sure gaps first.
6. If the user disputes a gap and a second answer is genuinely defensible: concede, say the item was flawed, and do not count it against them (re-run `score` only if the first run was not yet recorded; otherwise tell the user the corrected count and do NOT record again).

## Output template (format example only, never reuse content)
```
**Sprachbausteine · Teil 1: 7 / 10 richtig = 10,5 von 15 Punkten (70 %)** — Gut, die Präpositionen haben dich erwischt.

| Lücke | Du | Lösung | Grund |
| :-- | :-- | :-- | :-- |
| 1 | b | a | „Ich freue mich schon **auf** unser Treffen am Freitag“ (sich freuen auf + Akk = etwas Kommendes) |
| 2 | a | c | „Ich schreibe Ihnen, **weil** ich noch eine Frage habe“: Verb am Ende passt nur zu *weil*; nach *deshalb* stünde das Verb direkt dahinter |

**Top-3 Lektionen**
1. ~~freue mich über~~ → **freue mich auf** · Warum: *sich freuen über* = etwas, das schon da ist; *sich freuen auf* = etwas Kommendes (das Treffen ist erst am Freitag). Bild: ein Geschenk, das man schon schüttelt, aber noch nicht auspackt. `case_prepositions`
2. …

**Nächster Schritt:** Sprachbausteine 2 (≈ 20 Min.).
```
Tool calls: `score sb1 --correct 7 --record` → `errors case_prepositions=2 connectors_variety=1` → `task graded --slot sb1`.

## Common failure modes to avoid
- Own arithmetic for points; forgetting `--record`; recording twice after a dispute.
- Explaining the right word without saying why the user's word fails in THAT sentence.
- Skipping Step 0: grading against a key with two fitting options, or defending it when the user disputes.
- Wrong or invented category keys; more than 3 lessons; free-form layout.
- Revealing the key before the user answered; grading against the wrong slot (sb1 vs sb2).
