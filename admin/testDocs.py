#!/usr/bin/python
from doctest import DocFileSuite, ELLIPSIS

from txjsonrpc.testing.suite import buildDoctestSuite


# To add a new module to the test runner, simply include is in the list below:
modules = [
]

suites = [DocFileSuite("../docs/USAGE.txt", optionflags=ELLIPSIS)]
if modules:
    suites.append(buildDoctestSuite(modules))


if __name__ == "__main__":
    import unittest
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(unittest.TestSuite(suites))


