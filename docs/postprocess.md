# Postprocess with Custom Code

You can run the results of any query through your own custom postprocess function.

Yes, the main point of `yarm` is to make common data ~~wrangling~~ ~~munging~~ carpentry tasks as easy as a line of YAML config. But if you need more, you can write custom Python.

## The Basic Rules

- Each query can run **one** postprocess function.
- These function is executed **after** all other options.
  - E.g., if you use `replace:` to find and replace data in your query results, that happens _before_ your function is called.
- Your function must take **one argument**: the [pandas DataFrame] of your query results.
- Your function must **return one object**: another [pandas DataFrame], presumably those same results after your modifications.
- You save your function in a simple Python file in the same directory as your config file, and define it as a `path` under `import:`
- Make sure your file has a **docstring** at the top, or Python may have trouble importing your code.

## Minimal Example

Suppose you have a column `minutes`, and you'd like to know how many _hours_ they add up to.

Make a separate Python file, let's call it `custom.py`

```python

"""My custom code, complete with this fairly superfluous docstring."""

def add_hours(data):
    """Calculate how many hours are in each row's minutes. """

    data["hours"] = data["minutes"] / 60
    return data
```

Notice that:

- Our function `add_hours()` takes one argument, `data`.
- And we return one object, also `data`.

Now let's edit our config file, `yarm.yaml`.

Before, we had a very simple config file:

```{eval-rst}
.. literalinclude:: postprocess/postprocess_before.yaml
    :language: yaml
```

Now, we add:

- An `import:` key, with a `path` to our code at `custom.py`.
  - Note that as with tables, each source for import is a **list item**, even if we only have one.
- A `postprocess:` key to our query, with our function name `add_hours`.

Which gives us:

```{eval-rst}
.. literalinclude:: postprocess/postprocess_after.yaml
    :language: yaml
    :emphasize-lines: 2-3, 19
```

When you run your report, your output sheet `Times` will have an `hours` column, just as you coded.

## Do I Have to Name the Argument `data`?

No.

You can name this variable whatever you want. It just needs to be a pandas DataFrame.

The classic variable name for a pandas DataFrame is `df`; if you know anything about pandas, you've seen `df` a lot. If you prefer to use `df`, please do. You've earned it. I do myself.

## Remember to "Save" Your Changes To Your DataFrame

In one respect, this example was slightly misleading. We made a change to our `df` by adding a new column, and the change "stuck". Yes, this seems normal, but very often, when you manipulate a DataFrame, you need to remember to manually assign those changes back into the DataFrame.

For instance, this won't work:

```python
def halve(df):
    """Divide minutes by half, for some very good reason."""
    # WON'T WORK
    df['minutes'] / 2
    return df
```

This code won't throw an error... but it also won't do anything. Your output spreadsheet will show the original minutes, gleefully unchanged.

Instead, you want to do:

```python
def halve(df):
    """Divide minutes by half, for some very good reason."""
    # CORRECT!
    df['minutes'] = df['minutes'] / 2
    return df
```

Perhaps you already knew that. I remember I found it confusing.

## What If My Query Needs More Than One Function?

No worries. Write as many functions as you like... and then call them in sequence from one function.

## Can I Run a Table Through a Postprocess Function?

Um... no.

But you can make a query to select all the data from that table, and run _that_ through a function.

[pandas dataframe]: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.html

## What If I Define Two Functions With The Same Name?

If you try to do this in the same file, Python won't let you.

But what if you define the same function name in _two_ files, and then `import` them both?

The definition in the last file wins.

Remember, the imports are a **list**, and with a list, **order matters**.

So importing your custom Python modules here are like [CSS overrides]. The most recent definition wins.

In practice, this shouldn't usually be a problem.

[css overrides]: https://www.w3docs.com/snippets/css/how-to-override-css-styles.html#cascading-order-3
