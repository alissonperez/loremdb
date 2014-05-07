import unittest
from lordb.database import (DataBase, Table)
import sqlite3


class TestDataBase(unittest.TestCase):
    database_name = "/tmp/lordb-unittest-database"
    num = 10

    def setUp(self):
        self.create_tables()
        self.database = DataBase(
            engine="sqlite3",
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

    def test_fill(self):
        c = self.conn.cursor()

        results = c.execute("SELECT * from users")
        self.assertEquals(0, len(results.fetchall()))

        results = c.execute("SELECT * from permissions")
        self.assertEquals(0, len(results.fetchall()))

        self.database.fill(n=10)

        results = c.execute("SELECT * from users")
        self.assertEquals(10, len(results.fetchall()))

        results = c.execute("SELECT * from permissions")
        self.assertEquals(10, len(results.fetchall()))

    def test_get_tables(self):
        tables = self.database.get_tables()

        self.assertEquals(2, len(tables))

        self.assertTrue("users" in tables)
        self.assertTrue("permissions" in tables)


class TestTable(unittest.TestCase):
    database_name = "/tmp/lordb-unittest-database"

    def setUp(self):
        self.conn = sqlite3.connect(self.database_name)

        self.create_tables()
        self.table = Table(self.conn, "users")

    def create_tables(self):
        c = self.conn.cursor()

        c.execute("drop table if exists users")
        c.execute("""create table if not exists
        users (name text, age integer)""")

        self.conn.commit()

    def test_fill(self):
        c = self.conn.cursor()

        results = c.execute("SELECT name, age from users")
        self.assertEquals(0, len(results.fetchall()))

        self.table.fill(n=10)
        self.conn.commit()

        results = c.execute("SELECT name, age from users")
        self.assertEquals(10, len(results.fetchall()))
