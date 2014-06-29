import unittest
from lordb.database.core import DataBaseCreator
from lordb.database import mysql
from lordb.util import ContentGen
from random import Random
from abc import ABCMeta, abstractmethod
from datetime import date, datetime


class DataBaseTestCase(unittest.TestCase):
    def setUp(self):
        self.database = self.get_database()
        self.database.show_errors = False
        self.clean_tables()

    def tearDown(self):
        self.database.commit()

    def get_database(self):
        return DataBaseCreator().create_mysql(
            ContentGen(),
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
        self.table = mysql.Table(self.database, "users", ContentGen())
        self.table.show_errors = False

    def test_fill(self):
        c = self.table.get_cursor()

        c.execute("SELECT name, age from users")
        self.assertEquals(0, len(c.fetchall()))

        self.table.fill(n=10)
        self.database.commit()

        c.execute("SELECT name, age from users")
        self.assertEquals(10, len(c.fetchall()))


class TestFieldCreatorFromMysql(unittest.TestCase):
    def setUp(self):
        self.creator = mysql.FieldCreatorFromMysql()
        self.default_row = {
            "table_catalog": "def",
            "table_schema": "lordb",
            "table_name": "users",
            "column_name": "name",
            "ordinal_position": "2",
            "column_default": None,
            "is_nullable": "NO",
            "data_type": "varchar",
            "character_maximum_length": "100",
            "character_octet_length": "100",
            "numeric_precision": None,
            "numeric_scale": None,
            "character_set_name": "latin1",
            "collation_name": "latin1_swedish_ci",
            "column_type": "varchar(100)",
            "column_key": "",
            "extra": "",
            "privileges": "select,insert,update,references",
            "column_comment": "",
        }

    def test_create_varchar_field(self):
        field = self.creator.create(self.default_row)
        self.assertEquals(mysql.VarcharField, field.__class__)
        self.assertEquals("name", field.name)
        self.assertEquals(100, field.length)

    def test_create_integer_field(self):
        self.default_row["column_name"] = "age"
        self.default_row["data_type"] = "tinyint"
        self.default_row["column_type"] = "tinyint(3) unsigned"

        field = self.creator.create(self.default_row)
        self.assertEquals(mysql.TinyintField, field.__class__)
        self.assertEquals("age", field.name)
        self.assertTrue(field.unsigned)

    def test_create_enum_field(self):
        self.default_row["column_name"] = "some_options"
        self.default_row["data_type"] = "enum"
        self.default_row["column_type"] = "enum('a','b','c')"

        field = self.creator.create(self.default_row)
        self.assertEquals(mysql.EnumField, field.__class__)
        self.assertEquals("some_options", field.name)
        self.assertEquals(["a", "b", "c"], field.options)


class BaseTestField(unittest.TestCase):
    __metaclass__ = ABCMeta

    def setUp(self):
        self.field = self._create_field()

        seed = "28391kaasd9129akdbb1o293"
        rnd = Random()
        rnd.seed(seed)
        self.field.content_gen = ContentGen(rnd)

    def _create_field(self):
        return self.get_test_class()("generic_field")

    @abstractmethod
    def get_test_class(self):
        return NotImplemented


class TestIntegerField(BaseTestField):
    def get_test_class(self):
        return mysql.IntegerField

    def test_get_content_gen(self):
        self.assertEquals(1188699766, self.field.get_random_value())


class TestTinyintField(BaseTestField):
    def get_test_class(self):
        return mysql.TinyintField

    def test_get_content_gen(self):
        self.assertEquals(71, self.field.get_random_value())


class TestSmallintField(BaseTestField):
    def get_test_class(self):
        return mysql.SmallintField

    def test_get_content_gen(self):
        self.assertEquals(18138, self.field.get_random_value())


class TestMediumintField(BaseTestField):
    def get_test_class(self):
        return mysql.MediumintField

    def test_get_content_gen(self):
        self.assertEquals(4643358, self.field.get_random_value())


class TestIntField(BaseTestField):
    def get_test_class(self):
        return mysql.IntField

    def test_get_content_gen(self):
        self.assertEquals(1188699766, self.field.get_random_value())


class TestBigintField(BaseTestField):
    def get_test_class(self):
        return mysql.BigintField

    def test_get_content_gen(self):
        self.assertEquals(3741057809691319936, self.field.get_random_value())


class TestDecimalField(BaseTestField):
    def _create_field(self):
        return self.get_test_class()("value", 5, 2)

    def get_test_class(self):
        return mysql.DecimalField

    def test_creation_with_precision_less_then_scale(self):
        # Init method should raise an ValueError exception with
        # precision (3) < scale (4)
        self.assertRaises(ValueError, self.get_test_class(), "value", 3, 4)

    def test_get_content_gen(self):
        self.assertEquals(553.18, self.field.get_random_value())
        self.assertEquals(138.8, self.field.get_random_value())


class TestFloatField(TestDecimalField):
    def get_test_class(self):
        return mysql.FloatField


class TestRealField(TestDecimalField):
    def get_test_class(self):
        return mysql.RealField


class TestDoubleField(TestDecimalField):
    def get_test_class(self):
        return mysql.DoubleField


class TestNumericField(TestDecimalField):
    def get_test_class(self):
        return mysql.NumericField


class TestDateField(BaseTestField):
    def get_test_class(self):
        return mysql.DateField

    def test_get_content_gen(self):
        self.assertEquals(date(2016, 11, 16), self.field.get_random_value())


class TestDatetimeField(BaseTestField):
    def get_test_class(self):
        return mysql.DatetimeField

    def test_get_content_gen(self):
        dt = datetime(2016, 11, 16, 0, 18, 55, 319481)
        result = self.field.get_random_value()

        self.assertEquals(dt.year, result.year)
        self.assertEquals(dt.month, result.month)
        self.assertEquals(dt.day, result.day)
        self.assertIn(result.hour, range(0, 24))
        self.assertIn(result.minute, range(0, 59))
        self.assertIn(result.second, range(0, 59))


class TestTimestampField(BaseTestField):
    def get_test_class(self):
        return mysql.TimestampField

    def test_get_content_gen(self):
        self.assertEquals(371104841, self.field.get_random_value())


class TestTimeField(BaseTestField):
    def get_test_class(self):
        return mysql.TimeField

    def test_get_content_gen(self):
        self.assertEquals("18:11:34", self.field.get_random_value())


class TestYearField(BaseTestField):
    def get_test_class(self):
        return mysql.YearField

    def test_get_content_gen(self):
        self.assertEquals(2014, self.field.get_random_value())


class TestCharField(BaseTestField):
    def _create_field(self):
        return self.get_test_class()("name", 25)

    def get_test_class(self):
        return mysql.CharField

    def test_get_content_gen(self):
        self.assertEquals("Integ", self.field.get_random_value())
        self.assertEquals("Ut ", self.field.get_random_value())
        self.assertEquals("In ullamcor", self.field.get_random_value())


class TestVarcharFeld(TestCharField):
    def get_test_class(self):
        return mysql.VarcharField


class TestBinaryFeld(TestCharField):
    def get_test_class(self):
        return mysql.BinaryField


class TestVarbinaryFeld(TestCharField):
    def get_test_class(self):
        return mysql.VarbinaryField


class TestTextField(BaseTestField):
    def _create_field(self):
        return self.get_test_class()("name", 55)

    def get_test_class(self):
        return mysql.TextField

    def test_get_content_gen(self):
        self.assertEquals(
            "Integer ac quam vel erat tincidunt rhoncus ut ac elit",
            self.field.get_random_value()
        )


class TestEnumField(BaseTestField):
    database_spec =\
        "enum('option1','secondOption','strange''option','test'',strage2')"

    def _create_field(self):
        return self.get_test_class()(
            "enum_field",
            self.get_test_class().parse(self.database_spec)
        )

    def get_test_class(self):
        return mysql.EnumField

    def test_parse(self):
        self.assertEquals(
            ["option1", "secondOption", "strange'option", "test',strage2"],
            mysql.EnumField.parse(self.database_spec)
        )

    def test_get_content_gen(self):
        self.assertEquals("test',strage2", self.field.get_random_value())


class TestSetField(BaseTestField):
    database_spec =\
        "set('a','b''','c','dd','e')"

    def _create_field(self):
        return self.get_test_class()(
            "enum_field",
            self.get_test_class().parse(self.database_spec)
        )

    def get_test_class(self):
        return mysql.SetField

    def test_parse(self):
        self.assertEquals(
            ["a", "b'", "c", 'dd', 'e'],
            self.get_test_class().parse(self.database_spec)
        )

    def test_get_content_gen(self):
        self.assertEquals("a,b',c", self.field.get_random_value())
        self.assertEquals("a,dd", self.field.get_random_value())
        self.assertEquals("e", self.field.get_random_value())