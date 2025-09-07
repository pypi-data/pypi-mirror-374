import duckdb
import pandas as pd


def load_data_as_varchar(filename: str, delimiter: str, table_name: str = "raw_data") -> duckdb.DuckDBPyConnection:
    
    """
    Load the input delimited file into DuckDB as a table with all columns treated as VARCHAR.

    Parameters
    ----------
    filename : str
        Path to the input file.
    delimiter : str
        Delimiter used in the file.
    table_name : str, optional
        Name of the DuckDB table to create (default is "raw_data").

    Returns
    -------
    duckdb.DuckDBPyConnection
        DuckDB connection object with the loaded table.
    """
    
    # Establish a DuckDB in-memory connection
    con = duckdb.connect()
    
    # Create or replace a table in DuckDB using all columns as VARCHAR type
    query = (
        f"CREATE OR REPLACE TABLE {table_name} AS "
        f"SELECT * FROM read_csv_auto('{filename}', delim='{delimiter}', all_varchar=TRUE)"
    )
    con.execute(query)
    return con


def get_column_names(con: duckdb.DuckDBPyConnection, table_name: str) -> list:
    
    """
    Retrieve the list of column names from the specified DuckDB table.

    Parameters
    ----------
    con : duckdb.DuckDBPyConnection
        DuckDB connection object.
    table_name : str
        Name of the table to inspect.

    Returns
    -------
    list
        List of column names in the table.
    """
    
    # Execute PRAGMA command to get table info and extract column names
    result = con.execute(f"PRAGMA table_info('{table_name}')").fetchall()
    return [col[1] for col in result]


def detect_column_types(con: duckdb.DuckDBPyConnection, table_name: str) -> pd.DataFrame:
    
    """
    Detect data types of each column in the DuckDB table and count the occurrences 
    of each detected type: int, float, double, str, and null.

    Parameters
    ----------
    con : duckdb.DuckDBPyConnection
        DuckDB connection containing the loaded data.
    table_name : str
        Name of the table for type detection.

    Returns
    -------
    pandas.DataFrame
        Summary DataFrame with counts of each detected type per column, including a total count column.
        Columns include: 'col', 'int', 'float', 'double', 'str', 'null', and 'total'.
    """
    
    # SQL template to detect data type of each value in a column
    type_check_sql = """
    SELECT
      '{col}' AS column_name,
      CASE
        WHEN {col} IS NULL THEN 'null'
        WHEN TRY_CAST({col} AS INTEGER) IS NOT NULL THEN 'int'
        WHEN TRY_CAST({col} AS FLOAT) IS NOT NULL THEN 'float'
        WHEN TRY_CAST({col} AS DOUBLE) IS NOT NULL THEN 'double'
        ELSE 'str'
      END AS detected_type
    FROM {table}
    """
    
    columns = get_column_names(con, table_name)
    all_results = []
    
    # Loop through columns and get counts of each detected type
    for col in columns:
        query = type_check_sql.format(col=col, table=table_name)
        rows = con.execute(query).fetchall()
        all_results.extend(rows)
    
    # Create a DataFrame of results with columns: col and detected_type
    df = pd.DataFrame(all_results, columns=["col", "detected_type"])
    
    # Group by column and detected type and count occurrences, then reshape with unstack
    summary = (
        df.groupby(["col", "detected_type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    
    # Ensure all expected types are present with at least 0 count
    for dtype in ["int", "float", "double", "str", "null"]:
        if dtype not in summary.columns:
            summary[dtype] = 0
    
    # Add a total column summing counts of all types per column
    summary["total"] = summary[["int", "float", "double", "str", "null"]].sum(axis=1)
    return summary
