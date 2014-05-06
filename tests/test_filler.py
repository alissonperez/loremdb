import unittest
from lordb.filler import Filler
from lordb.database import DataBase
import sqlite3


class TestFiller(unittest.TestCase):
    database_name = "/tmp/lordb-unittest"
    number_of_registers = 10

    def setUp(self):
        self.create_table()
        self.f = Filler(
            database=DataBase(
                engine="sqlite3",
                name=self.database_name
            ),
            n=self.number_of_registers
        )

    def create_table(self):
        self.conn = sqlite3.connect(self.database_name)

        c = self.conn.cursor()

        # Create and clear table
        c.execute("create table if not exists users (name text, age integer)")
        c.execute("delete from users")

        self.conn.commit()

    def test_fill(self):
        self.f.fill()

        c = self.conn.cursor()

        c.execute("SELECT name, age from users")
        self.assertEquals(self.number_of_registers, c.rowcount)
