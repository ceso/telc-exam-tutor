# Bootcamp — Evaluator

Trigger: `/telc <level> correct bootcamp`. Tool prefix: `uv run $SKILL_DIR/tools/tutor.py` (`tutor.py` below). Load slot `bootcamp` (`tutor.py task show --slot bootcamp`), the user's answers, `rules/persona_franz.md`, `rules/feedback_format.md`.

## Steps (follow in order)
1. Match answers to items by number. Missing = wrong.
2. Judge each against `answer` / `accept`. Be strict on the targeted structure, lenient on unrelated slips: if the targeted error is fixed but another one appears, the item is **correct**; mention the slip in one line.
3. An ambiguous item: concede and leave it out of the call.
4. Record in ONE call, one `<category>=1` or `<category>=0` per scored item (1 correct, 0 wrong). Example: `tutor.py drill verb_position=1 verb_position=0 case_prepositions=1`. For final-check items add `--final`: `tutor.py drill --final verb_position=1 …` (do not mix final and normal items in one call).
5. Optional (last day, after a Schriftlich): `tutor.py transfer last --words W --errors E` (use `first` for the beginning measurement).
6. Output with the template below. Report the tool's numbers only (`accuracy_last10`, `band`, `confirmed`, `next_step`).
7. `next_step` says goal reached / expired / final due: follow it; `tutor.py bootcamp-close` only after the final check was graded or the bootcamp is expired. Then `tutor.py task graded --slot bootcamp`.

## Output template (format example only, never reuse content)
```
**Bootcamp · Tag 4/14: 11 / 15 richtig heute**

| Nr | Du | Besser | Warum |
| :-- | :-- | :-- | :-- |
| 1 | weil ich habe Fieber | weil ich Fieber habe | *weil* schickt das Verb ans Ende |
| 7 | auf den | auf dem | Wo? → Dativ |

**Lektionen (max. 3)**
1. Nebensatz: Konjunktion rein, Verb raus ans Ende. Bild: ein Zug, der am Endbahnhof hält.

**Scoreboard** (Zahlen vom Tool)
| Ziel | letzte 10 | Band | bis 80 % |
| :-- | :-- | :-- | :-- |
| Verbstellung | 70 % | near | noch 1 richtig |

Bestätigt: 0 von 5 (Ziel: copy `goal_needed` from the tool; ≥60 % der Ziele). Morgen: 2× Mittelfeld, 3× Verbstellung …
```
Tool calls for this example: `drill verb_position=1 verb_position=0 …` → `task graded --slot bootcamp`.

## Common failure modes to avoid
- Writing own percentages or declaring "mastered" without the tool saying so.
- Recording the same session twice; recording ambiguous items; forgetting `--final` on final-check items (they would count as normal drill).
- Penalising untargeted slips; more than 3 lessons; long lectures.
- Closing the bootcamp before the final check was graded (unless expired).
- Free-form layout instead of the template.
