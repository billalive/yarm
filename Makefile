.PHONY: nox tests docs mypy list-sessions coverage

nox:
	nox -r

tests:
	nox -rxs tests

mypy:
	nox -rxs mypy

docs:
	nox -rxs docs

build:
	poetry build

publish:
	poetry publish

run:
	poetry run yarm

list-sessions:
	nox --list-sessions

# https://cookiecutter-hypermodern-python.readthedocs.io/en/2022.6.3.post1/guide.html#version-constraints
lock:
	poetry lock --no-update

coverage:
	coverage html
	xdg-open htmlcov/index.html
