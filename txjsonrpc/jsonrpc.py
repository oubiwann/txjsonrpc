from twisted.internet import defer, protocol
from twisted.python import reflect

from txjsonrpc import jsonrpclib


class BaseSubhandler:
    """
    Sub-handlers for prefixed methods (e.g., system.listMethods)
    can be added with putSubHandler. By default, prefixes are
    separated with a '.'. Override self.separator to change this.
    """
    def __init__(self):
        self.subHandlers = {}

    def putSubHandler(self, prefix, handler):
        self.subHandlers[prefix] = handler

    def getSubHandler(self, prefix):
        return self.subHandlers.get(prefix, None)

    def getSubHandlerPrefixes(self):
        return self.subHandlers.keys()

    def _getFunction(self, functionPath):
        """
        Given a string, return a function, or raise jsonrpclib.NoSuchFunction.

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
                raise jsonrpclib.NoSuchFunction(jsonrpclib.METHOD_NOT_FOUND,
                    "no such sub-handler %s" % prefix)
            return handler._getFunction(functionPath)

        f = getattr(self, "jsonrpc_%s" % functionPath, None)
        if not f:
            raise jsonrpclib.NoSuchFunction(jsonrpclib.METHOD_NOT_FOUND,
                "function %s not found" % functionPath)
        elif not callable(f):
            raise jsonrpclib.NoSuchFunction(jsonrpclib.METHOD_NOT_CALLABLE,
                "function %s not callable" % functionPath)
        else:
            return f

    def _listFunctions(self):
        """
        Return a list of the names of all jsonrpc methods.
        """
        return reflect.prefixedMethodNames(self.__class__, 'jsonrpc_')


class BaseQueryFactory(protocol.ClientFactory):

    deferred = None
    protocol = None

    def __init__(self, method, version=jsonrpclib.VERSION_PRE1, *args):
        self.payload = self._buildVersionedPayload(version, method, args)
        self.deferred = defer.Deferred()

    def _buildVersionedPayload(self, version, *args):
        if version == jsonrpclib.VERSION_PRE1:
            return jsonrpclib._preV1Request(*args)
        elif version == jsonrpclib.VERSION_1:
            return jsonrpclib._v1Request(*args)
        elif version == jsonrpclib.VERSION_2:
            return jsonrpclib._v2Request(*args)

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

    def clientConnectionFailed(self, _, reason):
        if self.deferred is not None:
            self.deferred.errback(reason)
            self.deferred = None

    clientConnectionLost = clientConnectionFailed

    def badStatus(self, status, message):
        self.deferred.errback(ValueError(status, message))
        self.deferred = None


class BaseProxy:
    """
    A Proxy base class for making remote JSON-RPC calls.
    """
    def __init__(self, version=jsonrpclib.VERSION_PRE1, factoryClass=None):
        self.version = version
        self.factoryClass = factoryClass

    def _getVersion(self, keywords):
        version = keywords.get("version")
        if version == None:
            version = self.version
        return version

    def _getFactoryClass(self, keywords):
        factoryClass = keywords.get("factoryClass")
        if not factoryClass:
            factoryClass = self.factoryClass
        return factoryClass
