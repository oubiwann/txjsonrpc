from twisted.web import server
from twisted.application import service, internet

from txjsonrpc.web import jsonrpc


class Example(jsonrpc.JSONRPC):
    """
    An example object to be published.
    """

    addSlash = True

    def jsonrpc_echo(self, x):
        """Return all passed args."""
        return x


class Math(jsonrpc.JSONRPC):
    """
    An example subhandler.
    """
    def jsonrpc_add(self, a, b):
        """Return sum of arguments."""
        return a + b


application = service.Application("Example JSON-RPC Server")
root = Example()
root.putSubHandler('math', Math())
site = server.Site(root)
server = internet.TCPServer(6969, site)
server.setServiceParent(application)
