from util import ContentGen, OutputProgress
from abc import ABCMeta, abstractmethod
import sys
import argparse

version = "0.1.0"   # Application version


class ArgumentError(Exception):
    """
    Exception used when an Error
    with arguments in command line happens
    For an example: See '_validate_args' in the implementations of DbmsHandle.
    """
    pass


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

        self._parser.add_argument(
            "--filter", dest="filter", nargs="+",
            help=("Filter to populate specific tables in "
                  "the database; Separate tables with spaces ' '"))

    def execute(self, args=None):
        if args is None:
            args = sys.argv[1:]

        self.options = self._parser.parse_args(args)
        self._call_dbms()

    def _call_dbms(self):
        try:
            self._validate_args()
            self._dbms_handles[self.options.dbms](self.options).execute()
        except ArgumentError, e:
            self._parser.error(e.message)

    def _validate_args(self):
        if self.options.dbms is None:
            raise ArgumentError("Parameter '-d' (DBMS) is required.")


class DbmsHandle(object):
    __metaclass__ = ABCMeta

    def __init__(self, args):
        self.options = args
        self.output_progress = OutputProgress(args.number, sys.stdout.write)
        self.counters = {
            "inserts": 0,
            "insert_errors": 0,
        }

    def execute(self):
        """
        A "TemplateMethod" to execute the dbms handle
        """
        self._validate_args()

        self._show_intro()
        self._execute()
        self._show_ending()

    def _show_intro(self):
        print "LoremDb v" + version
        print "------------------------------------"

    def _execute(self):
        """
        Execute the program
        """
        db = self._create_database()

        # Adding main 'slots'
        db.on_change_table.register(self._current_table_changed)
        db.on_insert.register(self._insert_received)
        db.on_insert_error.register(self._insert_error_received)

        if self.options.filter is not None:
            db.filter(*self.options.filter)

        db.fill(self.options.number)

    def _current_table_changed(self, table_info):
        print ""
        print "Populating '{}'".format(table_info["name"])
        self.output_progress.reset()

    def _insert_received(self):
        self.output_progress()
        sys.stdout.flush()
        self.counters["inserts"] += 1

    def _insert_error_received(self, e):
        self.counters["insert_errors"] += 1

    def _show_ending(self):
        print ""
        print "... Finished"
        print ""
        print "------------------------------------"
        print "Inserts: {}".format(self.counters["inserts"])
        print "Inserts with error: {}".format(self.counters["insert_errors"])
        print "Inserts with success: {}".format(
            self.counters["inserts"] - self.counters["insert_errors"]
        )
        print "------------------------------------"
        print ""

    @abstractmethod
    def _validate_args(self):
        """
        Check if args are valid
        """
        return NotImplemented

    @abstractmethod
    def _create_database(self):
        """
        Create a database object.
        """
        return NotImplemented


class MysqlDbmsHandle(DbmsHandle):

    def _validate_args(self):
        if self.options.database is None:
            raise ArgumentError("Parameter '--db' (Database) is required.")

        if self.options.user is None:
            raise ArgumentError("Parameter '-u|--user' (User) is required.")

    def _create_database(self):
        params = {
            "user": self.options.user,
            "password": self.options.password,
            "database": self.options.database,
            "host": self.options.host,
            "port": self.options.port,
            "content_gen": ContentGen()
        }

        # Remove None values
        params = {k: v for k, v in params.iteritems() if v is not None}

        from database import mysql
        return mysql.DataBase(**params)


class SqliteDbmsHandle(DbmsHandle):
    def _validate_args(self):
        if self.options.database is None:
            raise ArgumentError("Parameter '--db' (Database) is required.")

    def _create_database(self):
        from database import sqlite
        return sqlite.DataBase(
            content_gen=ContentGen(),
            name=self.options.database)


class Signal(object):

    def __init__(self):
        self._slots = {}

    def __call__(self, *args, **kwargs):
        for key, func in self._slots.iteritems():
            func.im_func(func.im_self, *args, **kwargs)

    def register(self, slot):
        self._slots[self._get_key(slot)] = slot

    def unregister(self, slot):
        key = self._get_key(slot)
        if key in self._slots:
            del self._slots[key]

    def _get_key(self, slot):
        return (slot.im_func, id(slot.im_self))
