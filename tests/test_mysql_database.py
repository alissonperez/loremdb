import unittest
from lordb.database.core import DataBaseCreator
from lordb.database import mysql


class DataBaseTestCase(unittest.TestCase):

    def setUp(self):
        self.database = self.get_database()
        self.clean_tables()

    def tearDown(self):
        self.database.commit()

    def get_database(self):
        return DataBaseCreator().create_mysql(
            user="root",
            password="",
            database="lordb_test"
        )

    def clean_tables(self):
        c = self.database.get_cursor()
        c.execute("DELETE FROM users")
        self.database.commit()
        c.close()


class TestDataBase(DataBaseTestCase):
    num = 10

    def test_fill(self):
        c = self.database.get_cursor()

        c.execute("SELECT * from users")
        self.assertEquals(0, len(c.fetchall()))

        self.database.fill(n=10)

        c.execute("SELECT * from users")
        self.assertEquals(10, len(c.fetchall()))

        c.close()

    def test_get_tables(self):
        tables = self.database.get_tables()

        self.assertEquals(1, len(tables))

        self.assertTrue("users" in tables)


class TestTable(DataBaseTestCase):

    def setUp(self):
        super(TestTable, self).setUp()
        self.table = mysql.Table(self.database, "users")

    def test_fill(self):
        c = self.table.get_cursor()

        c.execute("SELECT name, age from users")
        self.assertEquals(0, len(c.fetchall()))

        self.table.fill(n=10)
        self.database.commit()

        c.execute("SELECT name, age from users")
        self.assertEquals(10, len(c.fetchall()))


class TestIntegerField(unittest.TestCase):

    def test_get_content_gen(self):
        f = mysql.IntegerField("age")
