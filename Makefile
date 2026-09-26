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
	@echo "  make check-python    Validate Python"
	@echo "  make python-install  Install the Python package locally"
	@echo "  make python-cli      Show the Python CLI help"
	@echo "  make python-gui      Open the Python GUI"
	@echo "  make clean           Remove local build artifacts"

check-python:
	@echo "Checking Python..."
	@$(PYTHON_BIN) --version
	@$(PYTHON_BIN) -c "import sys; assert sys.version_info >= (3, 12), f'Python 3.12+ required, found {sys.version.split()[0]}'"
	@echo "Python: OK"

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