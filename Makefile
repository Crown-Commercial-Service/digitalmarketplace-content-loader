SHELL := /bin/bash
VIRTUALENV_ROOT := $(shell [ -z $$VIRTUAL_ENV ] && echo $$(pwd)/venv || echo $$VIRTUAL_ENV)

virtualenv:
	[ -z $$VIRTUAL_ENV ] && [ ! -d venv ] && virtualenv -p python3 venv || true

requirements: virtualenv requirements.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements.txt

requirements-dev: virtualenv requirements-dev.txt
	${VIRTUALENV_ROOT}/bin/pip install -r requirements-dev.txt

test: test_pep8 test_python

test_pep8: virtualenv
	${VIRTUALENV_ROOT}/bin/pep8 .

test_python: virtualenv
	${VIRTUALENV_ROOT}/bin/py.test ${PYTEST_ARGS}
