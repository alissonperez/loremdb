from util import ContentGen
from abc import ABCMeta, abstractmethod
from common import version
from os import linesep
import sys
import argparse


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
        print ("LoremDb v{}"
               " by Alisson R. Perez"
               "<alissonperez@outlook.com>".format(version))
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


class OutputProgress(object):
    """
    Show progress acording with a size (param progress_size)
    Ex:
    o = OutputProgress(100, sys.stdout.write) # All dots will be
    # written in the screen.

    o() # This will print (using sys.stdout.write) a dots
    # quantity related with 100.

    # OBS: Raise an StandardError if number of calls exceed
    # progress_size parameter.
    """

    line_size = 50
    lines = 10

    # Number of calls and actual dots, respectively.
    _calls_counter = 0
    _actual_dots = 0

    def __init__(self, progress_size, callback):
        self.progress_size = progress_size
        self._callback = callback

    def reset(self):
        self._calls_counter = 0
        self._actual_dots = 0

    def __call__(self):
        # The number of calls does'n exceed progres_size
        if self._calls_counter + 1 > self.progress_size:
            raise StandardError("Number of calls exhausted")

        self._calls_counter += 1
        self._print_dots()

    def _print_dots(self):
        total_dots = self.line_size * self.lines
        new_dots = int(self._calls_counter * total_dots / self.progress_size)

        self._call_callback(new_dots - self._actual_dots)

        self._actual_dots = new_dots

    def _call_callback(self, diff):
        old_line = int(self._actual_dots / self.line_size)

        for c in range(1, diff+1):
            self._callback(".")

            # Show percent
            act_line = int((self._actual_dots + c) / self.line_size)
            if act_line > old_line:
                self._show_percent(self._actual_dots + c)
                old_line = act_line

    def _show_percent(self, dots):
        self._callback(
            " %.0f%%" % (float(dots) / (self.line_size * self.lines) * 100)
        )

        self._callback(linesep)
