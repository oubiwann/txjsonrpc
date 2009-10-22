# Copyright (c) 2001-2004 Twisted Matrix Laboratories.
# See LICENSE for details.
"""
A generic resource for publishing objects via JSON-RPC.

API Stability: semi-stable

Maintainer: U{Duncan McGreggor <mailto:oubiwann@adytum.us>}
"""
from twisted.protocols import basic
from twisted.internet import defer, protocol, reactor
from twisted.python import log, reflect

from txjsonrpc import jsonrpclib
from txjsonrpc.jsonrpc import (
    BaseProxy, BaseQueryFactory, BaseSubhandler, Introspection)


class JSONRPC(basic.NetstringReceiver, BaseSubhandler):
    """
    A protocol that implements JSON-RPC.
    
    Methods published can return JSON-RPC serializable results, Faults,
    Binary, Boolean, DateTime, Deferreds, or Handler instances.

    By default methods beginning with 'jsonrpc_' are published.
    """
    # Error codes for Twisted, if they conflict with yours then
    # modify them at runtime.
    NOT_FOUND = 8001
    FAILURE = 8002

    separator = '.'
    closed = 0

    def __call__(self):
        return self

    def connectionMade(self):
        self.MAX_LENGTH = self.factory.maxLength

    def stringReceived(self, line):
        parser, unmarshaller = jsonrpclib.getparser()
        deferred = defer.maybeDeferred(parser.feed, line)
        deferred.addCallback(lambda x: self._cbDispatch(
            parser, unmarshaller))
        deferred.addErrback(self._ebRender)
        deferred.addCallback(self._cbRender)
        return deferred

    def _cbDispatch(self, parser, unmarshaller):
        parser.close()
        args, functionPath = unmarshaller.close(), unmarshaller.getmethodname()
        function = self._getFunction(functionPath)
        return defer.maybeDeferred(function, *args)

    def _cbRender(self, result):
        if not isinstance(result, jsonrpclib.Fault):
            result = (result,)
        #s = None
        #e = None
        try:
            s = jsonrpclib.dumps(result)
        except:
            f = jsonrpclib.Fault(self.FAILURE, "can't serialize output")
            #e = jsonrpclib.dumps(f)
            s = jsonrpclib.dumps(f)
        #result = {'result': result, 'error': e}
        #return self.sendString(jsonrpclib.dumps(result))
        return self.sendString(s)

    def _ebRender(self, failure):
        if isinstance(failure.value, jsonrpclib.Fault):
            return failure.value
        log.err(failure)
        return jsonrpclib.Fault(self.FAILURE, "error")


class QueryProtocol(basic.NetstringReceiver):

    def connectionMade(self):
        self.data = ''
        msg = self.factory.payload
        packet = '%d:%s,' % (len(msg), msg)
        self.transport.write(packet)

    def stringReceived(self, string):
        self.factory.data = string
        self.transport.loseConnection()


class QueryFactory(BaseQueryFactory):

    protocol = QueryProtocol
    data = ''

    def clientConnectionLost(self, _, reason):
        self.parseResponse(self.data)


class Proxy(BaseProxy):
    """
    A Proxy for making remote JSON-RPC calls.

    Pass the URL of the remote JSON-RPC server to the constructor.

    Use proxy.callRemote('foobar', *args) to call remote method
    'foobar' with *args.
    """

    def __init__(self, host, port, version=jsonrpclib.VERSION_PRE1,
                 factoryClass=QueryFactory):
        """
        @type host: C{str}
        @param host: The host to which method calls are made.

        @type port: C{integer}
        @param port: The host's port to which method calls are made.

        @type version: C{int}
        @param version: The version indicates which JSON-RPC spec to support.
        The available choices are jsonrpclib.VERSION*. The default is to use
        the version of the spec that txJSON-RPC was originally released with,
        pre-Version 1.0.

        @type factoryClass: C{object}
        @param factoryClass: The factoryClass should be a subclass of
        QueryFactory (class, not instance) that will be used instead of
        QueryFactory.
        """
        BaseProxy.__init__(self, version, factoryClass)
        self.host = host
        self.port = port


    def callRemote(self, method, *args, **kwargs):
        version = self._getVersion(kwargs)
        factoryClass = self._getFactoryClass(kwargs)
        factory = factoryClass(method, version, *args)
        reactor.connectTCP(self.host, self.port, factory)
        return factory.deferred


class RPCFactory(protocol.ServerFactory):

    protocol = None

    def __init__(self, rpcClass, maxLength=1024):
        self.maxLength = maxLength
        self.protocol = rpcClass
        self.subHandlers = {}

    def buildProtocol(self, addr):
        p = protocol.ServerFactory.buildProtocol(self, addr)
        for key, val in self.subHandlers.items():
            klass, args, kws = val
            if args and args[0] == 'protocol':
                p.putSubHandler(key, klass(p))
            else:
                p.putSubHandler(key, klass(*args, **kws))
        return p

    def putSubHandler(self, name, klass, args=(), kws={}):
        self.subHandlers[name] = (klass, args, kws)

    def addIntrospection(self):
        self.putSubHandler('system', Introspection, ('protocol',))


__all__ = ["JSONRPC", "Proxy", "RPCFactory"]
