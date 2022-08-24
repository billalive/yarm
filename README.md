# yarm

Yarm: Yet Another Report Maker.

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

Yarm makes it easy for you to create **recurring reports** by:

- Importing **multiple spreadsheets and CSVs** into a temporary database.
- Offering **easy** options for **common data cleaning** tasks (e.g. `replace`, `slugify_columns`, `pivot`)
- Running **SQL queries** (or, for [pandas] fans, **Python** code) on all this data.
- **Exporting the results** as a new spreadsheet or CSV.
- All configured in a simple **YAML file** for easy **reuse**. Download fresh data, `yarm run`, and you're done.

## Basic Usage

### First Time You Run a New Report

- Collect your XLSX and/or CSV data files into a directory for this report.

- Initialize a new YAML config file:

```console
$ yarm new
```

- Edit the YAML config file (see below).

  - Configure your input spreadsheets and CSV files as tables.
  - Write one or more [SELECT] queries on these tables to create output sheets.
  - (Optional) Need advanced manipulation of your data? Write [pandas] code in a separate `.py` file.

- Run the report:

```yaml
$ yarm run
```

- Send the output spreadsheet to your boss/client/head of state. Was it really that easy?

### Every Subsequent Time

- Collect your data.

- Run the report:

```yaml
$ yarm run
```

- Send the output spreadsheet.

- Take the afternoon off.

## Advanced Usage

Please see the [documentation][read the docs] for more details and features.

## Example Report Config File

You configure a report in a single YAML file.

Each query becomes a separate sheet in your output spreadsheet.

This example config file is moderately complex. Your report can be much simpler; you might have only one or two tables and a single query. (Or you might have ten queries, each with a custom `postprocess` function...)

```yaml
---
output:
  dir: Output
  basename: Sales_Report

# Optional input options (more are available):
input:
  slugify_columns: true
  lowercase_columns: true

# Set up your data sources:
tables_config:
  # CSV file: the easiest data source.
  products:
    - path: Products.csv

  # Spreadsheet: You need both the path and the sheet name.
  orders:
    - path: Orders.xlsx
      sheet: Orders

  # You can import different sheets as separate tables.
  order_details:
    - path: Orders.xlsx
      sheet: Order Details

  # You can combine multiple data sources into a single table,
  # as long as their columns can be merged.
  tax:
    - path: Sales Tax Rates Northeast.xlsx
      sheet: NY
    - path: Sales Tax Rates Northeast.xlsx
      sheet: PA
    - path: TAXES_SOUTH.csv

# Set up your output spreadsheet:
queries:
  - name: Order Details with Product Names
    sql: |
      SELECT *
      FROM order_details as od
      JOIN products as p
      ON od.product_id = p.id
      ;

  - name: Orders With Sales Tax
    # These query results will need a Python function to complete this sheet:
    postprocess: calculate_tax
    # But we can do simple regex replacements right here:
    replace:
      billing_state:
        Virginia: VA
        West Virginia: WV
    sql: |
      SELECT orders.*,
      tax.rate
      FROM orders
      JOIN tax
      ON orders.billing_state = tax.state
      ;

# Since we need that custom function calculate_tax(), we'll
# write it in a separate Python file.
import:
  - path: custom.py
```

## Status: Alpha

Yarm is currently in **alpha**. Core features are already working, so if you are desperate to stop doing a recurring report by hand, give _yarm_ a try.

Then [file an issue] if something breaks. 😉

For more features and better [documentation][read the docs], come back soon.

## Requirements

- Python 3.7 or later
- A terminal
- One or more spreadsheets that you want to query
- Something to do with all this impending free time...

## Installation

You can install _yarm_ via [pip] from [PyPI]:

```console
$ pip install yarm
```

But since _yarm_ is a command line tool, you may prefer the excellent [pipx]:

```console
$ pipx install yarm
```

## Documentation

Full documentation is at [yarm.readthedocs.io][read the docs]

## Roadmap: Future Features

These features are not yet implemented, but they're on the roadmap.

### Import/Export other file formats?

In theory, it should be easy to import/export any file format that [pandas] can handle. (In _theory_.)

- JSON?
- SQL?
- HDF5?
- Anything else?

### `include` other config files

The `include` key will let you include other config files. For example, if you have a common set of data files that you often want to use in different reports, `include` will let you define their tables once, in one file.

This feature will be powerful, but for now, it's on the roadmap, because the recursion is complex.

It will also require careful thought to ensure that the overrides are intuitive.

For instance, what happens if a table with the same name is defined differently in `tables_config:` in two separate included files? I think that the most recent definition should _completely_ override any previous definitions, because it's quite possible that, without realizing it, you're using the same table name to describe different data.

On the other hand, I would like to be able to override `input:` and `output:` on a key by key basis. For example, I almost always want to set `input.slugify_columns` and `input.lowercase_columns` to `true`, but if I have a report where I need to override `input.lowercase_columns` to `false`, I'd like to be able to do this without also losing my included setting of `input.slugify_columns` as `true`.

So this feature will need some nuance.

### `create_tables`

If you want to include a configuration file that defines more tables than you want for a particular report, you will be able to use `create_tables` to limit the tables for _this_ report to a particular subset.

### Visualizations?

Since we're already loading all the data into [pandas], we might as well add [matplotlib] and let you generate some charts, right?

I'm not sure. I can see the use cases, but if you need charts, it might be time to upgrade to [Jupyter Lab].

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [Apache 2.0 license][license],
_Yarm_ is free and open source software.

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/billalive/yarm/issues
[pip]: https://pip.pypa.io/
[pipx]: https://pypa.github.io/pipx/
[matplotlib]: https://matplotlib.org/
[pandas]: https://pandas.pydata.org/
[jupyter lab]: https://jupyter.org/try
[select]: https://www.sqlite.org/lang_select.html

<!-- github-only -->

[license]: https://github.com/billalive/yarm/blob/main/LICENSE
[contributor guide]: https://github.com/billalive/yarm/blob/main/CONTRIBUTING.md
[command-line reference]: https://yarm.readthedocs.io/en/latest/usage.html
