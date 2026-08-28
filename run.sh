#!/usr/bin/env bash
# Einstiegspunkt fuer dieses Setup. Braucht nur bash - kein make, kein sonstwas.
#
#   ./run.sh check      Trockenlauf mit Diff (aendert nichts)
#   ./run.sh all        komplettes Setup
#   ./run.sh shell      nur zsh + starship + .zshrc
#   ./run.sh starship   nur Starship-Preset
#   ./run.sh tmux       nur tmux
#   ./run.sh fonts      nur Fonts (ohne sudo)
#   ./run.sh lint       Syntaxpruefung
set -euo pipefail
cd "$(dirname "$(readlink -f "$0")")"

usage() { sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

ensure_ansible() {
    command -v ansible-playbook >/dev/null 2>&1 && return 0
    echo "==> Ansible fehlt. Installiere es jetzt (benoetigt sudo)."
    sudo apt-get update -qq
    sudo apt-get install -y ansible
}

cmd="${1:-help}"; shift || true

case "$cmd" in
    help|-h|--help) usage 0 ;;
    lint)
        ensure_ansible
        ansible-playbook site.yml --syntax-check
        ;;
    fonts)
        ensure_ansible
        ansible-playbook site.yml --tags fonts "$@"
        ;;
    check)
        ensure_ansible
        ansible-playbook site.yml --check --diff --ask-become-pass "$@"
        ;;
    all)
        ensure_ansible
        ansible-playbook site.yml --ask-become-pass "$@"
        ;;
    shell|starship|tmux|base|zsh)
        ensure_ansible
        ansible-playbook site.yml --tags "$cmd" --ask-become-pass "$@"
        ;;
    *)
        echo "Unbekannt: $cmd" >&2
        usage 1 >&2
        ;;
esac
