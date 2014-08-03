import random
from loremdb.util import ContentGen
from loremdb import Signal
from abc import ABCMeta, abstractmethod


class DataBaseCreator(object):
    """
    Factory to create databases
    """

    def create_sqlite(
            self, content_gen, name, *args, **kargs):
        from sqlite import DataBase as _DataBase
        return _DataBase(content_gen, name, *args, **kargs)

    def create_mysql(
            self, content_gen, user, database, *args, **kargs):
        from mysql import DataBase as _DataBase
        return _DataBase(content_gen, user, database, *args, **kargs)


class Table(object):
    """
    Abstract entity representing a collection of data
    """

    __metaclass__ = ABCMeta

    def __init__(self, database, name, content_gen):
        self.name = name
        self._database = database
        self._content_gen = content_gen
        self.show_errors = False
        self.on_insert = Signal()

    def fill(self, n=10):
        c = self.get_cursor()

        sql = self._create_insert_sql()
        for i in xrange(n):
            try:
                self.on_insert()
                c.execute(sql, self._get_random_params())
            except Exception, e:
                if self.show_errors:
                    print "Exception: {0}".format(e)

        c.close()

    def get_cursor(self):
        return self._database.get_cursor()

    @property
    def table_info(self):
        return {"name": self.name}

    @abstractmethod
    def _create_insert_sql(self):
        """
        Creates an insert sql with 'wildcards'
        to use with _get_random_params().
        """
        return NotImplemented

    def _get_random_params(self):
        """
        Returns a dictionary with field names as index and
        its random values
        """

        values = []
        for field in self._get_fields():
            field.content_gen = self._content_gen
            values.append(field.get_random_value())

        return values

    @abstractmethod
    def _get_fields(self):
        """
        Returns fields in the Table
        Used with query returned in _create_insert_sql() and
        _get_random_params()
        """
        return NotImplemented


class Field(object):
    """
    Abstract entity representing a field in the Database
    """

    __metaclass__ = ABCMeta

    content_gen = None  # Instance of conntent generator

    def __init__(self, name, nullable=False, *args, **kargs):
        self.name = name
        self.nullable = nullable

    def get_name(self):
        return self.name

    def get_random_value(self):
        if self.nullable and self.content_gen.get_int(0, 4) == 1:
            return None

        return self._get_random_value()

    @abstractmethod
    def _get_random_value(self):
        return NotImplemented


class DataBase(object):
    """
    Abstract entity representing a database
    """

    __metaclass__ = ABCMeta

    _table_cls = Table

    def __init__(self, content_gen):
        self._content_gen = content_gen
        self.show_errors = False
        self._filter_args = None
        self.on_change_table = Signal()
        self.on_insert = Signal()

    def fill(self, *args, **kargs):
        c = self.get_cursor()

        for table in self.get_tables():
            table = self._table_cls(self, table, self._content_gen)
            table.show_errors = self.show_errors
            table.on_insert.register(self._on_insert_callback)
            self.on_change_table(table.table_info)
            table.fill(*args, **kargs)

        self.commit()
        c.close()

    def _on_insert_callback(self):
        self.on_insert()

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

    def filter(self, *args):
        """
        Filter param to fill
        """
        self._filter_args = args

    @abstractmethod
    def get_conn(self):
        """
        Returns a connection object.
        It is overridden by the subclasses
        """
        return NotImplemented

    @abstractmethod
    def get_tables_name_sql(self):
        """
        Returns a query with table's name in the first column.
        It is overridden by the subclasses
        """
        return NotImplemented
