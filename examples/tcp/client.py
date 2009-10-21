import os
import sys
sys.path.insert(0, os.getcwd())

from twisted.internet import reactor

from txjsonrpc.netstring.jsonrpc import Proxy


def printValue(value):
    print "Result: %s" % str(value)
    reactor.stop()


def printError(error):
    print 'error', error
    reactor.stop()


proxy = Proxy('127.0.0.1', 7080)
proxy.callRemote('add', 3, 5).addCallbacks(printValue, printError)
reactor.run()

