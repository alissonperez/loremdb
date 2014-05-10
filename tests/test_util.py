import unittest
from lordb.util import ContentGen


class test_content_gen(unittest.TestCase):

    def setUp(self):
        self.i = ContentGen()

    def test_get_int(self):
        for i in xrange(100):
            self.assertIn(self.i.get_int(1, 5), range(1, 6))

    def test_get_text(self):
        for i in xrange(100):
            text = self.i.get_text(50)
            self.assertTrue(len(text) > 0)
            self.assertTrue(len(text) <= 50)

    def test_get_in_enum(self):
        list = ["foo", "bar", "baz", "foobar"]
        for i in xrange(100):
            self.assertIn(self.i.get_in_list(list), list)
