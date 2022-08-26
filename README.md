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
- Running **SQL queries** (or, for [pandas] fans, [custom **Python** code][postprocess]) on all this data.
- **Exporting the results** as a new **spreadsheet**, **CSV**, or even SQLite **database**.
- All configured in a [simple **YAML file**][config] for easy **reuse**. Download fresh data, `yarm run`, and you're done.

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

- Collect fresh data. Save it over the old files.

- Run the report.

```yaml
$ yarm run -f
```

- Send the output spreadsheet.

- Take the afternoon off.

## Advanced Usage

Please see the extensive [documentation][read the docs] for more details and features.

## Example Report Config File

You configure a report in a [single YAML file][config].

Each query becomes a separate sheet in your output spreadsheet.

This example config file is moderately complex. Your report can be much simpler; you might have only one or two tables and a single query. (Or you might have ten queries, each with a [custom postprocess function][postprocess]...)

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
    sql: SELECT * FROM order_details as od JOIN products as p ON od.product_id = p.id;

  - name: Orders With Sales Tax
    sql: >
      SELECT orders.*,
      tax.rate
      FROM orders
      JOIN tax
      ON orders.billing_state = tax.state
      ;
    # These query results will need a Python function to complete this sheet:
    postprocess: calculate_tax
    # But first, we can do simple regex replacements right here:
    replace:
      billing_state:
        Virginia: VA
        West Virginia: WV

# Since we need that custom function calculate_tax(), we'll
# write it in a separate Python file.
import:
  - path: custom.py
```

Read more about [basic configuration][config] and [advanced options][options].

## Custom Postprocessing Code

If the power of SQL and make-it-easy options like `slugify_columns` aren't enough for you, you can write a [custom postprocess function][postprocess] for any query you like.

## Status: Alpha (Try It!)

Yarm is currently in **alpha**. Core features are **working** and thoroughly [documented][read the docs].

I rely on `yarm` for my own recurring reports.

If you are desperate to stop doing a recurring report by hand, give _yarm_ a try.

If something breaks, or if you have any suggestions or comments, please [file an issue]. I'd love to hear what you think.

For upcoming features, see the [Roadmap].

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

Complete, _extensive_ documentation is at [yarm.readthedocs.io][read the docs].

Dive right in.

## Is `yarm` for You?

This tool has a clear focus: Make it **easy** to run and **rerun reports** from the **command line** that query **multiple sources** of tabular data.

Once you set up the initial configuration file, the workflow for future reports is simple. Download fresh data over the old files, then rerun the report.

This means that `yarm` is **not** a tool for data **exploration**.

True, you may still want `yarm` to **prepare** your data for exploration. Once you get used to listing a few data sources, setting a few options, and spitting out a nice, clean SQLite database or set of CSV files to play with, you may get hooked.

But for iterative tinkering with your data, you're going to need other tools.

### Other Open Source Tools You Might Prefer

- [sqlitebrowser]: An excellent GUI for exploring your SQLite database. I sometimes use this to **figure out my queries** before I save them into my config file.

- [Jupyter Lab]: If you find your SQL queries getting more and more arcane and complex, it's probably time to learn [pandas], and that means unleashing the power of this [interactive "notebook"][jupyter lab]. Some reports are so complex that they really deserve to be run step-by-step, with immediate output after every command. Jupyter Lab makes that absurdly easy... and repeatable.

- [SQL Notebook]: A newer offering that I haven't used yet, but it looks like an interesting GUI combination of sqlitebrowser and a "Jupyter-style notebook interface". Could be very powerful.

- For quick, **one-off** data manipulations on the **command line**, you can reach for excellent tools like [jq] for JSON, [mlr] for CSV, and even [htmlq] for HTML. But once the command gets long and complex enough that you want to save it to a script, you might start missing SQL queries and `yarm` features like `slugify_columns: true`.

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
[sqlitebrowser]: https://sqlitebrowser.org/
[sql notebook]: https://sqlnotebook.com/
[jq]: https://stedolan.github.io/jq/
[mlr]: https://miller.readthedocs.io/en/latest/
[htmlq]: https://github.com/mgdm/htmlq
[config]: https://yarm.readthedocs.io/en/latest/config/
[options]: https://yarm.readthedocs.io/en/latest/config/options.html
[postprocess]: https://yarm.readthedocs.io/en/latest/postprocess.html
[roadmap]: https://yarm.readthedocs.io/en/latest/roadmap.html

<!-- github-only -->

[license]: https://github.com/billalive/yarm/blob/main/LICENSE
[contributor guide]: https://github.com/billalive/yarm/blob/main/CONTRIBUTING.md
[command-line reference]: https://yarm.readthedocs.io/en/latest/usage.html
