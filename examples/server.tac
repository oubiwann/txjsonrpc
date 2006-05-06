from twisted.web2 import server
from twisted.web2.channel import http
from twisted.application import service, internet

try:
    from adytum.twisted.web2 import jsonrpc
except ImportError:
    from pkg_resources import require
    require('Twisted-JSONRPC')
    from adytum.twisted.web2 import jsonrpc

class Example(jsonrpc.JSONRPC):
    """An example object to be published."""

    addSlash = True

    def jsonrpc_echo(self, request, x):
        """Return all passed args."""
        return x

    def jsonrpc_add(self, request, a, b):
        """Return sum of arguments."""
        return a + b

site = server.Site(Example())
chan = http.HTTPFactory(site)
application = service.Application("Example JSON-RPC Server")
jsonrpcServer = internet.TCPServer(7080, chan)
jsonrpcServer.setServiceParent(application)

