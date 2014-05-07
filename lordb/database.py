import random


class DataBase:
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
    text_options = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "In at mauris mattis, luctus purus ut, elementum nibh.",
        "Nunc imperdiet quam ut enim sodales, non lobortis quam lacinia.",
        "Donec eu risus pulvinar, luctus nisi vel, euismod turpis.",
        "Ut ornare lacus vitae placerat placerat.",
    ]

    def __init__(self, cursor, name):
        self.cursor = cursor
        self.name = name

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
                value = random.randint(0, 99999)
            elif field["type"] == "text":
                idx = random.randint(0, len(self.text_options) - 1)
                value = self.text_options[idx]

            values[field["name"]] = value

        return values

    def __populate_fields(self):
        c = self.cursor

        self.fields = []

        sql = "PRAGMA table_info({0})".format(self.name)
        for (num, name, f_type, _, _, _) in c.execute(sql):
            self.fields.append({"name": name, "type": f_type})
