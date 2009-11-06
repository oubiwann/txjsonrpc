"""
Utility functions for testing.
"""
import os
import unittest
import doctest


def importModule(name):
    mod = __import__(name)
    components = name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def fileIsTest(path, skipFiles=[]):
    if not os.path.isfile(path):
        return False
    filename = os.path.basename(path)
    if filename in skipFiles:
        return False
    if filename.startswith('test') and filename.endswith('.py'):
        return True


def find(start, func, skip=[]):
    for item in [os.path.join(start, x) for x in os.listdir(start)]:
        if func(item, skip):
            yield item
        if os.path.isdir(item):
            for subItem in find(item, func, skip):
                yield subItem


def findTests(startDir, skipFiles=[]):
    return find(startDir, fileIsTest, skipFiles)


def buildDoctestSuite(modules):
    suite = unittest.TestSuite()
    for modname in modules:
        mod = importModule(modname)
        suite.addTest(doctest.DocTestSuite(mod))
    return suite


def buildUnittestSuites(paths=[], skip=[]):
    """
    paths: a list of directories to search
    skip: a list of file names to skip
    """
    suites = []
    loader = unittest.TestLoader()
    for startDir in paths:
        for testFile in findTests(startDir, skip):
            modBase = os.path.splitext(testFile)[0]
            name = modBase.replace(os.path.sep, '.')
            # import the testFile as a module
            mod = importModule(name)
            # iterate through module objects, checking for TestCases
            for objName in dir(mod):
                if not objName.endswith('TestCase'):
                    continue
                obj = getattr(mod, objName)
                if not issubclass(obj, unittest.TestCase):
                    continue
                # create a suite from any test cases
                suite = loader.loadTestsFromTestCase(obj)
                # append to suites list
                suites.append(suite)
    return suites
