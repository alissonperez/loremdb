import random
from loremdb.util import ContentGen
from loremdb.common import Signal
from abc import ABCMeta, abstractmethod


class Table(object):
    """
    Abstract entity representing a collection of data.

    Signals:

    on_insert:
        Signal on insert an item in the table (with error or not).
        Usage:
        table_object.on_insert.register(self._callback_method)

    on_insert_error:
        Signal when an error happens on insert.
        Usage:
        table_object.on_insert_error.register(self._callback_method)
    """

    __metaclass__ = ABCMeta

    def __init__(self, database, name, content_gen):
        self.name = name
        self._database = database
        self._content_gen = content_gen
        self.show_errors = False

        # Signal on insert an item (with error or not)
        self.on_insert = Signal()

        # Signal when an error happens on insert
        self.on_insert_error = Signal()

    def fill(self, n=10):
        c = self.get_cursor()

        sql = self._create_insert_sql()
        for i in xrange(n):
            try:
                self.on_insert()
                c.execute(sql, self._get_random_params())
            except Exception, e:
                self.on_insert_error(e)
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

    def __init__(self, name, nullable=False, default=None, *args, **kargs):
        self.name = name
        self.nullable = nullable
        self.default = None

    def get_name(self):
        return self.name

    def get_random_value(self):
        if self.nullable and self.content_gen.get_int(0, 4) == 1:
            return None

        if self.default is not None and self.content_gen.get_int(0, 4) == 1:
            return self.default

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
        self.on_insert_error = Signal()

    def fill(self, *args, **kargs):
        c = self.get_cursor()

        for table in self.get_tables():
            table = self._table_cls(self, table, self._content_gen)
            table.show_errors = self.show_errors
            table.on_insert.register(self._on_insert_callback)
            table.on_insert_error.register(self._on_insert_error_callback)
            self.on_change_table(table.table_info)
            table.fill(*args, **kargs)

        self.commit()
        c.close()

    def _on_insert_callback(self, *args, **kargs):
        self.on_insert(*args, **kargs)

    def _on_insert_error_callback(self, *args, **kargs):
        self.on_insert_error(*args, **kargs)

    def get_tables(self):
        c = self.get_cursor()
        tables = []

        c.execute(self.get_tables_name_sql())
        for (name,) in c:
            tables.append(name)

        c.close()

        if self._filter_args is None:
            return tables

        # Check if filters are valid
        diff_tables = list(set(self._filter_args) - set(tables))
        if len(diff_tables) > 0:
            raise Exception(
                "Unespected filters: " + ", ".join(diff_tables)
            )

        return self._filter_args

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
