from distutils.core import setup
from distutils.core import Command


def discover_and_run_tests():
    import unittest
    import os

    project_dir = os.path.dirname(os.path.realpath(__file__))

    test_loader = unittest.defaultTestLoader
    test_suite = test_loader.discover("{0}/tests/".format(project_dir))

    unittest.TextTestRunner().run(test_suite)


class DiscoverTest(Command):
    description = "Discover and run all tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        discover_and_run_tests()


setup(
    name="LorDB",
    version="0.0.1",
    author="Alisson R. Perez",
    author_email="alissonperez@gmail.com",
    # @todo - Update with our PyPI package page
    url="https://pypi.python.org/pypi",
    packages=["lordb"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 1 - Planning",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Database",
    ],
    cmdclass={"test": DiscoverTest}
    # @todo - Include: "description" and "long_description"
)
