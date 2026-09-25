ENV_FILE := .env

ifneq (,$(wildcard $(ENV_FILE)))
	include $(ENV_FILE)
	export
endif

PYTHON_BIN ?= python3
VENV_DIR ?= .venv
PYTHON := $(VENV_DIR)/bin/python

.PHONY: help setup check-python python-install python-cli python-gui clean

help:
	@echo "FirebaseAppUtilities"
	@echo ""
	@echo "  make setup           Validate environment, create virtualenv and install Python package"
	@echo "  make check-python    Validate Python and Tkinter"
	@echo "  make python-install  Install the Python package locally"
	@echo "  make python-cli      Show the Python CLI help"
	@echo "  make python-gui      Open the Python GUI"
	@echo "  make clean           Remove local build artifacts"

check-python:
	@echo "Checking Python..."
	@$(PYTHON_BIN) --version
	@echo "Checking Tkinter..."
	@$(PYTHON_BIN) -c "import sys; exec('try:\\n import tkinter\\n print(\"Tkinter: OK\")\\nexcept Exception as error:\\n version = f\"{sys.version_info.major}.{sys.version_info.minor}\"\\n print()\\n print(\"ERROR: Tkinter is not available for the configured Python.\")\\n print()\\n print(f\"Python: {sys.executable}\")\\n print(f\"Version: {version}\")\\n print(f\"Reason: {error}\")\\n print()\\n print(\"If this Python was installed with Homebrew, install:\")\\n print(f\"  brew install python-tk@{version}\")\\n print()\\n sys.exit(1)')"

setup: check-python
	@echo ""
	@echo "Setting up FirebaseAppUtilities..."
	@test -f .env || cp .env-example .env
	$(PYTHON_BIN) -m venv $(VENV_DIR)
	$(PYTHON) -m pip install --upgrade pip
	$(MAKE) -C python install
	@echo ""
	@echo "FirebaseAppUtilities setup complete."

python-install:
	$(MAKE) -C python install

python-cli:
	$(MAKE) -C python cli

python-gui:
	$(MAKE) -C python gui

clean:
	$(MAKE) -C python clean
	rm -rf $(VENV_DIR)