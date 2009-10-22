from twisted.internet import defer, protocol

from txjsonrpc import jsonrpclib


class BaseQueryFactory(protocol.ClientFactory):

    deferred = None
    protocol = None

    def __init__(self, method, version=jsonrpclib.VERSION_PRE1, *args):
        self.payload = self._buildVersionedPayload(version, method, args)
        self.deferred = defer.Deferred()

    def _buildVersionedPayload(self, version, *args):
        #import pdb;pdb.set_trace()
        if version == jsonrpclib.VERSION_PRE1:
            return jsonrpclib._preV1Request(*args)
        elif version == jsonrpclib.VERSION_1:
            return jsonrpclib._v1Request(*args)
        elif version == jsonrpclib.VERSION_2:
            return jsonrpclib._v2Request(*args)
