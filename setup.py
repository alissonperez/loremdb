from distutils.core import setup
from tests import DiscoverTest


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
