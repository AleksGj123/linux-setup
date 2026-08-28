#!/usr/bin/env python3
"""Setzt "font.face" NUR bei Windows-Terminal-Profilen, deren Name/Quelle auf den
Filter passt (Standard: "Ubuntu") - PowerShell/cmd/Azure Cloud Shell bleiben
unangetastet. Damit gilt die Nerd Font wirklich nur im WSL-Terminal.

Aufruf: update-wt-font.py --user <WinUser> --family "<Font Family>" --match <Substring>

Teil von roles/fonts/tasks/main.yml - nicht eigenstaendig gedacht.
"""
import argparse
import glob
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", required=True, help="Windows-Benutzername (fuer /mnt/c/Users/<user>)")
    ap.add_argument("--family", required=True, help="Exakter Font-Familienname, wie Windows ihn vergeben hat")
    ap.add_argument("--match", required=True, help="Substring gegen Profilname/-quelle (case-insensitive)")
    args = ap.parse_args()

    # Deckt sowohl Store- als auch Preview-Paket ab (Microsoft.WindowsTerminal_*
    # bzw. Microsoft.WindowsTerminalPreview_*).
    pattern = f"/mnt/c/Users/{args.user}/AppData/Local/Packages/Microsoft.WindowsTerminal*/LocalState/settings.json"
    candidates = sorted(glob.glob(pattern))
    if not candidates:
        print(f"Windows Terminal settings.json nicht gefunden: {pattern}", file=sys.stderr)
        sys.exit(1)

    for path_str in candidates:
        path = Path(path_str)

        with path.open(encoding="utf-8-sig") as f:
            data = json.load(f)

        touched = 0
        for prof in data.get("profiles", {}).get("list", []):
            name = str(prof.get("name", ""))
            source = str(prof.get("source", ""))
            if args.match.lower() in name.lower() or args.match.lower() in source.lower():
                font = prof.setdefault("font", {})
                if font.get("face") != args.family:
                    font["face"] = args.family
                    touched += 1

        if touched:
            backup = path.with_name(path.name + f".bak-{datetime.now():%Y%m%d%H%M%S}")
            shutil.copy2(path, backup)
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
                f.write("\n")
            print(f"geaendert: {path} ({touched} Profil(e) auf '{args.family}', Backup {backup.name})")
        else:
            print(f"unveraendert: {path} (bereits '{args.family}' oder kein passendes Profil)")


if __name__ == "__main__":
    main()
