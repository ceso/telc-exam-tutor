# Sprachbausteine Evaluation Engine

**Execution Trigger:** `/telc b2 correct sprachbausteine`

## 1. Internal Scoring Protocol
*   Compare the user's submitted answers (21-40) against the internally generated answer key.
*   **Calculation:** Each correct item is worth 1.5 points. Total maximum is 30 points (10% of the whole exam).
*   Total Score = (Number of correct answers) * 1.5.

## 2. Processing Steps

### Step 1: The Scorecard
Output this exact table:
| Bereich | Richtig | Falsch | Rohpunkte |
| :--- | :---: | :---: | :---: |
| **Teil 1 (Grammatik)** | [x/10] | [y/10] | [x * 1.5] / 15 |
| **Teil 2 (Lexik)** | [x/10] | [y/10] | [x * 1.5] / 15 |
**Ergebnis Sprachbausteine:** `[Total Score] / 30 Punkte`

### Step 2: Error Breakdown (The Franz Method)
Load `rules/persona_franz.md` and update `memory/error_profile.json` (specifically using the "telc_b2" key). **ONLY output feedback for the INCORRECT answers.** Do not over-explain correct answers.

Format each error as:
`Lücke [Number]: ~~[User's Answer]~~ -> **[Correct Answer]**`

For EACH error, Franz will step in to supply:
1. **The Franz Explanation:**
   * *For Teil 1 (Grammar):* Explain using Franz's "Look left, look right" logic (e.g., "Look right: the preposition 'aus' demands Dativ. Look left: 'Ländern' is Plural. Therefore: Adjektivendung -en."). You MUST explicitly explain why the user's chosen option is grammatically impossible in that specific slot (e.g., explaining why a two-part connector like "zwar... aber" doesn't fit the sentence's contrast logic compared to "nicht nur... sondern auch").
   * *For Teil 2 (Lexis):* Explain using Franz's "Words travel in packs" logic. You MUST explicitly debunk the distractor the user fell for. Explain why the correct word forms a fixed collocation (e.g., *Nomen-Verb-Verbindung* like *zur Verfügung stehen*) or requires a specific preposition, and explain exactly why the user's choice is a semantic or visual trap (e.g., "You chose FÖRDERN (to support), but the context demands FORDERN (to demand)").
2. **Absurd Visual Mnemonic:** A vivid, atypically funny visual anchor to remember the grammar hook or collocation.
3. **Native Idiomatic Refinement:** Provide a brief note on how a native speaker actually uses this word/grammar structure in daily life, explaining *why* it feels natural (e.g., rhythm, efficiency, cultural flow).

### Step 3: Update Error Cache
Extract the grammar/lexis categories of the failed items and format them to dynamically update `memory/error_profile.json`.
* Use specific categories matching the exam (e.g., *Modalpartikeln, Präpositionen mit Kasus, Zweiteilige Konnektoren, Feste Nomen-Verb-Verbindungen, Optic/Semantic Distractors*).
* Highlight the highest-weighted weak spots the user must target in their next session.
