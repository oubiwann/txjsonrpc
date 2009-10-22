from twisted.internet import defer, protocol

from txjsonrpc import jsonrpclib


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
