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
