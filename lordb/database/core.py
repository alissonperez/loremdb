import random
from lordb.util import ContentGen


class DataBaseCreator(object):
    """Factory to create databases"""

    def create_sqlite(self, name, *args, **kargs):
        from sqlite import DataBase as _DataBase
        return _DataBase(name, *args, **kargs)

    def create_mysql(self, user, password, database, *args, **kargs):
        from mysql import DataBase as _DataBase
        return _DataBase(user, password, database, *args, **kargs)


class Table(object):
    """Abstract entity representing a collection of data"""

    def __init__(self, database, name):
        self.name = name

        self._database = database
        self._content_gen = ContentGen()

    def fill(self, n=10):
        c = self.get_cursor()

        sql = self._create_insert_sql()
        for i in xrange(n):
            params = self._get_random_params()
            c.execute(sql, self._get_random_params())

        c.close()

    def get_cursor(self):
        return self._database.get_cursor()

    def _create_insert_sql(self):
        """Creates an insert sql with 'wildcards'
        to use with _get_random_params()."""
        return NotImplemented

    def _get_random_params(self):
        """Returns a dictionary with field names as index and
        its random values"""

        values = {}
        for field in self._get_fields():
            values[field.get_name()] = field.get_random_value()

        return values

    def _get_fields(self):
        """Returns fields in the Table
        Used with query returned in _create_insert_sql() and
        _get_random_params()"""
        return NotImplemented


class Field(object):

    def __init__(self, name):
        self.name = name
        self._content_gen = ContentGen()

    def get_name(self):
        return self.name

    def get_random_value(self):
        return NotImplemented


class DataBase(object):
    """Abstract entity representing a database"""

    _table_cls = Table

    def fill(self, *args, **kargs):
        c = self.get_cursor()

        for table in self.get_tables():
            self._table_cls(self, table).fill(*args, **kargs)

        self.commit()
        c.close()

    def get_tables(self):
        c = self.get_cursor()
        tables = []

        c.execute(self.get_tables_name_sql())
        for (name,) in c:
            tables.append(name)

        c.close()

        return tables

    def get_cursor(self):
        return self.get_conn().cursor()

    def commit(self):
        self.get_conn().commit()

    def get_conn(self):
        """Returns a connection object.
        It is overridden by the subclasses"""
        return NotImplemented

    def get_tables_name_sql(self):
        """Returns a query with table's name in the first column.
        It is overridden by the subclasses"""
        return NotImplemented
