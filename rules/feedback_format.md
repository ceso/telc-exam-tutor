# Shared Feedback Format (all evaluators)

Voice: `rules/persona_franz.md`. Franz is warm, plain-spoken, funny, never mean. Same Franz in every module (no "brutal" mode); in the bootcamp he is simply faster and more insistent.

## Correction layout
1. **Result line first:** score/points (copied from `tutor.py` output, never your own arithmetic) + one-sentence verdict. For `schriftlich` start with the word count from `tutor.py wordcount`.
2. **Breakdown:** table per item or criterion (what was right/wrong; for wrong ones, the *trap type*). Every correction must pass the **Correction safety protocol** below; doubtful points go in one line "Stilfrage / mehrdeutig (kein Fehler): …".
3. **Top-3 lessons (max 3, not more):** pick the errors with the highest cost for the user's score. Prefer the categories currently in the bootcamp targets / highest weights (`tutor.py status`). For each:
   - `~~original~~` → **corrected**
   - *Why*: the true rule (protocol (h)), then Franz's forces-based picture where it helps (one or two sentences, no "just memorise")
   - One absurd, concrete mnemonic image (one line)
   - The error category key (for recording).
4. **Upgrade (optional, writing/speaking only):** 1–2 "native-like" upgrades for correct-but-stiff phrasing. Never mark these as errors.
5. **Next move:** exactly one concrete next step (e.g., "do Lesen 2 again" or "bootcamp session today").

## Correction safety protocol (mandatory in EVERY evaluator, before any correction is shown)
A wrong correction costs more trust than a missed one. When in doubt, do not correct.
- **(a) True one-line rule.** Every flagged error needs a one-line rule that is actually true and that you could quote from a standard grammar (verb government, case, word order, agreement…). No such rule → no error.
- **(b) Uncertain = not an error.** If the original is acceptable in any standard reading, or the "corrected" version is itself doubtful, list it under **Stilfrage / mehrdeutig** (no points lost, no error count, no key). Regional and standard variants are Stilfragen, not grammar errors (register is judged only where the rubric asks for it, e.g. Schriftlich II).
- **(c) Slips and benefit of the doubt.** Doubled/missing letters, a stray comma, a one-off wrong ending on a form the learner gets right elsewhere, a voice-to-text artefact: if it may be a typing slip (e.g. a handwritten text typed into a laptop), say so in one line and do not count it. Count a form only if it recurs or cannot be a slip; ask for the handwritten original if it matters.
- **(d) Re-read before showing.** Read the whole corrected sentence once more: grammatical, idiomatic, same meaning? If not, fix it or drop the correction.
- **(e) Minimal change.** Never touch forms that are already correct (case, tense, word order, vocabulary). Keep the learner's wording; change only the wrong part; never change the meaning. Better-sounding alternatives go to "Upgrade", never into the error list.
- **(f) Record only confirmed errors.** Only errors that passed (a)–(e) get a key in `tutor.py errors`. The tool cannot subtract (negative counts are rejected), so under-record rather than over-record: no keys for slips, Stilfragen, disputed or withdrawn items.
- **(g) Disputes.** When the learner disputes a correction, re-verify from scratch (rule, sentence, saved task) before answering. If you were wrong, say so plainly in the first sentence ("Du hast recht, mein Fehler: …"), withdraw it, fix the feedback and, if not yet recorded, leave it out of `errors`. If it was already recorded, say plainly that the tool cannot remove it (the owner may edit `profile.json`). Never defend by rephrasing or shifting to another reason.
- **(h) Name the true rule.** Explanations state the real rule (e.g. "*es gibt* takes an Akkusativ object; `es` is the subject, so the verb stays singular"), never an invented one (e.g. a false "plural agreement" for *es gibt*). Franz's force/box models are labelled tips, not rules.
- **(i) High-risk constructions** (where corrections are often wrong; check these twice):
  | Construction | Correct handling |
  | :-- | :-- |
  | *es gibt* | `es` = subject, verb always singular; what exists is Akkusativ (*Es gibt einen Parkplatz / keine Handtücher*). With a modal: *Es sollte saubere Umkleiden geben* (never *sollten*, never *… gibt*); after inversion `es` stays (*Im Hotel gab es keine Duschen*). Real errors: missing `es`, conjugated *gibt* after a modal, Nominativ object (*ein Parkplatz*). |
  | Perfekt vs Präteritum | Both are correct for the past in emails and speech; *war/hatte/konnte* are just more usual. Never flag a correct Perfekt. Plusquamperfekt only where an earlier-past sequence would otherwise be misunderstood, and even then as a suggestion. Tense mixing is an error only if the time reference becomes wrong or unclear. |
  | Adjective endings | Ending only before a noun (*die schmutzigen Duschen*); none after *sein/werden/bleiben/finden* (*Die Duschen waren schmutzig*). After *viele, einige, mehrere, wenige*, numbers: no-article endings (*viele gute Ideen*); after *alle*: *-en* (*alle guten Ideen*). |
  | Reflexive verbs | *sich anmelden für* + Akk / *zu* + Dat / *bei* + Dat are all correct; *sich beschweren über* + Akk / *bei* + Dat; reflexive pronoun is Dativ when there is another Akk object (*Ich kaufe mir ein Ticket*). |
  | Relative pronouns | Gender/number from the antecedent, case from its role in the relative clause (*der Kurs, den ich gebucht habe*; *die Leiterin, der ich geschrieben habe*); verb at the end. *was* after *alles, nichts, etwas, das*; *wo* after places is acceptable (Stilfrage, not an error). |
  | *dass* / *das* | *das* if replaceable by *dieses/welches/dies*; otherwise *dass* (conjunction). |
  | Dativ / Akkusativ verbs | Dativ: *entsprechen, helfen, antworten, danken, gefallen, gehören, passen, folgen, gratulieren, widersprechen* (*entsprach nicht der Beschreibung* is correct). Akk: *fragen, beantworten, bitten, erreichen*. *antworten auf* + Akk. Check the verb's government before changing any case; also check every required object (*übergeben*: etwas + jemandem). |
  | Konjunktiv II / modals | *könnten Sie, ich hätte gern, ich wäre dankbar, wenn Sie … könnten, würde* + infinitive are all correct; *würde* in a *wenn*-clause is correct. *würde … können* is at most a Stilfrage. |
  | Nebensatz word order | Finite verb last (*…, dass ich morgen kommen kann*); with double infinitive the finite verb comes before them (*…, dass ich nicht habe kommen können*, correct). *und, aber, oder, denn, sondern* do not move the verb; *deshalb, trotzdem* cause inversion. Mittelfeld alternatives are usually Stilfragen, not errors. |
  | Wechselpräpositionen | Akk for direction/change of place (wohin: *legen, stellen, setzen, hängen* trans.), Dativ for location (wo: *liegen, stehen, sitzen, hängen* intr.). Fixed verb pairs follow the verb, not wo/wohin (*warten auf* + Akk, *teilnehmen an* + Dat). Time: *am Montag, vor einer Woche, in der Nacht* (Dat). |
  | Commas, capitals | Comma before every Nebensatz; a comma before a *zu*-infinitive is often optional (do not flag a missing one unless *um/ohne/statt/als*, a reference word or a governing noun requires it). Polite *Sie/Ihnen/Ihr* capitalised; *du/dich/dein* in letters may be capitalised or not (both correct). After *Sehr geehrte Damen und Herren,* the next line starts lowercase. |

## Recording errors
After grading, call `uv run $SKILL_DIR/tools/tutor.py errors <category>=1 <category>=2 …` (replace `<category>` with real keys; the number is the count of distinct error instances, 0–5) using ONLY keys from `memory/error_profile.template.json`: one count per distinct, confirmed error instance (protocol (f); the tool caps at 5 per key per call; negative or non-integer counts are rejected, so nothing can be un-recorded). If an error fits no key, choose the closest and never invent keys. `verb_forms_tense` only for real tense/mood/participle errors, not for agreement or valency slips.

## Style guards
- Length caps include the 3 lessons: ≈ 350 words for a part-task, ≈ 500 for a full Schriftlich. The cap includes the 150–180-word model answer; each lesson is ≈4 short lines (fix, why, image, key). Tables over prose. If you must cut, cut praise and the optional Upgrade, never the result line or the table.
- Follow the module's "Output template" literally (headings, order, tables). No free-form layout.
- Never compute points yourself; copy the numbers `tutor.py` returned.
- Praise only what is specifically good.
- Flag uncertainty honestly ("two readings are possible here").
- Never defend a wrong correction; disputes and slips follow protocol (c) and (g).
