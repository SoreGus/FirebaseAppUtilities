ENV_FILE := ../.env

ifneq (,$(wildcard $(ENV_FILE)))
	include $(ENV_FILE)
	export
endif

PYTHON_BIN ?= python3
VENV_DIR ?= .venv

ROOT_DIR := ..
VENV := $(ROOT_DIR)/$(VENV_DIR)
BIN := $(VENV)/bin
PYTHON := $(BIN)/python
PIP := $(BIN)/pip

.PHONY: help venv install uninstall cli gui clean build

help:
	@echo "FirebaseAppUtilities Python"
	@echo "  make venv      Create the shared virtual environment"
	@echo "  make install   Install package in editable mode"
	@echo "  make uninstall Uninstall the Python package"
	@echo "  make cli       Show CLI help"
	@echo "  make gui       Open the local GUI"
	@echo "  make build     Build wheel and source distribution"
	@echo "  make clean     Remove Python build artifacts"

venv:
	@test -d $(VENV) || $(PYTHON_BIN) -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip

install: venv
	$(PIP) install -e .

uninstall:
	$(PIP) uninstall -y firebase-app-utilities || true

cli:
	$(BIN)/firebase-app-utils --help

gui:
	$(BIN)/firebase-app-utils gui

build: venv
	$(PIP) install --upgrade build
	$(PYTHON) -m build

clean:
	rm -rf build dist *.egg-info src/*.egg-info
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +