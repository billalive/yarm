# yarm

Yarm, yet another report maker.

[![PyPI](https://img.shields.io/pypi/v/yarm.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/yarm.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/yarm)][python version]
[![License](https://img.shields.io/pypi/l/yarm)][license]

[![Read the documentation at https://yarm.readthedocs.io/](https://img.shields.io/readthedocs/yarm/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/billalive/yarm/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/billalive/yarm/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/yarm/
[status]: https://pypi.org/project/yarm/
[python version]: https://pypi.org/project/yarm
[read the docs]: https://yarm.readthedocs.io/
[tests]: https://github.com/billalive/yarm/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/billalive/yarm
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

Yarm makes it easy for you to create recurring reports by:

- Importing spreadsheets and CSVs
- Running SQL queries or Python code on this data
- Exporting the results to spreadsheets, CSVs, charts, and more
- All configured in a simple YAML file

## Coming soon...

Yarm is nearly at alpha, but it's not yet ready for release. Come back soon.

## Requirements

- TODO

## Installation

You can install _Yarm_ via [pip] from [PyPI]:

```console
$ pip install yarm
```

## Usage

Please see the [Command-line Reference] for details.

## Documentation

Full documentation is at [yarm.readthedocs.io][read the docs]

## Roadmap: Future Features

These features are not yet implemented, but they're on the roadmap.

### `include`

The `include` key will let you include other config files. For example, if you have a set of tables that you often want to create in different reports, `include` will let you define them once, in one file.

This feature will be powerful, but for now, it's on the roadmap, because the recursion is complex.

It will also require careful thought to ensure that the overrides are intuitive.

For instance, what happens if a table with the same name is defined differently in `tables_config:` in two separate included files? I think that the most recent definition should _completely_ override any previous definitions, because it's quite possible that, without realizing it, you're using the same table name to describe different data.

On the other hand, I would like to be able to override `input:` and `output:` on a key by key basis. For example, I almost always want to set `input.slugify_columns` and `input.lowercase_columns` to `true`, but if I have a report where I need to override `input.lowercase_columns` to `false`, I'd like to be able to do this without also losing my included setting of `input.slugify_columns` as `true`.

So this feature will need some nuance.

### `create_tables`

If you want to include a configuration file that defines more tables than you want for a particular report, you will be able to use `create_tables` to limit the tables for _this_ report to a particular subset.

### (Basic) Visualizations?

Since we're already loading all the data into [pandas], we might as well add [matplotlib] and let you generate some charts, right?

I'm not sure. I can see the use cases, but by the time you start needing charts, it might be time to upgrade to [Jupyter Lab].

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [Apache 2.0 license][license],
_Yarm_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/billalive/yarm/issues
[pip]: https://pip.pypa.io/
[matplotlib]: https://matplotlib.org/
[pandas]: https://pandas.pydata.org/
[jupyter lab]: https://jupyter.org/try

<!-- github-only -->

[license]: https://github.com/billalive/yarm/blob/main/LICENSE
[contributor guide]: https://github.com/billalive/yarm/blob/main/CONTRIBUTING.md
[command-line reference]: https://yarm.readthedocs.io/en/latest/usage.html
