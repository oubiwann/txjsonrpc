from twisted.trial.unittest import TestCase

from txjsonrpc.jsonrpclib import (
    Fault, VERSION_PRE1, VERSION_1, VERSION_2, dumps, loads)


class DumpTestCase(TestCase):

    def test_noVersion(self):
        object = {"some": "data"}
        result = dumps(object)
        self.assertEquals(result, '{"some": "data"}')

    def test_noVersionError(self):
        object = Fault("code", "message")
        result = dumps(object)
        self.assertEquals(
            result, 
            '{"fault": "Fault", "faultCode": "code", "faultString": "message"}')

    def test_versionPre1(self):
        object = {"some": "data"}
        result = dumps(object, version=VERSION_PRE1)
        self.assertEquals(result, '{"some": "data"}')

    def test_errorVersionPre1(self):
        object = Fault("code", "message")
        result = dumps(object, version=VERSION_PRE1)
        self.assertEquals(
            result, 
            '{"fault": "Fault", "faultCode": "code", "faultString": "message"}')

    def test_version1(self):
        object = {"some": "data"}
        result = dumps(object, version=VERSION_1)
        self.assertEquals(
            result,
            '{"id": null, "result": {"some": "data"}, "error": null}')

    def test_errorVersion1(self):
        object = Fault("code", "message")
        result = dumps(object, version=VERSION_1)
        self.assertEquals(
            result, 
            ('{"id": null, "result": null, "error": {"fault": "Fault", '
             '"faultCode": "code", "faultString": "message"}}'))

    def test_version2(self):
        object = {"some": "data"}
        result = dumps(object, version=VERSION_2)
        self.assertEquals(
            result,
            '{"id": null, "result": {"some": "data"}, "error": null}')

    def test_errorVersion2(self):
        object = Fault("code", "message")
        result = dumps(object, version=VERSION_2)
        self.assertEquals(
            result, 
            ('{"id": null, "result": null, "error": {"fault": "Fault", '
             '"faultCode": "code", "faultString": "message"}}'))


class LoadsTestCase(TestCase):

    def test_loads(self):
        jsonInput = ["1", '"a"', '{"apple": 2}', '[1, 2, "a", "b"]']
        expectedResults = [1, "a", {"apple": 2}, [1, 2, "a", "b"]]
        for input, expected in zip(jsonInput, expectedResults):
            unmarshalled = loads(input)
            self.assertEquals(unmarshalled, expected)
