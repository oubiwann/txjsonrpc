from twisted.internet import reactor, defer

from txjsonrpc.web.jsonrpc import Proxy


def printValue(value):
    print "Result: %s" % str(value)


def printError(error):
    print 'error', error


def shutDown(data):
    print "Shutting down reactor..."
    reactor.stop()


proxy = Proxy('http://127.0.0.1:6969/')
dl = []

d = proxy.callRemote('echo', 'bite me')
d.addCallbacks(printValue, printError)
dl.append(d)

d = proxy.callRemote('math.add', 3, 5)
d.addCallbacks(printValue, printError)
dl.append(d)

dl = defer.DeferredList(dl)
dl.addCallback(shutDown)
reactor.run()
