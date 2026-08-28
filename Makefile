.PHONY: all check shell starship tmux fonts lint

all:            ## Komplettes Setup
	ansible-playbook site.yml --ask-become-pass

check:          ## Trockenlauf - zeigt Diffs, aendert nichts
	ansible-playbook site.yml --check --diff --ask-become-pass

shell:          ## Nur Shell (zsh + starship + .zshrc)
	ansible-playbook site.yml --tags shell --ask-become-pass

starship:       ## Nur Starship-Preset neu anwenden
	ansible-playbook site.yml --tags starship --ask-become-pass

tmux:           ## Nur tmux (setup_tmux muss true sein)
	ansible-playbook site.yml --tags tmux --ask-become-pass

fonts:          ## Nur Fonts
	ansible-playbook site.yml --tags fonts

lint:           ## Syntaxpruefung
	ansible-playbook site.yml --syntax-check
