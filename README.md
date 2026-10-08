# telc Exam Tutor (KI-Skill)

Ein KI-Skill für die Vorbereitung auf **telc-Prüfungen mit KI**: Er erzeugt
prüfungsnahe Aufgaben, korrigiert sie mit den offiziellen telc-Kriterien und
verfolgt deine persönlichen Fehler. Als Tutor-Persona begleitet dich **Franz**:
knapp, freundlich und grammatisch präzise, in der Sprache des Lernenden.

Module je Niveau: **Lesen**, **Sprachbausteine**, **Schriftlicher Ausdruck**,
**Hören** (optional mit TTS) und **Sprechen** (Text-Rollenspiel).

> **Ehrlicher Hinweis:** Inoffizielles Übungsmaterial, nicht mit telc
> verbunden. Die Aufgaben sind erfunden; telc-Audio wird nicht reproduziert.
> Hören mit TTS ist nur Hörverständnistraining.

## Status

Aktuell implementiert: nur **Deutsch B2**. Weitere Niveaus kommen als neue
Ordner `modules/<level>/` plus `rules/telc_<level>_architecture.md` hinzu (siehe
`SKILL.md`); ein Niveau existiert, sobald beides vorhanden ist.

### B2 (aktuell)

- Fünf Prüfungsteile: Lesen, Sprachbausteine, Schriftlicher Ausdruck (zwei
  Aufgaben zur Auswahl, Kriterien I–III), Hören, Sprechen (Erfahrungen,
  Diskussion, gemeinsames Planen).
- Bestehen: 60 % je Prüfungsteil, **135/225 schriftlich** und **45/75
  mündlich**. `exam-result` liefert Notenbänder nur aus echten Prüfungswerten
  (300–270 sehr gut, 269,5–240 gut, 239,5–210 befriedigend, 209,5–180
  ausreichend; sonst nicht bestanden).
- Der Mock kann den schriftlichen Block Lesen + Sprachbausteine + Schreiben als
  **150/225** simulieren; die abgeleitete 60-%-Orientierung ist **90/150**,
  keine offizielle Bestehensgrenze. Hören wird separat ausgewiesen.
- Sprechen: Getippt sind nur Ausdrucksfähigkeit, Aufgabenbewältigung und
  formale Richtigkeit schätzbar (7/5/3/0, höchstens 21 Punkte je Teil);
  **Aussprache und Intonation sind aus Text nicht beurteilbar**. Die Schätzung
  ist kein Prüfungsergebnis und geht nie in Ergebnisse, Mittelwerte oder
  Blocksummen ein.

## Kurzsyntax

`/telc <level> <aktion> [modul] [teil]`, z. B. `/telc <level> generate lesen 2`.
Aktionen: `generate`, `correct`, `plan`, `bootcamp`, `mock`; übergreifend
`status`, `help` und `exam-date <YYYY-MM-DD>`. Module: `lesen`,
`sprachbausteine`, `schriftlich`, `hoeren`, `sprechen`, `bootcamp`. Die
vollständige Syntax und die Protokolle stehen in `SKILL.md`.

Sobald du Antworten sendest, startet die Korrektur automatisch; ein
ausdrückliches `correct` ist ebenfalls möglich. Jede Korrektur aktualisiert
dein persönliches Fehlerprofil.

## Top-5-Fehler, Bootcamp und Prüfungstermin

Der Skill verfolgt deine häufigsten Fehler und trainiert sie in einem
Bootcamp. Standard sind **14 Tage**; bei nahem Prüfungstermin wird es
verkürzt, bei weniger als zehn Tagen gibt es stattdessen Triage und
Prüfungssimulationen. Ziel: mindestens **60 % der Ziele** (3 von 5 bzw. 2 von
3) mit mindestens 80 % in den letzten zehn Drill-Items, an mindestens drei
Tagen und über mindestens drei Kalendertage, plus bestandener Abschlusscheck.
Das misst Drillgenauigkeit, nicht Prüfungspunkte. Optional vergleicht
`transfer` Fehler pro 100 Wörter am Anfang und Ende.

Mit `exam-date` entsteht ein T-minus-Countdown-Plan: Bootcamp, zeitgebundene
Mocks, Wiederholung, Hören/Sprechen und die letzten Ruhe- und Checklisten-Tage.
Ohne Termin gilt der 14-Tage-Standard.

## Berechnungen

`tools/tutor.py` erledigt sämtliche Arithmetik (Teilpunkte, Blocksummen,
Bestehensregeln, Bootcamp-Statistiken); die KI rechnet nie selbst.

## Hören, TTS und Schutz der Lösungsschlüssel

`tools/tts.py` erzeugt Audio mit `edge-tts` (über `uv`, Internet erforderlich)
oder einem eigenen Kommando. Ist kein Audio möglich, bleibt das Transkript bis
nach der Antwort verborgen; Lesen ist nicht Hören.

Aufgaben, Schlüssel und Skripte werden lokal gespeichert. Der öffentliche
Task-Aufruf verbirgt Schlüssel, Begründungen, Hörskript und Franz’ geheime
Sprechhaltung bis zur Korrektur. Trotzdem sind gespeicherte Daten in der
lokalen KI-Umgebung bzw. deren Tool-Transkripten sichtbar: Wer ehrlich üben
will, schaut dort nicht nach.

Der lokale Zustand liegt in `~/.config/telc-tutor/`; `TELC_HOME` überschreibt
das Verzeichnis. Die Helfer nutzen nur `uv` und die Python-Standardbibliothek;
`edge-tts` wird nur bei Bedarf geladen.

## Installation, erster Start und Tests

Voraussetzung ist [`uv`](https://docs.astral.sh/uv/). Lege den Skill so ab,
dass `SKILL.md` direkt im Skill-Ordner liegt, lade die Skills im Agenten neu
und prüfe mit `/telc help`.

1. Optional: `/telc exam-date 2026-12-05` (ISO-Format; steuert Plan und
   Bootcamp-Länge).
2. `/telc b2 plan` zeigt den heutigen Plan (`b2` = aktuell einziges Niveau).
3. `/telc b2 generate lesen 1` erzeugt eine Aufgabe; Antworten einfach senden.
4. `/telc b2 bootcamp` startet bzw. setzt das Fehlertraining fort;
   `/telc status` zeigt Fortschritt und Scores.

Tests:

```bash
uv run python -m unittest discover -s tests
```

## Struktur

`SKILL.md` enthält Router und Protokolle. Offizielle Fakten, Rubrik,
Countdown, Feedbackformat, Module, Fehler-Taxonomie und Helfer stehen in
`rules/`, `modules/`, `memory/` und `tools/`; die Tests liegen in `tests/`.

## Credits

Die Franz-Persona ist von Emanuel inspiriert: https://yourdailygerman.com
