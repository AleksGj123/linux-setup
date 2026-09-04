#!/usr/bin/env python3
"""Setzt "terminal.integrated.fontFamily" in der Windows-seitigen VS-Code-settings.json.

VS Code rendert sein integriertes Terminal ueber Chromium und uebernimmt die
Windows-Terminal-Einstellungen nicht - ohne diesen Schritt bleibt dort die
Standardfont aktiv und die Nerd-Font-Icons fehlen.

Aufruf: update-vscode-font.py --user <WinUser> --family "<Font Family>"

Teil von roles/fonts/tasks/main.yml - nicht eigenstaendig gedacht.
"""
import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

SETTING_KEY = "terminal.integrated.fontFamily"
FALLBACK_FAMILY = "monospace"
# Roaming-Profile der stabilen und der Insiders-Ausgabe; beide werden bedient,
# falls installiert.
SETTINGS_LOCATIONS = ("Code", "Code - Insiders")
INDENT = " " * 4


def strip_jsonc(text):
    """Entfernt //- und /*...*/-Kommentare ausserhalb von Strings.

    VS Code erlaubt Kommentare in settings.json, json.loads nicht. Zum *Lesen* des
    Ist-Werts wird die Datei deshalb bereinigt; geschrieben wird immer auf dem
    Originaltext, damit Kommentare und Formatierung des Nutzers erhalten bleiben.
    """
    def replace(match):
        matched = match.group(0)
        return matched if matched.startswith(('"', "'")) else " "

    pattern = r'"(?:\\.|[^"\\])*"|//[^\n]*|/\*.*?\*/'
    without_comments = re.sub(pattern, replace, text, flags=re.DOTALL)
    # Trailing commas, die VS Code ebenfalls toleriert.
    return re.sub(r",(\s*[}\]])", r"\1", without_comments)


def current_value(text):
    try:
        return json.loads(strip_jsonc(text)).get(SETTING_KEY)
    except (json.JSONDecodeError, AttributeError):
        return None


def with_setting(text, value):
    """Gibt den Dateitext mit gesetztem Schluessel zurueck, oder None bei Unparsbarkeit."""
    encoded = json.dumps(value)
    existing = re.search(rf'("{re.escape(SETTING_KEY)}"\s*:\s*)("(?:\\.|[^"\\])*")', text)
    if existing:
        return text[:existing.start(2)] + encoded + text[existing.end(2):]

    opening_brace = text.find("{")
    if opening_brace < 0:
        return None
    rest = text[opening_brace + 1:]
    # Ob ein Komma noetig ist, entscheidet der erste echte Inhalt nach der Klammer -
    # nicht das naechste Zeichen, das auch ein Kommentar sein kann.
    is_only_entry = strip_jsonc(rest).lstrip().startswith("}")
    # Bei bisher leerem Objekt steht die schliessende Klammer sonst hinter dem Wert.
    tail = f"\n{rest.lstrip()}" if is_only_entry else f",{rest}"
    return f'{text[:opening_brace + 1]}\n{INDENT}"{SETTING_KEY}": {encoded}{tail}'


def update_file(path, family):
    font_family = f"'{family}', {FALLBACK_FAMILY}"

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({SETTING_KEY: font_family}, indent=4) + "\n", encoding="utf-8")
        print(f"geaendert: {path} (neu angelegt mit {font_family})")
        return True

    text = path.read_text(encoding="utf-8-sig")
    if current_value(text) == font_family:
        print(f"unveraendert: {path} (bereits {font_family})")
        return True

    updated = with_setting(text, font_family)
    if updated is None:
        print(f"uebersprungen: {path} nicht als JSON lesbar - bitte manuell setzen.", file=sys.stderr)
        return False

    backup = path.with_name(path.name + f".bak-{datetime.now():%Y%m%d%H%M%S}")
    shutil.copy2(path, backup)
    path.write_text(updated, encoding="utf-8")
    print(f"geaendert: {path} ({font_family}, Backup {backup.name})")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True, help="Windows-Benutzername (fuer /mnt/c/Users/<user>)")
    parser.add_argument("--family", required=True, help="Exakter Font-Familienname, wie Windows ihn vergeben hat")
    arguments = parser.parse_args()

    paths = [
        Path(f"/mnt/c/Users/{arguments.user}/AppData/Roaming/{location}/User/settings.json")
        for location in SETTINGS_LOCATIONS
    ]
    # Nur vorhandene Installationen bedienen; die stabile Ausgabe wird auch dann
    # angelegt, wenn sie noch keine settings.json hat.
    targets = [path for path in paths if path.parent.exists() or path == paths[0]]

    results = [update_file(path, arguments.family) for path in targets]
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
