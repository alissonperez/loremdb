import unittest
from lordb.database.core import DataBaseCreator, DataBase
from lordb.database.sqlite import DataBase as SqliteDataBase
from lordb.database.mysql import DataBase as MysqlDataBase
from lordb.util import ContentGen


class test_database_creator(unittest.TestCase):

    def test_create_sqlite(self):
        database = DataBaseCreator().create_sqlite(
            ContentGen(), "/tmp/db-test")

        self.assertTrue(isinstance(database, DataBase))
        self.assertTrue(isinstance(database, SqliteDataBase))

    def test_create_mysql(self):
        database = DataBaseCreator().create_mysql(
            content_gen=ContentGen(),
            user='root',
            password='',
            database='lordb_test'
        )

        self.assertTrue(isinstance(database, DataBase))
        self.assertTrue(isinstance(database, MysqlDataBase))
