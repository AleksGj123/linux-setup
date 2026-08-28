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

Die Font wird **nicht** in Linux installiert - Windows Terminal rendert die
Darstellung. `./run.sh fonts` erledigt das komplett automatisch, kein manueller
Klick noetig:

- **nur fuer den aktuellen Windows-User** installiert (Registry + `AddFontResourceW`,
  kein Admin/UAC, kein "Fuer alle Benutzer installieren")
- **nur im WSL-Terminalprofil** aktiviert (`font.face` wird ausschliesslich bei
  Windows-Terminal-Profilen gesetzt, deren Name/Quelle auf `wsl_terminal_profile_match`
  passt - Standard `Ubuntu`; PowerShell/cmd/Azure Cloud Shell bleiben unberuehrt)

Kein Neustart von Windows Terminal noetig - ein neuer Tab reicht. Der
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
