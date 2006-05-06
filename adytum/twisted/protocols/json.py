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

    def __init__(self, maxlen=32768):
        basic.LineReceiver.__init__(self)
        self.MAX_LENGTH = maxlen

    def connectionMade(self):
        pass

    def rawDataReceived(self, data):
        try:
            simplejson.loads(data)
        except JSONParseError:
            self.transport.loseConnection()

    def connectionLost(self, reason):
        pass
            
class JSONRawReceiverFactory(protocol.Protocol)

    def buildProtocol(self, addr):
        p = JSONLineReceiver()
        p.setRawMode()
        p.factory = self
        return p
