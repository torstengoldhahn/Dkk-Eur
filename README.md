# Dkk-Eur

Kleine, eigenständige Web-Werkzeuge — jede Datei läuft ohne Build und ohne Server,
einfach im Browser öffnen.

## `index.html` — Währungsrechner DKK ↔ EUR

Umrechnung in beide Richtungen zum festen EZB-Leitkurs (1 DKK = 0,13408 EUR).

## `diktat.html` — Diktat

Sprechen, und der Text entsteht automatisch mit.

- **Automatische Verschriftlichung** über die Spracherkennung des Browsers
  (Web Speech API) — läuft in Safari, Chrome und Edge; nicht in Firefox und nicht in
  Chrome auf dem iPhone.
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
- **Teilen** über das Teilen-Blatt des Systems (auf iPhone und iPad der direkte Weg
  in jede andere App), Export als `.txt` oder `.md`.
- Neun Diktiersprachen, Hell-/Dunkelmodus, `Strg`+`M` zum Starten und Stoppen,
  auf dem Telefon Daumen-taugliche Knöpfe und „Zum Home-Bildschirm“ als App.

Das Mikrofon muss einmalig freigegeben werden. Beim Öffnen per `file://` verweigern
manche Browser den Mikrofonzugriff — dann kurz lokal ausliefern, z. B.
`python3 -m http.server`, und `http://localhost:8000/diktat.html` aufrufen.

## Auf dem iPhone und iPad

Zuerst das Wichtigste, damit niemand etwas nachbaut, was schon da ist: **iOS diktiert
selbst.** Die Mikrofon-Taste rechts unten auf der Bildschirmtastatur schreibt in *jedes*
Textfeld — auch direkt in die Claude-App. Für „kurz etwas hineinsprechen“ ist das der
schnellste Weg, ganz ohne dieses Projekt.

Was iOS dabei **nicht** tut: Füllwörter entfernen, den Text aufräumen und ihn für später
aufbewahren. Dafür gibt es hier zwei Wege.

### Weg 1: `diktat.html` als App auf dem Home-Bildschirm

1. Die Seite in **Safari** öffnen (Chrome auf dem iPhone kann keine Spracherkennung).
2. Teilen-Symbol → **„Zum Home-Bildschirm“**. Dann startet Diktat ohne Safari-Leisten,
   mit eigenem Symbol.
3. Beim ersten Start einmal Mikrofon und Spracherkennung erlauben.

Danach: Knopf drücken, sprechen, Knopf drücken. Der Text ist aufgeräumt, liegt in der
Zwischenablage und im Verlauf. **Teilen** öffnet das Teilen-Blatt — von dort geht der Text
an Claude, Notizen, Mail, Nachrichten oder sonst wohin. **In Claude öffnen** startet damit
direkt eine neue Unterhaltung.

Zwei Eigenheiten von Safari: Es beendet die Erkennung nach längeren Sprechpausen von
selbst. Die Seite fängt das ab, legt den Text im Verlauf ab und wartet mit
„Weiter zuhören“ auf einen Tipper — nichts geht verloren. Und der Bildschirm sollte
an bleiben, sonst hört Safari auf zuzuhören.

Damit die Seite aufs Telefon kommt, braucht sie eine Adresse. Für dieses Repository
ist GitHub Pages bereits eingeschaltet — ausgeliefert wird aber immer nur **ein**
Branch, und der muss auf den zeigen, der `diktat.html` enthält:

1. Repository → **Settings** → **Pages**
2. Unter *Build and deployment* bei **Source**: „**Deploy from a branch**“
3. Branch auswählen (`main`, sobald die Dateien dort liegen — sonst den Arbeitsbranch),
   Ordner `/ (root)`, dann **Save**

Diesen Schalter kann nur jemand mit Administrationsrechten am Repository umlegen;
ein Zugriffstoken oder ein Workflow bekommt dafür `403 Resource not accessible by
integration`, selbst mit der Berechtigung `pages: write`. Die deckt nur
Pages-*Deployments* ab, nicht die Pages-*Einstellung*.

Ein bis zwei Minuten nach dem Speichern liegt die Seite unter
`https://<benutzername>.github.io/Dkk-Eur/diktat.html`. Ob der Bau geklappt hat, zeigt
der Lauf „pages build and deployment“ unter *Actions*. Die Datei `.nojekyll` im
Wurzelverzeichnis sorgt dafür, dass die HTML-Dateien unverändert ausgeliefert werden.

### Weg 2: Kurzbefehl — ein Tipp, und der Text ist fertig

Das kommt dem „automatisch einfügen“ vom Rechner am nächsten und braucht keine Webseite.
In der App **Kurzbefehle** einen neuen Kurzbefehl namens „Diktat“ anlegen:

1. **Text diktieren** — Sprache Deutsch, Anhalten „nach kurzer Pause“.
2. **Text ersetzen** — Suchen nach `\s*\b(ähm+|äh+|öhm?|hm+|mhm)\b`, ersetzen durch nichts,
   dabei *Regulärer Ausdruck* einschalten und Groß-/Kleinschreibung ignorieren.
3. **In die Zwischenablage kopieren** — danach genügt langes Tippen und „Einsetzen“.
4. Optional **An Notiz anhängen** für ein Archiv aller Diktate.
5. Optional für den direkten Weg zu Claude: **URL codieren**, dann **Text** mit
   `https://claude.ai/new?q=` davor, dann **URL öffnen**.

Auslösen lässt sich das ohne jedes Tippen auf einem Symbol:

- **Auf Rückseite tippen**: Einstellungen → Bedienungshilfen → Tippen →
  Auf Rückseite tippen → Doppeltippen → „Diktat“.
- **Actionstaste** (iPhone 15 Pro und neuer): Einstellungen → Actionstaste → Kurzbefehl.
- **Siri**: „Hey Siri, Diktat“.

Die Namen der Aktionen wandern zwischen den iOS-Versionen manchmal leicht; die
Reihenfolge bleibt.

### Was auf iOS nicht geht

`diktiergeraet.py` läuft dort nicht. iOS lässt kein Programm im Hintergrund auf einen
Hotkey lauschen und in fremde Apps tippen — das ist eine Grenze des Systems, keine
fehlende Zeile Code. Der Kurzbefehl oben ist der Ersatz dafür.

## `diktiergeraet.py` — Diktat in jedes Programm (Mac, Windows, Linux)

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
