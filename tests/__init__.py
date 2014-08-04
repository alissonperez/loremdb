from distutils.cmd import Command


class DiscoverTest(Command):
    command_name = "Discover Test"
    description = "Discover and run all tests"
    user_options = [
        ("filter=", "f", "Test filter (default unittest filter syntax)")
    ]

    def initialize_options(self):
        self.filter = None

    def finalize_options(self):
        pass

    def run(self):
        import unittest
        import os

        test_loader = unittest.TestLoader()

        if self.filter:
            test_suite = test_loader.loadTestsFromName("tests." + self.filter)
        else:
            project_dir = os.path.dirname(os.path.realpath(__file__))
            test_suite = test_loader.discover(project_dir)

        test_runner = unittest.TextTestRunner()
        if not test_runner.run(test_suite).wasSuccessful():
            raise SystemExit(1)
        else:
            return 0
