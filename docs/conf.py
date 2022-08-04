"""Sphinx configuration."""
project = "Yarm"
author = "Bill Alive"
copyright = "2022, Bill Alive"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"
