"""Create tables from validated configuration."""
import re
from pathlib import Path
from sqlite3 import Connection
from typing import Union

import pandas as pd
from nob.nob import Nob
from nob.nob import NobView
from pandas.core.frame import DataFrame
from slugify import slugify

from yarm.export import export_tables
from yarm.helpers import abort
from yarm.helpers import key_show_message
from yarm.helpers import msg
from yarm.helpers import msg_with_data
from yarm.helpers import show_df
from yarm.settings import Settings


def create_tables(conn: Connection, config: Nob):
    """Read data from :data:`tables_config:` into database and create tables.

    Args:
        conn: Temporary database in memory
        config: Report configuration

    See Also:
        - :func:`create_table_df()`
        - :func:`yarm.export.export_tables`

    """
    s = Settings()

    tables: NobView = config[s.KEY_TABLES_CONFIG]

    include_index_all: bool = get_include_index_all(config)

    # Input options apply to all tables, so show them once here.
    key_msg: list = [
        (s.KEY_INPUT__STRIP, s.MSG_STRIP_WHITESPACE),
        (s.KEY_INPUT__SLUGIFY_COLUMNS, s.MSG_SLUGIFY_COLUMNS),
        (s.KEY_INPUT__LOWERCASE_COLUMNS, s.MSG_LOWERCASE_COLUMNS),
        (s.KEY_INPUT__UPPERCASE_ROWS, s.MSG_UPPERCASE_ROWS),
    ]
    key_show_message(key_msg, config, verbose=1)

    for table_name in tables.keys():
        msg(s.MSG_LINE_DOUBLE, verbose=2)
        msg_with_data(s.MSG_CREATING_TABLE, table_name, verbose=2)

        # For each new table, mode should start as "replace"
        exists_mode: str = "replace"

        table: NobView = tables[table_name]
        table_df = None

        include_index_table: bool = get_include_index_table(
            table, table_name, include_index_all
        )

        for source, _val in enumerate(table):
            table_df = create_table_df(
                conn, config, table_df, table_name, table, source, exists_mode
            )

            # If there are any more paths for this table, we will want to append.
            exists_mode = "append"

        try:
            # TODO Is table_df ever None by now? If so, what action is needed?
            if table_df is not None:  # pragma: no branch
                table_df.to_sql(
                    table_name, conn, if_exists=exists_mode, index=include_index_table
                )
                msg_with_data(s.MSG_CREATED_TABLE, table_name)
        except pd.io.sql.DatabaseError as error:  # pragma: no cover
            # TODO Figure out how to test these errors.
            conn.close()
            abort(
                s.MSG_CREATE_TABLE_DATABASE_ERROR,
                error=error,
                data=table_name,
            )
        except ValueError as error:  # pragma: no cover
            conn.close()
            abort(
                s.MSG_CREATE_TABLE_VALUE_ERROR,
                error=str(error),
                data=table_name,
            )
    export_tables(config=config, conn=conn)


def create_table_df(
    conn: Connection,
    config: Nob,
    table_df: Union[None, DataFrame],
    table_name: str,
    table: NobView,
    source,
    exists_mode: str,
) -> DataFrame:
    """Create or append to a table from a configured source.

    Note:
        Each **table** is defined by a list of one or more **sources**,
        all of which are merged into a single table.

        This function is called separately for *each* source.

        (See :data:`yarm.validate.validate_key_tables_config`.)

    Args:
        conn: Temporary database in memory
        config: Report configuration
        table_df: :data:`None` if this table is new, otherwise the existing table
        table_name: Table we are creating or appending to
        table: Table configuration
        source: Source configuration
        exists_mode: :data:`replace` for a new table, otherwise :data:`append`

    Returns:
        DataFrame of our new or updated table

    See Also:
        - :func:`input_source`
        - :func:`create_tables`
        - :func:`df_input_options`
        - :func:`df_tables_config_options`
        - :func:`yarm.validate.validate_key_tables_config`

    """
    s = Settings()

    filename = table[source]["path"][:]
    file_ext = Path(filename).suffix
    msg_with_data(s.MSG_IMPORTING_DATA, filename, verbose=2, indent=1)

    source_config: NobView = table[source]

    if re.findall(s.CSV, file_ext):
        table_df = input_source(
            input_format=s.CSV,
            conn=conn,
            config=config,
            source_config=source_config,
            table_name=table_name,
            table_df=table_df,
            input_file=filename,
            input_sheet=None,
        )
    elif re.findall(s.XLSX, file_ext):
        sheet: Union[int, str] = 0
        if s.KEY_TABLE__SHEET in table[source]:
            sheet = table[source][s.KEY_TABLE__SHEET][:]
            msg_with_data(s.MSG_IMPORTING_SHEET, str(sheet), verbose=2, indent=2)
        else:
            # If no sheet is provided, use the first sheet.
            # TODO Implement option to import *all* sheets?
            # pd.read_excel() will do this if sheet_name = None
            # TODO Implement option to pass a sheet number instead of name?
            sheet = 0
            msg_with_data(s.MSG_NO_SHEET_PROVIDED, filename, indent=2)
        table_df = input_source(
            input_format=s.XLSX,
            conn=conn,
            config=config,
            source_config=source_config,
            table_name=table_name,
            table_df=table_df,
            input_file=filename,
            input_sheet=sheet,
        )
    else:
        abort(s.MSG_BAD_FILE_EXT, file_path=filename)
    return table_df


def get_include_index_all(config: Nob) -> bool:
    """Set default :data:`input:include_index` for all tables.

    Args:
        config: Report configuration

    Returns:
        **Default** value for whether to include the index in each table

    Note:
        This value can be overridden by each particular table.

    See Also:
        - :func:`get_include_index_table`
    """
    s = Settings()
    include_index_all: bool = False
    if s.KEY_INPUT__INCLUDE_INDEX in config:
        include_index_all = config[s.KEY_INPUT__INCLUDE_INDEX][:]
    if include_index_all:
        msg(s.MSG_INCLUDE_INDEX_ALL_TRUE, verbose=2)
    else:
        msg(s.MSG_INCLUDE_INDEX_ALL_FALSE, verbose=2)
    return include_index_all


def get_include_index_table(
    table: NobView, table_name: str, include_index_all: bool
) -> bool:
    """Set :data:`include_index` for a particular table.

    Args:
        table: Configuration for this table
        table_name: Name for this table
        include_index_all: Default :data:`include_index` value

    Returns:
        Whether to include the index in **this** table

    See Also:
        - :func:`get_include_index_all`
    """
    s = Settings()
    include_index_table: bool = include_index_all

    msg: Union[str, None] = None

    # Special case: by default, a pivot table loses its index, which is
    # confusing. Set this to true now, so that user can override below.
    if s.KEY_PIVOT in table:
        include_index_table = True
        msg = s.MSG_INCLUDE_INDEX_TABLE_PIVOT

    # NOTE We have already confirmed that only one include_index, at most,
    # is in this table. See validate_key_tables_config()
    if s.KEY_INCLUDE_INDEX in table:
        include_index_table = table[s.KEY_INCLUDE_INDEX][:]
        if table[s.KEY_INCLUDE_INDEX][:]:
            msg = s.MSG_INCLUDE_INDEX_TABLE_TRUE
        else:
            msg = s.MSG_INCLUDE_INDEX_TABLE_FALSE

    if msg:
        msg_with_data(msg, data=table_name, verbose=2, indent=1)

    return include_index_table


def input_source(
    input_format: str,
    conn,
    config: Nob,
    source_config: NobView,
    table_name: str,
    table_df: Union[DataFrame, None],
    input_file: str,
    input_sheet: Union[int, str, None],
) -> DataFrame:
    """Input a source into a table DataFrame.

    Args:
        input_format: Format for this source (e.g. :data:`CSV`)
        conn: Temporary database in memory
        config: Report configuration
        source_config: Configuration for this source
        table_name: Table we are creating or appending to
        table_df: :data:`None` if this table is new, otherwise the existing table
        input_file: Actual file with source data
        input_sheet: Name of sheet if source is spreadsheet, otherwise :data:`None`

    Returns:
        New or updated table

    Important:
        If a table has multiple sources, each subsequent source is merged with an
        **outer join**.

    See Also:
        - :func:`create_table_df`
    """
    s = Settings()

    msg_show_df: str = table_name

    if input_format == s.CSV:
        df: DataFrame = pd.read_csv(input_file)
    elif input_format == s.XLSX:
        msg_show_df += f": {input_sheet}"
        with open(input_file, "rb") as f:
            df = pd.read_excel(f, sheet_name=input_sheet)
    else:  # pragma: no cover
        # This branch should never execute, because of previous tests.
        abort(s.MSG_INPUT_FORMAT_UNRECOGNIZED, data=input_format)

    # Show data before any options (only at high verbosity)
    show_df(df, msg_show_df, 4)

    df = df_input_options(df, config)
    df = df_tables_config_options(df, source_config, table_name, input_file)

    # After all transformations, merge to existing table_df.
    msg_with_data(s.MSG_MERGING_PATH, data=input_file, indent=1, verbose=2)
    if isinstance(table_df, DataFrame):
        try:
            df = pd.merge(left=table_df, right=df, how="outer")
        except pd.errors.MergeError:
            abort(
                s.MSG_MERGE_ERROR,
                data=table_name,
                file_path=input_file,
                ps=s.MSG_MERGE_ERROR_PS,
            )
        except TypeError as error:  # pragma: no cover
            # TODO Figure out how to test this.
            abort(
                s.MSG_MERGE_TYPE_ERROR,
                error=str(error),
                data=table_name,
                file_path=input_file,
            )
        except ValueError as error:
            conn.close()
            abort(
                s.MSG_CREATE_TABLE_VALUE_ERROR,
                error=str(error),
                data=table_name,
            )
    show_df(df, table_name)
    return df


def df_input_options(df: DataFrame, config: Nob) -> DataFrame:
    """Process input data using the options in :data:`input:` key.

    These options are applied to *every* input file.

    Important:
        If you modify these options, you must also modify
        :func:`yarm.validate.validate_key_input`

    Note:
        For per-source options, see :func:`df_tables_config_options`.

    Args:
        df: Data we will manipulate
        config: Report configuration

    Returns:
        Data with options applied

    See Also:
        - :func:`yarm.validate.validate_key_input`
        - :func:`create_tables`
        - :func:`df_tables_config_options`

    """
    s = Settings()
    c: Nob = config
    if s.KEY_INPUT in c:
        # Strip whitespace at start and end of string.
        # https://stackoverflow.com/a/53089888
        # input:
        #   strip: true
        if s.KEY_INPUT__STRIP in c and c[s.KEY_INPUT__STRIP][:]:
            df = df.applymap(lambda x: x.strip() if type(x) == str else x)

        # input:
        #   slugify_columns: true
        if s.KEY_INPUT__SLUGIFY_COLUMNS in c and c[s.KEY_INPUT__SLUGIFY_COLUMNS][:]:
            df.columns = [
                slugify(col, lowercase=False, separator="_") for col in df.columns
            ]

        # input:
        #   lowercase_columns: true
        if s.KEY_INPUT__LOWERCASE_COLUMNS in c and c[s.KEY_INPUT__LOWERCASE_COLUMNS][:]:
            df.columns = [col.lower() for col in df.columns]

        # input:
        #   uppercase_rows: true
        # Note: The uppercase transformation happens BEFORE running query, replace
        # This matters for case-sensitive queries and regexes.
        if s.KEY_INPUT__UPPERCASE_ROWS in c and c[s.KEY_INPUT__UPPERCASE_ROWS][:]:
            df = df.applymap(lambda s: s.upper() if type(s) == str else s)

        # TODO Implement option to remove stopwords from column names with slugify?

        # include_index: not processed here, see create_tables()

    return df


def df_tables_config_options(
    df: DataFrame, source_config: NobView, table_name: str, input_file
) -> DataFrame:
    """Process options for a particular **source** in a **table**.

    Important:
        If you modify these source options, you must also modify
        :func:`yarm.validate.validate_key_tables_config`.

        That function also ensures that all necessary keys are present (e.g., that if
        a pivot stanza is present, it also has index, columns, and values).

    Note:
        For :data:`input:` options applied to all input files,
        see :func:`df_input_options`.

    Args:
        df: Table we will modify
        source_config: Configuration for this source
        table_name: Name of this table
        input_file: Path to this source data

    Returns:
        Updated table, with options applied from this source

    See Also:
        - :func:`create_tables`
        - :func:`yarm.validate.validate_key_tables_config`
        - :func:`df_input_options`.
    """
    s = Settings()
    sc: NobView = source_config
    # NOTE Pivot first, so that we can work with the new columns if needed.
    if s.KEY_PIVOT in sc:
        msg_with_data(s.MSG_APPLYING_PIVOT, input_file)
        # show_df(df, table_name, 4)
        try:
            df = pd.pivot(
                data=df,
                index=sc[s.KEY_PIVOT_INDEX][:],
                columns=sc[s.KEY_PIVOT_COLUMNS][:],
                values=sc[s.KEY_PIVOT_VALUES][:],
            )
        except KeyError as error:
            abort(s.MSG_PIVOT_FAILED_KEY_ERROR, data=str(error), file_path=input_file)
    if s.KEY_DATETIME in sc:
        msg(s.MSG_CONVERTING_DATETIME, indent=1, verbose=2)
        for key in sc[s.KEY_DATETIME][:]:
            if key in df.columns:
                df = back_up_column(df, key)

                # Make the original column datetime
                df[key] = pd.to_datetime(df[key])

                if sc[s.KEY_DATETIME][key][:] is not None:
                    # If value present, use as datetime format.
                    # TODO Test for bad format? strictyaml makes this a str,
                    # so it may not be possible to trigger an error.
                    datetime_format: str = sc[s.KEY_DATETIME][key][:]
                    msg_with_data(key, data=datetime_format, indent=2, verbose=2)
                    df[key] = df[key].dt.strftime(f"{datetime_format}")
                else:
                    msg_with_data(key, data="(default format)", indent=2, verbose=2)

            else:
                abort(s.MSG_MISSING_DATETIME, data=key, file_path=input_file)

    # Always return the dataframe!
    return df


def back_up_column(df: DataFrame, col: str):
    """Save a backup copy of a column.

    Args:
        df: data we are manipulating
        col: column to back up

    Returns:
        Data with copy of column :data:`col` that has :data:`_raw`
        appended to the column name. The original column can now safely
        be manipulated by further code.

    """
    # Make backup copy of this column at column_raw
    col_raw_name: str = f"{col}_raw"
    df[col_raw_name] = df[col]
    col_raw = df.pop(col_raw_name)

    # Move _raw copy to after original column.
    col_index = df.columns.get_loc(col)
    df.insert(col_index + 1, col_raw.name, col_raw)
    return df
