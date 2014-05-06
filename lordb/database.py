class DataBase:

    def __init__(self, engine, name):
        eng = __import__(engine)
        self.conn = eng.connect(name)

    def get_tables(self):
        c = self.conn.cursor()
        tables = []

        sql = "SELECT name FROM sqlite_master WHERE type='table'"
        for (name,) in c.execute(sql):
            tables.append(name)

        return tables
