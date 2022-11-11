.PHONY: nox tests docs mypy list-sessions coverage

# Disable keyring, see 1.2.0 bug:
# https://github.com/python-poetry/poetry/issues/1917
POETRY=PYTHON_KEYRING_BACKEND=keyring.backends.null.Keyring poetry

nox:
	nox -r

tests:
	nox -rxs tests

mypy:
	nox -rxs mypy

typeguard:
	nox -rxs typeguard

docs:
	nox -rxs docs

build:
	$(POETRY) build

# NOTE You will need your own local keyring to publish an update to PyPi.
publish:
	poetry publish

run:
	$(POETRY) run yarm

update:
	$(POETRY) update

list-sessions:
	nox --list-sessions

# https://cookiecutter-hypermodern-python.readthedocs.io/en/2022.6.3.post1/guide.html#version-constraints
lock:
	$(POETRY) lock --no-update

coverage:
	coverage html
	xdg-open htmlcov/index.html

3.10:
	pyenv local 3.10.5
	$(POETRY) env use 3.10.5

3.9:
	pyenv local 3.9.12
	$(POETRY) env use 3.9.12

3.7:
	pyenv local 3.7.13
	$(POETRY) env use 3.7.13

jupyter:
	$(POETRY) run jupyter notebook
