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


class JSONRPC(basic.NetstringReceiver):
    """
    A protocol that implements JSON-RPC.
    
    Methods published can return JSON-RPC serializable results, Faults,
    Binary, Boolean, DateTime, Deferreds, or Handler instances.

    By default methods beginning with 'jsonrpc_' are published.

    Sub-handlers for prefixed methods (e.g., system.listMethods)
    can be added with putSubHandler. By default, prefixes are
    separated with a '.'. Override self.separator to change this.
    """
    # Error codes for Twisted, if they conflict with yours then
    # modify them at runtime.
    NOT_FOUND = 8001
    FAILURE = 8002

    separator = '.'
    closed = 0

    def __init__(self):
        self.subHandlers = {}

    def __call__(self):
        return self

    def connectionMade(self):
        self.MAX_LENGTH = self.factory.maxLength

    def putSubHandler(self, prefix, handler):
        self.subHandlers[prefix] = handler

    def getSubHandler(self, prefix):
        return self.subHandlers.get(prefix, None)

    def getSubHandlerPrefixes(self):
        return self.subHandlers.keys()

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
        function = self.getFunction(functionPath)
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

    def getFunction(self, functionPath):
        """
        Given a string, return a function, or raise NoSuchFunction.

        This returned function will be called, and should return the result
        of the call, a Deferred, or a Fault instance.

        Override in subclasses if you want your own policy. The default
        policy is that given functionPath 'foo', return the method at
        self.jsonrpc_foo, i.e. getattr(self, "jsonrpc_" + functionPath).
        If functionPath contains self.separator, the sub-handler for
        the initial prefix is used to search for the remaining path.
        """
        if functionPath.find(self.separator) != -1:
            prefix, functionPath = functionPath.split(self.separator, 1)
            handler = self.getSubHandler(prefix)
            if handler is None:
                raise jsonrpclib.NoSuchFunction(self.NOT_FOUND, 
                    "no such subHandler %s" % prefix)
            return handler.getFunction(functionPath)

        f = getattr(self, "jsonrpc_%s" % functionPath, None)
        if not f:
            raise jsonrpclib.NoSuchFunction(self.NOT_FOUND, 
                "function %s not found" % functionPath)
        elif not callable(f):
            raise jsonrpclib.NoSuchFunction(self.NOT_FOUND, 
                "function %s not callable" % functionPath)
        else:
            return f

    def _listFunctions(self):
        """
        Return a list of the names of all jsonrpc methods.
        """
        return reflect.prefixedMethodNames(self.__class__, 'jsonrpc_')


class JSONRPCIntrospection(JSONRPC):
    """
    Implement the JSON-RPC Introspection API.

    By default, the methodHelp method returns the 'help' method attribute,
    if it exists, otherwise the __doc__ method attribute, if it exists,
    otherwise the empty string.

    To enable the methodSignature method, add a 'signature' method attribute
    containing a list of lists. See methodSignature's documentation for the
    format. Note the type strings should be JSON-RPC types, not Python types.
    """

    def __init__(self, parent):
        """
        Implement Introspection support for an JSONRPC server.

        @param parent: the JSONRPC server to add Introspection support to.
        """

        JSONRPC.__init__(self)
        self._jsonrpc_parent = parent

    def jsonrpc_listMethods(self):
        """
        Return a list of the method names implemented by this server.
        """
        functions = []
        todo = [(self._jsonrpc_parent, '')]
        while todo:
            obj, prefix = todo.pop(0)
            functions.extend([ prefix + name for name in obj._listFunctions() ])
            todo.extend([ (obj.getSubHandler(name),
                           prefix + name + obj.separator)
                          for name in obj.getSubHandlerPrefixes() ])
        functions.sort()
        return functions

    jsonrpc_listMethods.signature = [['array']]

    def jsonrpc_methodHelp(self, method):
        """
        Return a documentation string describing the use of the given method.
        """
        method = self._jsonrpc_parent.getFunction(method)
        return (getattr(method, 'help', None)
                or getattr(method, '__doc__', None) or '').strip()

    jsonrpc_methodHelp.signature = [['string', 'string']]

    def jsonrpc_methodSignature(self, method):
        """
        Return a list of type signatures.

        Each type signature is a list of the form [rtype, type1, type2, ...]
        where rtype is the return type and typeN is the type of the Nth
        argument. If no signature information is available, the empty
        string is returned.
        """
        method = self._jsonrpc_parent.getFunction(method)
        return getattr(method, 'signature', None) or ''

    jsonrpc_methodSignature.signature = [['array', 'string'],
                                        ['string', 'string']]


def addIntrospection(jsonrpc):
    """
    Add Introspection support to an JSONRPC server.

    @param jsonrpc: The jsonrpc server to add Introspection support to.
    """
    jsonrpc.putSubHandler('system', JSONRPCIntrospection, ('protocol',))


class QueryProtocol(basic.NetstringReceiver):

    def connectionMade(self):
        self.data = ''
        msg = self.factory.payload
        packet = '%d:%s,' % (len(msg), msg)
        self.transport.write(packet)

    def stringReceived(self, string):
        self.factory.data = string
        self.transport.loseConnection()


class QueryFactory(protocol.ClientFactory):

    deferred = None
    protocol = QueryProtocol
    data = ''

    def __init__(self, method, *args):
        # Pass the method name and JSON-RPC args (converted from python)
        # into the template.
        self.payload = jsonrpclib.dumps({
            'method':method, 
            'params':args})
        self.deferred = defer.Deferred()

    def parseResponse(self, contents):
        if not self.deferred:
            return
        try:
            # Convert the response from JSON-RPC to python.
            result = jsonrpclib.loads(contents)
            #response = jsonrpclib.loads(contents)
            #result = response['result']
            #error = response['error']
            #if error:
            #    self.deferred.errback(error)
            if isinstance(result, list):
                result = result[0]
        except Exception, error:
            self.deferred.errback(error)
            self.deferred = None
        else:
            self.deferred.callback(result)
            self.deferred = None

    def clientConnectionLost(self, _, reason):
        self.parseResponse(self.data)

    def clientConnectionFailed(self, _, reason):
        if self.deferred is not None:
            self.deferred.errback(reason)
            self.deferred = None

    def badStatus(self, status, message):
        self.deferred.errback(ValueError(status, message))
        self.deferred = None


class Proxy:
    """
    A Proxy for making remote JSON-RPC calls.

    Pass the URL of the remote JSON-RPC server to the constructor.

    Use proxy.callRemote('foobar', *args) to call remote method
    'foobar' with *args.
    """

    def __init__(self, host, port, factoryClass=QueryFactory):
        """
        @type host: C{str}
        @param host: The host to which method calls are made.

        @type port: C{integer}
        @param port: The host's port to which method calls are made.
        """
        self.host = host
        self.port = port
        self.factoryClass = factoryClass

    def callRemote(self, method, *args, **kwargs):
        factoryClass = kwargs.get("factoryClass")
        if not factoryClass:
            factoryClass = self.factoryClass
        factory = factoryClass(method, *args)
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
        self.putSubHandler('system', JSONRPCIntrospection, ('protocol',))


__all__ = ["JSONRPC", "Proxy", "RPCFactory"]
