import sys
import pandas as pd
from my_etl_package.utils import PostgresConnector


def load_to_db(df: pd.DataFrame, table_name: str) -> None:
    """
    Load a pandas DataFrame into a PostgreSQL database table.

    Args:
        df (pd.DataFrame): DataFrame to load.
        table_name (str): Name of the target table in the database.
        connection_string (str): SQLAlchemy connection string.

    Example:
        >>> import pandas as pd
        >>> df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        >>> engine = PostgresConnector().get_db_connection()
        >>> load_to_db(df, 'test_table', engine)  # doctest: +SKIP
    """
    connector = PostgresConnector()
    engine = connector.get_db_connection()
    try:
        df.to_sql(table_name, engine, if_exists='replace', index=False)
    except Exception:
        print('Could not load to the Database!')
        print(sys.exc_info())
