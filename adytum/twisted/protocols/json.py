import simplejson

from twisted.internet import protocol 
from twisted.protocols import basic

class Error(Exception):
    pass

class JSONParseError(Error):
    pass

class JSONStream(object):

    def parse(self, buffer):
        try:
            # XXX
            simplejson.loads(buffer)
        except JSONParseError, e:
            raise JSONParseError, str(e)

class JSONLineReceiver(basic.LineReceiver):

    def __init__(self):
        basic.LineReceiver.__init__(self)
        self.stream = None

    def connectionMade(self):
        self.stream = JSONStream()

    def rawDataReceived(self, data):
        try:
            self.stream.parse(data)
        except JSONParseError:
            self.transport.loseConnection()

    def connectionLost(self, reason):
        self.stream = None
            
class JSONRawReceiverFactory(protocol.Protocol)

    def buildProtocol(self, addr):
        p = JSONLineReceiver()
        p.setRawMode()
        p.factory = self
        return p
