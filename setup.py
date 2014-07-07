from distutils.core import setup
import os

# Compile a list of packages available
packages = []
for dirpath, dirnames, filenames in os.walk("loremdb"):
    if "__pycache__" in dirpath:
        continue

    packages.append(dirpath.replace("/", "."))

packages = set(packages)

cmdclass = {}
try:
    # Include additional command to run tests in develop env
    from tests import DiscoverTest
    cmdclass = {"test": DiscoverTest}
except Exception, e:
    pass

setup(
    name="LoremDB",
    version="0.0.1",
    author="Alisson R. Perez",
    author_email="alissonperez@gmail.com",
    # @todo - Update with our PyPI package page
    url="https://pypi.python.org/pypi",
    packages=packages,
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
    cmdclass=cmdclass
    # @todo - Include: "description" and "long_description"
)
