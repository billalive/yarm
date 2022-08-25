# Configuration Options

This page explains each configuration option in detail.

```{eval-rst}
For documentation on actual functions, see the :doc:`Reference <../reference>`.
```

## Overview

Remember, the basic steps for your configuration file are:

```{eval-rst}
.. include:: basic.rst
```

### Does Order Matter?

Order does **not** matter for keys, including top-level keys like `output:`. You can put the `output:` block at the top, at the end, wherever you want.

Within a block, you can order the keys however you want. E.g., each table in `tables_config:` is a key, so it doesn't matter which table you define first.

But order **does** matter for **list** items. E.g., within `import:`, it _does_ matter which order you import sources. The order is up to you, and for most reports, the order probably won't affect the outcome. You just need to be aware that list items are necessarily processed in the order you write them, while keys aren't.

```{eval-rst}
See :ref:`when-does-order-matter`
```

## `output:`

**REQUIRED.**

Configures your final report.

```{eval-rst}
.. literalinclude:: /validate/validate_key_output.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_output`
```

### `dir`:

**REQUIRED.** The output directory for your report and other exports.

If the directory does not exist, it will be created.

```{eval-rst}
.. include:: path_relative.rst

.. tip::

    When you rerun a report, you will usually need to overwrite the output from your last report.
    If you don't want to manually confirm each overwrite, add ``-f`` or ``--force``.
```

### `basename`:

**REQUIRED.** The basename for your output file(s).

```{eval-rst}
The way this basename is used depends on your export choices. See `export_tables:`_ and `export_queries:`_ below.
```

### `export_tables`:

_Optional._ Output format for your tables.

If omitted, **no** tables are exported.

```{eval-rst}
``csv``
  Export each table as a separate CSV file, named with the table's ``name:`` key.

``xlsx``
  Export each table as a separate sheet in a single spreadsheet named ``tables.xlsx``.

All files are exported to the output directory set in `dir:`_ above.
```

### `export_queries`:

_Optional._ Output format for your queries.

If omitted, defaults to `xlsx`.

```{eval-rst}
``csv``
  Export each query as a separate CSV file.

``xlsx``
  Export each query as a separate sheet in a single spreadsheet named with `basename:`_ (see above) and extension ``xlsx``.
```

### `styles`:

_Optional._ Options for formatting your output.

#### `column_width`:

_Optional._ Set the width for columns in your output spreadsheet.

This should be an integer.

If omitted, this will be an internal default.

#### TODO

_Add more output styling options?_

## `input:`

_Optional._ Options for modifying your input tables before you run the queries.

```{eval-rst}
.. literalinclude:: /validate/validate_key_input.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_input`

.. important::
    In general, if you omit any of these options, your data will be **unchanged**.
    Yarm only alters your data if you tell it to.

    Since you can omit this entire block, all options in this section are optional.
```

### `strip:`

If omitted, defaults to `false`.

```{eval-rst}
``true``
  Strip all **whitespace** from beginning and end of each data cell.

``false``
  Data is unchanged.
```

### `slugify_columns:`

If omitted, defaults to `false`.

```{eval-rst}
``true``
  "Slugify" all column names. This replaces all punctuation and spaces with an underscore.
  Rows stay unchanged.

``false``
  Data is unchanged.

.. seealso::
  This option does not change case. To also lowercase your columns, see `lowercase_columns:`_

.. attention::
  If you alter your column names, be sure to use these altered names in your queries.
```

### `lowercase_columns:`

If omitted, defaults to `false`.

```{eval-rst}
``true``
  Lowercase all column names. Rows stay unchanged.

``false``
  Data is unchanged.

.. seealso::
  You may also want to use `slugify_columns:`_

.. attention::
  If you alter your column names, be sure to use these altered names in your queries.
```

### `uppercase_rows:`

If omitted, defaults to `false`.

```{eval-rst}
``true``
  UPPERCASE the data in all **rows**. Column names stay unchanged.

``false``
  Data is unchanged.

.. note::
  Uppercasing makes your data more consistent, which can be useful for data like addresses.
```

### `include_index:`

If omitted, defaults to `false`, _except_ for tables which use `pivot:`\_. Pivot tables default to `true` (see below.)

```{eval-rst}
``true``
  Include a separate column for the index in the final output.

``false``
  Silently omit the index column.

.. important::
   You can override this value for each particular table in `tables_config:`_.
```

When each table is created in the database, an index column is also created. Usually, this index is added automatically, so it's confusing and unnecessary to see it in the final output.

Pivot tables are different, because in order to pivot a table, we manually set one of the original columns as the index. In this case, we default to `true`, so that this original column is kept in our final output.

## `tables_config:`

**REQUIRED.** Define one or more tables of source data.

```{eval-rst}
.. literalinclude:: /validate/validate_key_tables_config.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_tables_config`
```

### Each Table Needs a Unique Name

In this example, we define two tables, `TABLE_NAME_A` and `TABLE_NAME_B`. (Your tables will probably have slightly more normal names, like `Customers`.)

```{eval-rst}
Each table name must be **unique**, distinct not only from other tables but also from your queries (see `query:name: <query-name>`_).
```

**Avoid spaces and punctuation.** You'll be referencing these names in your queries, and if you don't use simple table names, you'll need to quote them in the query, which is a needless hassle.

### Each Table Is a List of Sources

Underneath each table, you have a **list** of one or more **sources**.

Each source is **one** table of data. Such as:

- A CSV file
- One sheet in a spreadsheet

Most tables probably only need one source. You take a CSV file or a sheet in a spreadsheet, and you turn it into a table. Simple.

#### Multiple Sources Get Merged

But sometimes you want to combine two or more CSVs or sheets into a single table. You can do this, as long as all the sources share at least **one column** in common.

```{eval-rst}
Behind the scenes, each source gets merged as an *outer join* (see :func:`yarm.tables.input_source`), and this requires a shared column.
```

In the example config above, both `SOURCE_B1.csv` and `SOURCE_B2.csv` get merged into a single table, `TABLE_NAME_B`.

### Source Options

```{eval-rst}
Each source must have, at minimum, a `path: <table-source-path>`_. But you have other options as well.
```

Remember, each source is a **separate list item** beneath its table.

### `path:`

```{eval-rst}

.. _table-source-path::

**REQUIRED.** Path to source file.

.. include:: path_relative.rst
```

#### Valid file formats for source paths:

- `.csv`
- `.xlsx`

### `sheet:`

_Optional._ Name or number of sheet in spreadsheet.

Only relevant for spreadsheets.

If omitted, the first sheet will be used.

```{eval-rst}
.. important::
    Normally, you'll probably use the **name** of the spreadsheet.
    If you opt to use the **number**, note that **numbering starts at 0**.
    The first sheet is ``0``, the second is ``1``, etc.
```

### `datetime:`

_Optional._ One or more columns ()

## `import:`

_Optional,_ but you need it if you set a `postprocess:` function for a query.

```{eval-rst}
.. literalinclude:: /validate/validate_key_import.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_import`

.. warning ::
   If more than one module in this list defines the same function,
   the **later module** in the list will **silently override** the
   previous definition.

   This may be desired behavior, but only if you expect it.

```

### `path:`

```{eval-rst}

.. _table-source-path::

**REQUIRED.** Path to Python module (``.py`` file).

.. include:: path_relative.rst
```

## `queries:`

**REQUIRED,** _unless_ you set `output: export_csv`. (You need to output _something_.)

```{eval-rst}
.. literalinclude:: /validate/validate_key_queries.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_queries`

```

### `name:`

```{eval-rst}

.. _query-name:

.. warning ::
   Use a **unique name** for each query. Do not use a name that you've already used for
   another query, or **even a table** in `tables_config:`_ Conflicting names will cause problems
   for the internal database. Case does not matter here, so ``QUERY A`` and ``query A``
   would conflict.
```
