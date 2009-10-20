# Copyright (c) 2001-2004 Twisted Matrix Laboratories.
# See LICENSE for details.
"""
Test XML-RPC support.
"""
from twisted.internet import reactor, defer
from twisted.trial import unittest
from twisted.web2 import server
from twisted.web2.channel import http

try:
    from txjsonrpc.web.jsonrpc import Proxy
except ImportError:
    Proxy = None

from txjsonrpc import jsonrpclib
from txjsonrpc.web2.jsonrpc import JSONRPC, addIntrospection


class TestRuntimeError(RuntimeError):
    pass


class TestValueError(ValueError):
    pass


class Test(JSONRPC):

    FAILURE = 666
    NOT_FOUND = 23
    SESSION_EXPIRED = 42

    addSlash = True
    
    def jsonrpc_add(self, request, a, b):
        """
        This function add two numbers.
        """
        # The doc string is part of the test.
        return a + b

    jsonrpc_add.signature = [['int', 'int', 'int'],
                            ['double', 'double', 'double']]

    def jsonrpc_pair(self, request, string, num):
        """
        This function puts the two arguments in an array.
        """
        # The doc string is part of the test.
        return [string, num]

    jsonrpc_pair.signature = [['array', 'string', 'int']]

    def jsonrpc_defer(self, request, x):
        """
        Help for defer.
        """
        # The doc string is part of the test.
        return defer.succeed(x)

    def jsonrpc_deferFail(self, request):
        return defer.fail(TestValueError())

    def jsonrpc_fail(self, request):
        # Don't add a doc string, it's part of the test.
        raise TestRuntimeError

    def jsonrpc_fault(self, request):
        return jsonrpclib.Fault(12, "hello")

    def jsonrpc_deferFault(self, request):
        return defer.fail(jsonrpclib.Fault(17, "hi"))

    def jsonrpc_complex(self, request):
        return {"a": ["b", "c", 12, []], "D": "foo"}

    def jsonrpc_dict(self, request, map, key):
        return map[key]

    def getFunction(self, functionPath):
        try:
            return JSONRPC.getFunction(self, functionPath)
        except jsonrpclib.NoSuchFunction:
            if functionPath.startswith("SESSION"):
                raise jsonrpclib.Fault(self.SESSION_EXPIRED, "Session non-existant/expired.")
            else:
                raise

    jsonrpc_dict.help = 'Help for dict.'


class JSONRPCTestCase(unittest.TestCase):
    
    if not Proxy:
        skip = "Until web2 has an XML-RPC client, this test requires twisted.web."

    def setUp(self):
        self.p = reactor.listenTCP(0, http.HTTPFactory(server.Site(Test())),
                                   interface="127.0.0.1")
        self.port = self.p.getHost().port

    def tearDown(self):
        return self.p.stopListening()

    def proxy(self):
        return Proxy("http://127.0.0.1:%d/" % self.port)

    def testResults(self):
        inputOutput = [
            ("add", (2, 3), 5),
            ("defer", ("a",), "a"),
            ("dict", ({"a": 1}, "a"), 1),
            ("pair", ("a", 1), ["a", 1]),
            ("complex", (), {"a": ["b", "c", 12, []], "D": "foo"})]

        dl = []
        for meth, args, outp in inputOutput:
            d = self.proxy().callRemote(meth, *args)
            d.addCallback(self.assertEquals, outp)
            dl.append(d)
        return defer.DeferredList(dl, fireOnOneErrback=True)

    def testErrors(self):
        dl = []
        for code, methodName in [(666, "fail"), (666, "deferFail"),
                                 (12, "fault"), (23, "noSuchMethod"),
                                 (17, "deferFault"), (42, "SESSION_TEST")]:
            d = self.proxy().callRemote(methodName)
            d = self.assertFailure(d, jsonrpclib.Fault)
            d.addCallback(lambda exc, code=code: self.assertEquals(exc.faultCode, code))
            dl.append(d)
        d = defer.DeferredList(dl, fireOnOneErrback=True)
        d.addCallback(lambda ign: self.flushLoggedErrors())
        return d


class JSONRPCTestCase2(JSONRPCTestCase):
    """Test with proxy that doesn't add a slash."""

    def proxy(self):
        return Proxy("http://127.0.0.1:%d" % self.port)


class JSONRPCTestIntrospection(JSONRPCTestCase):

    def setUp(self):
        jsonrpcService = Test()
        addIntrospection(jsonrpcService)
        self.p = reactor.listenTCP(
            0, http.HTTPFactory(server.Site(jsonrpcService)),
            interface="127.0.0.1")
        self.port = self.p.getHost().port

    def testListMethods(self):

        def cbMethods(meths):
            meths.sort()
            self.failUnlessEqual(
                meths,
                ['add', 'complex', 'defer', 'deferFail',
                 'deferFault', 'dict', 'fail', 'fault',
                 'pair', 'system.listMethods',
                 'system.methodHelp',
                 'system.methodSignature'])

        d = self.proxy().callRemote("system.listMethods")
        d.addCallback(cbMethods)
        return d

    def testMethodHelp(self):
        inputOutputs = [
            ("defer", "Help for defer."),
            ("fail", ""),
            ("dict", "Help for dict.")]

        dl = []
        for meth, expected in inputOutputs:
            d = self.proxy().callRemote("system.methodHelp", meth)
            d.addCallback(self.assertEquals, expected)
            dl.append(d)
        return defer.DeferredList(dl, fireOnOneErrback=True)

    def testMethodSignature(self):
        inputOutputs = [
            ("defer", ""),
            ("add", [['int', 'int', 'int'],
                     ['double', 'double', 'double']]),
            ("pair", [['array', 'string', 'int']])]

        dl = []
        for meth, expected in inputOutputs:
            d = self.proxy().callRemote("system.methodSignature", meth)
            d.addCallback(self.assertEquals, expected)
            dl.append(d)
        return defer.DeferredList(dl, fireOnOneErrback=True)
