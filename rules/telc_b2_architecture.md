# telc Deutsch B2 — Official Facts (single source of truth)

Sources: *telc Deutsch B2 Handbuch* (2019) = **[HB]** and *Tipps zur Prüfungsvorbereitung Deutsch B2* (telc, 2020) = **[TIPPS]**, plus the pages "Informationen zur Prüfung" of a NEWER official Handbuch edition = **[HB-neu]** (ground truth; supersedes the 2019/2020 PDFs where they differ). Modules MUST NOT contradict this file. Anything marked *derived* or *skill design* is this skill's own estimate: never present it as quoted rule. Anything not in this file is a *tip*.

## 1. Points and passing (300 total)
| Subtest | Max | Structure |
| :-- | :-- | :-- |
| Leseverstehen | 75 | T1: 5×5 · T2: 5×5 · T3: 10×2.5 |
| Sprachbausteine | 30 | T1: 10×1.5 · T2: 10×1.5 |
| Hörverstehen | 75 | T1: 5×5 · T2: 10×2.5 · T3: 5×5 (all Richtig/Falsch) |
| Schriftlicher Ausdruck | 45 | 3 criteria × (A5/B3/C1/D0), sum × 3 |
| **Schriftliche Prüfung total** | **225** | (75+30+75+45) [HB-neu] |
| Mündlicher Ausdruck | 75 | T1, T2, T3 = 25 each |

Point tables are in [HB] pp. 39–42, [TIPPS] and [HB-neu] (Lesen T1/T2 5×5, T3 10×2.5; SB 10×1.5 per part; Hören T1 5×5, T2 10×2.5, T3 5×5; Schriftlich 45; oral 75).
**Official pass rule [HB-neu]:** at least **60 % of the written part (135/225) AND 60 % of the oral part (45/75)**, each separately; written and oral points are then summed. **Grade bands of 300 [HB-neu]:** 300–270 sehr gut · 269.5–240 gut · 239.5–210 befriedigend · 209.5–180 ausreichend · 179.5–0 **or any part under 60 %** = nicht bestanden. Failed parts can be repeated separately (if the whole exam was failed, repeat it completely). `tutor.py exam-result --written W --oral O` applies this to REAL points only.
**Written-block estimate** (what this skill can simulate): Lesen 75 + Sprachbausteine 30 + Schriftlicher Ausdruck 45 = **150 of 225**; 60 % of the block = **90/150** (*derived estimate*, not an official figure). Hören (75) is only included if the user did the Hören module; otherwise any total is an estimate for the block, not the exam result. `tutor.py block-total` computes it; with Hören complete it also compares the written 225 with 135. A grade band needs written AND oral points, so the block estimate gets none.

## 2. Topics (Anhang T, T1–T16) — rotate, never repeat the last used
1 Persönliche Angaben · 2 Körper und Gesundheit · 3 Wohnen · 4 Orte · 5 Alltag · 6 Essen und Trinken · 7 Bildung · 8 Arbeit · 9 Einkaufen · 10 Dienstleistungen · 11 Natur und Umwelt · 12 Reisen und Verkehr · 13 Freizeit · 14 Medien und IT · 15 Gesellschaft und Staat · 16 Beziehungen und Kulturen

## 3. Timing and exam rules
- **Lesen + Sprachbausteine: 90 min total [HB p. 33; ≈ 3000 words of reading: TIPPS p. 8]**. Suggested split (tip): Lesen 1 ≈ 15 · Lesen 2 ≈ 20 · Lesen 3 ≈ 20 · SB 1 ≈ 15 · SB 2 ≈ 20 = 90, including the time needed to transfer answers to the Antwortbogen.
- Answers count only on the **Antwortbogen**, marked with **pencil** (scanner reads pencil); what is written in the Aufgabenheft is not graded. No dictionary. [TIPPS]
- Hören ≈ 20 min (T1 ≈ 5, T2 ≈ 7, T3 ≈ 6); each text ONCE; the tape cannot be stopped; read statements in the pause (T1: 30 s, T2: 1 min). Mark + (richtig) / – (falsch). [TIPPS]
- Schreiben **30 min**. **Before writing, copy the number of your Schreibaufgabe (printed in the Aufgabenheft; it is NOT just the letter A/B) onto the Antwortbogen S30. If the number is missing or wrong the writing cannot be graded: 0 points for the subtest.** [TIPPS §6] (In the [TIPPS] sample both tasks show the same boxed "Testversion" number; that this skill prints a distinct number per task is skill design.) Illegible text is not graded well: you may cross out, write between lines, add with asterisk/footnote if the corrections are clear. [TIPPS]
- Sprechen: 20 min preparation (shared by all parts); exam ca. 15 min for a pair, ca. 25 min for three [HB-neu] (older [TIPPS p. 30] says ca. 16 min); T1–T3 each ca. 5 min [HB pp. 43–45]; Kennenlernen ca. 1 min, ungraded [TIPPS p. 30, HB p. 29]. Notes allowed; Redemittel only on the Prüfungsblatt; no dictionary or smartphone/smartwatch. Written part: 140 min without a break (Lesen+Sprachbausteine 90 → Antwortbogen collected → Hören ca. 20 → collected → Schriftlich 30). Variants: paper, digital (type/tick/drag) and hybrid (written on paper or digital, oral by video conference); scoring is identical [HB-neu].

## 4. Format per part
- **Lesen 1 (Globalverstehen):** 5 short texts from **two topic areas**, 10 headlines (a–j), 5 distractors. Headline = main message of the whole text.
- **Lesen 2 (Detailverstehen):** **ONE** authentic-style text, 5 multiple-choice items (a/b/c) in text order. A wrong detail makes the whole option false; watch hidden negations; answer from the text, not world knowledge.
- **Lesen 3 (Selektives Lesen):** 10 situations, 12 texts. Each text used at most once; **not every situation has a text → x**. Read each text to its end.
- **Sprachbausteine 1:** semi-formal/informal email or letter, 10 gaps, 3 options each; all word classes (declension, articles, prepositions, pronouns, conjunctions, Pronominaladverbien, verbs, particles).
- **Sprachbausteine 2:** magazine-style text, 10 gaps, box of 15 words (5 distractors); tests vocabulary/function, not inflection. Never leave a gap empty (an empty gap cannot score; the PDFs do not say whether wrong answers are penalised, so guess; Tipps).
- **Hören 1:** radio news, **6 texts, 5 statements** (one item has no statement; a short introduction gives the context), Richtig/Falsch. "Richtig" = confirmable from the audio ("kann anhand des Textes bestätigt werden"); a "falsch" statement is not "information not in the text". Statements are paraphrased, not word-for-word. [HB-neu] confirms news items + "dazu fünf Aufgaben" (Richtig/Falsch), but the photographed digit before "Nachrichtenbeiträge" is illegible; the count of 6 comes from [HB]/[TIPPS]. **Hören 2:** radio interview or conversation with narrative character, **10 statements** in text order. **Hören 3:** 5 authentic short texts (announcements, radio, Sprachnachrichten), each starting with a short context introduction; 5 statements in order (statements usually contain two names/numbers). [HB pp. 39–41, TIPPS pp. 11–12; items 41–45 / 46–55 / 56–60]

## 5. Schriftlicher Ausdruck (official rubric, wording from [TIPPS] pp. 18–19)
- Two tasks (in der Regel **A: Bitte um Informationen**, **B: Beschwerde**; [TIPPS] p. 14), choose ONE ("eine aus einer Auswahl von zwei", [HB] p. 42). Semi-formal email reacting to an ad/letter, **4 Leitpunkte** as imperatives. Required form elements: passender **Betreff, Anrede, Einleitung, Schluss** (+ Schlussformel). Sender, recipient, date are NOT required. **Minimum 150 words** (stated in the task; no official automatic fail, see below). No memorised texts.
- Treat **3 Leitpunkte** (or 2 + 1 own aspect tied to the situation) "möglichst umfangreich". The task wording is "Behandeln Sie darin entweder a) drei der folgenden Punkte oder b) zwei … und einen weiteren Aspekt Ihrer Wahl" (Handbuch p. 28); never require all four.
- Criteria I–III, each 5 / 3 / 1 / 0 points; each criterion is multiplied by 3 (max 15 per criterion), total max 45. Newer [HB] edition (Informationen zur Prüfung, photo, ground truth): I = points by number of Leitpunkte (3 Leitpunkte or 2 + own aspect = 5; 2 or 1 + own aspect = 3; 1 or own aspect = 1; none = 0); II and III = level **B2 gut erfüllt = 5 · B2 erfüllt = 3 · B1 = 1 · A2 oder darunter = 0**; III is about Grammatik, Satzbau, Rechtschreibung, Zeichensetzung and how strongly errors disturb comprehension. The A/B/C/D letters are the [TIPPS] (2020) rating-grid labels for the same four levels (A = B2 gut erfüllt … D = A2 oder darunter). Each text is rated by **two** licensed raters; the second overrides the first. If III is D, I and II can still be A–C.

**I. Aufgabenbewältigung** (inhaltliche Angemessenheit; [HB] p. 42 lists the three criteria as "Berücksichtigung der Leitpunkte · Kommunikative Gestaltung · Formale Richtigkeit", [TIPPS] p. 15 as "Aufgabenbewältigung · Kommunikative Gestaltung · Formale Richtigkeit": same three criteria, this skill uses the [TIPPS] names)
- A: "Drei Leitpunkte bzw. zwei Leitpunkte und ein weiterer auf die Situierung bezogener Aspekt werden inhaltlich angemessen auf dem angezielten Niveau bearbeitet." B: two Leitpunkte, or one Leitpunkt + one own aspect. C: one Leitpunkt OR one own aspect. D: none.
- "Eine angemessene Behandlung eines Leitpunktes bzw. eines frei gewählten Aspekts erfordert **mehr als nur ein einziges Satzgefüge**." Appropriate "auf dem angezielten Niveau": a point treated only in simple main clauses, or merely touched on ("nur angerissen"), does not count. An own aspect counts only if tied to the situation (Situierung).
- "Eine **Reduktion inhaltlicher und sprachlicher Komplexität führt zu Abwertung**." (so simple-only language also lowers I.)
- **Thema verfehlt** (text has no or hardly any connection to the task) → D on ALL criteria. **Situierung verfehlt** (picks up the topic but does not fit the situation) or no Leitpunkt properly treated → D on I only; II and III are still graded. Official example: asked to request information about an internship — complaining about the firm's products = Thema verfehlt; writing a job application = Situierung verfehlt.

**II. Kommunikative Gestaltung** (Kohäsion + Kohärenz: Textlogik, Konnektoren, Register, Wortschatzspektrum, diskurssteuernde Verknüpfungselemente)
- "**A wird nicht gegeben, wenn die Textsortenmerkmale halbformeller oder formeller Schreiben (Betreffzeile, Anrede, Schlussformel) fehlen UND das Wortschatzspektrum nicht voll angemessen ist.**" Both conditions must hold: a missing Betreff alone does NOT cap II (official samples say "auch wenn der Betreff fehlt …" and still rate it well).
- "B wird nicht gegeben, wenn das falsche Register gewählt wurde oder der Gebrauch schwankt; wenn das Wortschatzspektrum für das Niveau B2 nicht angemessen ist; wenn die Leitpunkte linear ohne logische Verknüpfung aufgelistet sind."
- "**C** wird gegeben, wenn Textlogik, Verknüpfungselemente, Wortschatzspektrum und Register **überwiegend unpassend** sind und einen **negativen Eindruck auf den Empfänger** machen würden."
- "**D** wird gegeben, wenn Textlogik, Verknüpfungselemente, Wortschatzspektrum und Register **gänzlich unpassend** sind."
- Descriptors: A "breites Spektrum sprachlicher Mittel … vereinzelte Lücken im Wortschatz … verschiedene Verknüpfungsmittel sinnvoll"; B "hinreichend breites Spektrum … Lücken im Wortschatz … begrenzte Anzahl von Verknüpfungsmitteln … klarer, zusammenhängender Beitrag"; C "genügend sprachliche Mittel … lineare, zusammenhängende Äußerung"; D "elementare sprachliche Mittel … nur die häufigsten Konnektoren".

**III. Formale Richtigkeit** (all Schreibkonventionen incl. Groß-/Kleinschreibung)
- A: "gute Beherrschung der Grammatik. Macht **keine systematischen Fehler**, aber gelegentliche Ausrutscher **und Einflüsse der Erstsprache können vorkommen**"; Rechtschreibung/Zeichensetzung "weitgehend korrekt".
- B: "recht gute Beherrschung. Macht nur **wenige systematische Fehler**, die das Verständnis aber nicht gefährden. Ausrutscher und **Einflüsse der Erstsprache können vorkommen**"; "hinreichend korrekt".
- C: "ausreichende Beherrschung … **trotz deutlicher Einflüsse der Erstsprache**. Zwar kommen **mehrere systematische Fehler** vor, aber es bleibt **überwiegend klar**, was ausgedrückt werden soll"; Rechtschreibung "meistens verstehen".
- D: "einige einfache Strukturen korrekt … macht aber noch **viele systematische, elementare Fehler** (Zeitformen vermischen, Subjekt-Verb-Kongruenz vergessen). Trotzdem wird in der Regel klar, was ausgedrückt werden soll"; Rechtschreibung "häufig phonetisch".
- The key is *systematic* (recurring, rule-level) vs *Ausrutscher* (one-off slips), not error count alone. A text made only of simple, safe structures cannot show "gute Beherrschung" at B2: complexity is part of the grade (no B or A for simple-only grammar; it also lowers I).
- **Word count:** no official automatic fail below 150 words. Report it, let the criteria reflect missing content (usually fewer Leitpunkte → I drops).

**Grading rule (replaces any tie-break):** choose the grade whose official descriptor best fits the whole text. Quote evidence for every grade above C. Anchors: `rules/schriftlich_anchors.md`.

## 6. Hören and Sprechen — official tips to hand out
- **Hören:** read the statements in the preparation time, underline key words (names/numbers in T3); follow the gist, don't chase single words; each text once. Unknown words are fine. Regional accents (Bavaria, Austria, Switzerland) can occur. Mark an answer even if unsure, then move on.
- **Sprechen:** Kennenlernen (ungraded) → **T1 Über Erfahrungen sprechen** (list of 7 known topics, choose one; ca. 1½ min speaking, then 1–2 partner questions, then roles swap; keywords only [TIPPS p. 31]) → **T2 Diskussion** (same text for both candidates, read in ca. 10 of the 20 min preparation; reproduce main points, then discuss; seek a compromise) → **T3 Gemeinsam etwas planen** (Leitfragen that nearly always fit: Was? Wer? Wann? Wo? Essen/Trinken? Kosten?; make proposals, react to the partner's). Speak WITH the partner. Rating criteria [TIPPS/HB]: **1 Ausdrucksfähigkeit, 2 Aufgabenbewältigung, 3 Formale Richtigkeit, 4 Aussprache und Intonation**; 25 points per part, scored by both examiners [HB-neu]: criteria 1–3 each **7/5/3/0**, criterion 4 **4/2/1/0**; 3×25 = 75 = 25 % of 300. Kennenlernen is not scored. The older PDFs show A–D ticks with comments but no full descriptors. **Text estimate by this skill:** criteria 1–3 only on 7/5/3/0 (max 21 per part); the letters A–D and their mapping A=7/B=5/C=3/D=0 are skill design (the manuals define only the four point levels, not a letter mapping); Aussprache and Intonation cannot be judged from text and are excluded; the result is an estimate, never an exam score, and not out of 25. "Fehler und Vereinfachungen sind in gewissem Maße erlaubt", but "ausschließlich einfache Konstruktionen mit simplem Wortschatz" are not acceptable at B2. [TIPPS]
- Useful phrases: `rules/redemittel_b2.md`.

## 7. Calibration notes (official sample ratings, summarised)
- A memorised-sounding but correct and fitting text is judged on what is on the page.
- Typical C/D for II: list-like structure, only simple links, vocabulary copied from the prompt, wrong word choice.
- Typical D for III: many systematic elementary errors (tenses mixed, agreement missing) — still mostly understandable.
- Typical B2 speech: some errors that don't endanger the message ("das bessere Möglichkeit"), good discourse devices, lively exchange.
- Original anchor excerpts per grade (written by this skill, not telc): `rules/schriftlich_anchors.md`.
