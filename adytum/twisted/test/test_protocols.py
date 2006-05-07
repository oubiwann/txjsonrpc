"""
Test cases for adytum.twisted.protocols package.
"""
import StringIO
import string, struct

from twisted.trial import unittest
from twisted.protocols import basic
from twisted.internet import protocol

basic.DEBUG = 1

class StringIOWithoutClosing(StringIO.StringIO):
    def close(self):
        pass

class TestNetstring(basic.NetstringReceiver):

    closed = 0
    MAX_LENGTH = 50
    
    def connectionMade(self):
        self.received = []

    def stringReceived(self, s):
        self.received.append(s)


    def connectionLost(self, reason):
        self.closed = 1

class NetstringReceiverTestCase(unittest.TestCase):

    strings = ['hello', 'world', 'how', 'are', 'you123', ':today', "a"*515, "b"*699,
        "hey, here's a coma!,", '2:', '2:123',]

    illegalStrings = ['9999999999999999999999', "a"*499, 'abc', '4:abcde',
                       '51:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab,',]

    protocol = TestNetstring

    def getProtocol(self):
        transport = StringIOWithoutClosing()
        p = self.protocol()
        p.makeConnection(protocol.FileWrapper(transport))
        return p
    
    def testBuffer(self):
        for packet_size in range(1, 10):
            transport = StringIOWithoutClosing()
            p = TestNetstring()
            p.MAX_LENGTH = 699
            p.makeConnection(protocol.FileWrapper(transport))
            for string in self.strings:
                p.sendString(string)
            out = transport.getvalue()
            # test "chunked" strings of packet size ranging from one 
            # through 10 characters
            for i in range(len(out)/packet_size + 1):
                starting_index = i*packet_size
                ending_index = (i+1)*packet_size
                chunk = out[starting_index:ending_index]
                if chunk:
                    p.dataReceived(chunk)
            # make sure that all the chunks got "reassembled" properly
            self.assertEquals(p.received, self.strings)

    def testIllegal(self):
        for string in self.illegalStrings:
            p = self.getProtocol()
            for character in string:
                p.dataReceived(character)
            #self.assertEquals(p.received, string)
            self.assertEquals(p.transport.closed, 1)


class JSONNetstringTestCase(unittest.TestCase):

    jsonString = '{"a":"hello, world!", "b":"good-bye, cruel world."}'

    protocol = TestNetstring
