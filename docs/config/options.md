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
    :emphasize-lines: 1

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
    :emphasize-lines: 1

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

.. include:: altered_columns.rst
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

.. include:: altered_columns.rst
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

```{eval-rst}
.. _input-include-index:
```

### `include_index:`

```{eval-rst}
If omitted, defaults to ``false``, *except* for tables which use `pivot:`_. Pivot tables default to ``true`` (see below.)

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
    :emphasize-lines: 1

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

### Table Source Order of Operations

No matter what order you place these keys within each table source, the operations run in this order:

```{eval-rst}
1. The file in `path: <table-source-path>`_ (and, for a spreadsheet, the `sheet:`_ for this path), is read into the database.
2. If `pivot:`_ is defined, the table is pivoted. (This will usually create many new columns.)
3. If `datetime:`_ is defined, those columns are formatted.

.. seealso::
  Table operations order is set in: :func:`yarm.tables.df_tables_config_options`
```

### `path:`

```{eval-rst}

.. _table-source-path:

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

### `pivot:`

_Optional._ Pivot a table.

```{eval-rst}
.. literalinclude:: /validate/validate_key_tables_config_pivot.yaml
    :language: yaml
    :emphasize-lines: 4-7

.. include :: altered_columns_tables_config.rst
```

#### How Does Pivoting Work?

Pivoting is easiest to understand with an example.

In [WordPress](https://wordpress.org), there's a table called `postmeta`, used for storing extra _meta_ information about the _posts_. In theory, the designers could have tried to predict every kind of information that anyone would ever want to attach to their posts... plus every third-party plugin that would ever be written... and then made sure to add enough columns to cover every possible use case.

Right.

Instead, `postmeta` is extremely flexible. Each row has only four columns:

- `META_ID`
- `POST_ID`
- `META_KEY`
- `META_VALUE`

A few random rows from this table might look like this:

| META_ID | POST_ID | META_KEY       | META_VALUE  |
| ------- | ------- | -------------- | ----------- |
| 1000    | 42      | export_format  | pdf         |
| 1001    | 42      | shareability   | 97          |
| 1002    | 42      | oxford_commas  | 18          |
| 1003    | 43      | export_format  | docx        |
| 1004    | 43      | puppy_mentions | 0           |
| 1005    | 43      | shareability   | 31          |
| 1006    | 44      | export_format  | calligraphy |
| 1007    | 44      | unironic       | 1           |

As you can see, each row is bound to a particular post by `POST_ID`, and `META_KEY` is _basically_ a column name.

But trying to query this table would be a pain. It would be much easier if the data looked like this:

| POST_ID | export_format | shareability | oxford_commas | puppy_mentions | unironic |
| ------- | ------------- | ------------ | ------------- | -------------- | -------- |
| 42      | pdf           | 97           | 18            | NULL           | NULL     |
| 43      | docx          | 31           | NULL          | 0              | NULL     |
| 44      | calligraphy   | NULL         | NULL          | NULL           | 1        |

Which is what this bit of `pivot:` config will do:

```{eval-rst}
.. literalinclude:: /validate/validate_key_tables_config_pivot.yaml
    :language: yaml
```

#### `pivot:` and `include_index:`

```{eval-rst}
When a source is pivoted, the ref:`include_index: <table-include-index>` for the entire table
is automatically set to ``true``. This is because the index column was present in your original
data, so you probably expect to see it in the output.

If you don't want to see that index column, add ``include_index: false`` to **this source**.

It's not enough to set the overall ``include_index`` to ``false`` up in
:ref:`input: <input-include-index>`, because that already defaults to ``false``,
*except for pivot tables*.
```

#### A Pivot Only Affects This Source

```{eval-rst}
If your table includes multiple sources, only those sources with a `pivot:` block will be pivoted.

But you need to ensure that the non-pivoted source and the pivoted source (*after* its pivot) share at least one column, so they can merge. See `Multiple Sources Get Merged`_.
```

### `include_index:`

```{eval-rst}
*Optional.* Override the :ref:`overall value of include_index: <input-include-index>` for **this table**.

``true``
  For **this table**, include a separate column for the index in the final output.

``false``
  For **this table**, Silently omit the index column.

.. important::
   Unlike other keys in a source, this key affects the entire table. So you can only set it
   **once** in any particular table. It doesn't matter which source you choose.
   If you try to set ``include_index:`` on more than one source in a table, you'll get an error.
```

### `datetime:`

_Optional._ One or more columns that should be converted to `datetime` format.

Each column should be added as a key.

If you omit any value for the key, then the column will be converted to the default datetime format.

If you include a format string as the value, the column will formatted with that string. (See [Formatting Codes].)

```{eval-rst}
.. literalinclude:: /validate/validate_key_tables_config_datetime.yaml
    :language: yaml
    :emphasize-lines: 4-10

.. important ::
  Because these are keys in the same block, each column name must be **unique**.

.. include :: altered_columns_tables_config.rst

.. warning ::
  Similarly, if you `pivot:`_ the table, you will get a whole new set
  of columns than the original data. You need to use those **new**** column names here,
  not the column names in the original data.
```

[formatting codes]: https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

## `import:`

_Optional,_ but you need it if you set a `postprocess:` function for a query.

```{eval-rst}
.. literalinclude:: /validate/validate_key_import.yaml
    :language: yaml
    :emphasize-lines: 1

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

.. _import-path:

**REQUIRED.** Path to Python module (``.py`` file) where you have defined your `postprocess:`_ function(s).

.. include:: path_relative.rst

.. note::
   You can define more than one function in a file, so you normally will only need one `path:`.

```

```{eval-rst}
.. _queries:
```

## `queries:`

**REQUIRED,** _unless_ you set `output: export_csv`. (You need to output _something_.)

```{eval-rst}
.. literalinclude:: /validate/validate_key_queries.yaml
    :language: yaml
    :emphasize-lines: 1

.. note::
    Defined in: :func:`yarm.validate.validate_key_queries`

.. warning::
   Unlike tables in `tables_config:`_, each query is a **list item**. See :ref:`query-list-item`. The order in which you list the queries matters, at least if you want a later query to refer to an earlier query. The order of keys *within* each query does not matter, because the keys are always processed in the same order. See :ref:`when-does-order-matter`
```

In this block, you define one or more queries.

Each query will be output to either a single CSV file or a sheet in a spreadsheet.

Within each query, some keys are **REQUIRED**, while others are _Optional_.

### Query Order of Operations

No matter what order you place these keys, the operations run in this order:

```{eval-rst}
1. The statement in `sql:`_ is run, generating the query result.
2. If defined, the `replace:`_ items are processed.
3. Last of all, if it's defined, the data is run through the `postprocess:`_ function.

.. seealso::
  Query operations order is set in: :func:`yarm.queries.query_options`
```

### `name:`

**REQUIRED.** Name for this query.

The name is used:

- As the name of the database table that holds this query.

- When output to a spreadsheet: as the name of the sheet that contains this query.

- When output to CSV: as the filename for this CSV.

```{eval-rst}

.. _query-name:

.. important ::
   Use a **unique name** for each query. Do not use a name that you've already used for
   another query, or **even a table** in `tables_config:`_ Conflicting names will cause problems
   for the internal database. Case does not matter here, so ``QUERY A`` and ``query A``
   would conflict.
```

### `sql:`

**REQUIRED.** The SQL statement for this query.

```{eval-rst}
For readability, this can be a **multiline string**. See :ref:`sql-multiline`.

.. warning ::
   If you have altered your data in any earlier options, such as `input:`_ or `tables_config:`_,
   make sure you query this altered data.

   For instance, if you used `pivot:`_, you need to `SELECT` from the new columns you've created,
   not the columns in the original data.

   By contrast, all **other options in this block** run **after** this SQL statement.
   If you use `replace:`_ or `postprocess:`_, they can only operate on


```

### `replace:`

```{eval-rst}
*Optional.* After you have run the query in `sql:`_, you can find and replace data within particular columns.

.. literalinclude:: /validate/validate_key_queries.yaml
    :language: yaml
    :emphasize-lines: 17-23

.. important::
   Each match and replace happens **within one column**. If you need to find and replace the
   same patterns across multiple columns, you will need to define them separately for each column.

.. warning::
  If you have altered the data at any point (e.g. `uppercase_rows:`_), you'll need to
  match that altered data here.
```

Note that in this block, we do **not** use any lists.

Each column is a key, and within each column, each match pattern is a key.

#### Replacements Can Occur In Any Order

Because we're using matches as keys, not list items, replacements can occur in any order.

This has not been a problem for me yet, because I haven't needed to do cascading replacements that depend on earlier replacements.

This block is intended for casual, cosmetic replacements for reports, like replacing `member_level1` with `Bronze`.

```{eval-rst}
If your needs are more complex, you may want to write a :doc:`postprocess function </postprocess>`.
```

That said, if I get [feedback] that a strict order of replacements is desirable, I'm open to adding the extra code to allow processing this block as a list (or list of lists).

### `postprocess:`

```{eval-rst}
*Optional.* After you have run the query in `sql:`_ and applied any other alterations (currently just `replace:`_), run the data through this custom function you have defined.

.. important::
   This function must be defined in one of the ``.py`` files imported with `import:`_

.. seealso::
   For full details and examples on writing a postprocess function, see:
   :doc:`/postprocess`

```

[feedback]: https://github.com/billalive/yarm/issues
