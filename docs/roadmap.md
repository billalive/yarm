# Roadmap: Future Features

These features are not yet implemented, but they're on the roadmap.

## Import/Export other file formats?

In theory, it should be easy to import/export any file format that [pandas] can handle. (In _theory_.)

- JSON?
- SQL?
- HDF5?
- Anything else?

## `include` other config files

The `include` key will let you include other config files. For example, if you have a common set of data files that you often want to use in different reports, `include` will let you define their tables once, in one file.

This feature will be powerful, but for now, it's on the roadmap, because the recursion is complex.

It will also require careful thought to ensure that the overrides are intuitive.

For instance, what happens if a table with the same name is defined differently in `tables_config:` in two separate included files? I think that the most recent definition should _completely_ override any previous definitions, because it's quite possible that, without realizing it, you're using the same table name to describe different data.

On the other hand, I would like to be able to override `input:` and `output:` on a key by key basis. For example, I almost always want to set `input.slugify_columns` and `input.lowercase_columns` to `true`, but if I have a report where I need to override `input.lowercase_columns` to `false`, I'd like to be able to do this without also losing my included setting of `input.slugify_columns` as `true`.

So this feature will need some nuance.

## `create_tables`

If you want to include a configuration file that defines more tables than you want for a particular report, you'll be able to define a list as `create_tables` to limit the tables for _this_ report to a particular subset.

That might look like this:

```yaml
---
# Include a basic config file you always use for this client:
include:
  - path: ../Client_A/all.yaml

# For this report, we only want to use certain tables:
create_tables:
  - orders
  - products
  - tax
# The rest of the config file continues as usual...
```

## Visualizations?

Since we're already loading all the data into [pandas], we might as well add [matplotlib] and let you generate some charts, right?

I'm not sure. I can see the use cases, but if you need charts, it might be time to upgrade to [Jupyter Lab].

## Your Killer Feature?

Am I missing something? Is there some tedious bit of repetitive data wrangling that you'd _love_ to automate into a single line of YAML?

[File an issue][file an issue]! I'd love to hear from you.

[matplotlib]: https://matplotlib.org/
[pandas]: https://pandas.pydata.org/
[jupyter lab]: https://jupyter.org/try
[file an issue]: https://github.com/billalive/yarm/issues
