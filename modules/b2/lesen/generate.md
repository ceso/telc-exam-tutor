# Lesen — Generator

Trigger: `/telc b2 generate lesen [1|2|3]` (default 1). Facts: `rules/telc_b2_architecture.md` §3–4. Pick a topic from T1–T16 that was NOT the last one used; vary text types. Write original texts at B2 (never copy real telc material). Texts may be slightly harder than B2; the tested information stays B2 [HB p. 34–36]. Official: all texts of Lesen + Sprachbausteine together ≈ 3000 words [Tipps p. 8]. The per-text word ranges below are skill design, chosen so a full mock reaches about that; the minutes per part are telc's suggestions [Tipps p. 8–9], not fixed limits (90 min for Lesen + Sprachbausteine together, incl. ≈ 10 min to transfer answers). Points 5/5/2.5 per item (75 P) are confirmed by the newer Handbuch edition (Informationen zur Prüfung, points table). The real test numbers the items 1–5, 6–10, 11–20; the skill numbers locally 1–5 / 1–5 / 1–10 per part (skill design).

## Teil 1 — Globalverstehen (5 × 5 P · ≈ 15 min)
Official [HB p. 34, Tipps p. 8]: **5 texts from two topic areas, 10 short headlines**, 5 Zuordnungs-Items; the five headlines left over are distractors. Skill design: texts of 80–120 words.
Build: **5 texts of 80–120 words from TWO topic areas** (e.g., 3 about Arbeit, 2 about Medien), numbered 1–5; **10 headlines a–j**, exactly 5 match and 5 are distractors. Item category: `lesen_headline_trap`.
Per text: a main message + 1–2 concrete details. Distractor design (vary): (a) matches a *detail* but not the main message; (b) matches the *topic area* but another text's message; (c) near-synonym with the opposite stance. No headline fits two texts. Headlines: short noun phrases/statements (≤ 10 words).
Save the exam material as `material: {"texts":[...],"headlines":[...]}`; each text and headline must be present, not just the key.

## Teil 2 — Detailverstehen (5 × 5 P · ≈ 20 min)
Official [HB p. 35, Tipps p. 8–9]: ONE text (article of general interest, usually popular science), **5 multiple-choice items with three options, one correct**, items in the order of the text. Skill design: 550–700 words and the trap list below.
Build: **ONE** continuous text of **550–700 words** (popular science, report or essay with a clear line of argument) and **5 MC items a/b/c in text order**. Each item targets a different trap; each wrong option is wrong for a nameable reason.
Save `material: {"text":"...","options":[["a) …","b) …","c) …"], …×5]}` (exactly 5 entries, one per item) so the evaluator can quote the deciding sentence and display the choices. Trap → category key (use exactly these):
| Trap | `category` |
| :-- | :-- |
| wrong detail inside an otherwise plausible statement | `lesen_detail_trap` |
| hidden negation / absolutes (nie, alle, ausschließlich, kaum) | `lesen_negation_trap` |
| true in the real world but not in the text | `lesen_other_trap` |
| mixes up two people/figures/dates | `lesen_other_trap` |
| author's opinion vs opinion quoted from a third party | `lesen_other_trap` |

## Teil 3 — Selektives Lesen (10 × 2.5 P · ≈ 20 min)
Official [HB p. 36, Tipps p. 9]: **10 short situation statements, 12 ads/short info texts** (more than a picture ad, e.g. programmes, brochures); each text may be used **only once**; **not every situation has a text**. Skill design: 70–110 words per text, 2–3 `x`, the condition rules below.
Build: **10 situations (1–10)** ("Sie suchen…") and **12 texts (a–l)** of **70–110 words**: ads, short info texts, programmes. Rules:
- Each text fits **at most one** situation; **exactly 2–3 situations have no text → answer `x`** (the tool enforces 2–3). Remaining texts are distractors that match most but not all conditions.
- Every situation has 2–3 conditions (what, when/price, restriction). A distractor satisfies all but ONE condition, and that condition appears late in the text. Category for every item: `lesen_x_trap`.
Save `material: {"situations":[...10],"texts":[...12]}`. Use `x` for exactly 2–3 situations.

## Self-verification (mandatory, silent, before showing)
1. T1: re-read each headline against every text; confirm 5 unique matches, no ambiguity.
2. T2: for each item cite the sentence that makes the key correct and one that makes each distractor wrong.
3. T3: build the full matrix situation × text; confirm a unique one-to-one result and the `x` count.
4. Word counts within the ranges (use the wordcount tool on one text if unsure); topic-area spread.

## Output template (format example only, never reuse content)
```
telc B2 · Lesen · Teil 1  (≈ 15 Min.)
Lesen Sie die Texte 1–5 und ordnen Sie die passende Überschrift (a–j) zu. Fünf Überschriften bleiben übrig.

Text 1
<80–120 words>

Text 2
…

Überschriften
a) Neue Regeln für Homeoffice
b) …
j) …

Antwortbogen:  1 __   2 __   3 __   4 __   5 __
--- ENDE DER AUFGABE ---
```
Teil 2: title line, the text, then `1. <stem>` with options `a) … b) … c) …` on separate lines; grid `1 __ … 5 __`. Teil 3: `Situationen` block numbered 1–10, `Texte` block a–l, grid `1 __ … 10 __` and the sentence "Wenn kein Text passt, schreiben Sie x."
Save (one call per part, slot = `lesen<part>`):
`uv run $SKILL_DIR/tools/tutor.py task save --slot lesen1` with stdin
`{"level":"b2","module":"lesen","part":1,"topic":"T8","material":{"texts":["…×5"],"headlines":["…×10"]},"items":[{"n":1,"answer":"c","category":"lesen_headline_trap","why":"…decisive sentence…"}]}`
Then one Franz line: time + "Schick mir z. B. `1c 2a 3x …`".

## Common failure modes to avoid
- Printing the key, `why` or categories in the visible task.
- Two headlines (or two texts) that fit one item; a distractor that fully matches a situation.
- T3 without any `x`, or with every situation matched; texts outside the 70–110 / 80–120 / 550–700 ranges.
- T2 options that are all defensible, or answers needing world knowledge.
- Forgetting to save, saving in the wrong slot, or inventing a category key not in the template.
- Free-form layout: always use the template above.
