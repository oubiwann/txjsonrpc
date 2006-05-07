from twisted.application import service, internet

try:
    from adytum.twisted import jsonrpc
except ImportError:
    from pkg_resources import require
    require('Twisted-JSONRPC')
    from adytum.twisted import jsonrpc

class Example(jsonrpc.JSONRPC):
    """An example object to be published."""

    def jsonrpc_echo(self,  x):
        """Return all passed args."""
        return x

    def jsonrpc_add(self, a, b):
        """Return sum of arguments."""
        return a + b

server = jsonrpc.RPCFactory(Example)
application = service.Application("Example JSON-RPC Server")
jsonrpcServer = internet.TCPServer(7080, server)
jsonrpcServer.setServiceParent(application)

