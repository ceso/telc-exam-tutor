# Hören — Evaluator

Trigger: `/telc <level> correct hoeren [1|2|3]`. Load slot `hoeren<part>` (`uv run $SKILL_DIR/tools/tutor.py task show --slot hoeren1`; the full view incl. script is fine now, grading starts), the user's answers, `rules/feedback_format.md`.

## Steps (follow in order)
1. Normalise answers (`r`/`richtig`/`+` = r; `f`/`falsch`/`-` = f). Blank = wrong.
2. If `audio_status` of the task is not `rendered` (no audio): say clearly "Das war Lesen, nicht Hören; die Zahl sagt wenig über dein Hörverstehen." Do not record that score as a listening result.
3. Count correct statements N. Run `uv run $SKILL_DIR/tools/tutor.py score hoeren<part> --correct N` and add `--record` only if audio was rendered and played (T1 5 × 5, T2 10 × 2.5, T3 5 × 5). Copy its numbers; no own arithmetic.
4. Now (not before) show for each wrong statement: the statement, the right answer, the decisive sentence of the script (quote it), and WHY the user's answer fails: paraphrase not recognised, one changed detail missed, number/name confusion, or treating "falsch" as "not mentioned".
5. If audio was rendered, record errors: `uv run $SKILL_DIR/tools/tutor.py errors hoeren_paraphrase_trap=<n> hoeren_detail_missed=<n> hoeren_falsch_vs_not_mentioned=<n>` (only the keys that occurred). Without audio, skip both the score recording and listening-error recording because this was reading, not listening. In either case, finish with `tutor.py task graded --slot hoeren<part>`.
6. Optional: offer to replay only the wrong texts with the transcript visible as a study step (clearly not an exam condition).
7. Tips (official, max 2): read statements in the preparation time and underline names/numbers; follow the gist, unknown words are fine; never leave an answer empty.

## Output template (format example only, never reuse content)
```
**Hören · Teil 1: 3 / 5 richtig = 15 von 25 Punkten (60 %)** — Solide, die Zahlen haben dich erwischt.

| Nr | Du | Lösung | Beleg im Text | Warum |
| :-- | :-- | :-- | :-- | :-- |
| 2 | r | f | „…ab dem 1. März, nicht ab dem 1. Mai“ | Datum vertauscht: erst Zahl hören, dann urteilen |

**Top-3 Lektionen**
1. Zahlen und Namen: notiere nur die Zahl, nicht den Satz. Bild: ein Kassenbon, der nur Beträge zeigt. `hoeren_detail_missed`

**Nächster Schritt:** Hören 2 (≈ 7 Min.).
```
Tool calls: `score hoeren1 --correct 3 --record` → `errors hoeren_detail_missed=1 hoeren_paraphrase_trap=1` → `task graded --slot hoeren1`.

## Common failure modes to avoid
- Own arithmetic; recording a transcript-read score as a listening result.
- Showing the script before the user answered.
- Explaining "falsch" as "not mentioned"; explanations without the quoted sentence.
- More than 3 lessons; free-form layout; wrong slot.
