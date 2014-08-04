import unittest
import loremdb.util
from datetime import date, datetime
from os import linesep


class test_content_gen(unittest.TestCase):

    def setUp(self):
        self.i = loremdb.util.ContentGen()

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

    def test_get_in_list(self):
        list = ["foo", "bar", "baz", "foobar"]
        for i in xrange(100):
            self.assertIn(self.i.get_in_list(list), list)

    def test_get_list_subset(self):
        options = ["foo", "bar", "baz", "foobar"]
        for i in self.i.get_list_subset(options):
            self.assertIn(i, options)


class testOptionsParser(unittest.TestCase):

    def setUp(self):
        self.parser = loremdb.util.OptionsParser()

    def test_parser(self):
        self.assertEquals(
            ["a", "b"], self.parser.parse("'a','b'").options
        )

        self.assertEquals(
            ["a", "b", "c"], self.parser.parse("'a','b','c'").options
        )

        self.assertEquals(
            ["a"], self.parser.parse("'a'").options
        )

    def test_parser_with_an_option_with_quotes(self):
        self.assertEquals(
            ["a'b"], self.parser.parse("'a''b'").options
        )

        self.assertEquals(
            ["a'b", "C"], self.parser.parse("'a''b','C'").options
        )

    def test_parser_with_empty_str(self):
        self.assertEquals([], self.parser.parse("").options)

    def test_parser_with_quote(self):
        options_str = "'option1','secOpt','strange''option','test'',strage2'"
        self.assertEquals(
            ["option1", "secOpt", "strange'option", "test',strage2"],
            self.parser.parse(options_str).options
        )

        self.assertEquals(
            ["a", "b", "c'"],
            self.parser.parse("'a','b','c'''").options
        )

        self.assertEquals(
            ["a", "b',", "c'"],
            self.parser.parse("'a','b'',','c'''").options
        )

    def test_parser_with_wrong_quote(self):
        self.assertRaises(ValueError, self.parser.parse, "'a','b")


class testOutputProgress(unittest.TestCase):

    output = []

    def setUp(self):
        self.output = []
        self.obj = loremdb.util.OutputProgress(500, self.callback)

    def callback(self, to_print):
        self.output.append(to_print)

    def test_simple_dot_print(self):
        self.obj()
        self.assertEquals(["."], self.output)

    def test_line_break(self):
        for i in range(49):
            self.obj()

        test_list = ["." for __ in range(49)]
        self.assertEquals(test_list, self.output)

        # Adding two dots
        self.obj()
        self.obj()
        test_list += [".", " 10%", linesep, "."]

        self.assertEquals(test_list, self.output)

        # Completing another line
        for i in range(49):
            self.obj()

        test_list += ["." for __ in range(49)] + [" 20%", linesep]
        self.assertEquals(test_list, self.output)

    def test_reset(self):
        for i in range(49):
            self.obj()

        test_list = ["." for __ in range(49)]
        self.assertEquals(test_list, self.output)

        # Reseting
        self.output = []
        self.obj.reset()

        self.obj()
        self.assertEquals(["."], self.output)

    def test_call_overflow(self):
        self.obj.progress_size = 30

        for i in range(30):
            self.obj()

        self.assertRaises(StandardError, self.obj)
