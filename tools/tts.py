#!/usr/bin/env python3
"""Optional text-to-speech renderer for the Hören / Sprechen modules (stdlib only).

  uv run $SKILL_DIR/tools/tts.py config show
  uv run $SKILL_DIR/tools/tts.py config set --provider edge
  uv run $SKILL_DIR/tools/tts.py config set --provider command --command 'my-tts --text {text} --out {out}'
  uv run $SKILL_DIR/tools/tts.py render [script.json|-] [--outdir DIR] [--slot hoeren1]
      (omit the script to use the saved task script; "-" = stdin)
  uv run $SKILL_DIR/tools/tts.py say "Guten Tag" --voice katja --out DIR/x.mp3
  uv run $SKILL_DIR/tools/tts.py check

Providers
  edge     runs `uv run --with edge-tts edge-tts ...` (needs uv + internet; Microsoft neural voices).
  command  any shell template with {text} {out} [{voice}] placeholders; values are shell-quoted for you.
Script JSON: {"texts": [{"id": "n1", "voice": "katja", "text": "..."},
                         {"id": "iv", "turns": [{"voice": "katja", "text": "..."}, {"voice": "conrad", "text": "..."}]}]}
One mp3 per text (turns are rendered separately and byte-concatenated). Exit status 2 + {"error"} on failure.
With --slot the result is written into the saved task $TELC_HOME/tasks/<slot>.json as
"audio": [{"id", "path"}] (paths relative to $TELC_HOME when inside it) and "audio_status": "rendered";
if rendering fails the task gets "audio": [] and "audio_status": "failed" (no-audio fallback: transcript
stays hidden until the task is graded).
Config lives in $TELC_HOME/tts.json. Audio is synthetic: it does NOT reproduce telc audio.
"""
import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HOME = Path(os.environ.get("TELC_HOME", Path.home() / ".config" / "telc-tutor"))
CONFIG = HOME / "tts.json"
VOICES = {"katja": "de-DE-KatjaNeural", "conrad": "de-DE-ConradNeural",
          "amala": "de-DE-AmalaNeural", "killian": "de-DE-KillianNeural"}
DEFAULT = {"provider": "edge", "command": "", "rate": "+0%"}


def die(msg):
    print(json.dumps({"error": msg}, ensure_ascii=False), file=sys.stderr)
    sys.exit(2)


def load_config():
    if not CONFIG.exists():
        return dict(DEFAULT)
    try:
        cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
        if not isinstance(cfg, dict):
            raise ValueError("not an object")
    except (ValueError, OSError) as e:
        die(f"{CONFIG} is corrupt ({e}); delete it or run `config set` again")
    return {**DEFAULT, **cfg}


def save_config(cfg):
    HOME.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=HOME, prefix="tts.json.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(cfg, fh, indent=2)
    os.replace(tmp, CONFIG)


def voice_name(v):
    return VOICES.get((v or "katja").lower(), v)


def synth(cfg, text, voice, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if cfg["provider"] == "edge":
        if not shutil.which("uv"):
            die("provider 'edge' needs uv on PATH (or switch to provider 'command')")
        cmd = ["uv", "run", "--quiet", "--with", "edge-tts", "edge-tts", "--voice", voice_name(voice),
               f"--rate={cfg['rate']}", "--text", text, "--write-media", str(out)]
        r = subprocess.run(cmd, capture_output=True, text=True)
    elif cfg["provider"] == "command":
        tpl = cfg.get("command", "")
        if "{text}" not in tpl or "{out}" not in tpl:
            die("provider 'command' needs a template containing {text} and {out}")
        full = tpl.format(text=shlex.quote(text), out=shlex.quote(str(out)),
                          voice=shlex.quote(voice_name(voice)))
        r = subprocess.run(full, shell=True, capture_output=True, text=True)
    else:
        die(f"unknown provider {cfg['provider']!r}")
    if r.returncode != 0 or not out.exists() or out.stat().st_size == 0:
        die(f"TTS failed ({cfg['provider']}): {(r.stderr or r.stdout).strip()[:300]}")


def cmd_config(a):
    cfg = load_config()
    if a.action == "set":
        if a.provider:
            if a.provider not in ("edge", "command"):
                die("provider must be edge or command")
            cfg["provider"] = a.provider
        if a.command is not None:
            cfg["command"] = a.command
        if a.rate:
            cfg["rate"] = a.rate
        save_config(cfg)
    print(json.dumps({"config": cfg, "voices": VOICES}, ensure_ascii=False, indent=2))


def cmd_check(a):
    cfg = load_config()
    print(json.dumps({"provider": cfg["provider"], "uv": bool(shutil.which("uv")),
                      "command_template_set": bool(cfg.get("command")),
                      "hint": "if audio is impossible, show the transcript only AFTER the user answered"}, indent=2))


def cmd_say(a):
    synth(load_config(), a.text, a.voice, a.out)
    print(json.dumps({"file": a.out}))


def task_file(slot):
    if not slot or not all(c.isalnum() or c == "_" for c in slot):
        die(f"invalid slot {slot!r}")
    p = HOME / "tasks" / f"{slot}.json"
    if not p.exists():
        die(f"no saved task in slot {slot!r}: save the task first (tutor.py task save)")
    return p


def update_task_audio(path, files, status):
    task = json.loads(path.read_text(encoding="utf-8"))
    entries = []
    for tid, f in files:
        f = Path(f)
        try:
            f = f.resolve().relative_to(HOME.resolve())
        except ValueError:
            pass
        entries.append({"id": tid, "path": str(f)})
    task["audio"], task["audio_status"] = entries, status
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(task, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def cmd_render(a):
    tpath = task_file(a.slot) if a.slot else None
    try:
        render(a)
    except SystemExit:
        if tpath:
            update_task_audio(tpath, [], "failed")
        raise


def render(a):
    try:
        if a.script is None:
            script = json.loads(task_file(a.slot).read_text(encoding="utf-8")).get("script")
        else:
            script = json.loads(sys.stdin.read() if a.script == "-" else Path(a.script).read_text(encoding="utf-8"))
        texts = script["texts"]
    except (ValueError, OSError, KeyError, TypeError) as e:
        die(f"bad script JSON: {e}")
    cfg = load_config()
    outdir = Path(a.outdir or HOME / "audio")
    files = []
    for t in texts:
        tid = str(t.get("id", "")).strip()
        if not tid or not all(c.isalnum() or c in "_-" for c in tid):
            die(f"text id must be [A-Za-z0-9_-]: {tid!r}")
        turns = t.get("turns") or [{"voice": t.get("voice"), "text": t.get("text")}]
        if not all(isinstance(x.get("text"), str) and x["text"].strip() for x in turns):
            die(f"text {tid}: every turn needs non-empty 'text'")
        target = outdir / f"{tid}.mp3"
        if len(turns) == 1:
            synth(cfg, turns[0]["text"], turns[0].get("voice"), target)
        else:
            with tempfile.TemporaryDirectory(dir=HOME if HOME.exists() else None) as td:
                parts = []
                for i, x in enumerate(turns):
                    part = Path(td) / f"{i}.mp3"
                    synth(cfg, x["text"], x.get("voice"), part)
                    parts.append(part)
                target.write_bytes(b"".join(p.read_bytes() for p in parts))
        files.append(str(target))
    if a.slot:
        update_task_audio(task_file(a.slot), [(Path(f).stem, f) for f in files], "rendered")
    print(json.dumps({"files": files, "slot": a.slot, "note": "play each file ONCE, in order; do not show the transcript"}, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("config"); s.add_argument("action", choices=["show", "set"])
    s.add_argument("--provider"); s.add_argument("--command"); s.add_argument("--rate")
    s.set_defaults(f=cmd_config)
    s = sub.add_parser("check"); s.set_defaults(f=cmd_check)
    s = sub.add_parser("say"); s.add_argument("text"); s.add_argument("--voice", default="katja")
    s.add_argument("--out", required=True); s.set_defaults(f=cmd_say)
    s = sub.add_parser("render"); s.add_argument("script", nargs="?"); s.add_argument("--outdir")
    s.add_argument("--slot", help="record the audio paths in this saved task (e.g. hoeren1)")
    s.set_defaults(f=cmd_render)
    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
