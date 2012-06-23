from txjsonrpc.web import jsonrpc
from twisted.web import server
from twisted.internet import reactor, ssl

class Math(jsonrpc.JSONRPC):
    """
    An example object to be published.
    """
    def jsonrpc_add(self, a, b):
        """
        Return sum of arguments.
        """
        return a + b


sslContext = ssl.DefaultOpenSSLContextFactory(
	'privkey.pem', 
	'cacert.pem',
)

reactor.listenSSL(
	7443,
	server.Site(Math()),
	contextFactory = sslContext,
)
reactor.run()

