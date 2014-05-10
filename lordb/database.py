import random
from util import ContentGen


class DataBase:
    """Entity representing a database"""

    def __init__(self, engine, name):
        eng = __import__(engine)
        self.conn = eng.connect(name)

    def get_cursor(self):
        return self.conn.cursor()

    def fill(self, *args, **k_args):
        c = self.conn.cursor()

        for table in self.get_tables():
            Table(self.conn, table).fill(*args, **k_args)

        self.conn.commit()

    def get_tables(self):
        c = self.conn.cursor()
        tables = []

        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        for (name,) in c.execute(sql):
            tables.append(name)

        return tables


class Table:
    """Database entity representing a collection of data"""

    def __init__(self, cursor, name):
        self.cursor = cursor
        self.name = name
        self.content_gen = ContentGen()

    def fill(self, n=10):
        self.__populate_fields()

        c = self.cursor
        sql = self.create_sql()
        for i in xrange(n):
            c.execute(sql, self.get_random_params())

    def create_sql(self):
        field_names = [i["name"] for i in self.fields]

        return "INSERT INTO {0} VALUES ({1})".format(
            self.name,
            ", ".join([":{0}".format(i) for i in field_names])
        )

    def get_random_params(self):
        values = {}

        for field in self.fields:
            value = None
            if field["type"] == "integer":
                value = self.content_gen.get_int(0, 9999)
            elif field["type"] == "text":
                value = self.content_gen.get_text(255)

            values[field["name"]] = value

        return values

    def __populate_fields(self):
        c = self.cursor

        self.fields = []

        sql = "PRAGMA table_info({0})".format(self.name)
        for (num, name, f_type, _, _, _) in c.execute(sql):
            self.fields.append({"name": name, "type": f_type})
