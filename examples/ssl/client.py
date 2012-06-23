from twisted.internet import reactor, ssl
from txjsonrpc.web.jsonrpc import Proxy

def printValue(value):
    print "Result: %s" % str(value)

def printError(error):
    print 'error', error

def shutDown(data):
    print "Shutting down reactor..."
    reactor.stop()

class AltCtxFactory(ssl.ClientContextFactory):
    def getContext(self):
        #self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        #ctx.use_certificate_file('keys/client.crt')
        #ctx.use_privatekey_file('keys/client.key')
        return ctx

proxy = Proxy('https://127.0.0.1:7443/', ssl_ctx_factory=AltCtxFactory)

d = proxy.callRemote('add', 3, 5)
d.addCallback(printValue).addErrback(printError).addBoth(shutDown)
reactor.run()

