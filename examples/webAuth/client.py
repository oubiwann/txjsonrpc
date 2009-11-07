from twisted.internet import reactor, defer

from txjsonrpc.web.jsonrpc import Proxy


def printValue(value):
    print "Result: %s" % str(value)


def printError(error):
    status, message = error.value.args
    if status == "401":
        print message
        return
    print 'error', error


def shutDown(data):
    print "Shutting down reactor..."
    reactor.stop()


proxyUnauth = Proxy('http://127.0.0.1:6969/')
dl = []

d = proxyUnauth.callRemote('echo', 'bite me')
d.addCallbacks(printValue, printError)
dl.append(d)

d = proxyUnauth.callRemote('math.add', 3, 5)
d.addCallbacks(printValue, printError)
dl.append(d)

proxyAuth = Proxy('http://bob:p4ssw0rd@127.0.0.1:6969/')

d = proxyAuth.callRemote('echo', 'bite me')
d.addCallbacks(printValue, printError)
dl.append(d)

d = proxyAuth.callRemote('math.add', 3, 5)
d.addCallbacks(printValue, printError)
dl.append(d)

dl = defer.DeferredList(dl)
dl.addCallback(shutDown)
reactor.run()
