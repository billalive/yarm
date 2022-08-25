# Config

The configuration file is the heart of your report.

## The Basic Idea

```{eval-rst}
.. include:: basic.rst
```

## Minimal Working Config File

This file shows the bare minimum you need to run a report.

```{eval-rst}
.. literalinclude:: config_mwe.yaml
    :language: yaml
```

Actually, if you set a value for `export_tables`, you can even run a report with no `queries`. Sometimes it's useful to collect multiple sources into a single CSV.

Most of the time, though, you'll probably want more options.

```{toctree}
---
hidden:
maxdepth: 1
---

complete
options
solutions

```
