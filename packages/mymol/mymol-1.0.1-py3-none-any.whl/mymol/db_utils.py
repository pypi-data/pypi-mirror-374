import os
import configparser
import mysql.connector

#exceptions
class DatabaseConnectionError(Exception):
    """Raised when there is an issue connecting to the database."""

class QueryExecutionError(Exception):
    """Raised when there is an issue executing a query."""

#functions
def connect_mysql_db_config_file(config_file: str) -> object:
    """
    Connect to a MySQL database using a configuration file.

    Args:
        config_file (str): Path to the configuration file. The file should contain a [database] section
                           with keys: 'host', 'user', 'password', and 'db'.

    Returns:
        object: A connection object to interact with the database.

    Raises:
        FileNotFoundError: If the configuration file does not exist.
        KeyError: If the 'database' section or required keys are missing in the configuration file.
        Exception: If there is an error connecting to the database.

    Example:
        To use this function, create a configuration file (e.g., db_config.ini) with the following content:

        [database]
        host = your_host
        user = your_user
        password = your_password
        db = your_database
        Then, call the function as follows:

        >>> connection = connect_mysql_db_config_file('path/to/db_config.ini')
        >>> if test_connection(connection):
        ...     print("Connection successful!")
        ... else:
        ...     print("Connection failed.")
    """
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Configuration file '{config_file}' not found.")
    try:
        config = configparser.ConfigParser()
        config.read(config_file)
        if 'database' not in config:
            raise KeyError("The section [database] is missing in the config file.")
        mydb = mysql.connector.connect(
            host=['host'],
            user=['user'],
            password=['password'],
            database=['db']
        )
        return mydb
    except mysql.connector.Error as e:
        raise DatabaseConnectionError(f"Error connecting to the database:\n\n{e}")

def connect_mysql_db_config_dict(config_dict: dict) -> object:
    """
    Connect to a MySQL database using a configuration dictionary.

    Args:
        config_dict (dict): A dictionary containing the database configuration. The dictionary should have
                            keys: 'host', 'user', 'password', and 'db'.

    Returns:
        object: A connection object to interact with the database.

    Raises:
        ValueError: If any of the required keys are missing in the config dictionary.
        Exception: If there is an error connecting to the database.

    Example:
        >>> config = {
        ...     'host': 'localhost',
        ...     'user': 'root',
        ...     'password': 'password123',
        ...     'db': 'mydatabase'
        ... }
        >>> connection = connect_mysql_db_config_dict(config)
    """
    try:
        required_keys = ['host', 'user', 'password', 'db']
        for key in required_keys:
            if key not in config_dict:
                raise ValueError(f"The key '{key}' is missing in the config dictionary.")
        mydb = mysql.connector.connect(
            host=config_dict['host'],
            user=config_dict['user'],
            password=config_dict['password'],
            database=config_dict['db']
        )
        return mydb
    except mysql.connector.Error as e:
        raise DatabaseConnectionError(f"Error connecting to the database")

def close_connection(connection: object) -> None:
    """
    Closes the database connection.

    Args:
        connection (object): The database connection object.

    Raises:
        Exception: If there's an issue closing the connection.

    Example:
        >>> connection = mysql.connector.connect(user='user', password='password', host='127.0.0.1', database='mydb')
        >>> close_connection(connection)
    """
    try:
        connection.close()
    except Exception as e:
        raise DatabaseConnectionError(f"Error closing the connection: {e}")
    
def execute_query(connection, query, params=None) -> None:
    """
    Executes an SQL query on the given connection.

    Args:
        connection (CMySQLConnection): The database connection object.
        query (str): The SQL query to execute.
        params (tuple, optional): Parameters for the query (if needed). Defaults to None.

    Returns:
        list: Results of the query (for SELECT queries).
        
    Example:
        >>> results = execute_query(connection, "SELECT * FROM users WHERE id = %s", (user_id,))
    """
    try:
        cursor = connection.cursor()
        cursor.execute(query, params or ())
        if query.strip().lower().startswith("select"):
            return cursor.fetchall()
        connection.commit()
    except mysql.connector.Error as e:
        raise QueryExecutionError(f"Error executing query: {e}")
    finally:
        cursor.close()

def test_connection(connection):
    """
    Tests if the database connection is successful.

    Args:
        connection (CMySQLConnection): The database connection object.

    Returns:
        bool: True if the connection is alive, False otherwise.
        
    Example:
        >>> from mysql.connector import connect
        >>> connection = connect(user='user', password='password', host='127.0.0.1', database='test_db')
        >>> test_connection(connection)
        True

    """
    try:
        connection.ping(reconnect=True)
        return True
    except mysql.connector.Error:
        return False
    
def validate_mysql_config_file(config_file):
    """
    Validates the configuration file.

    Args:
        config_file (str): Path to the configuration file.

    Raises:
        KeyError: If required keys are missing.

    Example:
        >>> validate_mysql_config_file('path/to/db_config.ini')
    """
    config = configparser.ConfigParser()
    config.read(config_file)
    required_keys = ['host', 'user', 'password', 'db']
    if 'database' not in config:
        raise KeyError("Missing [database] section in the configuration file.")
    for key in required_keys:
        if key not in config['database']:
            raise KeyError(f"Missing '{key}' in the [database] section.")
        
def load_config(environment):
    """
    Loads the configuration for the specified environment.

    Args:
        environment (str): Environment name (e.g., 'development', 'production').

    Returns:
        dict: Database configuration for the environment.

    Example:
        >>> config = load_config('development')
        >>> connection = connect_mysql_db_config_dict(config)
        >>> if test_connection(connection):
        ...     print("Connection successful!")
        ... else:
        ...     print("Connection failed.")
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    return {
        "host": config[environment]['host'],
        "user": config[environment]['user'],
        "password": config[environment]['password'],
        "database": config[environment]['db']
    }
