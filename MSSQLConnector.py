import sqlalchemy as db
from sqlalchemy.sql import text


class MSSQLConnector:

    def __init__(self):
        self.engine = None
        self.conn = None
        self.dbname = None

    def connect(self, endereco, porta, banco, user, passwd):
        self.engine = db.create_engine('mssql+pyodbc://' + user + ':' + passwd + '@' + endereco + ':' + str(porta) + '/' + banco + '?driver=ODBC+Driver+17+for+SQL+Server')
        self.conn = self.engine.connect()
        self.dbname = banco

    def get_schemas(self):
        stmt = text(
            "SELECT schema_name FROM information_schema.schemata where schema_name = 'dbo' or (schema_name != 'information_schema' and schema_name not like 'db_%' and schema_name not in ('guest', 'sys')) order by schema_name")
        result = self.conn.execute(stmt)
        resultdata = result.fetchall()
        ret = []
        for row in resultdata:
            ret.append(row.values()[0])
        return ret

    def get_tables(self, schema):
        stmt = text(
            "select TABLE_NAME from {}.INFORMATION_SCHEMA.TABLES where TABLE_SCHEMA = '{}' order by TABLE_NAME".format(
                self.dbname, schema))
        result = self.conn.execute(stmt)
        resultdata = result.fetchall()
        ret = []
        for entry in resultdata:
            ret.append(entry[0])
        return ret

    def get_columns(self, schema, tablename):
        stmt = text(
            "select COLUMN_NAME, DATA_TYPE from INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{}' and TABLE_SCHEMA = '{}'".format(
                tablename, schema))
        result = self.conn.execute(stmt)
        result_data = result.fetchall()
        ret = {}
        for entry in result_data:
            datatype = 'Indefinido'
            if entry[1] == 'varchar':
                datatype = 'Texto'
            if entry[1] == 'bit':
                datatype = 'Booleano'
            if entry[1] == 'bigint' or entry[1] == 'smallint' or entry[1] == 'numeric' or entry[1] == 'int':
                datatype = 'Numérico'
            if entry[1] == 'datetime':
                datatype = 'Data / Hora'
            ret[entry[0]] = datatype
        return ret

    def execute(self, query):
        stmt = text(query)
        result = self.conn.execute(stmt)
        result_data = result.fetchall()
        return result_data

    def get_result(self, query, schema, tablename):
        columns = self.get_columns(schema, tablename)
        result = self.execute(query)
        return columns, result

    def close_connection(self):
        self.conn.close()
