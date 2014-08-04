import unittest
from loremdb.database.core import DataBaseCreator
from loremdb.database.sqlite import Table, TypeAffinity
from loremdb.util import ContentGen
import sqlite3


class TypeAffinityTestCase(unittest.TestCase):

    def test_integer(self):
        data_provider = [
            "BIGINT",
            "SMALLINT",
            "smallint",
            "UNSIGNED BIG INT",
            "tinyint",
        ]

        self._call_type_affinity_test("integer", data_provider)

    def test_text(self):
        data_provider = [
            "CHARACTER",
            "VARCHAR",
            "VARYING CHARACTER",
            "NCHAR",
            "NATIVE CHARACTER",
            "NVARCHAR",
            "TEXT",
            "CLOB",
        ]

        self._call_type_affinity_test("text", data_provider)

    def test_none(self):
        data_provider = [
            "BLOB",
            "",
        ]

        self._call_type_affinity_test("none", data_provider)

    def test_real(self):
        data_provider = [
            "REAL"
            "DOUBLE"
            "DOUBLE PRECISION"
            "FLOAT"
        ]

        self._call_type_affinity_test("real", data_provider)

    def test_numeric(self):
        data_provider = [
            "NUMERIC",
            "DECIMAL",
            "BOOLEAN",
            "DATE",
            "DATETIME"
        ]

        self._call_type_affinity_test("numeric", data_provider)

    def _call_type_affinity_test(self, espected, data_provider):
        for type_desc in data_provider:
            self._test_type_affinity(espected, type_desc)

    def _test_type_affinity(self, espected, type_desc):
        self.assertEquals(espected, TypeAffinity(type_desc).type)


class SqliteDataBaseTestCase(unittest.TestCase):
    database_name = "/tmp/loremdb-unittest-database"

    def setUp(self):
        self.create_tables()
        self._database = DataBaseCreator().create_sqlite(
            content_gen=ContentGen(),
            name=self.database_name
        )

    def create_tables(self):
        self.conn = sqlite3.connect(self.database_name)

        c = self.conn.cursor()

        c.execute("drop table if exists users")
        c.execute("drop table if exists permissions")

        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id integer PRIMARY KEY,
            name text,
            last_name VARCHAR,
            age integer,
            height real,
            creation_date date,
            profile_image blob,
            document UNSIGNED BIG INT
        )""")

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
        self.table = Table(self._database, "users", ContentGen())

    def test_fill(self):
        c = self._database.get_cursor()

        results = c.execute("SELECT name, age from users")
        self.assertEquals(0, len(results.fetchall()))

        self.table.fill(n=10)
        self._database.get_conn().commit()

        results = c.execute("SELECT name, age from users")
        self.assertEquals(10, len(results.fetchall()))
