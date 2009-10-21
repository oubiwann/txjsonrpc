from twisted.application import service, internet

from txjsonrpc.netstring import jsonrpc


class Example(jsonrpc.JSONRPC):
    """An example object to be published."""

    def jsonrpc_echo(self, x):
        """Return all passed args."""
        return x


class Testing(jsonrpc.JSONRPC):

    def jsonrpc_getList(self):
        """Return a list."""
        return [1,2,3,4,'a','b','c','d']


class Math(jsonrpc.JSONRPC):

    def jsonrpc_add(self, a, b):
        """Return sum of arguments."""
        return a + b


# Note that this is a different approach that that used by 
# twisted.web[2].xmlrpc. Here, we are putting the subhandlers on the 
# server as opposed to putting them on the top-level RPC class.
factory = jsonrpc.RPCFactory(Example)
factory.putSubHandler('math', Math)
factory.putSubHandler('testing', Testing)

# Let's add introspection, just for fun
factory.addIntrospection()

application = service.Application("Example JSON-RPC Server")
jsonrpcServer = internet.TCPServer(7080, factory)
jsonrpcServer.setServiceParent(application)
