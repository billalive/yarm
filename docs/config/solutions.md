# Solutions to Common Config Problems

Your report won't run? These tips might help.

```{eval-rst}
.. _right-dir:
```

## Are You In the Right Directory?

A normal config file will have relative paths that assume that all the files
you need are in the same directory. If your config file `yarm.yaml` includes this...

```{eval-rst}
.. literalinclude:: /validate/validate_key_import.yaml
    :language: yaml
.. literalinclude:: /validate/validate_key_tables_config.yaml
    :language: yaml
```

... then your directory, let's call it `report/` should look like this:

```
report/:

MODULE_A.py
MODULE_B.py
SOURCE_A.xlsx
SOURCE_B1.csv
SOURCE_B2.csv
yarm.yaml
```

As long as you are in this directory, you should be able to run your report.

```bash
# SUCCESS! This should work:
yarm run
```

But what if you change to a different directory? Can you use `-c` to read the config? **No.**

```bash
# FAIL!
cd ..
yarm run -c report/yarm.yaml
```

Why does this fail? Because `yarm` looks around for files like `MODULE_A.py`, and it can't find any of them. You're in the wrong directory.

### Basic Solution

Always run yarm from the same directory as your config file.

### Advanced Solution

If you already use tools like [`make`][makefile], you can easily switch into the correct directory before running `yarm`.

For instance, you could add a simple `Makefile` to your `report/` dir:

```Makefile
run:
    yarm run -f
```

Now, wherever you are in your filesystem, you can do...

```bash
make -C /path/to/report/ run
```

... and `yarm` will correctly write your output files to `report/output/`.

Now you can alias that long `make` command to a shortcut... or create a separate Makefile with commands for all your most common reports... the possibilities are limitless...

## Fix Invalid YAML

Sadly, sometimes the solution is more complex than switching to the right directory.

First and foremost, the config file can't have any syntax mistakes.

When you get a syntax error, usually you just need to add a colon or an indent (or two).

If you get stuck, you can consult any basic YAML tutorial, or even the full [YAML Specification].

### Use Syntax Highlighting

If you're not using an editor with **syntax highlighting** for YAML, definitely try that.

Or if you're in a hurry, try pasting your file into an [online YAML editor]. But after that... seriously, get yourself a good editor. A pleasure not to be missed.

### Check Previous Lines

The error messages here can be confusing; you'll get a line number, but the error is often on the **previous** line.

E.g., if you have `output` instead of `output:`, that will error, but error message might focus on a later line. It's confusing.

```{eval-rst}

.. _sql-multiline:
```

### Watch Out for the Multiline String in `sql:`

Each query needs an `sql` statement, and they can be gloriously long. So long, in fact, that I have toyed with having these statements in a separate `.sql` file that could be edited separately, with syntax highlighting, and then imported.

But so far, I think it's more convenient to have the sql right there in the config file. You just have to get the syntax right.

Turns out, there are **too many ways** to write [multilines in YAML].

But you'll be fine. Just:

- Add the `>` after `sql:`, like this: `sql: >`. This is **important.**
- Make sure every line of your statement is indented correctly.

```yaml
sql: >
  SELECT name
  FROM products
  ;
```

No problem.

### Avoid "Advanced" YAML

Our YAML validator is provided by [StrictYAML], which does [disallow some features]. These are not features I expect you'll ever need to use, but if you think you might have crossed the line, check that link.

## Follow the Schema

Even if your syntax is valid YAML, your config file must also follow the special **schema** we've defined.

The schema is as strict as possible, so that you can fix problems right away.

For instance, if you try to add a new option that doesn't exist...

```yaml
---
input:
  slugify-columns: true
  lowercase-columns: true
  magically-remove-pointless-junk-data: true
```

...this will (sadly) throw an error.

```{eval-rst}
.. _watch-out-lists:
```

### Watch Out For Lists!

One potential confusion: you really need to get clear on when to use lists and when to avoid them.

For instance, only ONE of these snippets is valid. Which one?

```yaml
---
tables_config:
  orders:
    - path: orders1.csv
  products:
    - path: products1.csv
    - path: products2.csv
```

```yaml
---
tables_config:
  orders:
    path: orders1.csv
  products:
    path: products1.csv
    path: products2.csv
```

The **first** is **correct**, the **second** is **invalid**.

Why?

Because in the second snippet, the `products` table has two `path` keys.

```yaml
---
# WRONG!
  products:
    path: products1.csv
    path: products2.csv
```

You cannot have **duplicate keys** at the same level.

Think about it: in this situation, what is `products['path']`? Is it the first CSV, or the second?

#### Each Table Is a Key, With a List of Sources

Because a table can have more than one source, each source is a separate **list** item.

```yaml
---
# RIGHT!
products:
  - path: products1.csv
  - path: products2.csv
```

It may look almost the same, but it's not. Behind the scenes, each of those list items is **separate** and **numbered**. We have `products[0]['path']` and `products[1]['path']`. Whew.

This becomes more clear if you add other keys to a list item, like `sheet`.

```yaml
---
# STILL RIGHT!
products:
  - path: products1.csv
  - path: products2.csv
  - path: products3.xlsx
    sheet: Lamps
  - sheet: More Lamps
    path: products4.xlsx
```

On the other hand, you very much do NOT want to put the tables into a list:

```yaml
---
# TOTALLY WRONG!!
tables_config:
  - orders:
      - path: orders1.csv
  - products:
      - path: products1.csv
      - path: products2.csv
```

But since each table name needs to be unique, this should be easy to remember.

```{eval-rst}
.. _query-list-item:
```

#### Each Query is a List Item

```{eval-rst}
Meanwhile, in :ref:`queries`, **each query** is a **list item**, *not* a key.
```

```yaml
---
queries:
  - name: Vacation Days
    sql: |
      SELECT * FROM clocks WHERE type LIKE "vacation";

  - name: Timesheets
    sql: |
      SELECT * FROM clocks WHERE type LIKE "work";
    postprocess: add_quarter_hours
```

Making each query a list item has these advantages:

- Queries are run in **order**. This means that a later query can `SELECT` from an earlier query, as if it were a table.
- Usually, the `name:` value will be used as the title of a sheet in a spreadsheet. Since we use the value, not the key (the way we use a key as the name for a table), you can use spaces and punctuation in this value without any trouble. Yes, technically you can use spaces and punctuation in a key, but I find it confusing. (And if you plan to reference this query in a later query, you may want to keep this name short anyway.)

```{eval-rst}
.. _when-does-order-matter:
```

### When Does Order Matter?

Note that:

- The order of top-level blocks (like `table_config:`) does **not matter**.
- The order of **list** items **matters**.
- But the order of **keys** (including keys _within_ a list item) does **NOT matter**

This is another reason we use lists for imports. The order **makes a difference** when you are importing sources into a table, importing Python code with `import:`, or running queries.

But when you are defining keys that have to be unique anyway, order does not matter. You can list `sheet` or `path` first, whichever you like.

For maximum clarity, you could even do:

```yaml
---
# PAINFUL, BUT RIGHT!
products:
  - path: products1.csv
  - path: products2.csv
  - path: products3.xlsx
    sheet: Lamps
  - sheet: More Lamps
    path: products4.xlsx
```

But I find this irritating.

## When These Options Aren't Enough

```{eval-rst}
Need to do more with your data than `yarm`'s generous :doc:`options <options>` or the most arcane nested SQL can offer? No worries! You can :doc:`postprocess </postprocess>` your queries with custom Python code.
```

[strictyaml]: https://hitchdev.com/strictyaml/
[disallow some features]: https://hitchdev.com/strictyaml/features-removed/
[online yaml editor]: https://duckduckgo.com/?q=online+editor+for+yaml&t=qupzilla&ia=web
[multilines in yaml]: https://stackoverflow.com/a/21699210
[yaml specification]: https://yaml.org/spec/1.2.2/
[makefile]: https://www.gnu.org/software/make/manual/html_node/Introduction.html
