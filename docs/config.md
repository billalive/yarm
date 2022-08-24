# Config

The configuration file is the heart of your report.

## The Basic Idea

- Set up your **output** options (`output:`).
- (Optional) Set any **input** options, for changes you want to make to data after you input it, but before you run your queries (`input:`).
- Define your **tables** you want to query (`tables_config:`)
- (Optional) If you want to apply a custom Python function to any of your queries, **import** your code file(s). (`import:`).
- Define your **queries** (`queries:`)

## Minimal Working Config File

This file shows the bare minimum you need to run a report.

```{eval-rst}
.. literalinclude:: config/config_mwe.yaml
    :language: yaml
```

Actually, if you set a value for `export_tables`, you can even run a report with no `queries`. Sometimes it's useful to collect multiple sources into a single CSV.

Most of the time, though, you'll probably want more options.

## Complete Config File

This example config file (should) demonstrate every possible config option.

As long as our unit tests are passing, anything you see here should work. 😅

Note that options shown here are **not necessarily the defaults**. For example, if you omit `slugify_columns`, it will be `false`, _not_ `true` as shown below.

```{eval-rst}
.. literalinclude:: config/config_complete.yaml
    :language: yaml
```

## TODO Actually document these options

Coming soon...

## Solutions to Common Config Problems

Your report won't run? These tips might help.

### Fix Invalid YAML

First and foremost, the config file can't have any syntax mistakes.

When you get a syntax error, usually you just need to add a colon or an indent (or two).

#### Use Syntax Highlighting

If you're not using an editor with **syntax highlighting** for YAML, definitely try that.

Or if you're in a hurry, try pasting your file into an [online YAML editor]. But then, seriously, get yourself a good editor.

#### Check Previous Lines

The error messages here can be confusing; you'll get a line number, but the error is often on the **previous** line.

E.g., if you have `output` instead of `output:`, that will error, but error message might focus on a later line. It's confusing.

#### Watch Out for the Multiline String in `sql`

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

#### Don't Try Any "Advanced" YAML

Our YAML validator is provided by [StrictYAML], which does [disallow some features]. These are not features I expect you'll ever need to use, but if you think you might have crossed the line, check that link.

### Follow the Schema

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

#### Watch Out For Lists!

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

#### When Does Order Matter?

Note that:

- The **order** of **list** items **matters**.
- But the **order** of **keys** (including keys _within_ a list item) does **NOT matter**

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
Need to do more with your data than `yarm`'s generous options or the most arcane nested SQL can offer? No worries! You can :doc:`postprocess <postprocess>` your queries with custom Python code.
```

[strictyaml]: https://hitchdev.com/strictyaml/
[disallow some features]: https://hitchdev.com/strictyaml/features-removed/
[online yaml editor]: https://duckduckgo.com/?q=online+editor+for+yaml&t=qupzilla&ia=web
[multilines in yaml]: https://stackoverflow.com/a/21699210
