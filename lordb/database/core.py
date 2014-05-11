import random
from lordb.util import ContentGen


class DataBaseCreator:
    """Factory to create databases"""

    def create_sqlite(self, name, engine="sqlite3"):
        from sqlite import DataBase as _DataBase
        return _DataBase(engine, name)


class Table:
    """Abstract entity representing a collection of data"""

    def __init__(self, cursor, name):
        self.cursor = cursor
        self.name = name
        self.content_gen = ContentGen()

    def get_cursor(self):
        return self.cursor

    def fill(self, n=10):
        c = self.cursor
        sql = self._create_sql()
        for i in xrange(n):
            c.execute(sql, self._get_random_params())

    def _create_sql(self):
        field_names = [i["name"] for i in self._get_fields()]

        return "INSERT INTO {0} VALUES ({1})".format(
            self.name,
            ", ".join([":{0}".format(i) for i in field_names])
        )

    def _get_random_params(self):
        return NotImplemented

    def _get_fields(self):
        return NotImplemented


class DataBase:
    """Abstract entity representing a database"""

    _table_cls = Table

    def __init__(self, engine, name):
        eng = __import__(engine)
        self.conn = eng.connect(name)

    def fill(self, *args, **k_args):
        c = self.conn.cursor()

        for table in self.get_tables():
            self._table_cls(self.conn, table).fill(*args, **k_args)

        self.conn.commit()

    def get_tables(self):
        c = self.conn.cursor()
        tables = []

        for (name,) in c.execute(self.get_tables_name_sql()):
            tables.append(name)

        return tables

    def get_tables_name_sql(self):
        """Returns a query with table's name in the first column.
        It is overridden by the subclasses"""
        return NotImplemented
