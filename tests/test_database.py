import unittest
from lordb.database import DataBase
import sqlite3


class TestDataBase(unittest.TestCase):
    database_name = "/tmp/lordb-unittest-database"

    def setUp(self):
        self.create_tables()
        self.database = DataBase(
            engine="sqlite3",
            name=self.database_name
        )

    def create_tables(self):
        self.conn = sqlite3.connect(self.database_name)

        c = self.conn.cursor()

        c.execute(
            "create table if not exists users (name text, age integer)"
        )

        c.execute(
            "create table if not exists permissions (name text, age integer)"
        )

        c.execute(
            "create table if not exists newstexts (name text, age integer)"
        )

        self.conn.commit()

    def test_get_tables(self):
        tables = self.database.get_tables()

        self.assertEquals(3, len(tables))

        self.assertTrue("users" in tables)
        self.assertTrue("permissions" in tables)
        self.assertTrue("newstexts" in tables)
