# Exam countdown plan (date-agnostic)

Used by `/telc <level> plan`. `tutor.py plan` / `status` return `days_left`, `t_minus` (T-N when ≤ 21), `bracket`, `plan_phase`,
`bootcamp_length_if_started_now` and `bootcamp_viable`. The exam date is per user (`tutor.py exam-date set YYYY-MM-DD`, stored in
the user's profile, never in this repo). If it is unset: ask once, then continue; without a date use the default 14-day bootcamp.
If `days_left < 0` the stored date is past: ask for the next exam date. Print only today's row (and tomorrow's), never the whole plan.

## Bootcamp length
`length = clamp(days_left − 7, 7, 14)`. It should end **≥7 days before the exam when possible; if that is not possible, use a 3-day fallback for triage/mocks** (`bootcamp_viable` false ⇒ `days_left < 10`).

## Plan by `days_left` bracket (before / outside the exam week)
| days_left | Plan |
| :-- | :-- |
| ≥ 28 | Optional extra weeks first: one module per day (Lesen, SB, Schriftlich, Hören, Sprechen) and Redemittel. Start the 14-day bootcamp when `days_left` reaches 21 (`days_until_ideal_bootcamp_start`). With a lot of time a second bootcamp round on the next top-5 is allowed (`bootcamp-close`, then `bootcamp-start`). |
| 21–27 | Start the 14-day bootcamp now, plus 1 module per day as in the day table below. Then 7 days mocks/taper. |
| 14–20 | Bootcamp length = `days_left − 7` (7–13 days). Compress phases A–D proportionally (the tool scales them). |
| 10–13 | 7-day bootcamp on the top-3 targets only. |
| 8–9 | Bootcamp not viable. Triage: drill the top-3 error categories (10 items each, `drill`), then mocks. |
| 7 | T-7 mock day: no bootcamp; do the timed mock and transfer answers. |
| < 7 | No bootcamp. Triage drill on top-3 errors (one 20-min session per day) + the T-minus plan below + checklist. |

## Bootcamp day table (L = length; scale phases with `status`)
| Day (14-day case) | Phase | Daily content (≈ minutes) |
| :-- | :-- | :-- |
| 1–2 | A diagnose/lock | Bootcamp (20). Beginning measurement: write one Schriftlich (30) and `transfer first --words W --errors E` (optional). |
| 3–9 | B | Bootcamp (20) + one module a day, rotating Lesen 1/2/3, SB 1/2, Schriftlich, Hören 1/2/3, Sprechen T1/T2/T3 (≈ 15–35). |
| 10–11 | C transfer | Transfer micro-tasks (20) + Schriftlich timed 30 min with correction. |
| 12–14 (L−2…L) | D final | `drill --final`, 3 hint-free items per target (20); delayed re-test; `bootcamp-close`; optional `transfer last`. |

## Exam week (last 7 days before the exam)
| T-minus | Plan |
| :-- | :-- |
| T-7 | **Mock Lesen + Sprachbausteine, 90 min timed** (Antwortbogen transfer ≈ 10 min inside the 90) + `block-total`. |
| T-6 | Schriftlich timed 30 min (copy the task number!) · Hören 1–3 · 1 bootcamp micro-session (10). |
| T-5 | Sprechen full run T1–T3 (≈ 20) · 1 micro-session (10). |
| T-4 | Mock Lesen + SB 90 min · `block-total`. |
| T-3 | Schriftlich timed (the other task) + Hören 1–3 · weakest-target micro-session (10). |
| T-2 | Light review ONLY (≤ 30 min): Top-3 lessons, Redemittel, Hören/Sprechen tips. No new mocks. |
| T-1 | Rest. Checklist: ID, pencil + eraser, route and time; Antwortbogen is what counts, pencil only; **copy the Schreibaufgabe NUMBER onto the Antwortbogen**, otherwise 0 points for the writing. |
| T-0 | Exam day: eat, arrive early, breathe. |

## Rules
1. Missing days: do not double up; shift the next day and keep T-2/T-1 untouched.
2. With less time than the bracket needs, drop modules, never the T-2 / T-1 rest.
3. Hören/Sprechen via TTS or text are optional practice, see their module files for limits.

## Realistic expectations
- Mastery = ≥ 80 % in the last 10 drill items, on ≥ 3 dates over a minimum span, plus a final check: it measures drill accuracy on your top error patterns, not exam points. The bootcamp goal is ≥60% of targets (3/5 or 2/3).
- A single mock total is noisy (about ±10 %); judge the trend over 2–3 mocks. Official pass rule: 60 % of the written part (135/225) AND of the oral part (45/75), see the architecture file §1.
