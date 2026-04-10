SHELL := /bin/bash
.DEFAULT_GOAL := help

PYTHON ?= python3
CODEX_HOME ?= $(HOME)/.codex
VALIDATOR := $(CODEX_HOME)/skills/.system/skill-creator/scripts/quick_validate.py
SKILL_DIRS := $(sort $(wildcard .agents/skills/*))
NEW_CHARACTER_SCRIPT := .agents/skills/last-epoch-offline-new-character/scripts/bootstrap_character.py
RESET_SPECIALIZATIONS_SCRIPT := .agents/skills/last-epoch-specialization-reset/scripts/reset_specializations.py

.PHONY: help validate test smoke smoke-scripts

help:
	@printf "Targets:\n"
	@printf "  make validate      Validate SKILL.md frontmatter and required UI metadata\n"
	@printf "  make test          Run fixture-based CLI tests\n"
	@printf "  make smoke         Run validate + test + script CLI smoke checks\n"

validate:
	@test -f "$(VALIDATOR)" || { echo "quick_validate.py not found at $(VALIDATOR)"; exit 1; }
	@for skill in $(SKILL_DIRS); do \
		echo "Validating $$skill"; \
		$(PYTHON) "$(VALIDATOR)" "$$skill" || exit $$?; \
		test -f "$$skill/agents/openai.yaml" || { echo "Missing $$skill/agents/openai.yaml"; exit 1; }; \
	done

test:
	$(PYTHON) -m unittest discover -s tests -v

smoke-scripts:
	$(PYTHON) "$(NEW_CHARACTER_SCRIPT)" --help > /dev/null
	$(PYTHON) "$(RESET_SPECIALIZATIONS_SCRIPT)" --help > /dev/null

smoke: validate test smoke-scripts
