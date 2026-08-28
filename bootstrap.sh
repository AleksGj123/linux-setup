#!/usr/bin/env bash
# Einmaliger Einstieg auf einer frischen Maschine:
#   git clone <repo> ~/projects/linux-setup && ~/projects/linux-setup/bootstrap.sh
set -euo pipefail
REPO_DIR="${REPO_DIR:-$HOME/projects/linux-setup}"

command -v git >/dev/null 2>&1 || { sudo apt-get update -qq && sudo apt-get install -y git; }

cd "$REPO_DIR"
./run.sh all "$@"
