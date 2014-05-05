import unittest
from lordb.filler import Filler


class FillerTest(unittest.TestCase):
    def setUp(self):
        self.f = Filler()

    def test_foo(self):
        self.assertEquals('foo', 'foo')
