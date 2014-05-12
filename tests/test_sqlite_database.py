import unittest
from lordb.database.core import DataBaseCreator
from lordb.database.sqlite import Table
import sqlite3


class SqliteDataBaseTestCase(unittest.TestCase):
    database_name = "/tmp/lordb-unittest-database"

    def setUp(self):
        self.create_tables()
        self._database = DataBaseCreator().create_sqlite(
            name=self.database_name
        )

    def create_tables(self):
        self.conn = sqlite3.connect(self.database_name)

        c = self.conn.cursor()

        c.execute("drop table if exists users")
        c.execute("drop table if exists permissions")

        c.execute("""create table if not exists
        users (user_id integer PRIMARY KEY, name text, age integer)""")

        c.execute("""create table if not exists
        permissions (
            permission_id integer PRIMARY KEY,
            user_id integer,
            action text
        )""")

        self.conn.commit()


class TestDataBase(SqliteDataBaseTestCase):
    num = 10

    def test_fill(self):
        c = self._database.get_cursor()

        results = c.execute("SELECT * from users")
        self.assertEquals(0, len(results.fetchall()))

        results = c.execute("SELECT * from permissions")
        self.assertEquals(0, len(results.fetchall()))

        self._database.fill(n=10)

        results = c.execute("SELECT * from users")
        self.assertEquals(10, len(results.fetchall()))

        results = c.execute("SELECT * from permissions")
        self.assertEquals(10, len(results.fetchall()))

    def test_get_tables(self):
        tables = self._database.get_tables()

        self.assertEquals(2, len(tables))

        self.assertTrue("users" in tables)
        self.assertTrue("permissions" in tables)


class TestTable(SqliteDataBaseTestCase):
    def setUp(self):
        super(TestTable, self).setUp()
        self.table = Table(self._database, "users")

    def test_fill(self):
        c = self._database.get_cursor()

        results = c.execute("SELECT name, age from users")
        self.assertEquals(0, len(results.fetchall()))

        self.table.fill(n=10)
        self._database.get_conn().commit()

        results = c.execute("SELECT name, age from users")
        self.assertEquals(10, len(results.fetchall()))
