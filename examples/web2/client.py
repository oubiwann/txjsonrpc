from twisted.internet import reactor
try:
    from adytum.twisted.web.jsonrpc import Proxy
except ImportError:
    from pkg_resources import require
    require('Twisted-JSONRPC')
    from adytum.twisted.web.jsonrpc import Proxy

def printValue(value):
    print repr(value)
    reactor.stop()

def printError(error):
    print 'error', error
    reactor.stop()

proxy = Proxy('http://127.0.0.1:7080/')
proxy.callRemote('add', 3, 5).addCallbacks(printValue, printError)
reactor.run()

