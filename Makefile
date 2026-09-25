ENV_FILE := .env

ifneq (,$(wildcard $(ENV_FILE)))
	include $(ENV_FILE)
	export
endif

PYTHON_BIN ?= python3
VENV_DIR ?= .venv
PYTHON := $(VENV_DIR)/bin/python

.PHONY: help setup python-install python-gui swift-resolve clean

help:
	@echo "FirebaseAppUtilities"
	@echo "  make setup           Create .env, virtual environment and install Python package"
	@echo "  make python-install  Install the Python package locally"
	@echo "  make python-gui      Open the Python GUI"
	@echo "  make swift-resolve   Resolve Swift Package dependencies"
	@echo "  make clean           Remove local build artifacts"

setup:
	@test -f .env || cp .env.example .env
	$(PYTHON_BIN) -m venv $(VENV_DIR)
	$(PYTHON) -m pip install --upgrade pip
	$(MAKE) -C python install

python-install:
	$(MAKE) -C python install

python-gui:
	$(MAKE) -C python gui

swift-resolve:
	cd swift && swift package resolve

clean:
	$(MAKE) -C python clean
	rm -rf $(VENV_DIR)
	rm -rf swift/.build swift/.swiftpm