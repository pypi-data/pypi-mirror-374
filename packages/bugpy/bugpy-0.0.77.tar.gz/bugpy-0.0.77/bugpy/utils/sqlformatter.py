""" Class for formatting SQL queries"""
import pandas as pd
from . import convert_json


class SqlFormatter:
    """ Tool to aid formatting SQL queries

        :param table_schema: dictionary containing the tables and their associated data types
    """

    def __init__(self, table, include_autokey, cxn):
        self.data_types = {'varchar': "'",
                           'int': "",
                           'json': "'",
                           'datetime': "'",
                           'bool': "",
                           'bit': "",
                           'tinyint': "",
                           'float': "",
                           'enum': "'",
                           'date': "'",
                           'time': "'"}

        query = f"""SHOW COLUMNS FROM {table}"""
        if not include_autokey:
            query += " WHERE Extra <> 'auto_increment'"

        self.table_schema = cxn.query(query)

    def string_wrap(self, string, column, table_schema):
        """ Formats string appropriately for insertion into column """
        if pd.isnull(string):
            output = 'NULL'
        else:
            wrapper = self.data_types[table_schema[column]]
            if type(string)==str:
                string = string.replace("'","\\'")
            output = "{0}{1}{0}".format(wrapper, string)

        return output

    def format(self, dataframe):
        """ Formats a dataframe for insert into the table """

        table_schema = self.table_schema[self.table_schema['Field'].isin(dataframe.columns)].reset_index(drop=True)

        if type(table_schema['Type'][0]) == bytes:
            table_schema['Type'] = table_schema['Type'].str.decode("utf-8")

        table_schema['Type'] = table_schema['Type'].str.split('(', expand=True)[0]

        table_schema = pd.Series(table_schema['Type'].values, index=table_schema['Field']).to_dict(
            into=dict)

        dataframe = dataframe[table_schema.keys()]

        for column in dataframe:
            if table_schema[column] == 'json':
                dataframe.loc[:, column] = dataframe[column].apply(convert_json)

            if table_schema[column] == 'datetime':
                dataframe[column] = dataframe[column].astype('O')

            dataframe[column] = dataframe[column].astype(object)
            dataframe.loc[:, column] = dataframe[column].apply(self.string_wrap, column=column,
                                                               table_schema=table_schema)

        return dataframe
