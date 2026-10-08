# Lesen — Evaluator

Trigger: `/telc b2 correct lesen [part]`. Load the slot `lesen<part>` (`uv run $SKILL_DIR/tools/tutor.py task show --slot lesen1`), the user's answers, `rules/feedback_format.md`. Without a part: use the most recent lesen slot from `task list`.

## Steps (follow in order)
1. Parse the answers (`1b 2a`, lists, or a grid). Missing answer = wrong (an empty item cannot score; the manuals do not say whether wrong answers are penalised, so recommend always guessing).
2. Mark each item against the saved key. Count the correct ones; do not add points yourself.
3. Run: `uv run $SKILL_DIR/tools/tutor.py score lesen<part> --correct N --record` (T1 5×5, T2 5×5, T3 10×2.5). Copy its numbers.
4. For each WRONG item name the trap from the item's `category` and `why`, and quote the deciding sentence from saved `material`. T3: say which single condition ruled the user's choice out, or why `x` was right.
5. Strategy line (one or two, only if relevant; official [Tipps p. 8–9]): T1 read the headlines first, read the texts globally for the main content, and at the end check that the unused headlines really can be excluded (several sound alike); T2 one wrong detail makes the whole option false, check hidden negations, decide from the text not from world knowledge, items follow the text order so read in parallel; T3 read the situations first, read each text to the end (don't decide too fast), each text only once, not every situation has a text → `x`.
6. Record: `uv run $SKILL_DIR/tools/tutor.py errors <category>=1 …` (counts per category of wrong items). Then `uv run $SKILL_DIR/tools/tutor.py task graded --slot lesen<part>` (do not clear).
7. Print the Output template.

## Franz angle
Reading traps are *trust* problems: the user trusted a keyword instead of the sentence. Say it once, with a mnemonic. 4–5 of 5 in T1/T2 over two attempts is a good sign (tip, no official claim); suggest the next part.

## Output template (format example only, never reuse content)
```
**Lesen · Teil 2: 3 / 5 richtig = 15 von 25 Punkten (60 %)**  — Solide, aber zwei Details haben dich ausgetrickst.

| Item | Du | Lösung | Falle |
| :-- | :-- | :-- | :-- |
| 2 | a | c | lesen_detail_trap — Text: „…ab dem dritten Monat…“, Option a sagt „ab dem ersten“ |
| 4 | b | a | lesen_negation_trap — „kaum“ ≠ „nie“ |

**Top-3 Lektionen**
1. ~~Option a~~ → **Option c** · Warum: ein falsches Detail macht die ganze Option falsch. Bild: ein Kuchen mit einem Salzkorn pro Stück. `lesen_detail_trap`
2. …

**Nächster Schritt:** Lesen 2 noch einmal mit neuem Thema.
```
Tool calls used: `score lesen2 --correct 3 --record` → `errors lesen_detail_trap=1 lesen_negation_trap=1` → `task graded --slot lesen2`.

## Common failure modes to avoid
- Computing points yourself or rounding differently from the tool.
- Forgetting `--record`, recording errors for correct items, or inventing category keys.
- Revealing the key before the user answered; grading from a different slot than the one the user practised.
- Calling `task clear` (keep the task for disputes) or recording a second time on a re-check.
- More than 3 lessons, no quote from the text, or free-form layout.
