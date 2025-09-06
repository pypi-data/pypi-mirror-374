import unittest
import xmlrunner


def runTests():
    tests = unittest.defaultTestLoader.discover("tests", pattern='test_sed_extract.py')
    xmlrunner.XMLTestRunner(output='test-reports').run(tests)


if __name__ == "__main__":
    runTests()
