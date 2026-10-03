 # Bootcamp Evaluation Engine

**Execution Trigger:** `/telc <level> correct bootcamp`

## 1. Internal Scoring & Adjustment Protocol
*   Compare the user's submitted answers against your internally generated answer key for the custom drill.
*   **The Healing Logic:**
    *   For every weakness the user successfully masters in this drill, you MUST reduce its `priority_weight` in `memory/error_profile.json` (under the appropriate level key) by `0.3`. (If it reaches 0.0 or below, it is "cured" and its weight resets to 0.0).
    *   For every weakness the user fails again, increase its `priority_weight` by `0.2` and keep it in the Active Focus.

## 2. Processing Steps

### Step 1: The Bootcamp Scorecard
Output a brief summary of what was tested and whether the user passed or failed that specific micro-skill.

### Step 2: Error Breakdown (The Franz Method)
Load `rules/persona_franz.md`. **ONLY output feedback for the INCORRECT answers.**

Format each error as:
`Übung [Number]: ~~[User's Answer]~~ -> **[Correct Answer]**`

For EACH error, Franz will step in to supply:
1. **The Franz Explanation:** Direct, rule-based debunking of exactly why the trap snapped shut.
2. **Absurd Visual Mnemonic:** A vivid, atypically funny visual anchor.

### Step 3: Update Error Cache
Output a confirmation of the exact math applied to `memory/error_profile.json`. Highlight any newly "cured" weaknesses!

**Example output for Step 3:**
*Profile Updates:*
*   *V2-Syntax: Mastered! Weight reduced (-0.3).*
*   *Präpositionaladverbien: Failed. Weight increased (+0.2).*
*(Make sure to dynamically update the actual `memory/error_profile.json` file in the background).*
