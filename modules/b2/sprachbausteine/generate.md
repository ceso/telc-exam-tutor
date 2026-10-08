# Sprachbausteine — Generator

Trigger: `/telc b2 generate sprachbausteine [1|2]` (default 1). Facts: `rules/telc_b2_architecture.md` §3–4. Official [HB p. 37–38]: 10 gaps × 1.5 P per part (15 P each, 30 P total; confirmed by the newer Handbuch edition's points table); minutes are telc's suggestion [Tipps p. 9–10]: ≈ 15 (T1) / ≈ 20 (T2), inside the shared 90 min with Lesen. Numbering is local (1–10) per part (skill design; the real test numbers items 21–30 and 31–40). Rotate topics (T1–T16).

## Teil 1 — Grammatik-Lücken (E-Mail/Brief)
Official [HB p. 37, Tipps p. 9]: semi-formal or informal correspondence (letter/email), 10 gaps, **3 options each, one correct**, focus on grammar; all word classes occur. Skill design: length and gap mix below.
Build: a **semi-formal or informal email/letter of 150–200 words**, 10 gaps, **each with 3 options (a/b/c)** listed under the text. Gap mix (all word classes, max 2 of one type): declined adjective/article · preposition + case · pronoun (Personal/Relativ/Reflexiv) · conjunction (subordinating vs adverb with different word order) · Pronominaladverb · verb form (Konjunktiv II, Passiv, Partizip) · particle/fixed phrase.
Save the full material as `material: {"gap_text":"...","options":[{"n":1,"choices":["a) …","b) …","c) …"]},...]}`.
Distractors: each wrong option is wrong **in the sentence** for a nameable reason (case, agreement, word order consequence such as `deshalb` vs `weil`, collocation). Exactly one option fits.
**Category per gap = ONE key only**: the most precise grammar key (`case_prepositions`, `adjective_endings`, `relative_pronouns`, `pronominaladverbien`, `verb_forms_tense`, `connectors_variety`, `article_gender_agreement`, `verb_position`); use `sb_grammar_gap` only when no precise key fits.

## Teil 2 — Lexik-Lücken (Magazintext)
Official [HB p. 38, Tipps p. 10]: simple newspaper/magazine article of general interest, 10 gaps, **word box of 15 options** (10 fit, **5 are left over**), focus on vocabulary (not inflection), all word classes occur. Skill design: length, the "each word once" rule and the distractor types.
Build: a **magazine-style text of 180–230 words**, 10 gaps, a **box of 15 words a–o** (10 correct + 5 distractors), each word usable once. All word classes may appear (nouns, verbs, adjectives, adverbs, prepositions, conjunctions …). Gaps test vocabulary and function, not inflection: box words fit grammatically as given. Distractors: same word class and similar meaning as a correct word but wrong collocation or register.
Save the full material as `material: {"gap_text":"...","word_box":["…", "..."]}` including all 15 words.
**Category per gap = ONE key**: `word_choice_collocation` when the decisive reason is a collocation/Nomen-Verb-Verbindung/near-synonym; `sb_distractor_box` when the reason is the box mechanics (a distractor fits the sentence meaning but not the context, or an already-used word tempts). Never both.

## Self-verification (mandatory, silent)
1. Solve the finished task yourself with the key hidden: every gap has exactly ONE defensible answer. Try each distractor in each gap; none may fit.
2. T2: each box word used at most once; exactly 5 unused; no unused word fits any gap.
3. Gap numbers in the text = numbers in the options list (1–10, no leftovers, no example gap with a clashing number).
4. T1 word count 150–200, T2 180–230.

## Output template (format example only, never reuse content)
```
telc B2 · Sprachbausteine · Teil 1  (≈ 15 Min.)
Lesen Sie den Text und wählen Sie für jede Lücke (1–10) die richtige Lösung a, b oder c.

Liebe Frau Weber,
vielen Dank für Ihre E-Mail. Ich freue mich __1__ Ihr Angebot, __2__ ich noch eine Frage habe …

1  a) auf   b) über   c) für
2  a) deshalb   b) aber   c) weil
…
10 a) …

Antwortbogen:  1 __  2 __  3 __  4 __  5 __  6 __  7 __  8 __  9 __  10 __
--- ENDE DER AUFGABE ---
```
Teil 2: same header, text with `__1__`…`__10__`, then the box `a) … o)` in two columns, grid `1 __ … 10 __`; instruction "Jedes Wort passt nur einmal. Fünf Wörter bleiben übrig. Lassen Sie keine Lücke leer." (skill wording; the manuals say only that five options are left over [Tipps p. 10] and give "never leave a gap empty" as a tip).
Save with slot `sb<part>`: `uv run $SKILL_DIR/tools/tutor.py task save --slot sb1` with stdin
`{"level":"b2","module":"sprachbausteine","part":1,"topic":"T10","material":{"gap_text":"…","options":[{"n":1,"choices":["a) …","b) …","c) …"]}]},"items":[{"n":1,"answer":"a","category":"case_prepositions","why":"sich freuen auf + Akk"}]}`.
Then one Franz line: time + answer format (`1a 2c …`).

## Common failure modes to avoid
- Gap number mismatch between text and option list; a gap with two correct options.
- T2: a distractor that fits a gap; more or fewer than 5 unused words.
- Several categories on one gap, or keys not in the template.
- Showing the key, `why`, or categories; forgetting to save in slot `sb1`/`sb2`.
- Free-form layout instead of the template.
