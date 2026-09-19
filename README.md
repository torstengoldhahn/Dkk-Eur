# Dkk-Eur

Kleine, eigenständige Web-Werkzeuge — jede Datei läuft ohne Build und ohne Server,
einfach im Browser öffnen.

## `index.html` — Währungsrechner DKK ↔ EUR

Umrechnung in beide Richtungen zum festen EZB-Leitkurs (1 DKK = 0,13408 EUR).

## `diktat.html` — Diktat

Sprechen, und der Text entsteht automatisch mit.

- **Automatische Verschriftlichung** über die Spracherkennung des Browsers
  (Web Speech API) — läuft in Chrome, Edge und Safari, nicht in Firefox.
- **Automatische Formatierung**: Satzzeichen ohne Abstand davor, Großschreibung
  am Satzanfang, saubere Absätze.
- **Satzzeichen-Befehle**: „Punkt“, „Komma“, „Fragezeichen“, „Klammer auf“,
  „neuer Absatz“ und weitere werden beim Sprechen direkt gesetzt. Die vollständige
  Liste steht in der Seite selbst und passt sich der gewählten Sprache an.
- **Füllwörter entfernen**: „ähm“, „äh“, „öhm“ und Verwandte fliegen automatisch raus.
- **Automatisches Speichern** im Browser — beim nächsten Öffnen ist der Text wieder da.
  Er verlässt das Gerät nicht.
- **Automatisch in die Zwischenablage** — wahlweise beim Stoppen oder nach jedem Satz.
  Danach reicht `Strg`+`V` im Zielprogramm.
- **Verlauf**: jedes beendete Diktat wird abgelegt und lässt sich später mit einem Klick
  kopieren oder zurück in den Editor holen.
- **In Claude öffnen** startet mit dem diktierten Text direkt eine neue Unterhaltung.
- Export als `.txt` oder `.md`, neun Diktiersprachen, Hell-/Dunkelmodus,
  `Strg`+`M` zum Starten und Stoppen.

Das Mikrofon muss einmalig freigegeben werden. Beim Öffnen per `file://` verweigern
manche Browser den Mikrofonzugriff — dann kurz lokal ausliefern, z. B.
`python3 -m http.server`, und `http://localhost:8000/diktat.html` aufrufen.

## `diktiergeraet.py` — Diktat in jedes Programm

Was eine Webseite nicht darf: Text in ein **fremdes** Fenster schreiben. Dieses kleine
Programm kann es. Hotkey drücken, sprechen, Hotkey drücken — der Text erscheint dort,
wo der Cursor gerade steht: in Claude, in Word, im Mail-Programm, im Terminal.

```bash
pip install -r requirements.txt
python3 diktiergeraet.py
```

- **`F9`** startet und stoppt die Aufnahme (`--hotkey '<ctrl>+<alt>+d'` für etwas anderes).
- Erkennung standardmäßig **lokal und offline** mit `faster-whisper`; das Modell wird beim
  ersten Start einmalig heruntergeladen (`--modell tiny` ist schneller, `medium` genauer).
  Mit `--erkenner google` läuft es stattdessen über Googles Web-Dienst.
- Dieselben Regeln wie in der Webseite: Satzzeichen-Befehle, Füllwörter raus, Formatierung.
- Jedes Diktat wandert zusätzlich nach `~/.diktat/verlauf.md`.
- `--einfuegen tippen` tippt Zeichen für Zeichen, falls ein Programm Einfügen blockiert;
  `--einfuegen zwischenablage` legt den Text nur ab, ohne selbst Tasten zu drücken.
- `python3 diktiergeraet.py --selbsttest` prüft die Textregeln ohne Mikrofon.

Hinweise zu den Rechten: Unter **macOS** muss das Terminal in den Systemeinstellungen unter
„Datenschutz & Sicherheit → Bedienungshilfen“ freigegeben werden, sonst darf das Programm
weder den Hotkey hören noch Tasten senden. Unter **Wayland** (Linux) sind globale Hotkeys
oft gesperrt — dann `python3 diktiergeraet.py --modus terminal` nutzen, dort löst `Enter` aus.
Unter Linux zusätzlich `xclip` (X11) oder `wl-clipboard` (Wayland) installieren.
