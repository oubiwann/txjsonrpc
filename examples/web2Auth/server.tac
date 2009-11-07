import os

from twisted.application import service, internet
from twisted.cred.checkers import FilePasswordDB
from twisted.web2 import server
from twisted.web2.channel import http

from txjsonrpc.auth import wrapResource
from txjsonrpc.web2 import jsonrpc


class Example(jsonrpc.JSONRPC):
    """An example object to be published."""

    addSlash = True

    def jsonrpc_echo(self, request, x):
        """Return all passed args."""
        return x

    def jsonrpc_add(self, request, a, b):
        """Return sum of arguments."""
        return a + b


# Set up the application and the JSON-RPC resource.
application = service.Application("Example JSON-RPC Server")
root = Example()

# Define the credential checker the application will be using and wrap the
# JSON-RPC resource.
dirname = os.path.dirname(__file__)
checker = FilePasswordDB(os.path.join(dirname, "passwd.db"))
realmName = "My JSON-RPC App"
wrappedRoot = wrapResource(root, [checker], realmName=realmName)

# With the wrapped root, we can set up the server as usual.
site = server.Site(wrappedRoot)
chan = http.HTTPFactory(site)
jsonrpcServer = internet.TCPServer(7080, chan)
jsonrpcServer.setServiceParent(application)
