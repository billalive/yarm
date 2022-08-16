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

3.10:
	pyenv local 3.10.5
	poetry env use 3.10.5

3.9:
	pyenv local 3.9.12
	poetry env use 3.9.12

3.7:
	pyenv local 3.7.13
	poetry env use 3.7.13

jupyter:
	poetry run jupyter notebook
