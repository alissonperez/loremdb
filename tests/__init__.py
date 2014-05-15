from distutils.core import Command


class DiscoverTest(Command):
    description = "Discover and run all tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import unittest
        import os

        project_dir = os.path.dirname(os.path.realpath(__file__))

        test_loader = unittest.defaultTestLoader
        test_suite = test_loader.discover(project_dir)

        test_runner = unittest.TextTestRunner()
        return 1 if test_runner.run(test_suite).wasSuccessful() else 0
