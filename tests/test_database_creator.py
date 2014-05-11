import unittest
from lordb.database.core import DataBaseCreator, DataBase
from lordb.database.sqlite import DataBase as SqliteDataBase


class test_database_creator(unittest.TestCase):

    def test_create(self):
        database = DataBaseCreator().create_sqlite("/tmp/db-test")

        self.assertTrue(isinstance(database, DataBase))
        self.assertTrue(isinstance(database, SqliteDataBase))
