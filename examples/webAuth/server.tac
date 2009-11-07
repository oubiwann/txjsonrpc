import os

from twisted.application import service, internet
from twisted.cred.checkers import FilePasswordDB
from twisted.web import server

from txjsonrpc.auth import wrapResource
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


# Set up the application and the JSON-RPC resources.
application = service.Application("Example JSON-RPC Server")
root = Example()
root.putSubHandler('math', Math())

# Define the credential checker the application will be using and wrap the
# JSON-RPC resource.
dirname = os.path.dirname(__file__)
checker = FilePasswordDB(os.path.join(dirname, "passwd.db"))
realmName = "My JSON-RPC App"
wrappedRoot = wrapResource(root, [checker], realmName=realmName)

# With the wrapped root, we can set up the server as usual.
site = server.Site(resource=wrappedRoot)
server = internet.TCPServer(6969, site)
server.setServiceParent(application)
