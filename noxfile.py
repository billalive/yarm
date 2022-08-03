#!/usr/bin/env python3

import nox

locations = "src", "tests", "noxfile.py"


@nox.session(python=["3.10", "3.9", "3.8", "3.7"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python=["3.10", "3.9", "3.8", "3.7"])
def lint(session):
    args = session.posargs or locations
    session.install("flake8")
    session.run("flake8", *args)
