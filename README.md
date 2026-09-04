# linux-setup

Reproduzierbares Workstation-Setup (Look & Convenience) fuer Ubuntu / WSL2.
Ansible, lokal ausgefuehrt - kein SSH, kein Control-Node.

## Warum ueberhaupt

Das manuelle Setup ist an vier Stellen gescheitert. Alle vier sind hier
strukturell ausgeschlossen:

| Problem damals | Loesung hier |
|---|---|
| `starship init` landete in `.bashrc`, Login-Shell war aber zsh | `.zshrc` wird komplett aus Template geschrieben |
| `echo >>` ohne Newline klebte zwei Befehle zusammen | Es wird **nie** angehaengt, immer die ganze Datei geschrieben |
| `~/.config` existierte nicht | `base`-Rolle legt es an, laeuft garantiert zuerst |
| Reihenfolge (`starship init` vs. `oh-my-zsh`) | Im Template fest verdrahtet, Starship immer als Letztes |

Zusaetzlich: `validate: zsh -n %s` prueft die Syntax, **bevor** die neue
`.zshrc` aktiv wird. Ein kaputtes Template kann dir die Shell nicht zerlegen.

## Benutzung

```bash
./run.sh check      # Trockenlauf mit Diff - aendert nichts
./run.sh all        # komplettes Setup
./run.sh shell      # nur zsh + starship + .zshrc
./run.sh starship   # nur Preset wechseln
```

`run.sh` braucht nur bash und installiert Ansible bei Bedarf selbst.
Ein `Makefile` mit denselben Zielen liegt bei - `make` ist auf einem frischen
Ubuntu aber nicht vorhanden, deshalb ist `run.sh` der Einstieg.

Auf einer frischen Maschine:

```bash
git clone <dein-repo> ~/projects/linux-setup
cd ~/projects/linux-setup && ./bootstrap.sh
```

## Anpassen

Fast alles steht in `group_vars/all.yml`:

- `starship_preset` - z.B. `tokyo-night`, `pastel-powerline`, `gruvbox-rainbow`
- `omz_plugins` - oh-my-zsh Plugins
- `apt_packages` - Pakete
- `setup_tmux` / `setup_fonts` - optionale Bereiche

Preset wechseln = Wert aendern, dann `./run.sh starship`. Ein Marker
(`~/.config/.starship-preset`) sorgt dafuer, dass nur bei echter Aenderung
geschrieben wird - und die alte `starship.toml` wird vorher gesichert.

Shell-Aliases und Optionen: `roles/shell_config/templates/zshrc.j2`.

## Wichtig: Nerd Font unter WSL

Die Font wird **nicht** in Linux installiert - die Darstellung macht die
Windows-Seite. `./run.sh fonts` erledigt das automatisch; der einzige manuelle
Schritt ist eine UAC-Bestaetigung pro frischer Maschine:

- **systemweit** installiert (`C:\Windows\Fonts` + `HKLM`, Registry +
  `AddFontResourceW`)
- **nur im WSL-Terminalprofil** aktiviert (`font.face` wird ausschliesslich bei
  Windows-Terminal-Profilen gesetzt, deren Name/Quelle auf `wsl_terminal_profile_match`
  passt - Standard `Ubuntu`; PowerShell/cmd/Azure Cloud Shell bleiben unberuehrt)
- zusaetzlich im **integrierten Terminal von VS Code** gesetzt
  (`terminal.integrated.fontFamily`, abschaltbar ueber `setup_vscode_font`)

### Warum systemweit und nicht pro Benutzer

Frueher installierte diese Rolle nur fuer den aktuellen Windows-User
(`%LOCALAPPDATA%`, `HKCU`) - ohne UAC, aber kaputt: eine so registrierte Font
sieht ausschliesslich GDI. Das Ergebnis war ein Prompt, der je nach Startweg
anders aussah:

| Startweg | rendert ueber | sah per-User-Font |
|---|---|---|
| Startmenue-Verknuepfung `Ubuntu` | conhost / GDI | ja - korrekt |
| Windows Terminal | Paket-App, DirectWrite | nein - Icons fehlten |
| VS Code | Chromium / DirectWrite | nein - Icons fehlten |

Windows Terminal loest `font.face` dann nicht auf und faellt still auf die
Standardfont zurueck, in der die Nerd-Font-Icons nicht enthalten sind. Deshalb
ist die einmalige UAC-Abfrage der Preis fuer eine Darstellung, die ueberall
stimmt. Ein Wiederholungslauf erkennt die vorhandene Installation und eskaliert
gar nicht erst - die Abfrage kommt also wirklich nur einmal. Eine noch
vorhandene alte per-User-Registrierung raeumt die Rolle dabei weg, damit
dieselbe Familie nicht aus zwei Quellen kommt.

Windows Terminal muss nach dem ersten Lauf **komplett beendet und neu
gestartet** werden - ein neuer Tab genuegt nicht. Die DirectWrite-Font-Liste
wird einmal beim Prozessstart gelesen und danach gecacht; eine Instanz, die
schon vor der Installation lief, kennt die neue Font nicht und faellt still auf
die Standardfont ohne Icons zurueck. `settings.json` selbst wird zwar live
nachgeladen, die Font-Liste nicht - deshalb sieht der Prompt trotz korrekter
Einstellung unveraendert aus. Fuer VS Code gilt dasselbe: "Fenster neu laden"
reicht nicht, VS Code muss beendet und neu gestartet werden. Der
tatsaechlich vergebene Font-Familienname wird pro Lauf aus der installierten
Datei ausgelesen statt angenommen, weil Nerd-Fonts-Releases ihn zwischen
Versionen aendern koennen (z.B. `CaskaydiaCove Nerd Font Mono` -> `CaskaydiaCove NFM`).

## Struktur

```
site.yml               Reihenfolge der Rollen (dokumentiert, warum)
group_vars/all.yml     alle Stellschrauben
roles/base/            Pakete + Verzeichnisse   -> zuerst
roles/zsh/             oh-my-zsh + Plugins
roles/starship/        Binary + Preset
roles/shell_config/    .zshrc (Template)        -> zuletzt
roles/tmux/            optional
roles/fonts/           optional
```
