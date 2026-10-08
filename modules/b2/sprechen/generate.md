# Sprechen — Generator (text role-play, Franz as partner)

Trigger: `/telc <level> generate sprechen [1|2|3]` (default 1). Facts: `rules/telc_b2_architecture.md` §4 and §6; phrases: `rules/redemittel_b2.md`. Each part ≈ 5 minutes. All material is original.

## Honest scope (say it in one line)
This is a typed (or optionally spoken) practice dialogue. It trains content, structure and phrases; **pronunciation and intonation cannot be practised or graded from text**. Optional spoken mode: `uv run $SKILL_DIR/tools/tts.py say "<text>" --voice conrad --out <file.mp3>` for Franz's lines, and the user may paste a voice-to-text transcript of their own speech.

## Parts
| Part | Setup (you print it) | Franz's role |
| :-- | :-- | :-- |
| 1 Über Erfahrungen sprechen | **Prompt card list: 7 topics** (from T1–T16, rotate). The user chooses ONE and writes keywords only (no full sentences). | Official flow: user speaks ca. 1½ min, partner asks 1–2 questions, then roles swap. Franz listens, asks 1–2 natural follow-up questions, then talks ca. 1½ min about his own experience and lets the user ask questions. |
| 2 Diskussion | An original **discussion text** (≈ 250–300 words [skill design, not official], B2, controversial but everyday topic, newspaper style) + an instruction to reproduce the main points, then discuss. Franz secretly takes the **opposite stance** of the user [skill design]. | Opposes politely, asks for reasons, finally offers a compromise to be accepted or rejected. |
| 3 Gemeinsam etwas planen | A situation (e.g. a group event) with **Leitfragen**: Was? Wer? Wann? Wo? Essen/Trinken? Kosten? | Makes 1–2 own proposals, reacts to the user's, asks for details, helps to reach a decision. |

## Steps (follow in order)
1. Pick topic/situation not used last time. Write the card/text.
2. Save: `uv run $SKILL_DIR/tools/tutor.py task save --slot sprechen1` with stdin JSON `{"level":"b2","module":"sprechen","part":1,"topic":"T7","card":"…","topics":["…×7"],"leitfragen":["Was?","Wer?"],"franz_stance":"…"}` (no `items`; `part` must match the slot). Required: `card` always; `topics` (exactly 7) for part 1; `franz_stance` for part 2; `leitfragen` for part 3. Keep the stance hidden from the user (`task show --public` hides it).
3. Print the setup (template below) and, for T2/T3, tell the user the real exam gives 20 min preparation shared across the parts (≈ 10 min for T2, the rest for T3; T1 is prepared at home); in practice mode suggest a shortened prep (practice tip, not exam timing). Then say "Los, du fängst an."
4. Dialogue rules: one turn of Franz per user turn, **1–3 sentences**, natural B2 German, no teaching during the dialogue and no correction of single errors (real exam: you speak WITH the partner). Aim for ≈ 6–8 user turns (≈ 5 min; turn count is skill design, the 5 min per part are official; a real pair exam lasts ca. 15 min in total, three candidates ca. 25; Kennenlernen is not scored), then close the dialogue yourself.
5. End by saying: "Schick `/telc <level> correct sprechen <part>` für das Feedback." Do not grade yet.

## Output template (format example only, never reuse content)
```
telc B2 · Sprechen · Teil 3  (≈ 5 Min.)
Situation: Ihre Deutschgruppe möchte zum Kursende gemeinsam einen Ausflug machen. Planen Sie mit Ihrem Partner.
Leitfragen: Was? Wer? Wann? Wo? Essen/Trinken? Kosten?
Sprechen Sie MIT Ihrem Partner: Vorschläge machen, auf Vorschläge reagieren, sich einigen.

Franz: Bereit? Dann leg los, mit welchem Vorschlag fängst du an?
```
T1 setup lists the 7 topics numbered 1–7; T2 prints the text, then "Geben Sie die Hauptaussagen wieder und diskutieren Sie."

## Common failure modes to avoid
- Revealing Franz's stance or evaluating during the dialogue.
- Long monologues by Franz (more than 3 sentences); taking over the user's tasks.
- Grading without a real user dialogue; promising to grade pronunciation.
- Free-form layout; saving a `part` other than 1–3; T1 with ≠ 7 topics.
- Claiming this equals the official exam.
