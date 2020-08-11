SHELL := /bin/bash
VIRTUALENV_ROOT := $(shell [ -z $$VIRTUAL_ENV ] && echo $$(pwd)/venv || echo $$VIRTUAL_ENV)

.PHONY: virtualenv
virtualenv:
	[ -z $$VIRTUAL_ENV ] && [ ! -d venv ] && python3 -m venv venv || true

.PHONY: requirements
requirements: virtualenv requirements.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements.txt

.PHONY: requirements-dev
requirements-dev: virtualenv requirements.txt requirements-dev.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements.txt -r requirements-dev.txt

.PHONY: freeze-requirements
freeze-requirements: virtualenv requirements-dev requirements-dev.in
	${VIRTUALENV_ROOT}/bin/pip-compile requirements-dev.in

.PHONY: test
test: test-flake8 test-python

.PHONY: test-flake8
test-flake8: virtualenv
	${VIRTUALENV_ROOT}/bin/flake8 .

.PHONY: test-python
test-python: virtualenv
	${VIRTUALENV_ROOT}/bin/py.test ${PYTEST_ARGS}
