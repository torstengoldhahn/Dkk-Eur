#!/usr/bin/env python3
"""Diktiergerät — sprechen, und der Text landet im gerade aktiven Fenster.

Hotkey drücken, sprechen, Hotkey drücken: das Gesagte wird verschriftlicht,
aufgeräumt, in die Zwischenablage gelegt und dort eingefügt, wo der Cursor
gerade steht — Claude, Word, E-Mail, Terminal, egal.

    python3 diktiergeraet.py                     # F9 startet und stoppt
    python3 diktiergeraet.py --modus terminal    # ohne Hotkey, mit Enter
    python3 diktiergeraet.py --einfuegen tippen  # tippt statt einzufügen
    python3 diktiergeraet.py --selbsttest        # prüft nur die Textregeln

Einrichtung: siehe README.md, Abschnitt „diktiergeraet.py“.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

ABLAGE = Path.home() / ".diktat"
VERLAUF = ABLAGE / "verlauf.md"
RATE = 16000  # Abtastrate, die alle Erkenner mögen


# --------------------------------------------------------------------------
# Textregeln — dieselben wie in diktat.html
# --------------------------------------------------------------------------

BEFEHLE = {
    "de": {
        "punkt": ".", "komma": ",", "fragezeichen": "?", "ausrufezeichen": "!",
        "doppelpunkt": ":", "semikolon": ";", "strichpunkt": ";",
        "bindestrich": "-", "gedankenstrich": "–", "schrägstrich": "/",
        "klammer auf": "(", "klammer zu": ")",
        "anführungszeichen auf": "„", "anführungszeichen zu": "“",
        "neue zeile": "\n", "neuer absatz": "\n\n", "absatz": "\n\n",
    },
    "en": {
        "period": ".", "full stop": ".", "comma": ",", "question mark": "?",
        "exclamation mark": "!", "colon": ":", "semicolon": ";",
        "hyphen": "-", "dash": "–", "slash": "/",
        "open bracket": "(", "close bracket": ")",
        "new line": "\n", "new paragraph": "\n\n",
    },
}

FUELLWOERTER = {
    "de": {"ähm", "ähmm", "äh", "ah", "öh", "öhm", "ehm", "em", "hm", "hmm", "mhm", "mmh", "tja"},
    "en": {"um", "umm", "uh", "uhh", "erm", "er", "hmm", "mhm"},
}

_RAND = ".,!?;:"


def _dialekt(sprache: str) -> str:
    kurz = sprache[:2].lower()
    return kurz if kurz in BEFEHLE else "en"


def _befehle_ersetzen(text: str, sprache: str, befehle: bool, fueller: bool) -> str:
    """Wandelt gesprochene Satzzeichen um und streicht Füllwörter."""
    karte = BEFEHLE[_dialekt(sprache)]
    raus = FUELLWOERTER.get(_dialekt(sprache), set())
    woerter = text.split()
    ergebnis: list[str] = []
    i = 0

    while i < len(woerter):
        blank = woerter[i].lower().strip(_RAND)

        if befehle and i + 1 < len(woerter):
            paar = blank + " " + woerter[i + 1].lower().strip(_RAND)
            if paar in karte:
                ergebnis.append(karte[paar])
                i += 2
                continue
        if befehle and blank in karte:
            ergebnis.append(karte[blank])
            i += 1
            continue
        if fueller and blank in raus:
            i += 1
            continue

        ergebnis.append(woerter[i])
        i += 1

    return " ".join(ergebnis)


def _aufraeumen(text: str) -> str:
    """Abstände und Großschreibung geradeziehen."""
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\s+([,.;:!?…])", r"\1", text)
    text = re.sub(r"([,;:])(?=[^\s\n])", r"\1 ", text)
    # Abstand nach Satzende — aber "3.5" bleibt heil
    text = re.sub(r"([.!?])(?=[A-Za-zÄÖÜäöüß])", r"\1 ", text)
    text = re.sub(r"(?<=[^\d])([.!?])(?=\d)", r"\1 ", text)
    text = re.sub(r"([(„])\s+", r"\1", text)
    text = re.sub(r"\s+([)“])", r"\1", text)
    text = re.sub(
        r"(^|[.!?]\s+|\n\s*)([a-zäöüß])",
        lambda m: m.group(1) + m.group(2).upper(),
        text,
    )
    return re.sub(r"[ \t]+$", "", text, flags=re.M).strip()


def aufbereiten(roh: str, sprache: str = "de", *, befehle: bool = True,
                fueller: bool = True, formatieren: bool = True) -> str:
    """Rohes Erkanntes in einen sauberen Text verwandeln."""
    text = _befehle_ersetzen(roh.strip(), sprache, befehle, fueller)
    return _aufraeumen(text) if formatieren else text


# --------------------------------------------------------------------------
# Zwischenablage und Einfügen
# --------------------------------------------------------------------------

def in_zwischenablage(text: str) -> bool:
    """Text in die Zwischenablage legen — über pyperclip oder Systemwerkzeug."""
    try:
        import pyperclip

        pyperclip.copy(text)
        return True
    except Exception:
        pass

    if sys.platform == "darwin":
        kandidaten = [["pbcopy"]]
    elif sys.platform.startswith("win"):
        kandidaten = [["clip"]]
    else:
        kandidaten = [["wl-copy"], ["xclip", "-selection", "clipboard"], ["xsel", "-ib"]]

    for befehl in kandidaten:
        if shutil.which(befehl[0]):
            try:
                subprocess.run(befehl, input=text.encode("utf-8"), check=True)
                return True
            except Exception:
                continue
    return False


def einfuegen(text: str, modus: str, verzoegerung: float = 0.25) -> None:
    """Text dort absetzen, wo der Cursor gerade steht."""
    kopiert = in_zwischenablage(text)

    if modus == "zwischenablage":
        print("  → in der Zwischenablage" if kopiert else "  ! Zwischenablage nicht erreichbar")
        return

    try:
        from pynput.keyboard import Controller, Key
    except ImportError:
        print("  ! pynput fehlt — Text liegt nur in der Zwischenablage (Strg+V)")
        return

    tastatur = Controller()
    time.sleep(verzoegerung)  # kurz warten, bis der Hotkey wirklich losgelassen ist

    if modus == "tippen" or not kopiert:
        tastatur.type(text)
        print("  → getippt")
        return

    mod = Key.cmd if sys.platform == "darwin" else Key.ctrl
    with tastatur.pressed(mod):
        tastatur.press("v")
        tastatur.release("v")
    print("  → eingefügt")


def merken(text: str) -> None:
    """Jedes Diktat zusätzlich in ~/.diktat/verlauf.md ablegen."""
    try:
        ABLAGE.mkdir(parents=True, exist_ok=True)
        stempel = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
        with VERLAUF.open("a", encoding="utf-8") as datei:
            datei.write(f"\n## {stempel}\n\n{text}\n")
    except OSError as fehler:
        print(f"  ! Verlauf nicht schreibbar: {fehler}")


# --------------------------------------------------------------------------
# Aufnahme
# --------------------------------------------------------------------------

class Aufnahme:
    """Nimmt vom Mikrofon auf, bis sie gestoppt wird."""

    def __init__(self) -> None:
        import numpy  # noqa: F401  — nur prüfen, ob vorhanden
        import sounddevice as sd

        self._sd = sd
        self._stapel: list = []
        self._strom = None
        self._schloss = threading.Lock()

    def _zurueck(self, daten, frames, zeit, status) -> None:
        if status:
            print(f"  ! Audio: {status}", file=sys.stderr)
        with self._schloss:
            self._stapel.append(daten.copy())

    def start(self) -> None:
        with self._schloss:
            self._stapel = []
        self._strom = self._sd.InputStream(
            samplerate=RATE, channels=1, dtype="float32", callback=self._zurueck
        )
        self._strom.start()

    def stop(self):
        import numpy as np

        if self._strom is not None:
            self._strom.stop()
            self._strom.close()
            self._strom = None
        with self._schloss:
            stuecke = self._stapel
            self._stapel = []
        if not stuecke:
            return np.zeros(0, dtype="float32")
        return np.concatenate(stuecke, axis=0).flatten()


# --------------------------------------------------------------------------
# Erkennung
# --------------------------------------------------------------------------

class Whisper:
    """Lokale Erkennung mit faster-whisper — läuft ohne Internet."""

    name = "whisper"

    def __init__(self, modell: str, sprache: str) -> None:
        from faster_whisper import WhisperModel

        print(f"  Lade Modell „{modell}“ … (beim ersten Mal dauert das)")
        self._modell = WhisperModel(modell, device="cpu", compute_type="int8")
        self._sprache = sprache[:2]

    def erkenne(self, audio) -> str:
        teile, _ = self._modell.transcribe(
            audio, language=self._sprache, vad_filter=True, beam_size=5
        )
        return " ".join(teil.text.strip() for teil in teile).strip()


class Google:
    """Erkennung über Googles Web-Dienst — braucht Internet, kein Schlüssel."""

    name = "google"

    def __init__(self, sprache: str) -> None:
        import speech_recognition as sr

        self._sr = sr
        self._erkenner = sr.Recognizer()
        self._sprache = sprache

    def erkenne(self, audio) -> str:
        import numpy as np

        roh = (np.clip(audio, -1.0, 1.0) * 32767).astype("<i2").tobytes()
        daten = self._sr.AudioData(roh, RATE, 2)
        try:
            return self._erkenner.recognize_google(daten, language=self._sprache)
        except self._sr.UnknownValueError:
            return ""


def erkenner_bauen(wunsch: str, modell: str, sprache: str):
    """Den gewünschten Erkenner aufbauen, sonst den verfügbaren."""
    versuche = [wunsch] if wunsch != "auto" else ["whisper", "google"]
    letzter = None
    for art in versuche:
        try:
            return Whisper(modell, sprache) if art == "whisper" else Google(sprache)
        except ImportError as fehler:
            letzter = fehler
            if wunsch != "auto":
                break
    hinweis = "faster-whisper" if wunsch == "whisper" else "SpeechRecognition"
    raise SystemExit(
        f"Kein Erkenner verfügbar ({letzter}).\n"
        f"Bitte installieren:  pip install {hinweis}"
    )


# --------------------------------------------------------------------------
# Ablauf
# --------------------------------------------------------------------------

class Diktiergeraet:
    def __init__(self, argumente) -> None:
        self.arg = argumente
        self.aufnahme = Aufnahme()
        self.erkenner = erkenner_bauen(argumente.erkenner, argumente.modell, argumente.sprache)
        self.laeuft = False
        self.beschaeftigt = threading.Lock()

    def umschalten(self) -> None:
        if not self.beschaeftigt.acquire(blocking=False):
            return
        try:
            self.stoppen() if self.laeuft else self.starten()
        finally:
            self.beschaeftigt.release()

    def starten(self) -> None:
        self.aufnahme.start()
        self.laeuft = True
        print("\n● Aufnahme läuft — sprich. Zum Beenden noch einmal auslösen.")

    def stoppen(self) -> None:
        audio = self.aufnahme.stop()
        self.laeuft = False
        dauer = len(audio) / RATE
        print(f"■ Gestoppt nach {dauer:.1f} s — verschriftliche …")

        if dauer < 0.4:
            print("  (zu kurz, nichts erkannt)")
            return

        roh = self.erkenner.erkenne(audio)
        if not roh.strip():
            print("  (nichts verstanden)")
            return

        text = aufbereiten(
            roh,
            self.arg.sprache,
            befehle=not self.arg.ohne_befehle,
            fueller=not self.arg.ohne_fuellwoerter,
            formatieren=not self.arg.ohne_format,
        )
        print(f"  „{text}“")
        merken(text)
        einfuegen(text, self.arg.einfuegen)


def selbsttest() -> int:
    faelle = [
        ("also ähm das ist ein test punkt", "de", "Also das ist ein test."),
        ("klammer auf wichtig klammer zu komma oder", "de", "(wichtig), oder"),
        ("wie geht es dir fragezeichen mir geht es gut punkt", "de",
         "Wie geht es dir? Mir geht es gut."),
        ("der wert ist 3.5 prozent punkt", "de", "Der wert ist 3.5 prozent."),
        ("erste zeile neuer absatz zweite zeile punkt", "de",
         "Erste zeile\n\nZweite zeile."),
        ("hello um world comma this is a test period", "en",
         "Hello world, this is a test."),
    ]
    fehler = 0
    for roh, sprache, erwartet in faelle:
        ist = aufbereiten(roh, sprache)
        ok = ist == erwartet
        fehler += 0 if ok else 1
        print(f"{'✓' if ok else '✗'} {roh!r}\n    → {ist!r}"
              + ("" if ok else f"\n    erwartet: {erwartet!r}"))
    print(f"\n{len(faelle) - fehler}/{len(faelle)} bestanden")
    return 1 if fehler else 0


def argumente_lesen(argv=None):
    p = argparse.ArgumentParser(
        description="Diktieren und den Text ins aktive Fenster einfügen.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--sprache", default="de-DE", help="Diktiersprache (Vorgabe: de-DE)")
    p.add_argument("--erkenner", choices=["auto", "whisper", "google"], default="auto",
                   help="whisper = lokal und offline, google = online (Vorgabe: auto)")
    p.add_argument("--modell", default="small",
                   help="Whisper-Modell: tiny, base, small, medium, large-v3 (Vorgabe: small)")
    p.add_argument("--hotkey", default="<f9>",
                   help="Taste zum Starten/Stoppen, z. B. '<ctrl>+<alt>+d' (Vorgabe: <f9>)")
    p.add_argument("--modus", choices=["hotkey", "terminal"], default="hotkey",
                   help="terminal = mit Enter auslösen, falls der Hotkey nicht darf")
    p.add_argument("--einfuegen", choices=["einfuegen", "tippen", "zwischenablage"],
                   default="einfuegen",
                   help="einfuegen = Strg+V senden, tippen = Zeichen für Zeichen")
    p.add_argument("--ohne-befehle", action="store_true",
                   help="gesprochene Satzzeichen nicht umwandeln")
    p.add_argument("--ohne-fuellwoerter", action="store_true",
                   help="„ähm“ und Co. stehen lassen")
    p.add_argument("--ohne-format", action="store_true",
                   help="keine Groß-/Kleinschreibung und Abstände korrigieren")
    p.add_argument("--selbsttest", action="store_true",
                   help="nur die Textregeln prüfen, ohne Mikrofon")
    return p.parse_args(argv)


def main(argv=None) -> int:
    arg = argumente_lesen(argv)
    if arg.selbsttest:
        return selbsttest()

    try:
        geraet = Diktiergeraet(arg)
    except ImportError as fehler:
        print(f"Fehlende Abhängigkeit: {fehler}\n"
              f"Bitte installieren:  pip install -r requirements.txt", file=sys.stderr)
        return 2

    print(f"Diktiergerät bereit · Sprache {arg.sprache} · Erkenner {geraet.erkenner.name} "
          f"· Einfügen: {arg.einfuegen}")
    print(f"Verlauf: {VERLAUF}")

    if arg.modus == "terminal":
        print("Enter startet und stoppt die Aufnahme, Strg+C beendet.\n")
        try:
            while True:
                input()
                geraet.umschalten()
        except (KeyboardInterrupt, EOFError):
            print("\nTschüss.")
            return 0

    try:
        from pynput import keyboard
    except ImportError:
        print("pynput fehlt — bitte `pip install pynput` oder `--modus terminal` nutzen",
              file=sys.stderr)
        return 2

    print(f"{arg.hotkey} startet und stoppt die Aufnahme, Strg+C beendet.\n")
    try:
        with keyboard.GlobalHotKeys({arg.hotkey: geraet.umschalten}) as lauscher:
            lauscher.join()
    except KeyboardInterrupt:
        print("\nTschüss.")
    except Exception as fehler:
        print(f"\nHotkey nicht möglich ({fehler}).\n"
              f"Unter macOS muss das Terminal in den Systemeinstellungen unter "
              f"„Bedienungshilfen“ freigegeben sein.\n"
              f"Alternative ohne Rechte:  python3 diktiergeraet.py --modus terminal",
              file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
