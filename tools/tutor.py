#!/usr/bin/env python3
"""Deterministic helper for the telc-exam-tutor skill (stdlib only).

Run with:  uv run $SKILL_DIR/tools/tutor.py <command> ...
State lives in $TELC_HOME (default ~/.config/telc-tutor): profile.json and tasks/<slot>.json.
Every command prints JSON so the agent never has to count or do arithmetic itself.
Errors print {"error": ...} to stderr and exit with status 2.
"""
import argparse
import datetime as dt
import json
import math
import os
import re
import sys
import tempfile
from pathlib import Path

HOME = Path(os.environ.get("TELC_HOME", Path.home() / ".config" / "telc-tutor"))
PROFILE = HOME / "profile.json"
TASKS = HOME / "tasks"
ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "memory" / "error_profile.template.json"

# Point tables: telc Deutsch B2 Handbuch (2019) / Tipps zur Prüfungsvorbereitung (2020); confirmed by the newer Handbuch edition
POINTS_PER_ITEM = {
    "lesen1": (5, 5), "lesen2": (5, 5), "lesen3": (10, 2.5),
    "sb1": (10, 1.5), "sb2": (10, 1.5),
    "hoeren1": (5, 5), "hoeren2": (10, 2.5), "hoeren3": (5, 5),
}
LETTER_POINTS = {"A": 5, "B": 3, "C": 1, "D": 0}
# Written block simulated by this skill: Lesen 75 + Sprachbausteine 30 + Schriftlicher Ausdruck 45.
# Pass rule: >= 60 % of the written part (135/225) AND of the oral part (45/75) - newer telc Handbuch edition,
# "Informationen zur Prüfung" (not in the 2019 Handbuch / 2020 Tipps PDFs). 90/150 for this block is skill design.
BLOCK_MODULES = ["lesen1", "lesen2", "lesen3", "sb1", "sb2", "schriftlich"]
BLOCK_MAX = 150
BLOCK_PASS_60 = 90
WRITTEN_PASS_60 = 135  # official: 60 % of the 225 written points
ORAL_PASS_60, ORAL_MAX, WRITTEN_MAX = 45, 75, 225  # official: 60 % of the 75 oral points
# Official grade bands of the 300 total (lower bounds); below 180 or any part under 60 % = nicht bestanden
GRADE_BANDS = [(270, "sehr gut"), (240, "gut"), (210, "befriedigend"), (180, "ausreichend")]
# Official oral scale per criterion 1-3 (Ausdrucksfähigkeit, Aufgabenbewältigung, Formale Richtigkeit): 7/5/3/0.
# Criterion 4 (Aussprache und Intonation, 4/2/1/0) is not assessable from text. A-D = this skill's rating labels.
SPEAKING_POINTS = {"A": 7, "B": 5, "C": 3, "D": 0}
SPEAKING_EST_MAX = 21
HOEREN_MODULES = ["hoeren1", "hoeren2", "hoeren3"]  # reported separately, never inside the written-block total
HOEREN_MAX = 75

# Per-slot task format (rules/telc_b2_architecture.md §4): item count and allowed answers.
LETTERS = lambda a, b: set(map(chr, range(ord(a), ord(b) + 1)))
SLOT_SPEC = {
    "lesen1": {"module": "lesen", "part": 1, "n": 5, "answers": LETTERS("a", "j"), "unique": True},
    "lesen2": {"module": "lesen", "part": 2, "n": 5, "answers": LETTERS("a", "c")},
    "lesen3": {"module": "lesen", "part": 3, "n": 10, "answers": LETTERS("a", "l") | {"x"}, "unique": True},
    "sb1": {"module": "sprachbausteine", "part": 1, "n": 10, "answers": LETTERS("a", "c")},
    "sb2": {"module": "sprachbausteine", "part": 2, "n": 10, "answers": LETTERS("a", "o"), "unique": True},
    "hoeren1": {"module": "hoeren", "part": 1, "n": 5, "answers": {"r", "f"}},
    "hoeren2": {"module": "hoeren", "part": 2, "n": 10, "answers": {"r", "f"}},
    "hoeren3": {"module": "hoeren", "part": 3, "n": 5, "answers": {"r", "f"}},
    "schriftlich": {"module": "schriftlich"},
    "sprechen1": {"module": "sprechen", "part": 1},
    "sprechen2": {"module": "sprechen", "part": 2},
    "sprechen3": {"module": "sprechen", "part": 3},
    "bootcamp": {"module": "bootcamp", "min_n": 1, "max_n": 15},
}

MATERIAL_COUNTS = {
    "lesen1": {"texts": 5, "headlines": 10},
    "lesen2": {"options": 5},
    "lesen3": {"situations": 10, "texts": 12},
    "sb1": {"options": 10},
    "sb2": {"word_box": 15},
}

# Bootcamp parameters
WINDOW = 10            # attempts that define current accuracy
MASTERY = 0.80         # accuracy over the window that counts as "stopped making this mistake"
NEAR = 0.70
MIN_DAYS = 3           # distinct calendar dates inside the window
BOOTCAMP_DAYS = 14     # default length; shortened when the exam is near (see choose_length)
MIN_LENGTH = 7
EXAM_BUFFER = 7        # bootcamp ends >= 7 days before the exam when possible (exam week = mocks/taper)


def min_span(length):
    """Calendar days between first and last attempt inside the window. Fixed at 3: the window of 10 items
    spans only ~4 days at 2-3 items/target/day, so a larger span would make the goal unreachable."""
    return 3


def final_from(length):
    """Final check = delayed re-test in the last 3 days of the bootcamp (day 12 of 14)."""
    return length - 2
FINAL_MIN_ITEMS = 3
SESSION_ITEMS = 15
SEED_AFTER = 3         # first diagnostic attempts seed the weight
SEED_SCALE = 6.0       # weight = (1 - accuracy) * SEED_SCALE
MAX_ERRORS_PER_KEY = 5
W_ERROR, W_DRILL_WRONG, W_DRILL_RIGHT = 1.0, 0.5, -0.25
SLOT_RE = re.compile(r"^[a-z0-9_]{1,32}$")


def die(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(2)


def today(args=None):
    d = getattr(args, "date", None) if args else None
    if not d:
        return dt.date.today()
    try:
        return dt.date.fromisoformat(d)
    except ValueError:
        die(f"--date must be YYYY-MM-DD, got {d!r}")


def write_atomic(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    except BaseException:
        Path(tmp).unlink(missing_ok=True)
        raise


def dump(obj):
    return json.dumps(obj, ensure_ascii=False, indent=2)


def out(obj):
    print(dump(obj))


def load_template():
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def new_cat():
    return {"errors_total": 0, "weight": 0.0, "drill": []}


def new_bootcamp():
    return {"status": "inactive", "start": None, "end": None, "targets": [],
            "diagnostic": [], "seeded": [], "transfer": {}}


def migrate_cat(c):
    """Old format: drill = [0/1,...] plus a separate days list. New: [{d, ok, f?}]."""
    c.setdefault("errors_total", 0)
    c.setdefault("weight", 0.0)
    drill = []
    for e in c.get("drill", []):
        if isinstance(e, dict):
            drill.append(e)
        elif e in (0, 1, True, False):
            drill.append({"d": None, "ok": int(e)})  # undated: counts for accuracy, never for mastery dates
    c["drill"] = drill
    c.pop("days", None)
    return c


def load_profile():
    tpl = load_template()
    if not PROFILE.exists():
        prof = {"version": tpl["version"], "submissions": [], "estimates": [],
                "categories": {k: new_cat() for k in tpl["categories"]},
                "bootcamp": new_bootcamp()}
        save_profile(prof)
        return prof
    try:
        prof = json.loads(PROFILE.read_text(encoding="utf-8"))
        if not isinstance(prof, dict) or not isinstance(prof.get("categories"), dict):
            raise ValueError("missing 'categories' object")
    except (ValueError, OSError) as e:
        die(f"{PROFILE} is corrupt ({e}). Move or delete it (it will be recreated) and retry.")
    prof.setdefault("submissions", [])
    prof.setdefault("estimates", [])
    prof["bootcamp"] = {**new_bootcamp(), **prof.get("bootcamp", {})}
    for k in tpl["categories"]:
        prof["categories"].setdefault(k, new_cat())
    for c in prof["categories"].values():
        migrate_cat(c)
    return prof


def save_profile(prof):
    write_atomic(PROFILE, dump(prof))


def parse_pairs(pairs, mode):
    """errors: key[=n] with n an int >= 0 (clamped to 5). drill: key=0 or key=1 (mandatory)."""
    valid = load_template()["categories"]
    res = {}
    for p in pairs:
        k, eq, v = p.partition("=")
        if k not in valid:
            die(f"Unknown category key {k!r}. Valid: {sorted(valid)}")
        if mode == "drill":
            if v not in ("0", "1"):
                die(f"drill needs {k}=0 or {k}=1, got {p!r}")
            res.setdefault(k, []).append(int(v))
        else:
            if not eq:
                n = 1
            elif re.fullmatch(r"\d+", v):
                n = int(v)
            else:
                die(f"error count must be an integer >= 0, got {p!r}")
            res[k] = min(MAX_ERRORS_PER_KEY, res.get(k, 0) + n)
    return res


# ---------- bootcamp maths ----------
def window(cat):
    return cat["drill"][-WINDOW:]


def accuracy(cat):
    w = window(cat)
    return (sum(e["ok"] for e in w) / len(w)) if w else None


def window_dates(cat):
    return sorted({e["d"] for e in window(cat) if e.get("d")})


def span_days(cat):
    ds = window_dates(cat)
    if len(ds) < 2:
        return 0
    return (dt.date.fromisoformat(ds[-1]) - dt.date.fromisoformat(ds[0])).days


def band(cat, length=BOOTCAMP_DAYS):
    w = window(cat)
    if len(w) < WINDOW:
        return "building"
    a = accuracy(cat)
    if a >= MASTERY and len(window_dates(cat)) >= MIN_DAYS and span_days(cat) >= min_span(length):
        return "mastered"
    return "near" if a >= NEAR else "weak"


def final_status(cat):
    """First final batch (max 5 items) decides; retakes do not replace it."""
    f = [e for e in cat["drill"] if e.get("f")][:5]
    n = len(f)
    if n < FINAL_MIN_ITEMS:
        return {"n": n, "ok": sum(e["ok"] for e in f), "needed": None, "status": "pending"}
    need = math.ceil(2 * n / 3 - 1e-9) if n <= 4 else math.ceil(0.8 * n - 1e-9)
    ok = sum(e["ok"] for e in f)
    return {"n": n, "ok": ok, "needed": need, "status": "passed" if ok >= need else "failed"}


def top_n(prof, n=5):
    tpl = load_template()
    ranked = sorted(prof["categories"].items(), key=lambda kv: -kv[1]["weight"])
    picked = [k for k, v in ranked if v["weight"] > 0 and k in tpl["categories"]][:n]
    for k in tpl["default_priors"]:  # diagnostic fallback for a fresh profile
        if len(picked) == n:
            break
        if k not in picked:
            picked.append(k)
    return [{"key": k, "name": tpl["categories"][k]["name"],
             "weight": round(prof["categories"][k]["weight"], 2),
             "from_data": prof["categories"][k]["weight"] > 0} for k in picked]


def allocate(rows):
    """15 items: mastered = 1 spaced-review item, open targets = 2 + weight-proportional share (largest remainder)."""
    alloc = {r["key"]: 1 for r in rows if r["band"] == "mastered"}
    open_rows = [r for r in rows if r["band"] != "mastered"]
    if not open_rows:
        return alloc
    left = SESSION_ITEMS - len(alloc) - 2 * len(open_rows)
    ws = [max(r["weight"], 1.0) for r in open_rows]
    raw = [left * w / sum(ws) for w in ws]
    base = [int(x) for x in raw]
    order = sorted(range(len(raw)), key=lambda i: -(raw[i] - base[i]))
    for i in order[:left - sum(base)]:
        base[i] += 1
    for r, b in zip(open_rows, base):
        alloc[r["key"]] = 2 + b
    return alloc


def phase(day, length=BOOTCAMP_DAYS):
    r = day / length
    return ("A_diagnose_and_lock" if r <= 2 / 14 else "B_drill" if r <= 9 / 14 else
            "C_transfer" if day < final_from(length) else "D_final_check")


def choose_length(days_left):
    if days_left is None:
        return BOOTCAMP_DAYS
    return max(MIN_LENGTH, min(BOOTCAMP_DAYS, days_left - EXAM_BUFFER))


def days_left_for(prof, d):
    e = prof.get("exam_date")
    return (dt.date.fromisoformat(e) - d).days if e else None


def plan_phase(days_left, bootcamp_active):
    if days_left is None:
        return "no_exam_date"
    if days_left < 0:
        return "exam_passed"
    if days_left == 0:
        return "exam_day"
    if days_left == 1:
        return "rest_and_checklist"
    if days_left == 2:
        return "light_review_only"
    if days_left <= 7:
        return "timed_mocks_alternating_with_micro_session"
    if bootcamp_active:
        return "bootcamp"
    if days_left < MIN_LENGTH + 3:
        return "triage_top3_errors_then_mocks"
    return "prep_before_bootcamp" if days_left > BOOTCAMP_DAYS + EXAM_BUFFER else "bootcamp_should_run_now"


def bracket(dl):
    return (">=28" if dl >= 28 else "21-27" if dl >= 21 else "14-20" if dl >= 14
            else "10-13" if dl >= 10 else "8-9" if dl >= 8 else "7" if dl == 7 else "<7")


def default_targets(dl):
    """3 targets when the bootcamp is short (10-13 days left), else 5."""
    return 3 if dl is not None and dl < 14 else 5


def goal_needed(n_targets):
    return math.ceil(0.6 * n_targets - 1e-9)


def plan_info(prof, d):
    dl = days_left_for(prof, d)
    if dl is None:
        return {"exam_date": None, "days_left": None, "plan_phase": "no_exam_date",
                "needs_exam_date": True,
                "prompt": "Ask the user once for the exam date, then run exam-date set YYYY-MM-DD "
                          "(plan works without it; default bootcamp = 14 days)."}
    if dl < 0:
        return {"exam_date": prof["exam_date"], "days_left": dl, "plan_phase": "exam_passed",
                "needs_exam_date": True,
                "prompt": "Stored exam date is in the past: ask the user for the next exam date (exam-date set)."}
    return {"exam_date": prof["exam_date"], "days_left": dl, "needs_exam_date": False,
            "plan_phase": plan_phase(dl, prof["bootcamp"]["status"] == "active"),
            "bracket": bracket(dl), "t_minus": f"T-{dl}" if dl <= 21 else "T-21+",
            "bootcamp_length_if_started_now": choose_length(dl),
            "days_until_ideal_bootcamp_start": max(0, dl - (BOOTCAMP_DAYS + EXAM_BUFFER)),
            "bootcamp_viable": dl - choose_length(dl) >= 3}


def averages(entries):
    per = {}
    for s in entries:
        per.setdefault(s["module"], []).append(s["score"] / s["max"] * 100 if s.get("max") else 0)
    return {m: {"n": len(v), "avg_pct": round(sum(v) / len(v))} for m, v in per.items()}


def recent_and_averages(prof):
    """Exam-style scores only. Typed-speaking estimates (own index, not telc points) are listed apart."""
    subs = [s for s in prof["submissions"] if not s.get("estimate")]
    est = prof.get("estimates", []) + [s for s in prof["submissions"] if s.get("estimate")]
    return {"recent_scores": subs[-5:], "module_averages": averages(subs),
            "speaking_estimates": {"recent": est[-5:], "averages": averages(est),
                                   "note": "typed-text estimate (criteria 1-3 only, max 21 per part), "
                                           "NOT an exam score; excluded from scores, averages and block totals"}}


def bootcamp_report(prof, d):
    bc = prof["bootcamp"]
    tpl = load_template()["categories"]
    day = (d - dt.date.fromisoformat(bc["start"])).days + 1
    L = bc.get("length", BOOTCAMP_DAYS)
    rows = []
    for k in bc["targets"]:
        c = prof["categories"][k]
        a = accuracy(c)
        fin = final_status(c)
        b = band(c, L)
        rows.append({"key": k, "name": tpl[k]["name"],
                     "accuracy_last10": None if a is None else round(a, 2),
                     "attempts": len(c["drill"]), "dates_in_window": len(window_dates(c)),
                     "span_days_in_window": span_days(c), "band": b, "weight": c["weight"],
                     "final": fin, "confirmed": b == "mastered" and fin["status"] == "passed"})
    mastered = [r["key"] for r in rows if r["band"] == "mastered"]
    confirmed = [r["key"] for r in rows if r["confirmed"]]
    pending = [r["key"] for r in rows if r["final"]["status"] == "pending"]
    expired = day > L
    goal_n = goal_needed(len(rows))
    goal = len(confirmed) >= goal_n
    final_due = day >= final_from(L) and bool(pending) and not goal
    if final_due:
        alloc = {k: FINAL_MIN_ITEMS for k in pending}
    else:
        alloc = allocate(rows)
    if goal:
        step = f"goal reached (>={goal_n} targets confirmed): run bootcamp-close"
    elif expired:
        step = (f"EXPIRED (day {day} > {L}): run bootcamp-close"
                + ("; final check is still pending for: " + ", ".join(pending) if pending else ""))
    elif final_due:
        step = "final check today: 3 hint-free items per pending target (drill --final)"
    elif len(mastered) >= goal_n:
        step = f"provisionally mastered; keep spaced review, final check from day {final_from(L)}"
    else:
        step = "run today's session"
    return {"day": day, "of": L, "phase": phase(min(day, L), L), "min_span_days": min_span(L),
            "expired": expired, "goal_reached": goal, "goal_needed": goal_n, "provisionally_mastered": mastered,
            "confirmed": confirmed, "targets": rows, "todays_allocation": alloc,
            "transfer": transfer_view(bc), "next_step": step,
            "measures": "drill accuracy (last 10, >=3 dates, >=3-day span) + first final batch (>=2/3 of 3, >=4/5 of 5); "
                        "transfer (errors/100 words) is optional and separate"}


def transfer_view(bc):
    t = bc.get("transfer", {})
    v = dict(t)
    if "first" in t and "last" in t:
        v["change_per100"] = round(t["last"]["per100"] - t["first"]["per100"], 2)
    return v


# ---------- commands ----------
def cmd_wordcount(args):
    try:
        text = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
    except OSError as e:
        die(str(e))
    words = re.findall(r"[^\W_]+(?:[-'’][^\W_]+)*", text, flags=re.UNICODE)
    out({"words": len(words), "meets_150": len(words) >= 150})


def record_submission(args, entry, bucket="submissions"):
    prof = load_profile()
    if getattr(args, "recheck", False):
        entry = {**entry, "recheck": True}
    prof[bucket].append({"date": today(args).isoformat(), **entry})
    save_profile(prof)


def guard_graded(args, slot):
    """A graded slot must not be scored again (double recording) unless --recheck is explicit."""
    if getattr(args, "recheck", False) or not SLOT_RE.match(slot) or not (TASKS / f"{slot}.json").exists():
        return
    if read_task(slot).get("graded"):
        die(f"task slot {slot!r} is already graded; pass --recheck to score it again on purpose")


def cmd_score_writing(args):
    guard_graded(args, "schriftlich")
    L = [x.upper() for x in (args.I, args.II, args.III)]
    if any(x not in LETTER_POINTS for x in L):
        die("Ratings must be A, B, C or D")
    flags = []
    if args.thema_verfehlt:      # D on all criteria
        L = ["D", "D", "D"]
        flags.append("thema_verfehlt")
    elif args.situierung_verfehlt:   # D on criterion I only
        L[0] = "D"
        flags.append("situierung_verfehlt")
    pts = [LETTER_POINTS[x] for x in L]
    total = sum(pts) * 3
    res = {"letters": dict(zip(["I", "II", "III"], L)), "criteria": dict(zip(["I", "II", "III"], pts)),
           "flags": flags, "total": total, "max": 45, "pct": round(total / 45 * 100)}
    out(res)
    if args.record:
        record_submission(args, {"module": "schriftlich", "score": total, "max": 45,
                                 "criteria": res["letters"], "flags": flags})


def cmd_score(args):
    if args.module not in POINTS_PER_ITEM:
        die(f"module must be one of {sorted(POINTS_PER_ITEM)}")
    guard_graded(args, args.module)
    n, per = POINTS_PER_ITEM[args.module]
    if not 0 <= args.correct <= n:
        die(f"--correct must be 0..{n}")
    score, mx = args.correct * per, n * per
    out({"module": args.module, "correct": args.correct, "of": n, "score": score, "max": mx,
         "pct": round(score / mx * 100)})
    if args.record:
        record_submission(args, {"module": args.module, "score": score, "max": mx})


def cmd_block_total(args):
    prof = load_profile()
    since = args.since or today(args).isoformat()
    try:
        dt.date.fromisoformat(since)
    except ValueError:
        die(f"--since must be YYYY-MM-DD, got {since!r}")
    latest, latest_h = {}, {}
    for s in prof["submissions"]:  # later entries override earlier ones: the latest score per module counts
        if s.get("estimate") or s["date"] < since:
            continue
        if s["module"] in BLOCK_MODULES:
            latest[s["module"]] = s
        elif s["module"] in HOEREN_MODULES:
            latest_h[s["module"]] = s
    parts = {m: latest[m]["score"] for m in BLOCK_MODULES if m in latest}
    missing = [m for m in BLOCK_MODULES if m not in latest]
    total = sum(parts.values())
    mx = sum(latest[m]["max"] for m in parts)
    groups = {"lesen": ["lesen1", "lesen2", "lesen3"], "sprachbausteine": ["sb1", "sb2"],
              "schriftlich": ["schriftlich"]}
    hoeren = {m: latest_h[m]["score"] for m in HOEREN_MODULES if m in latest_h}
    res = {"scope": "written block WITHOUT Hören (Lesen + Sprachbausteine + Schriftlicher Ausdruck)",
           "since": since, "parts": parts, "missing": missing, "complete": not missing,
           "subtotals": {g: sum(parts.get(m, 0) for m in ms) for g, ms in groups.items()},
           "total": total, "max_recorded": mx, "block_max": BLOCK_MAX,
           "pct_of_recorded": round(total / mx * 100) if mx else None,
           "hoeren_separate": {"parts": hoeren, "total": sum(hoeren.values()), "max": HOEREN_MAX,
                               "complete": len(hoeren) == len(HOEREN_MODULES),
                               "note": "Hören is NOT in this total and has no threshold of its own here"},
           "sprechen": "typed Sprechen estimates are not telc points and never enter this total",
           "note": "Estimate only. Written exam = this block (150) + Hören (75) = 225; official pass rule "
                   "(newer telc Handbuch, Informationen zur Prüfung): >= 60 % of the written part = 135/225 "
                   "and >= 60 % of the oral part = 45/75. The 90/150 block share is skill design."}
    if not missing:
        res["on_track_for_block_60pct"] = total >= BLOCK_PASS_60
        res["points_to_90"] = max(0, BLOCK_PASS_60 - total)
        if res["hoeren_separate"]["complete"]:
            written = total + res["hoeren_separate"]["total"]
            res["written_total_225"] = written
            res["written_passed_135"] = written >= WRITTEN_PASS_60
    out(res)


def cmd_errors(args):
    prof = load_profile()
    pairs = parse_pairs(args.pairs, "errors")
    for k, n in pairs.items():
        if n == 0:
            continue
        c = prof["categories"][k]
        c["errors_total"] += n
        c["weight"] = round(c["weight"] + W_ERROR * n, 2)
    save_profile(prof)
    out({"recorded": pairs, "top5": top_n(prof)})


def cmd_drill(args):
    prof, d = load_profile(), today(args)
    bc = prof["bootcamp"]
    if bc["status"] != "active":
        die("no active bootcamp: run bootcamp-start first")
    day = (d - dt.date.fromisoformat(bc["start"])).days + 1
    L = bc.get("length", BOOTCAMP_DAYS)
    if args.final and day < final_from(L):
        die(f"final check (delayed re-test) is only allowed from day {final_from(L)}; today is day {day}")
    pairs = parse_pairs(args.pairs, "drill")
    off = [k for k in pairs if k not in bc["targets"]]
    if off:
        die(f"not bootcamp targets: {off}. Targets: {bc['targets']}")
    for k, oks in pairs.items():
        c = prof["categories"][k]
        for ok in oks:
            entry = {"d": d.isoformat(), "ok": ok}
            if args.final:
                entry["f"] = True
            c["drill"] = (c["drill"] + [entry])[-60:]
            if k in bc["diagnostic"] and k not in bc["seeded"]:
                if len(c["drill"]) >= SEED_AFTER:
                    first = c["drill"][:SEED_AFTER]
                    acc = sum(e["ok"] for e in first) / len(first)
                    c["weight"] = round((1 - acc) * SEED_SCALE, 2)
                    bc["seeded"].append(k)
            else:
                c["weight"] = round(max(0.0, c["weight"] + (W_DRILL_RIGHT if ok else W_DRILL_WRONG)), 2)
    save_profile(prof)
    cmd_status(args)


def cmd_start(args):
    prof = load_profile()
    bc = prof["bootcamp"]
    if bc["status"] == "active" and not args.force:
        die(f"a bootcamp is already active (started {bc['start']}). Use status / bootcamp-close, "
            "or bootcamp-start --force to discard it.")
    d = today(args)
    dl = days_left_for(prof, d)
    t = top_n(prof, default_targets(dl))
    for x in t:
        prof["categories"][x["key"]]["drill"] = []
    L = choose_length(dl)
    warning = None
    if dl is not None and dl - L < 3:
        warning = (f"only {dl} days to the exam: a {L}-day bootcamp would end {dl - L} days before it. "
                   "Prefer exam-week mocks (see rules/exam_countdown.md) over a bootcamp.")
    prof["bootcamp"] = {**new_bootcamp(), "status": "active", "start": d.isoformat(), "length": L,
                        "end": (d + dt.timedelta(days=L - 1)).isoformat(),
                        "targets": [x["key"] for x in t],
                        "diagnostic": [x["key"] for x in t if not x["from_data"]]}
    save_profile(prof)
    out({"bootcamp": prof["bootcamp"], "targets": t, "diagnostic_needed_for": prof["bootcamp"]["diagnostic"],
         "forced_over_active": bool(bc["status"] == "active"), "length_days": L,
         "min_span_days": min_span(L), "final_check_from_day": final_from(L), "warning": warning,
         **plan_info(prof, d)})


def cmd_status(args):
    prof = load_profile()
    bc = prof["bootcamp"]
    extra = recent_and_averages(prof)
    if bc["status"] != "active":
        out({"bootcamp": bc["status"], "top5": top_n(prof), **plan_info(prof, today(args)), **extra})
        return
    out({**bootcamp_report(prof, today(args)), **plan_info(prof, today(args)), **extra})


def cmd_exam_date(args):
    prof = load_profile()
    if args.action == "show" and args.date_value is not None:
        die("exam-date show takes no trailing arguments")
    if args.action == "set":
        if not args.date_value:
            die("exam-date set needs YYYY-MM-DD")
        try:
            e = dt.date.fromisoformat(args.date_value)
        except ValueError:
            die(f"exam date must be YYYY-MM-DD, got {args.date_value!r}")
        if e < today(args):
            die("exam date is in the past")
        prof["exam_date"] = e.isoformat()
        save_profile(prof)
    out(plan_info(prof, today(args)))


def cmd_speaking(args):
    """Estimate on the official 7/5/3/0 scale for criteria 1-3; Aussprache is excluded, so max 21 (official 25)."""
    L = [x.upper() for x in (args.I, args.II, args.III)]
    if any(x not in SPEAKING_POINTS for x in L):
        die("Ratings must be A, B, C or D")
    guard_graded(args, f"sprechen{args.part}")
    names = ["Ausdrucksfaehigkeit", "Aufgabenbewaeltigung", "Formale_Richtigkeit"]
    pts = [SPEAKING_POINTS[x] for x in L]
    est = sum(pts)
    res = {"part": args.part, "letters": dict(zip(names, L)), "criteria_points": dict(zip(names, pts)),
           "estimate_points": est, "of": SPEAKING_EST_MAX, "pct": round(est / SPEAKING_EST_MAX * 100),
           "aussprache_intonation": "not assessable from text, excluded (official 4/2/1/0; part max 25)",
           "note": "typed-text ESTIMATE out of 21, NOT an exam score and not out of 25; "
                   "kept apart from scores, averages and block totals"}
    out(res)
    if args.record:
        record_submission(args, {"module": f"sprechen{args.part}", "score": est, "max": SPEAKING_EST_MAX,
                                 "criteria": res["letters"], "estimate": True}, bucket="estimates")


def cmd_exam_result(args):
    """Pass rule and grade band from REAL exam points (official result), never from estimates."""
    w, o = args.written, args.oral
    if not 0 <= w <= WRITTEN_MAX or not 0 <= o <= ORAL_MAX:
        die(f"--written 0..{WRITTEN_MAX} and --oral 0..{ORAL_MAX}")
    ok = w >= WRITTEN_PASS_60 and o >= ORAL_PASS_60
    grade = next((n for lo, n in GRADE_BANDS if w + o >= lo), "nicht bestanden") if ok else "nicht bestanden"
    out({"written": w, "oral": o, "total": w + o, "max": 300, "written_ok": w >= WRITTEN_PASS_60,
         "oral_ok": o >= ORAL_PASS_60, "grade": grade, "passed": grade != "nicht bestanden",
         "source": "Handbuch, Informationen zur Prüfung, newer edition",
         "note": "failed parts can be repeated separately" if grade == "nicht bestanden"
         else "written and oral points are summed"})


def cmd_transfer(args):
    prof = load_profile()
    bc = prof["bootcamp"]
    if bc["status"] != "active":
        die("no active bootcamp")
    if args.words < 50 or args.errors < 0:
        die("--words must be >= 50 and --errors >= 0")
    bc["transfer"][args.label] = {"words": args.words, "errors": args.errors,
                                  "per100": round(args.errors / args.words * 100, 2),
                                  "date": today(args).isoformat()}
    save_profile(prof)
    out({"transfer": transfer_view(bc)})


def cmd_plan(args):
    prof = load_profile()
    out({**plan_info(prof, today(args)), "today": today(args).isoformat(),
         "bootcamp": prof["bootcamp"]["status"],
         "instruction": "print the matching row (t_minus / bracket) from rules/exam_countdown.md"})


def cmd_close(args):
    prof = load_profile()
    bc = prof["bootcamp"]
    if bc["status"] != "active":
        die("no active bootcamp to close")
    rep = bootcamp_report(prof, today(args))
    bc["status"] = "done"
    bc["result"] = {"closed": today(args).isoformat(), "confirmed": rep["confirmed"],
                    "goal_reached": rep["goal_reached"]}
    save_profile(prof)
    out({"closed": True, "result": bc["result"], "targets": rep["targets"]})


# ---------- task slots ----------
def slot_path(slot):
    if not SLOT_RE.match(slot):
        die(f"invalid slot {slot!r} (use a-z, 0-9, _)")
    return TASKS / f"{slot}.json"


def nonempty(v):
    return isinstance(v, str) and bool(v.strip())


def validate_task(data, slot):
    if not isinstance(data, dict) or not isinstance(data.get("module"), str):
        die("task JSON must be an object with a string 'module'")
    spec = SLOT_SPEC.get(slot)
    if spec is None:
        die(f"unknown slot {slot!r}. Valid: {sorted(SLOT_SPEC)}")
    mod = data["module"]
    if mod != spec["module"]:
        die(f"slot {slot!r} needs module {spec['module']!r}, got {mod!r}")
    if "part" in spec and (type(data.get("part")) is not int or data["part"] != spec["part"]):
        die(f"slot {slot!r} needs 'part': {spec['part']}, got {data.get('part')!r}")
    cats = load_template()["categories"]
    if mod == "schriftlich":
        tasks = data.get("tasks")
        if not isinstance(tasks, dict) or set(tasks) != {"A", "B"}:
            die("schriftlich task needs 'tasks' with exactly A and B: {text, number, leitpunkte}")
        for name, t in tasks.items():
            if not isinstance(t, dict) or not nonempty(t.get("text")):
                die(f"tasks.{name} needs a non-empty 'text'")
            if type(t.get("number")) is not int or t["number"] < 1:
                die(f"tasks.{name} needs the printed task 'number' (positive integer)")
            lp = t.get("leitpunkte")
            if not isinstance(lp, list) or len(lp) != 4 or not all(nonempty(x) for x in lp):
                die(f"tasks.{name} needs exactly 4 non-empty 'leitpunkte'")
        if tasks["A"]["number"] == tasks["B"]["number"]:
            die("tasks A and B need different printed numbers")
    elif mod == "sprechen":
        if not nonempty(data.get("card")):
            die("sprechen task needs a non-empty 'card'")
        part = data["part"]
        if part == 1 and not (isinstance(data.get("topics"), list) and len(data["topics"]) == 7
                              and all(nonempty(x) for x in data["topics"])):
            die("sprechen part 1 needs 'topics': exactly 7 non-empty topics")
        if part == 2 and not nonempty(data.get("franz_stance")):
            die("sprechen part 2 needs 'franz_stance'")
        if part == 3 and not (isinstance(data.get("leitfragen"), list) and data["leitfragen"]
                              and all(nonempty(x) for x in data["leitfragen"])):
            die("sprechen part 3 needs a non-empty 'leitfragen' list")
    else:
        items = data.get("items")
        if not isinstance(items, list) or not items:
            die("task needs a non-empty 'items' list")
        if spec.get("n") and len(items) != spec["n"]:
            die(f"slot {slot!r} needs exactly {spec['n']} items, got {len(items)}")
        if spec.get("min_n") and not spec["min_n"] <= len(items) <= spec["max_n"]:
            die(f"slot {slot!r} needs {spec['min_n']}..{spec['max_n']} items, got {len(items)}")
        for i, it in enumerate(items, 1):
            if not isinstance(it, dict) or it.get("category") not in cats:
                die(f"every item needs a valid 'category' key; bad item: {it!r}")
            if "n" in it and it["n"] != i:
                die(f"item numbers must run 1..{len(items)} in order; item {i} has n={it['n']!r}")
            if mod != "bootcamp":
                if "answer" not in it:
                    die(f"every item needs an 'answer'; bad item: {it!r}")
                if not isinstance(it["answer"], str):
                    die(f"item {i}: 'answer' must be a string")
                if it["answer"] not in spec["answers"]:
                    die(f"item {i}: answer {it['answer']!r} not allowed for {slot} "
                        f"(allowed: {sorted(spec['answers'])})")
        if spec.get("unique"):
            used = [it["answer"] for it in items if it["answer"] != "x"]
            if len(used) != len(set(used)):
                die(f"slot {slot!r}: each answer letter may be used at most once")
        if mod == "lesen" and data["part"] == 3:
            x_count = sum(it.get("answer") == "x" for it in items)
            if x_count not in (2, 3):  # 2-3 is skill design; the manuals only say not every situation has a text
                die("lesen part 3 needs exactly 2 or 3 items with answer 'x'")
        if mod in ("lesen", "sprachbausteine"):
            material = data.get("material")
            if not isinstance(material, dict):
                die(f"{mod} task needs a 'material' object for the exam text and options")
            required = (
                (("texts", "headlines") if data["part"] == 1 else
                 ("text", "options") if data["part"] == 2 else ("situations", "texts"))
                if mod == "lesen" else
                (("gap_text", "options") if data["part"] == 1 else ("gap_text", "word_box"))
            )
            for field in required:
                value = material.get(field)
                valid = bool(value.strip()) if isinstance(value, str) else bool(value) if isinstance(value, list) else False
                if not valid:
                    die(f"{mod} part {data['part']} material needs non-empty '{field}'")
            # Official counts [HB p. 34-38]: L1 5 texts/10 headlines, L3 10 situations/12 texts,
            # L2 5 MC items (a/b/c each), SB1 10 gaps x 3 options, SB2 15-word box.
            for field, count in MATERIAL_COUNTS.get(slot, {}).items():
                if len(material[field]) != count:
                    die(f"{slot} material '{field}' needs exactly {count} entries, got {len(material[field])}")
        if mod == "hoeren":
            expected_texts = {1: 6, 2: 1, 3: 5}[data["part"]]
            script = data.get("script")
            texts = script.get("texts") if isinstance(script, dict) else None
            if not isinstance(texts, list) or len(texts) != expected_texts:
                die(f"hoeren part {data['part']} 'script' needs exactly "
                    f"{expected_texts} texts")
            if not all(isinstance(text, dict) and nonempty(text.get("id")) for text in texts):
                die("hoeren 'script' texts need non-empty ids")
            text_ids = {text["id"] for text in texts}
            if len(text_ids) != len(texts):
                die("hoeren 'script' texts need distinct ids")
            for i, item in enumerate(items, 1):
                if not nonempty(item.get("text_id")) or item["text_id"] not in text_ids:
                    die(f"hoeren item {i} needs a 'text_id' from script.texts")
            if data["part"] == 1 and len({item["text_id"] for item in items}) != 5:
                die("hoeren part 1 needs statements for exactly 5 of the 6 text ids")
            if data["part"] == 3 and len({item["text_id"] for item in items}) != 5:
                die("hoeren part 3 needs 5 distinct text ids")


def default_slot(data):
    mod, part = data["module"], data.get("part")
    if mod == "lesen" and part:
        return f"lesen{part}"
    if mod == "sprachbausteine" and part:
        return f"sb{part}"
    if mod in ("hoeren", "sprechen") and part:
        return f"{mod}{part}"
    return mod


def read_task(slot):
    p = slot_path(slot)
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (ValueError, OSError) as e:
        die(f"task slot {slot!r} unreadable: {e}")


PUBLIC_TOP_LEVEL_KEYS = {
    "module", "part", "slot", "topic", "level", "day", "material", "items",
    "card", "topics", "leitfragen", "tasks", "audio", "audio_status", "graded",
    "saved", "transcript_visible",
}
PUBLIC_ITEM_KEYS = {
    "n", "statement", "format", "prompt", "options", "option", "choices",
    "text_id", "material", "situation", "text", "question",
}


def public_view(t):
    """What may be shown before grading: no key, no explanations, no Hören script, no Sprechen stance.
    Hören: tells whether audio exists; without audio the transcript stays hidden until graded."""
    if t.get("graded"):
        v = {k: t[k] for k in PUBLIC_TOP_LEVEL_KEYS if k in t}
        v["transcript_visible"] = True
        for key in ("script", "franz_stance"):
            if key in t:
                v[key] = t[key]
        return v
    v = {k: x for k, x in t.items() if k in PUBLIC_TOP_LEVEL_KEYS}
    if isinstance(t.get("items"), list):
        v["items"] = [{k: x for k, x in it.items() if k in PUBLIC_ITEM_KEYS} for it in t["items"]]
    if t.get("module") == "hoeren":
        v["audio_status"] = t.get("audio_status") or ("rendered" if t.get("audio") else "none")
        v["transcript_visible"] = False
    return v


def cmd_task(args):
    a = args.action
    if a == "save":
        try:
            raw = Path(args.file).read_text(encoding="utf-8") if args.file else sys.stdin.read()
            data = json.loads(raw)
        except (ValueError, OSError) as e:
            die(f"task JSON invalid: {e}")
        slot = args.slot or default_slot(data) if isinstance(data, dict) and "module" in data else args.slot
        validate_task(data, slot)
        data["slot"] = slot
        data["saved"] = dt.datetime.now().isoformat(timespec="seconds")
        data["graded"] = False
        write_atomic(slot_path(slot), dump(data))
        out({"saved": True, "slot": slot})
    elif a == "list":
        res = []
        for p in sorted(TASKS.glob("*.json")) if TASKS.exists() else []:
            try:
                t = json.loads(p.read_text(encoding="utf-8"))
                res.append({"slot": p.stem, "module": t.get("module"), "part": t.get("part"),
                            "saved": t.get("saved"), "graded": t.get("graded", False)})
            except ValueError:
                res.append({"slot": p.stem, "corrupt": True})
        out({"slots": res})
    elif a == "show":
        view = public_view if args.public else (lambda t: t)
        if args.slot:
            p = slot_path(args.slot)
            out(view(read_task(args.slot)) if p.exists() else {"active": None})
            return
        files = sorted(TASKS.glob("*.json"), key=lambda p: p.stat().st_mtime) if TASKS.exists() else []
        out(view(read_task(files[-1].stem)) if files else {"active": None})
    elif a == "graded":
        if not args.slot:
            die("--slot required")
        t = read_task(args.slot)
        t["graded"] = True
        t["graded_at"] = dt.datetime.now().isoformat(timespec="seconds")
        write_atomic(slot_path(args.slot), dump(t))
        out({"graded": True, "slot": args.slot})
    else:  # clear
        if args.all:
            n = 0
            for p in TASKS.glob("*.json") if TASKS.exists() else []:
                p.unlink()
                n += 1
            out({"cleared": n})
        elif args.slot:
            slot_path(args.slot).unlink(missing_ok=True)
            out({"cleared": args.slot})
        else:
            die("clear needs --slot <slot> or --all")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--date", help="override today (YYYY-MM-DD), for testing")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("wordcount"); s.add_argument("file", nargs="?"); s.set_defaults(f=cmd_wordcount)
    s = sub.add_parser("score-writing")
    for r in ("I", "II", "III"):
        s.add_argument(r)
    s.add_argument("--thema-verfehlt", action="store_true")
    s.add_argument("--situierung-verfehlt", action="store_true")
    s.add_argument("--record", action="store_true")
    s.add_argument("--recheck", action="store_true", help="score a slot that is already graded"); s.set_defaults(f=cmd_score_writing)
    s = sub.add_parser("score"); s.add_argument("module"); s.add_argument("--correct", type=int, required=True)
    s.add_argument("--record", action="store_true")
    s.add_argument("--recheck", action="store_true", help="score a slot that is already graded"); s.set_defaults(f=cmd_score)
    s = sub.add_parser("block-total", aliases=["written-block-total"])
    s.add_argument("--since", help="YYYY-MM-DD, default today"); s.set_defaults(f=cmd_block_total)
    s = sub.add_parser("errors"); s.add_argument("pairs", nargs="+"); s.set_defaults(f=cmd_errors)
    s = sub.add_parser("drill"); s.add_argument("pairs", nargs="+")
    s.add_argument("--final", action="store_true", help="mark these items as the final check (day >= 12)")
    s.set_defaults(f=cmd_drill)
    s = sub.add_parser("bootcamp-start"); s.add_argument("--force", action="store_true")
    s.set_defaults(f=cmd_start)
    s = sub.add_parser("status"); s.set_defaults(f=cmd_status)
    s = sub.add_parser("transfer"); s.add_argument("label", choices=["first", "last"])
    s.add_argument("--words", type=int, required=True); s.add_argument("--errors", type=int, required=True)
    s.set_defaults(f=cmd_transfer)
    s = sub.add_parser("exam-date"); s.add_argument("action", choices=["set", "show"])
    s.add_argument("date_value", nargs="?"); s.set_defaults(f=cmd_exam_date)
    s = sub.add_parser("plan"); s.set_defaults(f=cmd_plan)
    s = sub.add_parser("exam-result"); s.add_argument("--written", type=float, required=True)
    s.add_argument("--oral", type=float, required=True); s.set_defaults(f=cmd_exam_result)
    s = sub.add_parser("score-speaking"); s.add_argument("part", choices=["1", "2", "3"])
    for r in ("I", "II", "III"):
        s.add_argument(r)
    s.add_argument("--record", action="store_true")
    s.add_argument("--recheck", action="store_true", help="score a slot that is already graded"); s.set_defaults(f=cmd_speaking)
    s = sub.add_parser("bootcamp-close"); s.set_defaults(f=cmd_close)
    s = sub.add_parser("task")
    s.add_argument("action", choices=["save", "show", "list", "graded", "clear"])
    s.add_argument("file", nargs="?"); s.add_argument("--slot"); s.add_argument("--all", action="store_true")
    s.add_argument("--public", action="store_true", help="show: hide key, why, script and stance until graded")
    s.set_defaults(f=cmd_task)

    args = p.parse_args()
    args.f(args)


if __name__ == "__main__":
    main()
