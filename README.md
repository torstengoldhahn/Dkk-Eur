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
- **Automatisch in die Zwischenablage** (optional), außerdem Export als `.txt` oder `.md`.
- Neun Diktiersprachen, Hell-/Dunkelmodus, `Strg`+`M` zum Starten und Stoppen.

Das Mikrofon muss einmalig freigegeben werden. Beim Öffnen per `file://` verweigern
manche Browser den Mikrofonzugriff — dann kurz lokal ausliefern, z. B.
`python3 -m http.server`, und `http://localhost:8000/diktat.html` aufrufen.
