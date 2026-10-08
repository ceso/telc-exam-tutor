import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parent.parent / "tools" / "tutor.py"
TTS = TOOL.with_name("tts.py")
SCRATCH = Path(os.environ.get("TELC_TEST_DIR", Path(__file__).resolve().parent / "_scratch"))


# All dates below are arbitrary fixtures, not real exam dates.
class Base(unittest.TestCase):
    def setUp(self):
        self.home = SCRATCH / self.id().split(".")[-1]
        shutil.rmtree(self.home, ignore_errors=True)
        self.home.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.home, ignore_errors=True)
        try:
            SCRATCH.rmdir()
        except OSError:
            pass

    def run_tool(self, *args, date=None, stdin=None, ok=True):
        cmd = [sys.executable, str(TOOL)] + (["--date", date] if date else []) + list(args)
        r = subprocess.run(cmd, input=stdin, capture_output=True, text=True,
                           env={**os.environ, "TELC_HOME": str(self.home)})
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
            return json.loads(r.stdout)
        self.assertNotEqual(r.returncode, 0, r.stdout)
        return r.stderr

    def day(self, n, start="2030-03-01"):
        return (dt.date.fromisoformat(start) + dt.timedelta(days=n - 1)).isoformat()

    def targets(self, date="2030-03-01"):
        return self.run_tool("bootcamp-start", date=date)["bootcamp"]["targets"]


class Mastery(Base):
    def test_cram_in_one_day_is_not_mastered(self):  # C1
        t = self.targets()
        k = t[0]
        for i in range(10):
            self.run_tool("drill", f"{k}=1", date=self.day(1))
        row = [r for r in self.run_tool("status", date=self.day(1))["targets"] if r["key"] == k][0]
        self.assertNotEqual(row["band"], "mastered")

    def test_spread_over_dates_is_mastered(self):
        k = self.targets()[0]
        for d in (1, 1, 3, 3, 5, 5, 7, 7, 9, 9):
            self.run_tool("drill", f"{k}=1", date=self.day(d))
        row = [r for r in self.run_tool("status", date=self.day(9))["targets"] if r["key"] == k][0]
        self.assertEqual(row["band"], "mastered")

    def test_old_days_outside_window_do_not_count(self):  # C1
        k = self.targets()[0]
        for d in (1, 2, 3):
            self.run_tool("drill", f"{k}=0", date=self.day(d))
        for _ in range(10):
            self.run_tool("drill", f"{k}=1", date=self.day(9))
        row = [r for r in self.run_tool("status", date=self.day(9))["targets"] if r["key"] == k][0]
        self.assertNotEqual(row["band"], "mastered")

    def test_legacy_profile_migrates(self):
        self.targets()
        p = self.home / "profile.json"
        prof = json.loads(p.read_text())
        prof["categories"]["verb_position"] = {"errors_total": 3, "weight": 3.0,
                                                "drill": [1, 1, 0], "days": ["2030-02-22"]}
        p.write_text(json.dumps(prof))
        st = self.run_tool("status", date=self.day(2))
        self.assertIn("targets", st)


class Start(Base):
    def test_start_resets_and_refuses(self):  # C2
        t = self.targets()
        self.run_tool("drill", f"{t[0]}=1", date=self.day(1))
        err = self.run_tool("bootcamp-start", date=self.day(2), ok=False)
        self.assertIn("already active", err)
        self.run_tool("bootcamp-start", "--force", date=self.day(2))
        st = self.run_tool("status", date=self.day(2))
        self.assertTrue(all(r["attempts"] == 0 for r in st["targets"]))

    def test_exam_date_scales_length(self):
        self.run_tool("exam-date", "set", "2030-03-22", date="2030-03-01")
        r = self.run_tool("bootcamp-start", date="2030-03-01")
        self.assertEqual(r["length_days"], 14)
        self.assertEqual(r["days_left"], 21)
        self.run_tool("bootcamp-start", "--force", date="2030-03-13")
        r = self.run_tool("status", date="2030-03-13")
        self.assertEqual(r["of"], 7)
        self.assertEqual(r["min_span_days"], 3)
        self.assertEqual(r["plan_phase"], "bootcamp")


def lesen_task(part, answers, cat="lesen_headline_trap"):
    material = (
        {"texts": [f"Text {i}" for i in range(1, 6)], "headlines": [f"Überschrift {i}" for i in range(1, 11)]}
        if part == 1 else
        {"text": "Ein langer Entscheidungstext.", "options": [["a", "b", "c"]] * 5}
        if part == 2 else
        {"situations": [f"Situation {i}" for i in range(1, 11)], "texts": [f"Text {i}" for i in range(1, 13)]}
    )
    return {"level": "b2", "module": "lesen", "part": part, "material": material,
            "items": [{"n": i, "answer": a, "category": cat} for i, a in enumerate(answers, 1)]}


def schriftlich_task(**over):
    t = {"text": "Anzeige ...", "number": 1, "leitpunkte": ["a", "b", "c", "d"]}
    return {"level": "b2", "module": "schriftlich",
            "tasks": {"A": {**t, **over}, "B": {**t, "number": 2}}}


def hoeren_task(part=1, n=5, with_script=True):
    d = {"level": "b2", "module": "hoeren", "part": part,
         "items": [{"n": i, "text_id": f"h{part}_n{i if part != 2 else 1}",
                    "answer": "r", "category": "hoeren_paraphrase_trap", "why": "geheim"}
                   for i in range(1, n + 1)]}
    if with_script:
        text_count = {1: 6, 2: 1, 3: 5}[part]
        d["script"] = {"texts": [
            {"id": f"h{part}_n{i}", "voice": "katja", "text": "Geheimes Transkript"}
            for i in range(1, text_count + 1)
        ]}
    return d


class Tasks(Base):
    def save(self, slot, data=None, ok=True):
        data = data or lesen_task(int(slot[-1]), "abcde" if slot != "lesen3" else "abcdefghxx")
        return self.run_tool("task", "save", "--slot", slot, stdin=json.dumps(data), ok=ok)

    def test_slots_are_independent(self):  # C3
        self.save("lesen1")
        self.save("lesen2", lesen_task(2, "abcab"))
        self.assertEqual(len(self.run_tool("task", "list")["slots"]), 2)
        self.run_tool("task", "graded", "--slot", "lesen1")
        self.assertTrue(self.run_tool("task", "show", "--slot", "lesen1")["graded"])
        self.assertFalse(self.run_tool("task", "show", "--slot", "lesen2")["graded"])
        self.run_tool("task", "clear", "--slot", "lesen1")
        self.assertEqual(self.run_tool("task", "show", "--slot", "lesen1"), {"active": None})

    def test_bad_task_rejected(self):
        self.run_tool("task", "save", stdin="{nope", ok=False)
        self.run_tool("task", "save", stdin=json.dumps({"module": "lesen", "items": [{"category": "zzz"}]}), ok=False)
        self.run_tool("task", "save", "--slot", "../x", stdin="{}", ok=False)

    def test_item_counts(self):
        self.save("lesen1", lesen_task(1, "abcd"), ok=False)
        self.save("lesen1", lesen_task(1, "abcdef"), ok=False)
        self.save("lesen3", lesen_task(3, "abcde"), ok=False)
        self.save("sb1", {"level": "b2", "module": "sprachbausteine", "part": 1,
                          "items": [{"answer": "a", "category": "case_prepositions"}] * 9}, ok=False)
        self.save("hoeren1", hoeren_task(1, 6), ok=False)
        self.save("hoeren2", hoeren_task(2, 10))
        bootcamp = {"level": "b2", "module": "bootcamp",
                    "items": [{"n": i, "category": "verb_position"} for i in range(1, 15)]}
        self.save("bootcamp", {"level": "b2", "module": "bootcamp", "items": []}, ok=False)
        self.save("bootcamp", {**bootcamp, "items": bootcamp["items"] + [
            {"n": 15, "category": "verb_position"},
        ] * 2}, ok=False)
        bootcamp["items"].append({"n": 15, "category": "verb_position"})
        self.save("bootcamp", bootcamp)

    def test_answer_alphabets(self):
        self.save("lesen1", lesen_task(1, "abcdk"), ok=False)      # k outside a-j
        self.save("lesen1", lesen_task(1, "abcdj"))
        self.save("lesen2", lesen_task(2, "abcad"), ok=False)      # d outside a-c
        self.save("lesen2", lesen_task(2, "AB" "cab"), ok=False)   # case matters
        self.save("lesen3", lesen_task(3, "abcdefgh" + "xx"))           # x allowed
        self.save("lesen3", lesen_task(3, "abcdefghim"), ok=False)  # m outside a-l
        self.save("lesen3", lesen_task(3, "aacdefghix"), ok=False)  # text used twice
        self.save("lesen3", lesen_task(3, "xxcdefghij"))           # x may repeat
        bad = hoeren_task(1, 5)
        bad["items"][0]["answer"] = "a"
        self.save("hoeren1", bad, ok=False)
        bad["items"][0]["answer"] = "f"
        self.save("hoeren1", bad)

    def test_lesen1_answers_must_be_unique(self):
        self.save("lesen1", lesen_task(1, "aabcd"), ok=False)

    def test_part_matches_slot(self):
        self.save("lesen2", lesen_task(1, "abcab"), ok=False)
        self.save("lesen2", {**lesen_task(2, "abcab"), "module": "hoeren"}, ok=False)
        self.save("lesen2", {**lesen_task(2, "abcab"), "part": "2"}, ok=False)
        self.save("mystery", lesen_task(1, "abcde"), ok=False)
        d = lesen_task(2, "abcab")  # default slot derives from module/part
        self.assertEqual(self.run_tool("task", "save", stdin=json.dumps(d))["slot"], "lesen2")

    def test_schriftlich_schema(self):
        self.save("schriftlich", schriftlich_task())
        self.save("schriftlich", schriftlich_task(leitpunkte=["a", "b", "c"]), ok=False)
        self.save("schriftlich", schriftlich_task(leitpunkte=["a", "b", "c", "d", "e"]), ok=False)
        self.save("schriftlich", schriftlich_task(leitpunkte=["a", "b", "c", " "]), ok=False)
        self.save("schriftlich", schriftlich_task(text=" "), ok=False)
        self.save("schriftlich", schriftlich_task(number=2), ok=False)  # same number twice
        only_a = schriftlich_task()
        del only_a["tasks"]["B"]
        self.save("schriftlich", only_a, ok=False)

    def test_sprechen_schema(self):
        base = {"level": "b2", "module": "sprechen", "card": "Karte"}
        self.save("sprechen1", {**base, "part": 1, "topics": [f"t{i}" for i in range(7)]})
        self.save("sprechen1", {**base, "part": 1, "topics": ["a"] * 6}, ok=False)
        self.save("sprechen2", {**base, "part": 2}, ok=False)
        self.save("sprechen2", {**base, "part": 2, "franz_stance": "dagegen"})
        self.save("sprechen3", {**base, "part": 3}, ok=False)
        self.save("sprechen3", {**base, "part": 3, "leitfragen": ["Was?", "Wer?"]})
        self.save("sprechen3", {**base, "part": 3, "card": "", "leitfragen": ["Was?"]}, ok=False)
        self.save("sprechen3", {**base, "part": 2, "franz_stance": "x"}, ok=False)  # part vs slot
        self.save("sprechen3", {**base, "part": 4, "leitfragen": ["Was?"]}, ok=False)

    def test_public_view_hides_key_until_graded(self):
        self.save("hoeren1", hoeren_task(1))
        pub = self.run_tool("task", "show", "--slot", "hoeren1", "--public")
        self.assertNotIn("script", pub)
        self.assertNotIn("Geheim", json.dumps(pub))
        self.assertTrue(all("answer" not in i and "why" not in i for i in pub["items"]))
        self.assertEqual(pub["audio_status"], "none")  # no-audio fallback
        self.assertFalse(pub["transcript_visible"])
        self.run_tool("task", "graded", "--slot", "hoeren1")
        pub = self.run_tool("task", "show", "--slot", "hoeren1", "--public")
        self.assertTrue(pub["transcript_visible"])
        self.assertIn("script", pub)

    def test_public_view_allows_only_known_top_level_keys(self):
        task = hoeren_task(1)
        task.update({"transcript": "secret", "answers": ["r"], "key": "secret"})
        self.save("hoeren1", task)
        pub = self.run_tool("task", "show", "--slot", "hoeren1", "--public")
        self.assertNotIn("transcript", pub)
        self.assertNotIn("answers", pub)
        self.assertNotIn("key", pub)

    def test_bootcamp_public_view_hides_accept(self):
        task = {"level": "b2", "module": "bootcamp",
                "items": [{"n": 1, "format": "choose", "prompt": "…",
                           "answer": "b", "accept": ["b", "B"], "category": "verb_position",
                           "why": "geheim"}]}
        self.save("bootcamp", task)
        pub = self.run_tool("task", "show", "--slot", "bootcamp", "--public")
        self.assertEqual(pub["items"], [{"n": 1, "format": "choose", "prompt": "…"}])
        self.assertNotIn("accept", json.dumps(pub))

    def test_six_item_final_batch_is_valid(self):
        task = {"level": "b2", "module": "bootcamp",
                "items": [{"n": i, "format": "choose", "prompt": f"p{i}",
                           "answer": "b", "accept": ["b"], "category": "verb_position"}
                          for i in range(1, 7)]}
        self.save("bootcamp", task)

    def test_material_is_required_and_public(self):
        task = lesen_task(1, "abcde")
        task.pop("material")
        self.save("lesen1", task, ok=False)
        task = lesen_task(1, "abcde")
        pub = self.run_tool("task", "save", "--slot", "lesen1", stdin=json.dumps(task))
        self.assertTrue(pub["saved"])
        shown = self.run_tool("task", "show", "--slot", "lesen1", "--public")
        self.assertIn("material", shown)

    def test_material_counts_follow_the_handbuch(self):
        task = lesen_task(1, "abcde")
        task["material"]["headlines"] = task["material"]["headlines"][:9]
        self.save("lesen1", task, ok=False)
        task = lesen_task(3, "abcdefghxx")
        task["material"]["texts"] = task["material"]["texts"][:10]
        self.save("lesen3", task, ok=False)
        sb2 = {"level": "b2", "module": "sprachbausteine", "part": 2,
               "material": {"gap_text": "Text", "word_box": [f"w{i}" for i in range(14)]},
               "items": [{"n": i, "answer": "abcdefghij"[i - 1], "category": "word_choice_collocation"}
                         for i in range(1, 11)]}
        self.save("sb2", sb2, ok=False)
        sb2["material"]["word_box"].append("w14")
        self.save("sb2", sb2)

    def test_hoeren_text_ids_match_script(self):
        task = hoeren_task(1)
        task["items"][0]["text_id"] = "missing"
        self.save("hoeren1", task, ok=False)

    def test_hoeren_part_2_has_one_text(self):
        task = hoeren_task(2, 10)
        task["script"]["texts"].append({"id": "extra", "text": "Nebenhörtext"})
        self.save("hoeren2", task, ok=False)

    def test_hoeren_part_3_needs_distinct_text_ids(self):
        task = hoeren_task(3, 5)
        task["items"][1]["text_id"] = task["items"][0]["text_id"]
        self.save("hoeren3", task, ok=False)

    def test_non_string_answer_is_rejected_cleanly(self):
        task = lesen_task(1, "abcde")
        task["items"][0]["answer"] = ["a"]
        err = self.save("lesen1", task, ok=False)
        self.assertIn("'answer' must be a string", err)

    def test_public_view_preserves_failed_audio_status(self):
        task = hoeren_task(1)
        task["audio_status"] = "failed"
        self.save("hoeren1", task)
        pub = self.run_tool("task", "show", "--slot", "hoeren1", "--public")
        self.assertEqual(pub["audio_status"], "failed")

    def test_missing_hoeren_script_rejected(self):
        self.save("hoeren1", hoeren_task(1, with_script=False), ok=False)

    def test_no_audio_score_is_not_recorded(self):
        self.save("hoeren1", hoeren_task(1))
        self.run_tool("score", "hoeren1", "--correct", "3")
        self.assertEqual(self.run_tool("status")["recent_scores"], [])


class Scores(Base):
    def test_block_total(self):  # C3
        for m, c in (("lesen1", 5), ("lesen2", 4), ("lesen3", 8), ("sb1", 7), ("sb2", 6)):
            self.run_tool("score", m, "--correct", str(c), "--record", date="2030-03-03")
        r = self.run_tool("block-total", date="2030-03-03")
        self.assertEqual(r["missing"], ["schriftlich"])
        self.run_tool("score-writing", "B", "B", "C", "--record", date="2030-03-03")
        r = self.run_tool("block-total", date="2030-03-03")
        self.assertTrue(r["complete"])
        self.assertEqual(r["total"], 25 + 20 + 20 + 10.5 + 9 + 21)
        self.assertEqual(r["block_max"], 150)
        self.assertIn("on_track_for_block_60pct", r)

    def test_block_total_official_written_pass_135(self):
        d = "2030-03-03"
        for m, c in (("lesen1", 5), ("lesen2", 5), ("lesen3", 10), ("sb1", 10), ("sb2", 10)):
            self.run_tool("score", m, "--correct", str(c), "--record", date=d)
        self.run_tool("score-writing", "A", "A", "A", "--record", date=d)
        r = self.run_tool("block-total", date=d)
        self.assertNotIn("written_total_225", r)
        for m, c in (("hoeren1", 5), ("hoeren2", 10), ("hoeren3", 5)):
            self.run_tool("score", m, "--correct", str(c), "--record", date=d)
        r = self.run_tool("block-total", date=d)
        self.assertEqual(r["written_total_225"], 225)
        self.assertTrue(r["written_passed_135"])

    def test_status_recent_and_averages(self):  # M8
        self.run_tool("score", "lesen1", "--correct", "3", "--record")
        st = self.run_tool("status")
        self.assertEqual(len(st["recent_scores"]), 1)
        self.assertEqual(st["module_averages"]["lesen1"]["avg_pct"], 60)


class Recording(Base):
    def test_no_double_recording(self):
        self.run_tool("task", "save", "--slot", "lesen1", stdin=json.dumps(lesen_task(1, "abcde")))
        self.run_tool("score", "lesen1", "--correct", "3", "--record")
        self.run_tool("task", "graded", "--slot", "lesen1")
        self.run_tool("score", "lesen1", "--correct", "4", "--record", ok=False)
        self.run_tool("score", "lesen1", "--correct", "4", ok=False)
        self.assertEqual(len(self.run_tool("status")["recent_scores"]), 1)
        self.run_tool("score", "lesen1", "--correct", "4", "--record", "--recheck")
        st = self.run_tool("status")
        self.assertTrue(st["recent_scores"][-1]["recheck"])

    def test_no_double_recording_writing_and_speaking(self):
        self.run_tool("task", "save", "--slot", "schriftlich", stdin=json.dumps(schriftlich_task()))
        self.run_tool("task", "graded", "--slot", "schriftlich")
        self.run_tool("score-writing", "A", "B", "C", "--record", ok=False)
        self.run_tool("score-writing", "A", "B", "C", "--record", "--recheck")
        sp = {"level": "b2", "module": "sprechen", "part": 2, "card": "k", "franz_stance": "s"}
        self.run_tool("task", "save", "--slot", "sprechen2", stdin=json.dumps(sp))
        self.run_tool("task", "graded", "--slot", "sprechen2")
        self.run_tool("score-speaking", "2", "A", "B", "C", "--record", ok=False)
        self.run_tool("score-speaking", "2", "A", "B", "C", "--record", "--recheck")

    def test_score_without_saved_task_still_works(self):
        self.run_tool("score", "sb1", "--correct", "10", "--record")

    def test_boundaries(self):
        self.assertEqual(self.run_tool("score", "lesen3", "--correct", "10")["score"], 25)
        self.assertEqual(self.run_tool("score", "lesen3", "--correct", "0")["score"], 0)
        self.run_tool("score", "lesen3", "--correct", "11", ok=False)
        self.run_tool("score", "lesen3", "--correct", "-1", ok=False)
        self.run_tool("score", "hoeren2", "--correct", "11", ok=False)
        self.run_tool("score", "nope", "--correct", "1", ok=False)
        self.assertEqual(self.run_tool("score-writing", "A", "A", "A")["total"], 45)
        self.assertEqual(self.run_tool("score-writing", "D", "D", "D")["total"], 0)
        self.assertEqual(self.run_tool("score-writing", "a", "b", "c")["total"], 27)
        self.run_tool("score-writing", "E", "A", "A", ok=False)
        self.assertEqual(self.run_tool("score-writing", "A", "A", "A", "--thema-verfehlt")["total"], 0)
        r = self.run_tool("score-writing", "A", "A", "A", "--situierung-verfehlt")
        self.assertEqual(r["letters"]["I"], "D")
        self.assertEqual(r["total"], 30)

    def test_speaking_estimate_is_separate(self):
        self.run_tool("score", "lesen1", "--correct", "5", "--record")
        r = self.run_tool("score-speaking", "1", "A", "A", "A", "--record")
        self.assertEqual(r["estimate_points"], 21)
        self.assertEqual(r["of"], 21)
        self.assertIn("excluded", r["aussprache_intonation"])
        self.assertEqual(self.run_tool("score-speaking", "1", "B", "C", "D")["estimate_points"], 8)
        st = self.run_tool("status")
        self.assertEqual([x["module"] for x in st["recent_scores"]], ["lesen1"])
        self.assertEqual(list(st["module_averages"]), ["lesen1"])
        self.assertEqual(st["speaking_estimates"]["recent"][0]["module"], "sprechen1")
        self.assertEqual(st["speaking_estimates"]["averages"]["sprechen1"]["avg_pct"], 100)
        prof = json.loads((self.home / "profile.json").read_text())
        self.assertTrue(all(x["module"] != "sprechen1" for x in prof["submissions"]))
        self.assertIn("NOT an exam score", st["speaking_estimates"]["note"])

    def test_exam_result_bands_and_part_rule(self):
        r = self.run_tool("exam-result", "--written", "200", "--oral", "70")
        self.assertEqual((r["total"], r["grade"]), (270, "sehr gut"))
        self.assertEqual(self.run_tool("exam-result", "--written", "170", "--oral", "70")["grade"], "gut")
        self.assertEqual(self.run_tool("exam-result", "--written", "199.5", "--oral", "70")["grade"], "gut")  # 269,5
        self.assertEqual(self.run_tool("exam-result", "--written", "169.5", "--oral", "70")["grade"], "befriedigend")  # 239,5
        self.assertEqual(self.run_tool("exam-result", "--written", "135", "--oral", "45")["grade"], "ausreichend")
        r = self.run_tool("exam-result", "--written", "225", "--oral", "44.5")
        self.assertEqual(r["grade"], "nicht bestanden")
        self.assertFalse(r["oral_ok"])
        self.run_tool("exam-result", "--written", "226", "--oral", "10", ok=False)

    def test_legacy_speaking_in_submissions_excluded(self):
        self.run_tool("status")
        p = self.home / "profile.json"
        prof = json.loads(p.read_text())
        prof["submissions"].append({"date": "2030-01-01", "module": "sprechen1", "score": 6, "max": 9,
                                    "estimate": True})
        p.write_text(json.dumps(prof))
        st = self.run_tool("status")
        self.assertEqual(st["recent_scores"], [])
        self.assertEqual(st["module_averages"], {})
        self.assertEqual(st["speaking_estimates"]["averages"]["sprechen1"]["n"], 1)

    def test_block_total_uses_latest_and_ignores_estimates(self):
        d = "2030-03-03"
        self.run_tool("score", "lesen1", "--correct", "1", "--record", date=d)
        self.run_tool("score", "lesen1", "--correct", "5", "--record", "--recheck", date=d)
        self.run_tool("score-speaking", "1", "A", "A", "A", "--record", date=d)
        self.run_tool("score", "hoeren1", "--correct", "5", "--record", date=d)
        r = self.run_tool("block-total", date=d)
        self.assertEqual(r["parts"], {"lesen1": 25})
        self.assertEqual(r["total"], 25)
        self.assertIn("WITHOUT Hören", r["scope"])
        self.assertEqual(r["hoeren_separate"]["total"], 25)
        self.assertFalse(r["hoeren_separate"]["complete"])
        self.assertEqual(self.run_tool("written-block-total", date=d)["total"], 25)

    def test_block_total_since_and_threshold_edge(self):
        for m, c in (("lesen1", 5), ("lesen2", 5), ("lesen3", 10), ("sb1", 10), ("sb2", 10)):
            self.run_tool("score", m, "--correct", str(c), "--record", date="2030-03-01")
        self.run_tool("score-writing", "A", "A", "A", "--record", date="2030-03-01")
        r = self.run_tool("block-total", "--since", "2030-03-01", date="2030-03-05")
        self.assertEqual(r["total"], 150)
        self.assertTrue(r["on_track_for_block_60pct"])
        self.assertEqual(r["points_to_90"], 0)
        r = self.run_tool("block-total", date="2030-03-05")  # default since = today: nothing yet
        self.assertEqual(r["total"], 0)
        self.assertFalse(r["complete"])
        self.run_tool("block-total", "--since", "03/01/2030", ok=False)


class Tts(Base):
    def tts(self, *args, stdin=None, ok=True):
        r = subprocess.run([sys.executable, str(TTS)] + list(args), input=stdin, capture_output=True,
                           text=True, env={**os.environ, "TELC_HOME": str(self.home)})
        if ok:
            self.assertEqual(r.returncode, 0, r.stderr)
            return json.loads(r.stdout)
        self.assertNotEqual(r.returncode, 0)
        return r.stderr

    def configure(self, code):
        cmd = f"{sys.executable} -c '{code}' {{text}} {{out}}"
        self.tts("config", "set", "--provider", "command", "--command", cmd)

    SCRIPT = json.dumps({"texts": [{"id": "h1_n1", "voice": "katja", "text": "Eins"},
                                   {"id": "h1_n2", "voice": "conrad", "text": "Zwei"}]})

    def test_render_success_records_paths_in_task(self):
        self.run_tool("task", "save", "--slot", "hoeren1", stdin=json.dumps(hoeren_task(1)))
        self.configure("import sys; open(sys.argv[2], \"wb\").write(b\"mp3\")")
        r = self.tts("render", "-", "--slot", "hoeren1", stdin=self.SCRIPT)
        self.assertEqual(len(r["files"]), 2)
        pub = self.run_tool("task", "show", "--slot", "hoeren1", "--public")
        self.assertEqual(pub["audio_status"], "rendered")
        self.assertEqual([a["path"] for a in pub["audio"]], ["audio/h1_n1.mp3", "audio/h1_n2.mp3"])
        self.assertTrue(all((self.home / a["path"]).exists() for a in pub["audio"]))
        self.assertNotIn("script", pub)  # transcript still hidden

    def test_render_defaults_to_saved_task_script(self):
        self.run_tool("task", "save", "--slot", "hoeren1", stdin=json.dumps(hoeren_task(1)))
        self.configure("import sys; open(sys.argv[2], \"wb\").write(b\"mp3\")")
        r = self.tts("render", "--slot", "hoeren1")
        self.assertEqual(len(r["files"]), 6)

    def test_render_failure_preserves_failed_audio_status(self):
        self.run_tool("task", "save", "--slot", "hoeren1", stdin=json.dumps(hoeren_task(1)))
        self.configure("import sys; sys.exit(3)")
        err = self.tts("render", "-", "--slot", "hoeren1", stdin=self.SCRIPT, ok=False)
        self.assertIn("TTS failed", err)
        pub = self.run_tool("task", "show", "--slot", "hoeren1", "--public")
        self.assertEqual(pub["audio_status"], "failed")
        self.assertEqual(pub["audio"], [])
        self.assertFalse(pub["transcript_visible"])
        self.assertNotIn("Geheim", json.dumps(pub))

    def test_render_needs_saved_task(self):
        self.configure("import sys; open(sys.argv[2], \"wb\").write(b\"x\")")
        self.tts("render", "-", "--slot", "hoeren1", stdin=self.SCRIPT, ok=False)
        self.tts("render", "-", "--slot", "../x", stdin=self.SCRIPT, ok=False)


class ExamDate(Base):
    def test_edges(self):
        self.run_tool("exam-date", "set", "2030-03-01", date="2030-03-02", ok=False)  # past
        r = self.run_tool("exam-date", "set", "2030-03-01", date="2030-03-01")  # today allowed
        self.assertEqual((r["days_left"], r["plan_phase"]), (0, "exam_day"))
        phases = {1: "rest_and_checklist", 2: "light_review_only", 3: "timed_mocks_alternating_with_micro_session",
                  7: "timed_mocks_alternating_with_micro_session"}
        for left, ph in phases.items():
            d = (dt.date(2030, 3, 1) - dt.timedelta(days=left)).isoformat()
            self.assertEqual(self.run_tool("plan", date=d)["plan_phase"], ph)
        r = self.run_tool("plan", date="2030-03-05")
        self.assertEqual(r["plan_phase"], "exam_passed")
        self.assertTrue(r["needs_exam_date"])
        self.run_tool("exam-date", "set", "2030-13-01", ok=False)
        self.run_tool("exam-date", "set", ok=False)

    def test_unset(self):
        r = self.run_tool("plan")
        self.assertTrue(r["needs_exam_date"])
        self.assertEqual(r["plan_phase"], "no_exam_date")

    def test_exam_date_show_rejects_trailing_args(self):
        self.run_tool("exam-date", "show", "unexpected", ok=False)

    def test_short_bootcamp_uses_three_targets(self):
        self.run_tool("exam-date", "set", "2030-03-12", date="2030-03-01")
        result = self.run_tool("bootcamp-start", date="2030-03-01")
        self.assertEqual(result["days_left"], 11)
        self.assertEqual(len(result["bootcamp"]["targets"]), 3)

    def test_bootcamp_length_edges(self):
        self.run_tool("exam-date", "set", "2030-03-30", date="2030-03-01")
        self.assertEqual(self.run_tool("bootcamp-start", date="2030-03-01")["length_days"], 14)  # 29 left
        self.run_tool("bootcamp-start", "--force", date="2030-03-24")  # 6 left: shortest bootcamp + warning
        st = self.run_tool("status", date="2030-03-24")
        self.assertEqual(st["of"], 7)
        self.assertEqual(st["plan_phase"], "timed_mocks_alternating_with_micro_session")


class Validation(Base):
    def test_inputs(self):  # M11
        self.run_tool("errors", "verb_position=-1", ok=False)
        self.run_tool("errors", "verb_position=abc", ok=False)
        self.run_tool("errors", "nonsense=1", ok=False)
        r = self.run_tool("errors", "verb_position=99")
        self.assertEqual(r["recorded"]["verb_position"], 5)
        self.run_tool("status", date="2026-13-45", ok=False)
        self.targets()
        self.run_tool("drill", "verb_position=abc", ok=False)
        self.run_tool("drill", "verb_position=7", ok=False)

    def test_corrupt_profile(self):
        (self.home / "profile.json").write_text("{broken")
        self.assertIn("corrupt", self.run_tool("status", ok=False))
        self.assertEqual((self.home / "profile.json").read_text(), "{broken")

    def test_final_check_rules(self):  # M10
        t = self.targets()
        self.run_tool("drill", f"{t[0]}=1", "--final", date=self.day(3), ok=False)
        self.run_tool("drill", f"{t[0]}=1", "--final", date=self.day(12))

    def test_expired_status(self):
        self.targets()
        st = self.run_tool("status", date=self.day(16))
        self.assertTrue(st["expired"])
        self.assertIn("bootcamp-close", st["next_step"])

    def test_allocation_sums_to_15(self):
        self.targets()
        st = self.run_tool("status", date=self.day(1))
        self.assertEqual(sum(st["todays_allocation"].values()), 15)

    def test_diagnostic_seeds_weight(self):
        t = self.targets()
        for ok in (0, 0, 1):
            self.run_tool("drill", f"{t[0]}={ok}", date=self.day(1))
        row = [r for r in self.run_tool("status", date=self.day(1))["targets"] if r["key"] == t[0]][0]
        self.assertEqual(row["weight"], 4.0)

    def test_final_batch_can_be_partial(self):
        task = {"level": "b2", "module": "bootcamp",
                "items": [{"n": i, "format": "choose", "prompt": f"p{i}",
                           "answer": "b", "accept": ["b"], "category": "verb_position"}
                          for i in range(1, 7)]}
        self.run_tool("task", "save", "--slot", "bootcamp", stdin=json.dumps(task))
        self.assertEqual(len(self.run_tool("task", "show", "--slot", "bootcamp")["items"]), 6)


if __name__ == "__main__":
    unittest.main()
