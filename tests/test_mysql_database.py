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

    def test_fill(self):
        c = self.table.get_cursor()

        c.execute("SELECT name, age from users")
        self.assertEquals(0, len(c.fetchall()))

        self.table.fill(n=10)
        self.database.commit()

        c.execute("SELECT name, age from users")
        self.assertEquals(10, len(c.fetchall()))


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


class TestTinyIntField(BaseTestField):

    def get_test_class(self):
        return mysql.TinyIntField

    def test_get_content_gen(self):
        self.assertEquals(71, self.field.get_random_value())


class TestMediumIntField(BaseTestField):

    def get_test_class(self):
        return mysql.SmallIntField

    def test_get_content_gen(self):
        self.assertEquals(18138, self.field.get_random_value())


class TestIntField(BaseTestField):

    def get_test_class(self):
        return mysql.IntField

    def test_get_content_gen(self):
        self.assertEquals(1188699766, self.field.get_random_value())


class TestBigIntField(BaseTestField):

    def get_test_class(self):
        return mysql.BigIntField

    def test_get_content_gen(self):
        self.assertEquals(3741057809691319936, self.field.get_random_value())


class TestDecimalField(BaseTestField):

    def _create_field(self):
        return self.get_test_class()("value", 5, 2)

    def get_test_class(self):
        return mysql.Decimalfield

    def test_creation_with_precision_less_then_scale(self):
        # Init method should raise an ValueError exception with
        # precision (3) < scale (4)
        self.assertRaises(ValueError, self.get_test_class(), "value", 3, 4)

    def test_get_content_gen(self):
        self.assertEquals(553.18, self.field.get_random_value())
        self.assertEquals(138.8, self.field.get_random_value())


class TestDateField(BaseTestField):

    def get_test_class(self):
        return mysql.DateField

    def test_get_content_gen(self):
        self.assertEquals(date(2010, 10, 14), self.field.get_random_value())


class TestDateTimeField(BaseTestField):

    def get_test_class(self):
        return mysql.DateTimeField

    def test_get_content_gen(self):
        dt = datetime(2011, 3, 26, 0, 18, 55, 319481)
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
            mysql.EnumField.parse(self.database_spec)
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
