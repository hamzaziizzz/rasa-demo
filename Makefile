SHELL := /bin/bash

# Path to the virtual environment's activate script
VENV_PATH := .venv/bin/activate

help:
	@source $(VENV_PATH) && echo "make"
	@source $(VENV_PATH) && echo "    install"
	@source $(VENV_PATH) && echo "        Install all requirements for running the bot."
	@source $(VENV_PATH) && echo "    install-dev"
	@source $(VENV_PATH) && echo "        Install all requirements for development."
	@source $(VENV_PATH) && echo "    clean"
	@source $(VENV_PATH) && echo "        Remove Python/build artifacts."
	@source $(VENV_PATH) && echo "    formatter"
	@source $(VENV_PATH) && echo "        Apply black formatting to code."
	@source $(VENV_PATH) && echo "    lint"
	@source $(VENV_PATH) && echo "        Lint code with flake8, and check if black formatter should be applied."
	@source $(VENV_PATH) && echo "    types"
	@source $(VENV_PATH) && echo "        Check for type errors using pytype."
	@source $(VENV_PATH) && echo "    test-actions"
	@source $(VENV_PATH) && echo "        Run custom action unit tests"

install:
	@source $(VENV_PATH) && python3 -m pip install --upgrade pip
	@source $(VENV_PATH) && python3 -m pip install --upgrade setuptools wheel
	@source $(VENV_PATH) && python3 -m pip install -r requirements.txt
	@source $(VENV_PATH) && python3 -m spacy download en_core_web_md
	@source $(VENV_PATH) && python3 -m pip install -e .

install-dev:
	@source $(VENV_PATH) && python3 -m pip install --upgrade pip
	@source $(VENV_PATH) && python3 -m pip install -r requirements-dev.txt
	@source $(VENV_PATH) && python3 -m spacy download en_core_web_md
	@source $(VENV_PATH) && python3 -m spacy link en_core_web_md en
	@source $(VENV_PATH) && python3 -m pip install -e .

clean:
	@source $(VENV_PATH) && find . -name '*.pyc' -exec rm -f {} +
	@source $(VENV_PATH) && find . -name '*.pyo' -exec rm -f {} +
	@source $(VENV_PATH) && find . -name '*~' -exec rm -f  {} +
	@source $(VENV_PATH) && rm -rf build/
	@source $(VENV_PATH) && rm -rf .pytype/
	@source $(VENV_PATH) && rm -rf dist/
	@source $(VENV_PATH) && rm -rf docs/_build

formatter:
	@source $(VENV_PATH) && black --verbose --config pyproject.toml actions tests

lint:
	@source $(VENV_PATH) && flake8 actions tests
	@source $(VENV_PATH) && black --check --verbose --config pyproject.toml actions tests

types:
	@source $(VENV_PATH) && pytype --keep-going actions tests

test-actions:
	@source $(VENV_PATH) && pytest . -vv
