test:
	nox -r

build:
	poetry build

publish:
	poetry publish

run:
	poetry run yarm

list-sessions:
	nox --list-sessions
