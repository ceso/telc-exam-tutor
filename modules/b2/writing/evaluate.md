# Writing Correction & Evaluation Engine

**Execution Trigger:** `/telc b2 correct write`

## 1. Internal Scoring Rubric (Max 45 Points)
Evaluate the text strictly against these telc B2 criteria.
**Calculation:** (Kriterium I + Kriterium II + Kriterium III) * 3 = Total Score.
*Gatekeeper Rule: If Kriterium I or III is a D (0), the entire writing section is graded 0*.

**I. Behandlung des Schreibanlasses (Adressatengerechtigkeit & Leitpunkte)**
- **A (5 Pkt):** Voll angemessen. Mindestens 3 Leitpunkte (oder 2 + 1 eigener) fundiert bearbeitet. Jeder Punkt erfordert mehr als ein einziges Satzgefüge.
- **B (3 Pkt):** Im Großen und Ganzen angemessen. Weniger als 3 Leitpunkte ohne Zusatzaspekt, oder 1 Leitpunkt + 1 Aspekt.
- **C (1 Pkt):** Kaum noch akzeptabel. Nur 1 Leitpunkt oder nur 1 Zusatzaspekt bearbeitet.
- **D (0 Pkt):** Thema verfehlt oder kein Leitpunkt fundiert behandelt.

**II. Kommunikative Gestaltung (Kohäsion, Register & Wortschatz)**
- **A (5 Pkt):** Register voll getroffen, flüssige Verknüpfungen (Konnektoren), gutes B2-Vokabular. Formale Merkmale (Absender, Datum, Betreff) sind vorhanden.
- **B (3 Pkt):** Register schwankt, Leitpunkte sind linear ohne logische Verknüpfung aufgelistet, oder Wortschatz ist unter B2-Niveau.
- **C (1 Pkt):** Starke Missachtung von Adressatenbezug und Register.
- **D (0 Pkt):** Der Text ist an zentralen Stellen unklar oder widersprüchlich.

**III. Formale Richtigkeit (Syntax, Morphologie, Orthographie)**
- **A (5 Pkt):** Keine oder nur vereinzelte Fehler, die das Verständnis nicht stören.
- **B (3 Pkt):** Wenige Fehler, beim ersten Lesen verständlich.
- **C (1 Pkt):** Viele Fehler, mehrmaliges Lesen nötig. Schreibabsicht gefährdet.
- **D (0 Pkt):** Unverständlich wegen Fehlerhäufung.

## 2. Processing Steps

### Step 1: Struktureller Audit & Form-Check (telc B2 Guidelines)
Check the text for the following mandatory elements based on the official telc guidelines:
- **Wortanzahl:** Mindestens 150 Wörter.
- **Formale Struktur:** Betreff, Anrede, Einleitung, Hauptteil, Schluss, Grußformel und Unterschrift müssen zwingend vorhanden sein.
- **Leitpunkte (Maximal 3):** Es dürfen exakt 3 Leitpunkte behandelt werden (entweder 3 vorgegebene oder 2 vorgegebene + 1 eigener). Ausufernde Ideen oder mehr Leitpunkte geben keine Extrapunkte!
- **Absätze:** Jeder bearbeitete Leitpunkt MUSS in einem eigenen Absatz stehen.
- **Logische Reihenfolge:**
  - *Bei Aufgabe A (Bitte um Informationen):* Zuerst die Begründung, warum man sich interessiert, anschließend weitere Fragen stellen.
  - *Bei Aufgabe B (Beschwerde):* Zuerst ursprüngliche Erwartungen beschreiben, dann aufgetretene Probleme schildern, am Schluss Forderungen stellen.
- **Authentizität:** Der Text muss genau zur Aufgabe passen. Auswendig gelernte Musterlösungen ohne direkten Bezug geben Punktabzug.

### Step 2: telc B2 Grading
Grade the text using the standard A-D scale and calculate points (max 45):
- I. Behandlung der Aufgabe
- II. Kommunikative Gestaltung (inklusive Reihenfolge und formaler Struktur)
- III. Formale Richtigkeit

### Step 3: Top-3 Fehleranalyse (The Franz Method)
Load `rules/persona_franz.md` and check `memory/error_profile.json` (specifically use the "telc_b2" key to find the active_focus).
Isoliere exakt die **TOP 3 wichtigsten grammatikalischen oder strukturellen Fehler** aus dem Text des Users. Priorisiere diese strikt nach dem `active_focus` in der Datei `error_profile.json`.
Format these 3 priority errors with strikethrough and side-by-side correction:
`~~original error~~` -> `**korrigierte Fassung**`

For EACH of the Top-3 errors, Franz will supply:
1. **The Franz Explanation:** Why the error occurred using Franz's grammar logic.
2. **Absurd Visual Mnemonic:** A vivid, atypically funny visual anchor.

### Step 4: Redemittel-Tuning (Native-Like Upgrades)
WICHTIG: Wenn der User Redemittel oder Phrasen verwendet, die grammatikalisch korrekt, aber unnatürlich, starr oder zu simpel sind, markiere sie **NICHT als Fehler** (kein strikethrough).
Stattdessen gib am Ende 1-2 "Native-Like Upgrades" (wie in den echten telc-Beispiellösungen):
- Zeige, wie ein Muttersprachler den Satz flüssiger formulieren würde (z.B. "Aus diesem Grund bin ich auf der Suche nach..." statt "Deswegen suche ich..." oder "Meine Erwartungen wurden jedoch leider nicht erfüllt").
- Erkläre kurz, warum das vorgeschlagene Redemittel natürlicher oder professioneller (B2-Niveau) klingt.
