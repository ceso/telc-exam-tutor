# Leseverstehen Evaluation Engine

**Execution Trigger:** `/telc b2 correct lesen`

## 1. Internal Scoring Protocol
*   Compare the user's submitted answers (1-20) against the internally generated answer key.
*   **Calculation:**
    *   Teil 1 (Aufgaben 1-5): 5 points per correct answer (Max 25).
    *   Teil 2 (Aufgaben 6-10): 5 points per correct answer (Max 25).
    *   Teil 3 (Aufgaben 11-20): 2.5 points per correct answer (Max 25).
*   Total maximum is 75 points (25% of the whole exam).

## 2. Processing Steps

### Step 1: The Scorecard
Output this exact table:
| Bereich | Richtig | Falsch | Rohpunkte |
| :--- | :---: | :---: | :---: |
| **Teil 1 (Globalverstehen)** | [x/5] | [y/5] | [x * 5] / 25 |
| **Teil 2 (Detailverstehen)** | [x/5] | [y/5] | [x * 5] / 25 |
| **Teil 3 (Selektives Lesen)** | [x/10] | [y/10] | [x * 2.5] / 25 |
**Ergebnis Leseverstehen:** `[Total Score] / 75 Punkte`

### Step 2: Error Breakdown (The Franz Method)
Load `rules/persona_franz.md` and update `memory/error_profile.json` (specifically using the "telc_b2" key). **ONLY output feedback for the INCORRECT answers.** Do not over-explain correct answers.

Format each error as:
`Aufgabe [Number]: ~~[User's Answer]~~ -> **[Correct Answer]**`

For EACH error, Franz will step in to supply:
1. **The Franz Explanation:**
   * *For Teil 1 (Global):* Explain why the user's chosen headline was a "Micro-Detail Trap" (it only mentioned one word/detail from the text) while the correct headline captures the "Global Umbrella".
   * *For Teil 2 (Detail):* Point out the exact synonym, antonym, or modal verb trick in the text that changes the meaning. Debunk "absolutisms" (e.g., the text says *many*, the wrong answer says *all*).
   * *For Teil 3 (Selective):* Identify the specific "Dealbreaker Keyword" in the situation (e.g., *am Wochenende*, *kostenlos*, *für Kinder*, *für Anfänger*) that the user ignored when they picked their text. If the correct answer is 'x', explicitly prove how the closest text failed at least one condition.
2. **Absurd Visual Mnemonic:** A vivid, atypically funny visual anchor to remember the reading strategy (e.g., "The 'X' in Teil 3 is a grumpy bouncer rejecting everyone who doesn't have the exact VIP ticket combo").
3. **Native Reading Strategy:** Provide a brief tip on how to scan German texts faster (e.g., scanning for contrast connectors like *jedoch* or *dennoch* where the real answer hides, or watching out for double negatives).

### Step 3: Update Error Cache
Extract the reading error categories and format them to dynamically update `memory/error_profile.json`.
* Use specific categories matching the reading traps (e.g., *Globalverstehen-Micro-Traps, Detailverstehen-Synonym-Traps, Detailverstehen-Absolutisms, Selektives-Lesen-Dealbreaker, Selektives-Lesen-X-Failure*).
* Highlight the highest-weighted weak spots the user must target in their next session.
