import core
from importlib import import_module
from loremdb.util import OptionsParser
import re


class Table(core.Table):
    def __init__(self, *args, **kargs):
        super(Table, self).__init__(*args, **kargs)
        self.field_creator = FieldCreatorFromMysql()

    def _create_insert_sql(self):
        fields_num = len(self._get_fields())
        return "INSERT INTO {0} ({1}) VALUES ({2})".format(
            self.name,
            ", ".join([i.name for i in self._get_fields()]),
            ", ".join(["%s" for i in range(fields_num)])
        )

    def _get_fields(self):
        if hasattr(self, "fields"):
            return self.__fields

        c = self.get_cursor()

        self.__fields = []
        cols = [
            "table_catalog", "numeric_precision",
            "table_schema", "numeric_scale",
            "table_name", "character_set_name",
            "column_name", "collation_name",
            "ordinal_position", "column_type",
            "column_default", "column_key",
            "is_nullable", "extra",
            "data_type", "privileges",
            "character_maximum_length", "column_comment",
            "character_octet_length"
        ]

        sql = """SELECT {0}
            FROM information_schema.columns
            WHERE table_schema = %s and table_name = %s
            ORDER BY ordinal_position""".format(",".join(cols))

        c.execute(sql, (self._database.database, self.name))

        for row in c:
            self.__fields.append(
                self.field_creator.create(dict(zip(cols, row)))
            )

        c.close()

        return self.__fields


class FieldCreatorFromMysql(object):
    def create(self, mysql_specs):
        field_class = self._get_field_class(mysql_specs["data_type"])
        specs = self._sanitize_specs(mysql_specs)
        return field_class(**specs)

    def _sanitize_specs(self, specs):
        precision = None
        if specs["numeric_precision"] is not None:
            precision = int(specs["numeric_precision"])

        scale = None
        if specs["numeric_scale"] is not None:
            scale = int(specs["numeric_scale"])

        options = []
        if specs["data_type"].lower() in ["enum", "set"]:
            field_class = self._get_field_class(specs["data_type"])
            options = field_class.parse(specs["column_type"])

        length = None
        if specs["character_maximum_length"] is not None:
            length = int(specs["character_maximum_length"])

        return {
            "name": specs["column_name"],
            "length": length,
            "unsigned": "unsigned" in specs["column_type"],
            "precision": precision,
            "scale": scale,
            "options": options,
        }

    def _get_field_class(self, data_type):
        class_name = "{0}Field".format(data_type.capitalize())
        return eval(class_name)


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


class TinyintField(IntegerField):
    num_signed_max = 127


class SmallintField(IntegerField):
    num_signed_max = 32767


class MediumintField(IntegerField):
    num_signed_max = 8388607


class IntField(IntegerField):
    pass


class BigintField(IntegerField):
    num_signed_max = 9223372036854775807


class DecimalField(core.Field):
    def __init__(self, name, precision, scale=0, *args, **kargs):
        super(DecimalField, self).__init__(name, *args, **kargs)

        if scale > precision:
            raise ValueError("Value of 'precision' must be >= 'scale' value")

        self.precision = precision
        self.scale = scale

    def get_random_value(self):
        int_range = 10 ** (self.precision - self.scale) - 1
        int_rand = self.content_gen.get_int(-1 * int_range, int_range)
        decimal_range = 10 ** self.scale - 1
        decimal_rand = self.content_gen.get_int(0, decimal_range)
        return float("{0}.{1}".format(int_rand, decimal_rand))


class FloatField(DecimalField):
    pass


class RealField(DecimalField):
    pass


class DoubleField(DecimalField):
    pass


class NumericField(DecimalField):
    """
    In MySQL, NUMERIC is implemented as DECIMAL...
    """
    pass


class DateField(core.Field):
    def get_random_value(self):
        return self.content_gen.get_date()


class DatetimeField(core.Field):
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


class CharField(core.Field):
    def __init__(self, name, length, *args, **kargs):
        super(CharField, self).__init__(name, *args, **kargs)
        self.length = length

    def get_random_value(self):
        return self.content_gen.get_text(self.length)


class VarcharField(CharField):
    pass


class BinaryField(CharField):
    pass


class VarbinaryField(CharField):
    pass


class TextField(CharField):
    pass


class EnumField(core.Field):
    def __init__(self, name, options=[], *args, **kargs):
        super(EnumField, self).__init__(name, *args, **kargs)
        self.options = options

    def get_random_value(self):
        return self.content_gen.get_in_list(self.options)

    @classmethod
    def parse(cls, enum_str):
        m = re.search(cls.get_spec_regex(), enum_str)

        if not m:
            raise ValueError("Unespected field specification: " + enum_str)

        str_options = m.group(1)
        return OptionsParser().parse(str_options).options

    @classmethod
    def get_spec_regex(cls):
        return r"^enum\((.*)\)$"


class SetField(EnumField):
    def get_random_value(self):
        options = self.content_gen.get_list_subset(self.options)
        return ",".join(sorted(options))

    @classmethod
    def get_spec_regex(self):
        return r"^set\((.*)\)$"


class DataBase(core.DataBase):
    _table_cls = Table

    def __init__(
            self, content_gen, user, database, password=None,
            host="localhost", engine="mysql.connector", port="3306"):
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
        """
        Returns a query with table's name in the first column
        """

        return """SELECT table_name
            FROM information_schema.tables
            WHERE TABLE_SCHEMA = '{0}'""".format(self.database)
