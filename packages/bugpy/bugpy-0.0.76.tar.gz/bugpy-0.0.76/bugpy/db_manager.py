import mysql.connector
import numpy as np
import pandas as pd
from pandas import read_sql
from bugpy.utils import SqlFormatter, get_credentials
import warnings

pd.options.mode.chained_assignment = None

warnings.filterwarnings('ignore', '.*SQLAlchemy.*')


class Connection:
    """
    A class to handle MySQL database connections and interactions.
    """

    def __init__(self, user=None, password=None, host=None, database=None, port=3306):
        """
        Initializes the connection object and attempts to connect to the database.

        :param user: Database username, if unset then uses keyring credentials.
        :param password: Database password, if unset then uses keyring credentials.
        :param host: Database host address, if unset then uses keyring credentials.
        :param database: Name of the database, if unset then uses keyring credentials.
        :param port: Port number for the database connection, defaults to 3306.
        """
        self.set_variable('user', user)
        self.set_variable('password', password)
        self.set_variable('host', host)
        self.set_variable('database', database)
        self.port = port

        self.db = None
        self.cursor = None
        self.connect()

    def set_variable(self, key, value, credential_type='db'):
        """
        Sets keys as class variables. Collects variables from credential store if value is None.

        :param key: The name of the parameter (e.g., 'user').
        :param value: The value of the parameter. If None, will be retrieved.
        :param credential_type: The credential type for keyring retrieval, defaults to 'db'
        """
        setattr(self, key, value if value is not None else get_credentials(credential_type, key))

    def connected(self):
        """
        Checks whether the connection to the database is active.

        :return: True if connected, False otherwise.
        :rtype: bool
        """
        if self.db is None:
            return False
        if self.db.is_connected():
            return True
        return False

    def close(self):
        """
        Closes the database connection.

        :return: True if closed successfully, False otherwise.
        :rtype: bool
        """
        try:
            self.db.close()
            return True
        except Exception as e:
            print(e)
            return False

    def commit(self):
        """
        Commits the current transaction to the database.
        """
        if not self.connected():
            self.connect()
        self.db.commit()

    def connect(self, force_reconnect=False) -> bool:
        """
        Establishes a connection to the MySQL database.

        :param force_reconnect: Whether to force a new connection if one already exists.
        :return: True if the connection was successful, False otherwise.
        :rtype: bool
        """
        if not force_reconnect:
            if self.connected():
                return True
        try:
            if self.connected():
                self.close()
            self.db = mysql.connector.connect(host=self.host, database=self.database, user=self.user,
                                              passwd=self.password, use_pure=True, port=self.port)
            self.cursor = self.db.cursor()
            return True
        except mysql.connector.Error as err:
            raise PermissionError(f"Could not connect to MySQL database, reason: {err}")
        except Exception as e:
            print(e)
            return False

    def query(self, query: str, retries=1) -> pd.DataFrame:
        """
        Executes an SQL query and returns the result as a DataFrame.

        :param query: The SQL query to execute.
        :type query: str
        :param retries: Number of times to retry the query on failure, defaults to 1.
        :type retries: int
        :return: Query results as a pandas DataFrame.
        :rtype: pd.DataFrame
        """
        if not self.connected():
            self.connect()
        success = False
        for i in range(retries + 1):
            try:
                output_df = read_sql(query, self.db)
                success = True
                break
            except mysql.connector.errors.DatabaseError as e:
                error = e
        if not success:
            raise Exception(str(error))

        return output_df

    def update(self, query: str, verbose=False, commit=None, retries=2) -> int:
        """ Updates a table, returns number of edited lines

            :param query: a valid SQL query updating a table
            :param verbose: if true, prints the query before executing
            :param commit: whether to commit the result to the database
            :param retries: number of times to reattempt query after failure
            :return: the number of rows successfully updated
        """

        if commit is None:
            commit = self.commit

        if verbose:
            print(query)

        if not self.connected():
            self.connect()

        success = False
        error = Exception("retries must be greater than or equal to 0")
        for i in range(retries + 1):
            try:
                self.cursor.execute(query)
                success = True
                break
            except mysql.connector.errors.DatabaseError as e:
                error = e
        if not success:
            raise Exception(str(error))

        if commit:
            self.commit()
        records = self.cursor.rowcount
        if verbose:
            print(f'{records} rows updated.')

        if commit:
            self.close()

        return records

    def _format_df(self, dataframe: pd.DataFrame, table: str, include_autokey=False) -> pd.DataFrame:
        """
        Formats a DataFrame to match the schema of a given database table.

        :param dataframe: The DataFrame to format.
        :param table: Name of the target database table.
        :param include_autokey: Whether to include an auto-generated primary key.
        :return: Formatted DataFrame.
        :rtype: pd.DataFrame
        """

        fmt = SqlFormatter(table, include_autokey, self)

        dataframe = fmt.format(dataframe)

        return dataframe

    def _generate_insert_query(self, df, table):
        """
        Generates a raw SQL INSERT query for a given DataFrame and table.

        :param df: DataFrame of values to insert.
        :param table: Name of the table to insert into.
        :return: SQL INSERT query string.
        :rtype: str
        """
        df = self._format_df(df, table)
        df = df.drop_duplicates()
        query = f"INSERT INTO {table} ({','.join([col for col in df])}) VALUES "
        for i, row in df.iterrows():
            query += '(' + ','.join([row[col] for col in df]) + '),'
        query = query[:-1]
        return query

    def insert(self, df: pd.DataFrame, table: str, batch_size=10000, retries=1):
        """
        Inserts data from a DataFrame into a database table in batches.

        :param df: The DataFrame containing data to insert.
        :param table: The name of the target table.
        :param batch_size: Number of rows per batch insert, defaults to 10000.
        :param retries: Number of times to retry on failure, defaults to 1.
        :return: True if successful, False otherwise.
        :rtype: bool
        """
        if len(df) == 0:
            print("Dataframe is empty!")
            return False
        records = 0
        if not self.connected():
            self.connect()

        inserted_ids = []
        for i in np.arange(0, len(df), batch_size):
            batch = df.iloc[i:i + batch_size]
            query = self._generate_insert_query(batch, table)
            success = False
            for j in range(retries + 1):
                try:
                    self.cursor.execute(query)
                    success = True
                    break
                except mysql.connector.errors.DatabaseError as e:
                    error = e
            if not success:
                raise Exception(error.__str__())
            records = records + self.cursor.rowcount

        first_id = self.cursor.lastrowid
        num_rows = self.cursor.rowcount
        if first_id is not None and num_rows > 0:
            inserted_ids.extend(range(first_id, first_id + num_rows))

        self.commit()
        print(f'{records} records inserted')

        return inserted_ids

    def callproc(self, sp, args=None, num_outputs=0, output_table=None, commit=None, retries=0):
        """ Calls a stored procedure

            :param sp: the name of the stored procedure
            :type sp: str
            :param args: the input arguments for the stored procedure
            :param num_outputs: the number of outputs of the stored procedure, defaults to 0
            :type num_outputs: int
            :param output_table: the name of the table where any expected outputs are stored, defaults to None
            :type output_table: str
            :param commit: whether the result of the stored procedure should be committed
            :type commit: bool
            :param retries: number of time to retry process before giving up, defaults to 0
            :type retries: int
            :return: Depending on `num_outputs` and `output_table`, returns result(s) or result DataFrame.
        """
        if args is None:
            args = []
        if commit is None:
            commit = True

        if not self.connected():
            self.connect()

        if type(args) != list:
            args = [args]

        input_args = args

        success = False
        result = []
        result_table = pd.DataFrame()
        error = Exception("retries must be greater than or equal to 0")
        for i in range(retries + 1):
            try:
                args = input_args + ['0'] * num_outputs
                result = list(self.cursor.callproc(sp, args))[-num_outputs:]
                if output_table is not None:
                    result_table = self.query(f"SELECT * FROM {output_table}")
                success = True
                break
            except mysql.connector.errors.DatabaseError as e:
                error = Exception(e.__str__())
            except mysql.connector.errors.InterfaceError as e:
                error = Exception(e.__str__())
            except Exception as e:
                error = e
        if not success:
            raise error

        if len(result) == 1:
            result = result[0]

        if commit:
            self.commit()

        if output_table:
            if num_outputs == 0:
                return result_table
            else:
                return result, result_table
        return result
