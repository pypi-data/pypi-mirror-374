import os
import configparser
from sqlalchemy.engine import URL
from sqlalchemy import create_engine, text, event

import pandas as pd
from time import sleep


class SQLUtils:
    """
    A utility class for interacting with SQL databases using SQLAlchemy.

    This class provides methods to establish a database engine connection and to fetch a list of all databases from the SQL Server instance.

    Attributes:
        db_server (str): The server address of the SQL database.
        db_username (str): The username for SQL database authentication.
        db_password (str): The password for SQL database authentication.
    """

    def __init__(self, config=None, server=None, username=None, password=None):
        """
        Initializes the SQLUtils instance either from a configuration file or from directly provided credentials.

        Args:
            config (str, optional): The path to the configuration file. Defaults to None.
            server (str, optional): The server address of the SQL database. Defaults to None.
            username (str, optional): The username for SQL database authentication. Defaults to None.
            password (str, optional): The password for SQL database authentication. Defaults to None.

        Raises:
            ValueError: If neither config nor (server, username, and password) are provided.
        """
        if config:
            config_parser = configparser.ConfigParser()
            self.config_path = os.path.join(os.path.dirname(__file__), config)
            config_parser.read(self.config_path)

            self.db_server = config_parser['SQL AUTH']['SERVER']
            self.db_username = config_parser['SQL AUTH']['USERNAME']
            self.db_password = config_parser['SQL AUTH']['PASSWORD']

        elif all([server, username, password]):
            self.db_server = server
            self.db_username = username
            self.db_password = password

        else:
            raise ValueError("Either a config file or server, username, and password must be provided.")

    def create_sql_engine(self, database):
        """
        Establishes a connection to the specified SQL Server database using SQLAlchemy and returns the database engine instance.

        Args:
            database (str): The name of the database to connect to.

        Returns:
            sqlalchemy.engine.base.Engine: The database engine instance for the specified database.
        """

        conn_string = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + self.db_server + ';DATABASE=' + database + ';UID=' + self.db_username + ';PWD=' + self.db_password
        conn_url = URL.create("mssql+pyodbc", query={"odbc_connect": conn_string})
        engine = create_engine(conn_url)

        # Add event listener to enable fast_executemany
        @event.listens_for(engine, "before_cursor_execute")
        def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
            if executemany:
                cursor.fast_executemany = True

        return engine

    def list_all_databases(self):
        """
        Fetches and returns a list of all database names from the SQL Server instance.

        Returns:
            list: A list of database names.
        """
        master_engine = self.create_sql_engine('master')
        with master_engine.connect() as conn:
            result = conn.execute(text("SELECT name FROM sys.databases"))
            database_list = [row[0] for row in result]
        return database_list

    def execute_query(self, database, query):
        """
        Executes a raw SQL query on the specified database and returns the results as a pandas DataFrame.

        Args:
            database (str): The name of the database to execute the query on.
            query (str): The SQL query to execute.

        Returns:
            pandas.DataFrame: A DataFrame containing the results of the query execution.
        """
        engine = self.create_sql_engine(database)
        with engine.connect() as conn:
            result_df = pd.read_sql_query(query, conn)
        return result_df

    def get_sessions(self, database):
        """
        Retrieves session information from the specified database and returns it as a dictionary mapping session names to their IDs.

        Args:
            database (str): Name of the database from which to fetch session information.

        Returns:
            dict: Dictionary mapping session names to session IDs.
        """
        engine = self.create_sql_engine(database)
        sessions_query = 'SELECT SessionName, IDCollectionSession FROM dbo.CollectionSession'
        sessions_df = pd.read_sql(sessions_query, engine)
        session_dict = dict(zip(sessions_df['SessionName'], sessions_df['IDCollectionSession']))
        return session_dict

    def create_batch(self, database, batch_sessions, batch_name, batch_color, desc=None):
        """
        Creates a new batch in the specified database with the given parameters and associates it with specified sessions.

        Args:
            database (str): Name of the database in which to create the batch.
            batch_sessions (list[str]): List of session names to associate with the batch.
            batch_name (str): Name of the batch.
            batch_color (str): Color identifier for the batch.
            desc (str, optional): Description of the batch. Defaults to None.
        """

        engine = self.create_sql_engine(database)

        new_batch_df = pd.DataFrame({
            'BatchName': [batch_name],
            'BatchDescription': [desc],
            'BatchColor': [batch_color],
            'IDUserLogin': [6317],  # Assuming a static user ID for simplicity; consider parameterizing
            'UpdateTime': [pd.to_datetime('now')]
        })
        new_batch_df.to_sql(name='CollectionBatch', con=engine, schema='dbo', index=False, if_exists="append")

        # Polling the database for the new batch ID
        batch_id = None
        attempts = 0
        while batch_id is None and attempts < 10:
            current_batches = pd.read_sql('SELECT * FROM CollectionBatch WHERE BatchName = ?', engine, params=[batch_name])
            if not current_batches.empty:
                batch_id = current_batches['IDCollectionBatch'].iloc[0]
                break
            sleep(2)
            attempts += 1

        if batch_id is None:
            raise Exception("Failed to confirm batch creation within the allotted time.")

        current_batches = pd.read_sql('SELECT * FROM CollectionBatch', engine)
        batch_id = current_batches.loc[current_batches['BatchName'] == batch_name]['IDCollectionBatch'].values[0]
        database_sessions = self.get_sessions(database)
        BatchSession = pd.DataFrame()
        BatchSession['IDCollectionSession'] = [int(database_sessions[str(session)]) for session in batch_sessions]
        BatchSession['IDCollectionBatch'] = batch_id
        BatchSession = BatchSession[['IDCollectionBatch', 'IDCollectionSession']]
        BatchSession.to_sql(name='BatchSession', con=engine, schema='dbo', index=False, if_exists="append")
