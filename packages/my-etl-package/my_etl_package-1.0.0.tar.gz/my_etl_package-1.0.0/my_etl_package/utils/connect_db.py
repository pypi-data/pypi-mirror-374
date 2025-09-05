import os
import logging
from sqlalchemy import create_engine
from sqlalchemy import Engine


# Setup logging to capture errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostgresConnector:
    """
    A class to manage the connection to a PostgreSQL database and return the connection string.

    Attributes:
        host (str): The hostname of the PostgreSQL server.
        database (str): The name of the database to connect to.
        user (str): The username to authenticate with.
        password (str): The password to authenticate with.
        port (int): The port on which the PostgreSQL server is listening.
    """

    def __init__(self):
        """
        Initializes the connection parameters by loading from environment variables.
        """
        self.host = os.getenv("DB_HOST")
        self.database = os.getenv("DB_NAME")
        self.user = os.getenv("DB_USER")
        self.password = os.getenv("DB_PASSWORD")
        self.port = str(os.getenv("DB_PORT", 5432))  # Default to 5432 if not found
        if not all([self.host, self.database, self.user, self.password]):
            raise ValueError("Missing database connection details in the .env file.")
        logger.info("PostgresConnector initialized with loaded credentials.")

    def get_db_connection(self) -> Engine:
        """
        Returns the connection string for PostgreSQL.

        Returns:
            str: The connection string.

        Example:
            >>> db = PostgresConnector()
            >>> db.get_db_connection()  # doctest: +SKIP
        """
        conn_str = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        engine = create_engine(conn_str)
        logger.info(f"Database engine generated for: {conn_str}.")
        return engine
