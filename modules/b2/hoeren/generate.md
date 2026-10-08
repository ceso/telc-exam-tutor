# Hören — Generator (optional module, ≈ 20 min for T1–T3)

Trigger: `/telc <level> generate hoeren [1|2|3]` (default 1). Facts: `rules/telc_b2_architecture.md` §4 and §6. All texts are **original**; the telc audio is not reproduced. Statements are paraphrases of the text, never word-for-word. All items are **Richtig/Falsch**; each text is played **ONCE**.

## Honest scope (say it in one line to the user)
TTS voices are synthetic: good for listening-comprehension practice, not a copy of telc's speakers, speed or accents. Without audio, reading a transcript trains reading, not listening.

## Formats
| Part | Texts | Statements | Points | Length target (official ≈ minutes; word counts are skill design) |
| :-- | :-- | :-- | :-- | :-- |
| 1 | 6 short radio news items (≈ 70–90 words each), each with a short intro giving the context, one speaker (voice `katja` or `conrad`) | **5** (one news item has NO statement) | 5 × 5 | ≈ 5 min |
| 2 | one radio interview or conversation with narrative character, host + guest (`katja` + `conrad`), ≈ 600–700 words | **10**, in text order | 10 × 2.5 | ≈ 7 min |
| 3 | 5 short authentic texts (announcements, radio, voice messages), each starting with a short context intro (≈ 80–110 words each; voices `amala`, `killian`, `katja`, `conrad`) | **5**, in text order, each with 2 names/numbers to catch | 5 × 5 | ≈ 6 min |

## Steps (follow in order)
1. Pick a topic area from T1–T16 that is NOT the last one used.
2. Write the texts (spoken style: contractions OK, hesitation sparingly, numbers and names clearly given).
3. Write the statements. Rules: about half true, half false; a false statement changes ONE detail, number, name or relation that the audio states clearly (never "not mentioned"; "falsch" ≠ "not in the text"). Include paraphrase traps and 2 numbers/names per T3 statement.
4. Silent self-check: for every statement cite the sentence of the text that proves it right or wrong; confirm exactly one answer.
5. Save the task (slot `hoeren<part>`), key and script included, via `uv run $SKILL_DIR/tools/tutor.py task save --slot hoeren1` with stdin JSON:
   Save six text objects for Teil 1 (`h1_n1` through `h1_n6`); each item includes the `text_id` it tests, and exactly one text id has no item:
   `{"level":"b2","module":"hoeren","part":1,"topic":"T5","script":{"texts":[{"id":"h1_n1","voice":"katja","text":"…"}]},"items":[{"n":1,"text_id":"h1_n1","statement":"…","answer":"r","category":"hoeren_paraphrase_trap","why":"news 2: '…' proves it"}]}`
   The tool checks item count per part (5 / 10 / 5), answers `r`/`f` only, and that the slot matches `part`.
   (`answer` is `r` or `f`; `category` is one of `hoeren_falsch_vs_not_mentioned`, `hoeren_paraphrase_trap`, `hoeren_detail_missed`.)
6. Audio (try in this order):
   a. `uv run $SKILL_DIR/tools/tts.py check`. If OK: render the saved task script with `uv run $SKILL_DIR/tools/tts.py render --slot hoeren<part>` (or pass the same script JSON on stdin with `render -`): it writes one mp3 per text id into `$TELC_HOME/audio` and records the paths (relative to `$TELC_HOME`) as `audio` + `audio_status: "rendered"` in the saved task. On failure the task gets `audio_status: "failed"`. Turn-based texts use `{"id":"h2_iv","turns":[{"voice":"katja","text":"…"},{"voice":"conrad","text":"…"}]}`. Voices: katja (de-DE-KatjaNeural), conrad (ConradNeural), amala (de-DE-AmalaNeural), killian (de-DE-KillianNeural).
   b. The user can plug their own TTS: `tts.py config set --provider command --command '<template with {text} {out}>'`.
   c. No audio possible: tell the user honestly, show the statements now and keep the transcript until after they answered (see evaluator).
7. Show the task from `uv run $SKILL_DIR/tools/tutor.py task show --slot hoeren<part> --public` (template below): it hides key, `why` and script until graded, and its `audio_status` (`rendered` / `failed` / `none`) says whether to list audio files or use the no-audio variant. **Never print the script, the key or `why`** before the user answered.

## Output template (format example only, never reuse content)
```
telc B2 · Hören · Teil 1  (≈ 5 Min.)
Sie hören sechs Meldungen. Jede Meldung hören Sie EINMAL. Zu fünf Meldungen gibt es eine Aufgabe.
Lesen Sie jetzt die Aussagen (30 Sek.). Markieren Sie: r = richtig, f = falsch.

1  Die Bahn erhöht die Preise im Fernverkehr.
2  …
5  …

Audio (der Reihe nach, jede Datei nur EINMAL, nicht zurückspulen):
1. `$TELC_HOME/audio/h1_n1.mp3`
…
6. `$TELC_HOME/audio/h1_n6.mp3`

Antwortbogen:  1 __  2 __  3 __  4 __  5 __
--- ENDE DER AUFGABE ---
```
No-audio variant: replace the audio block with "Kein Audio verfügbar. Antworte aus deinem Gefühl nicht; ich zeige dir das Transkript erst nach deinen Antworten (Lesen ist kein Hören)." Teil 2 header: "Gespräch (≈ 7 Min.), 10 Aussagen, 1 Minute Vorbereitung". Teil 3: "Fünf Ansagen, 5 Aussagen". Then one Franz line: "Hör einmal, antworte `1r 2f …`."

## Common failure modes to avoid
- Printing transcript, key, `why` or filenames that reveal content (use neutral ids `h1_n1`).
- A statement that is "not mentioned", or one with two defensible answers; copying words from the text 1:1.
- T1 with 6 statements (must be 5, one news item without one) or T2 statements out of text order.
- Computing points yourself; wrong slot name; invented category keys.
- Offering replays ("noch einmal hören") — the exam plays once.
- Claiming TTS equals the real exam.
