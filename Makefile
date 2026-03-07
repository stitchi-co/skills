.PHONY: audit list-skills

audit:
	python3 scripts/skill_audit.py

list-skills:
	@find . -maxdepth 1 -mindepth 1 -type d \
		-not -name '.git' \
		-not -name 'catalog' \
		-not -name 'docs' \
		-not -name 'scripts' \
		-not -name '__pycache__' \
		| sed 's#^./##' | sort
