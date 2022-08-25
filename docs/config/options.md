# Configuration Options

This page explains each configuration option in detail.

```{eval-rst}
For documentation on actual functions, see the :doc:`Reference <../reference>`.

.. include:: basic.rst
```

## `output:`

**REQUIRED.**

```{eval-rst}
.. literalinclude:: /validate/validate_key_output.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_output`
```

## `input:`

_Optional._

```{eval-rst}
.. literalinclude:: /validate/validate_key_input.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_input`
```

## `tables_config:`

**REQUIRED.**

```{eval-rst}
.. literalinclude:: /validate/validate_key_tables_config.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_tables_config`
```

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

## `queries:`

**REQUIRED,** _unless_ you set `output: export_csv`. (You need to output _something_.)

```{eval-rst}
.. literalinclude:: /validate/validate_key_queries.yaml
    :language: yaml

.. note::
    Defined in: :func:`yarm.validate.validate_key_queries`
```
