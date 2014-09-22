from distutils.core import setup
from loremdb.common import version
import os


def get_cmdclass():
    """
    Return the command class parameter
    """

    try:
        # Include additional command to run tests in develop env
        from tests import DiscoverTest
        return {"test": DiscoverTest}
    except Exception, e:
        pass

    return {}


def get_packages():
    """
    Compile and return a list of packages available
    """

    packages = []
    for dirpath, dirnames, filenames in os.walk("loremdb"):
        if "__pycache__" in dirpath:
            continue

        packages.append(dirpath.replace("/", "."))

    return set(packages)

setup(
    name="LoremDB",
    version=version,
    author="Alisson R. Perez",
    author_email="alissonperez@gmail.com",
    # @todo - Update with our PyPI package page
    url="https://pypi.python.org/pypi",
    packages=get_packages(),
    scripts=["bin/loremdb"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 1 - Planning",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Database",
    ],
    cmdclass=get_cmdclass()
    # @todo - Include: "description" and "long_description"
)
