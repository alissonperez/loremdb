import unittest
from loremdb.util import ContentGen
from loremdb.database import sqlite
from loremdb.database.core import TableKeySorterByRelation
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
        self.assertEquals(espected, sqlite.TypeAffinity(type_desc).type)


class SqliteDataBaseTestCase(unittest.TestCase):
    database_name = "/tmp/loremdb-unittest-database"

    def setUp(self):
        self.create_tables()
        self._database = sqlite.DataBase(ContentGen(), self.database_name)

    def create_tables(self):
        self.conn = sqlite3.connect(self.database_name)

        c = self.conn.cursor()

        c.execute("drop table if exists users")
        c.execute("drop table if exists permissions")
        c.execute("drop table if exists permissions_roles")

        c.execute("""CREATE TABLE IF NOT EXISTS users (
            user_id integer PRIMARY KEY,
            name text,
            last_name VARCHAR,
            age integer,
            height real,
            creation_date date,
            profile_image blob,
            document UNSIGNED BIG INT)""")

        c.execute("""CREATE TABLE IF NOT EXISTS permissions (
            permission_id integer PRIMARY KEY,
            user_id integer,
            action text,
            FOREIGN KEY (user_id) REFERENCES users(user_id))""")

        c.execute("""CREATE TABLE IF NOT EXISTS permissions_roles (
            permission_role_id integer PRIMARY KEY,
            permission_id integer,
            role_id integer,
            FOREIGN KEY (permission_id) REFERENCES permissions(permission_id))""")

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

        self.assertEquals(3, len(tables))

        self.assertTrue("users" in tables)
        self.assertTrue("permissions" in tables)
        self.assertTrue("permissions_roles" in tables)


class TestTable(SqliteDataBaseTestCase):
    def setUp(self):
        super(TestTable, self).setUp()
        self.table = sqlite.Table(self._database, "users", ContentGen())

    def test_fill(self):
        c = self._database.get_cursor()

        results = c.execute("SELECT name, age from users")
        self.assertEquals(0, len(results.fetchall()))

        self.table.fill(n=10)
        self._database.get_conn().commit()

        results = c.execute("SELECT name, age from users")
        self.assertEquals(10, len(results.fetchall()))

    def test_get_relations(self):
        self.table = sqlite.Table(self._database, "permissions", ContentGen())

        test_relations = [{"columns": ["user_id"],
                           "ref_table": "users",
                           "ref_columns": ["user_id"]}]

        self.assertEquals(test_relations, self.table.get_relations())

    def test_get_related_tables(self):
        self.table = sqlite.Table(self._database, "permissions", ContentGen())
        self.assertEquals(["users"], self.table.get_related_tables())

    def test_sorter(self):
        tables = [
            sqlite.Table(self._database, "permissions_roles", ContentGen()),
            sqlite.Table(self._database, "permissions", ContentGen()),
            sqlite.Table(self._database, "users", ContentGen()),
        ]

        tables_sorted = sorted(tables, key=TableKeySorterByRelation)

        self.assertEquals("users", tables_sorted[0].name)
        self.assertEquals("permissions", tables_sorted[1].name)
        self.assertEquals("permissions_roles", tables_sorted[2].name)
