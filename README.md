# telc Exam Tutor (KI Skill)

Ein KI-gestütztes Tutor-System für die telc Deutsch-Prüfungen (B2, C1, C2). Der Skill generiert authentische Prüfungsaufgaben, bewertet Einreichungen nach offiziellen telc-Kriterien (Stand 2026) und trackt individuelle Fehlerprofile mit der pragmatischen Tutor-Persona "Franz".

## Aktuelle Funktionen
Zurzeit unterstützt der Skill ausschließlich folgende B2-Module:
* **Schriftlicher Ausdruck:** Generiert Text-Szenarien für Beschwerden sowie Bitten um Informationen und korrigiert die anschließenden Einreichungen.
* **Sprachbausteine (Teil 1 & 2):** Generiert Lückentexte für Grammatik und Lexik und wertet die Lösungen anhand eines internen Schlüssels aus.

## Installation
Um den Skill in deiner KI-Umgebung zu nutzen, klone dieses Repository direkt in deinen lokalen Skill-Pfad (z. B. `~/.claude/skills/telc-exam-tutor`):

```bash
git clone https://github.com/ceso/telc-exam-tutor.git ~/.claude/skills/telc-exam-tutor
```

(Hinweis: Die Datei SKILL.md muss im Hauptverzeichnis liegen, damit der Agent das System korrekt initialisiert)

## TODO:
* B2: Leseverstehen implementieren
* C1 & C2: Architektur, Regeln und Module vollständig integrieren

## Credits
Für die Persona „Franz“ habe ich mich von Emmanuel (https://yourdailygerman.com) inspirieren lassen. Schaut unbedingt mal auf seiner Seite vorbei!
