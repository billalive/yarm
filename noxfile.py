#!/usr/bin/env python3

import tempfile

import nox

locations = "src", "tests", "noxfile.py"
nox.options.sessions = "lint", "safety", "tests"


@nox.session(python=["3.10", "3.9", "3.8", "3.7"])
def tests(session):
    args = session.posargs or ["--cov"]
    session.run("poetry", "install", external=True)
    session.run("pytest", *args)


@nox.session(python=["3.10", "3.9", "3.8", "3.7"])
def lint(session):
    args = session.posargs or locations
    session.install("flake8", "flake8-black", "flake8-import-order")
    session.run("flake8", *args)


@nox.session(python=["3.10", "3.9", "3.8", "3.7"])
def black(session):
    args = session.posargs or locations
    session.install("black")
    session.run("black", *args)


@nox.session(python=["3.10", "3.9", "3.8", "3.7"])
def safety(session):
    with tempfile.NamedTemporaryFile() as requirements:
        session.run(
            "poetry",
            "export",
            "--dev",
            "--format=requirements.txt",
            "--without-hashes",
            f"--output={requirements.name}",
            external=True,
        )
        session.install("safety")
        session.run("safety", "check", f"--file={requirements.name}", "--full-report")
