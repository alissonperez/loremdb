from core import DataBase as _DataBase
from core import Table as _Table
from importlib import import_module


class Table(_Table):

    def _create_insert_sql(self):
        fields_num = len(self._get_fields())
        return "INSERT INTO {0} ({1}) VALUES ({2})".format(
            self.name,
            ", ".join([i["name"] for i in self._get_fields()]),
            ", ".join(["%s" for i in range(fields_num)])
        )

    def _get_random_params(self):
        values = []

        for field in self._get_fields():
            value = ''
            # TODO: Implements this
            values.append(value)

        return values

    def _get_fields(self):
        if hasattr(self, "fields"):
            return self.__fields

        c = self.get_cursor()

        self.__fields = []

        sql = """SELECT
            column_name, data_type
            FROM information_schema.columns
            WHERE TABLE_SCHEMA = %s AND table_name = %s
            ORDER BY ordinal_position"""

        c.execute(sql, (self._database.database, self.name))

        for (name, data_type) in c:
            self.__fields.append({"name": name, "type": data_type})

        c.close()

        return self.__fields


class DataBase(_DataBase):
    _table_cls = Table

    def __init__(self, user, password, database, engine="mysql.connector", port='3306'):
        self.user = user
        self.password = password
        self.database = database
        self.port = port

        self._engine = engine

    def get_conn(self):
        if hasattr(self, "_conn"):
            return self._conn

        eng = import_module(self._engine)

        self._conn = eng.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )

        return self._conn

    def get_tables_name_sql(self):
        """Returns a query with table's name in the first column"""
        return """SELECT
            table_name
            FROM information_schema.tables
            WHERE TABLE_SCHEMA = '{0}'""".format(self.database)
