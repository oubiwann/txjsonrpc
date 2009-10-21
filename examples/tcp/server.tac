from twisted.application import service, internet

from txjsonrpc.netstring import jsonrpc


class Example(jsonrpc.JSONRPC):
    """An example object to be published."""

    def jsonrpc_echo(self,  x):
        """Return all passed args."""
        return x

    def jsonrpc_add(self, a, b):
        """Return sum of arguments."""
        return a + b


factory = jsonrpc.RPCFactory(Example())
application = service.Application("Example JSON-RPC Server")
jsonrpcServer = internet.TCPServer(7080, factory)
jsonrpcServer.setServiceParent(application)

