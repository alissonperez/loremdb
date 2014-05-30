import core
from importlib import import_module


class Table(core.Table):

    def _create_insert_sql(self):
        fields_num = len(self._get_fields())
        return "INSERT INTO {0} ({1}) VALUES ({2})".format(
            self.name,
            ", ".join([i["name"] for i in self._get_fields()]),
            ", ".join(["%s" for i in range(fields_num)])
        )

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
            # @todo - Implement
            pass

        c.close()

        return self.__fields


class IntegerField(core.Field):
    unsigned = False
    num_signed_max = 2147483647  # Int Default

    def __init__(self, name, unsigned=False, *args, **kargs):
        super(IntegerField, self).__init__(name, *args, **kargs)
        self.unsigned = unsigned

    def get_random_value(self):
        if self.unsigned:
            return self._content_gen.get_int(0, self.num_signed_max * 2)

        return self._content_gen.get_int(
            self.num_signed_max * -1, self.num_signed_max
        )


class TinyIntField(IntegerField):
    num_signed_max = 127


class SmallIntField(IntegerField):
    num_signed_max = 32767


class SmallIntField(IntegerField):
    num_signed_max = 8388607


class IntField(IntegerField):
    pass


class IntField(IntegerField):
    num_signed_max = 9223372036854775807


class DateField(core.Field):
    def get_random_value(self):
        return self._content_gen.get_date()


class DateTimeField(core.Field):
    def get_random_value(self):
        return self._content_gen.get_datetime()


class TimestampField(core.Field):
    def get_random_value(self):
        return 126144000 + self._content_gen.get_int(0, 315360000)


class DataBase(core.DataBase):
    _table_cls = Table

    def __init__(
            self, user, password, database,
            engine="mysql.connector", port="3306"):
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
        return """SELECT table_name
            FROM information_schema.tables
            WHERE TABLE_SCHEMA = '{0}'""".format(self.database)
