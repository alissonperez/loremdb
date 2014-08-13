import unittest
import loremdb.cmd
from os import linesep


class testOutputProgress(unittest.TestCase):

    output = []

    def setUp(self):
        self.output = []
        self.obj = loremdb.cmd.OutputProgress(500, self.callback)

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
