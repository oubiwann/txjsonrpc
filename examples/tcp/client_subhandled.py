import os
import sys
sys.path.insert(0, os.getcwd())

from twisted.internet import reactor
from twisted.internet import defer

from txjsonrpc.netstring.jsonrpc import Proxy


def printValue(value):
    print "Result: %s" % str(value)


def printError(error):
    print 'error', error


def shutDown(data):
    print "Shutting down reactor..."
    reactor.stop()


proxy = Proxy('127.0.0.1', 7080)
dl = []

d = proxy.callRemote('system.listMethods')
d.addCallbacks(printValue, printError)
dl.append(d)

d = proxy.callRemote('echo', 'bite me')
d.addCallbacks(printValue, printError)
dl.append(d)

d = proxy.callRemote('testing.getList')
d.addCallbacks(printValue, printError)
dl.append(d)

d = proxy.callRemote('math.add', 3, 5)
d.addCallbacks(printValue, printError)
dl.append(d)

dl = defer.DeferredList(dl)
dl.addCallback(shutDown)
reactor.run()
