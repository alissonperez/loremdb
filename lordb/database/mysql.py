# -*- coding: UTF-8 -*-

import core
from importlib import import_module
import re


class Table(core.Table):

    def _create_insert_sql(self):
        fields_num = len(self._get_fields())
        return "INSERT INTO {0} ({1}) VALUES ({2})".format(
            self.name,
            ", ".join([i["name"] for i in self._get_fields()]),
            ", ".join(["%s" for i in range(fields_num)])
        )

    def _get_fields(self):
        if hasattr(self, "fields"):
            return self.__fields

        c = self.get_cursor()

        self.__fields = []

        sql = """SELECT
            column_name, data_type
            FROM information_schema.columns
            WHERE TABLE_SCHEMA = %s AND table_name = %s
            ORDER BY ordinal_position"""

        c.execute(sql, (self._database.database, self.name))

        for (name, data_type) in c:
            # @todo - Implement
            pass

        c.close()

        return self.__fields


class IntegerField(core.Field):
    unsigned = False
    num_signed_max = 2147483647  # Int Default

    def __init__(self, name, unsigned=False, *args, **kargs):
        super(IntegerField, self).__init__(name, *args, **kargs)
        self.unsigned = unsigned

    def get_random_value(self):
        if self.unsigned:
            return self.content_gen.get_int(0, self.num_signed_max * 2)

        return self.content_gen.get_int(
            self.num_signed_max * -1, self.num_signed_max
        )


class TinyIntField(IntegerField):
    num_signed_max = 127


class SmallIntField(IntegerField):
    num_signed_max = 32767


class MediumIntField(IntegerField):
    num_signed_max = 8388607


class IntField(IntegerField):
    pass


class BigIntField(IntegerField):
    num_signed_max = 9223372036854775807


class DateField(core.Field):
    def get_random_value(self):
        return self.content_gen.get_date()


class DateTimeField(core.Field):
    def get_random_value(self):
        return self.content_gen.get_datetime()


class TimestampField(core.Field):
    def get_random_value(self):
        return 126144000 + self.content_gen.get_int(0, 315360000)


class TimeField(core.Field):
    def get_random_value(self):
        return '{0}:{1}:{2}'.format(
            self.content_gen.get_int(0, 23),
            self.content_gen.get_int(0, 59),
            self.content_gen.get_int(0, 59)
        )


class YearField(core.Field):
    def get_random_value(self):
        return self.content_gen.get_int(1990, 2020)


class TextField(core.Field):
    def __init__(self, name, length):
        super(TextField, self).__init__(name)
        self.length = length

    def get_random_value(self):
        return self.content_gen.get_text(self.length)


class EnumField(core.Field):
    def __init__(self, name, options=[]):
        super(EnumField, self).__init__(name)
        self.options = options

    def get_random_value(self):
        return self.content_gen.get_in_list(self.options)

    # @todo - Improve this method (separate it in a another class), it is awful!
    @classmethod
    def parse(cls, enum_str):
        # # enum('male','female')
        m = re.search(r"^enum\((.*)\)$", enum_str)

        if not m:
            raise ValueError("Unespected 'enum' string: " + enum_str)

        str_options = m.group(1)

        # Grammar:
        #   OPTION = QUOTE OPTION_VALUE QUOTE SEPARATOR | OPTION
        #   OPTION_VALUE = PARTIAL_OPTION | QUOTE QUOTE | COMMA
        #   SEPARATOR = COMMA | $
        #   QUOTE = '''
        #   PARTIAL_VALUE = '[^',]'
        #   COMMA = ','

        tokens = {
            "QUOTE": r"^(')",
            "COMMA": r"(\,)",
            "PARTIAL_OPTION": r"^([^'\,]+)",
        }

        tokenized_options = []
        i = 0

        while (i<len(str_options)):
            increment = None
            for token, pattern in tokens.iteritems():
                m = re.search(pattern, str_options[i:])
                if m is not None:
                    tokenized_options.append((token, m.group(1)))
                    increment = len(m.group(0))
                    break

            if increment is None:
                raise ValueError(
                    "Unexpected value on parse enum options: \"{0}\"".format(str_options[i:])
                )

            i = i + increment

        tokens_len = len(tokenized_options)
        options = []
        pos = 0
        while pos < tokens_len:
            token = tokenized_options[pos][0]

            if token != "QUOTE":
                raise ValueError("Unexpected token: " + token)

            pos += 1

            value = ""
            while pos < tokens_len:
                token = tokenized_options[pos][0]
                val = tokenized_options[pos][1]

                try:
                    next_token = tokenized_options[pos+1][0]
                except IndexError:
                    next_token = None

                if token == "PARTIAL_OPTION":
                    value += val
                elif token == "QUOTE" and ( next_token == "COMMA" or next_token is None ):
                    pos += 2
                    break
                elif token == "QUOTE" and next_token == "QUOTE":
                    value += val
                    pos += 1
                elif token == "COMMA":
                    value += val
                else:
                    raise ValueError("Unexpected token: " + token)

                pos += 1

            options.append(value)

        return options


class DataBase(core.DataBase):
    _table_cls = Table

    def __init__(
            self, content_gen, user, password, database,
            engine="mysql.connector", port="3306"):
        super(DataBase, self).__init__(content_gen)
        self.user = user
        self.password = password
        self.database = database
        self.port = port

        self._engine = engine

    def get_conn(self):
        if hasattr(self, "_conn"):
            return self._conn

        eng = import_module(self._engine)

        self._conn = eng.connect(
            user=self.user,
            password=self.password,
            database=self.database,
            port=self.port
        )

        return self._conn

    def get_tables_name_sql(self):
        """Returns a query with table's name in the first column"""
        return """SELECT table_name
            FROM information_schema.tables
            WHERE TABLE_SCHEMA = '{0}'""".format(self.database)
