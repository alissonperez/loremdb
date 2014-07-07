from util import ContentGen
from abc import ABCMeta, abstractmethod
import sys
import argparse

version = "0.0.1"   # Application version


class LoremDb(object):

    def __init__(self):
        self._dbms_handles = {
            "mysql": MysqlDbmsHandle,
            "sqlite": SqliteDbmsHandle,
        }

        self._parser = argparse.ArgumentParser(description='LoremDb')

        self._parser.add_argument(
            "-d", "--dbms", dest="dbms",
            help="e.g.: " + self._dbms_handles.keys()[0],
            choices=self._dbms_handles.keys())

        self._parser.add_argument(
            "-b", "--db", dest="database", help="Database name")

        self._parser.add_argument(
            "-u", "--user", dest="user", help="Database user")

        self._parser.add_argument(
            "-p", "--password", dest="password", help="Database pass")

        self._parser.add_argument(
            "--host", dest="host", help="Database host")

        self._parser.add_argument(
            "--port", dest="port", help="Database port")

        self._parser.add_argument(
            "-n", "--number", default=100, type=int,
            dest="number", help="Number of registers to fill")

        self._parser.add_argument(
            "--version", action="version", version="%(prog)s "+version)

    def execute(self, args=None):
        if args is None:
            args = sys.argv[1:]

        self.options = self._parser.parse_args(args)
        self._call_dbms()

    def _call_dbms(self):
        try:
            self._validate_args()
            self._dbms_handles[self.options.dbms](self.options).execute()
        except Exception, e:
            self._parser.error(e.message)

    def _validate_args(self):
        if self.options.dbms is None:
            raise Exception("Parameter '-d' (DBMS) is required.")


class DbmsHandle(object):
    __metaclass__ = ABCMeta

    def __init__(self, args):
        self.options = args

    def execute(self):
        """
        A "TemplateMethod" to execute the dbms handle
        """
        self._validate_args()
        self._execute()

    @abstractmethod
    def _validate_args(self):
        """
        Check if args are valid
        """
        return NotImplemented

    @abstractmethod
    def _execute(self):
        """
        Execute the program
        """
        return NotImplemented


class MysqlDbmsHandle(DbmsHandle):

    def _validate_args(self):
        if self.options.database is None:
            raise Exception("Parameter '--db' (Database) is required.")

        if self.options.user is None:
            raise Exception("Parameter '-u|--user' (User) is required.")

    def _execute(self):
        params = self._get_params()
        params["content_gen"] = ContentGen()

        from database import mysql
        db = mysql.DataBase(**params)
        db.fill(self.options.number)

    def _get_params(self):
        params = {
            "user": self.options.user,
            "password": self.options.password,
            "database": self.options.database,
            "host": self.options.host,
            "port": self.options.port,
        }

        # Remove None values
        return {k: v for k, v in params.iteritems() if v is not None}


# @todo
class SqliteDbmsHandle(object):
    pass