import core


class Table(core.Table):

    def _create_insert_sql(self):
        field_names = [i.get_name() for i in self._get_fields()]

        return "INSERT INTO {0} VALUES ({1})".format(
            self.name,
            ", ".join([":{0}".format(i) for i in field_names])
        )

    def _get_fields(self):
        if hasattr(self, "fields"):
            return self.__fields

        c = self.get_cursor()

        self.__fields = []

        sql = "PRAGMA table_info({0})".format(self.name)
        for (num, name, f_type, _, _, _) in c.execute(sql):
            if f_type == "integer":
                field = IntegerField(name, 0, 9999)
            elif f_type == "text":
                field = TextField(name, 255)
            else:
                raise Exception("Unexpected column type '{0}'".format(f_type))

            self.__fields.append(field)

        return self.__fields


class IntegerField(core.Field):
    def __init__(self, name, min, max):
        super(IntegerField, self).__init__(name)
        self.min = min
        self.max = max

    def get_random_value(self):
        return self._content_gen.get_int(self.min, self.max)


class TextField(core.Field):
    def __init__(self, name, length):
        super(TextField, self).__init__(name)
        self.length = length

    def get_random_value(self):
        return self._content_gen.get_text(self.length)


class DataBase(core.DataBase):
    _table_cls = Table

    def __init__(self, name, engine="sqlite3"):
        self.name = name
        self._engine = engine

    def get_conn(self):
        if hasattr(self, '_conn'):
            return self._conn

        eng = __import__(self._engine)
        self._conn = eng.connect(self.name)
        return self._conn

    def get_tables_name_sql(self):
        """Returns a query with table's name in the first column"""
        return "SELECT name FROM sqlite_master WHERE type='table'"
