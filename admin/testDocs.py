#!/usr/bin/python
import os
import unittest
from doctest import DocFileSuite, ELLIPSIS
from glob import glob

from txjsonrpc.testing.suite import buildDoctestSuite


# To add a new module to the test runner, simply include is in the list below:
modules = [
]

files = glob("docs/specs/*.txt")
files.append("docs/USAGE.txt")
suites = []
for file in files:
    file = os.path.join("..", file)
    suites.append(DocFileSuite(file, optionflags=ELLIPSIS))
if modules:
    suites.append(buildDoctestSuite(modules))


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(suites))
