import unittest
from lordb.util import ContentGen
from datetime import date, datetime


class test_content_gen(unittest.TestCase):

    def setUp(self):
        self.i = ContentGen()

    def test_get_int(self):
        for i in xrange(100):
            self.assertIn(self.i.get_int(1, 5), range(1, 6))

    def test_get_float(self):
        for i in xrange(100):
            rand = self.i.get_float(1, 2)
            self.assertTrue(rand >= 1.0)
            self.assertTrue(rand <= 2.0)

    def test_get_text(self):
        for i in xrange(100):
            text = self.i.get_text(50)
            self.assertTrue(len(text) > 0)
            self.assertTrue(len(text) <= 50)

    def test_get_date(self):
        for i in xrange(100):
            rand_date = self.i.get_date()
            self.assertTrue(isinstance(rand_date, date))

    def test_get_date_with_range(self):
        start = date(1990, 8, 28)
        end = date.today()

        for i in xrange(100):
            rand_date = self.i.get_date(start, end)
            self.assertTrue(start <= rand_date)
            self.assertTrue(rand_date <= end)

    def test_get_date_with_range_and_start_and_end_equals(self):
        start = date(1990, 8, 28)
        end = date(1990, 8, 28)

        self.assertEquals(start, self.i.get_date(start, end))

    def test_get_datetime(self):
        for i in xrange(100):
            rand_date = self.i.get_datetime()
            self.assertTrue(isinstance(rand_date, datetime))

    def test_get_datetime_with_range(self):
        start = datetime(1990, 8, 28, 12, 40, 20)
        end = datetime(1990, 8, 28, 12, 50, 00)

        for i in xrange(100):
            rand_datetime = self.i.get_datetime(start, end)
            self.assertTrue(start <= rand_datetime)
            self.assertTrue(rand_datetime <= end)

    def test_get_in_enum(self):
        list = ["foo", "bar", "baz", "foobar"]
        for i in xrange(100):
            self.assertIn(self.i.get_in_list(list), list)
