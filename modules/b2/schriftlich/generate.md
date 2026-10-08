# Schriftlicher Ausdruck — Generator

Trigger: `/telc b2 generate schriftlich`. Facts: `rules/telc_b2_architecture.md` §3 and §5. 30 min, ≥ 150 words, choose ONE of two tasks.

## Build (always TWO tasks, as in the real exam)
Pick two different scenarios from Anhang T (e.g. T7 Bildung, T12 Reisen, T10 Dienstleistungen, T13 Freizeit), not the last one used.
- **Aufgabe A — Bitte um Informationen:** an advertisement/notice (≈ 60–110 words; counted official sample ads are ≈ 75–120 words: Jugendcamp 75, Secura ≈ 100, Handbuch Radel ≈ 120; the 60–110 range is skill design) for an offer; the candidate writes a semi-formal email to the provider.
- **Aufgabe B — Beschwerde:** an advertisement (or email) for an offer the candidate has already used (same length), plus a one-sentence situation ("Sie waren nicht zufrieden. Schreiben Sie eine Beschwerde an …"). Official complaint tasks always react to a given ad/text ([TIPPS] p. 14, p. 17), and a Leitpunkt may refer to it ("Erwartungen nach der Lektüre der Werbeanzeige").
Each task has **4 Leitpunkte** as official imperatives (the official samples use e.g. "Beschreiben Sie…", "Legen Sie dar…", "Erläutern Sie…", "Erklären Sie…", "Stellen Sie weitere Fragen…"; other verbs such as "Fragen Sie nach…" are skill design). The candidate is given four Leitpunkte but must treat **only three of them, or two plus one own aspect of their choice** (official wording, Handbuch p. 28: "Behandeln Sie darin entweder a) drei der folgenden Punkte oder b) zwei der folgenden Punkte und einen weiteren Aspekt Ihrer Wahl"). Never instruct the candidate to cover all four.
Give each task a printed **Aufgabennummer** (e.g. "Aufgabe 1 (A)" / "Aufgabe 2 (B)"), because on the real exam the number must be copied onto the Antwortbogen ([TIPPS] p. 17-18, paper exam; in the digital exam there is no Antwortbogen, the text is typed into a field next to the task [HB-neu]).

## Self-verification (silent)
1. The two tasks differ in topic and function; each Leitpunkt asks for different content (no overlap) and fits 3–5 sentences.
2. The situation gives enough concrete facts (names, dates, prices) to refer to.
3. Both texts are original B2 German; no real company names.

## Output template (format example only, never reuse content)
```
telc B2 · Schriftlicher Ausdruck  (30 Min. · mindestens 150 Wörter)
Wählen Sie Aufgabe A ODER Aufgabe B. Schreiben Sie eine halbformelle E-Mail.
Wichtig: Schreiben Sie zuerst die Nummer Ihrer Aufgabe auf den Antwortbogen (sonst keine Bewertung).

Aufgabe 1 (A) — Bitte um Informationen
<ad text, 60–110 words>
Schreiben Sie an <recipient>. Behandeln Sie darin entweder a) drei der folgenden Punkte oder b) zwei der folgenden Punkte und einen weiteren Aspekt Ihrer Wahl:
• Beschreiben Sie …   • Fragen Sie nach …   • Legen Sie dar …   • Stellen Sie weitere Fragen …
Überlegen Sie sich vor dem Schreiben eine passende Reihenfolge der Punkte, einen passenden Betreff, eine passende Anrede, Einleitung und einen passenden Schluss.
Schreiben Sie mindestens 150 Wörter. (Absender, Adresse, Datum sind nicht nötig.)

Aufgabe 2 (B) — Beschwerde
…
--- ENDE DER AUFGABE ---
```
Franz line (also remind): skim both tasks briefly and decide quickly ("2 minutes" is a tip, not official), no first draft ([TIPPS]: do not pre-write and copy), no memorised text, copy the task number first; three points done properly beat four done thinly (tip). Cross-outs are fine if clear.
Save the FULL text of both tasks: `uv run $SKILL_DIR/tools/tutor.py task save --slot schriftlich` with stdin (exactly tasks A and B, each with a distinct printed `number` and exactly 4 `leitpunkte`; the tool rejects anything else)
`{"level":"b2","module":"schriftlich","topic":"T7","tasks":{"A":{"number":1,"text":"…","leitpunkte":["…","…","…","…"]},"B":{"number":2,"text":"…","leitpunkte":["…","…","…","…"]}}}`.

## Common failure modes to avoid
- Leitpunkte that overlap, or that cannot be developed in 3–5 sentences.
- No concrete facts in the ad; real company names; ad text far over 110 words.
- Showing only one task; forgetting the printed task numbers or the form-element reminder.
- Saving only Leitpunkte without the ad text (the evaluator needs it for Situierung).
- Free-form layout instead of the template.
