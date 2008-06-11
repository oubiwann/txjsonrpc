"""
Requires simplejson; can be downloaded from 
http://cheeseshop.python.org/pypi/simplejson
"""
import xmlrpclib

import simplejson

# From xmlrpclib
# From xmlrpclib
SERVER_ERROR          = xmlrpclib.SERVER_ERROR
NOT_WELLFORMED_ERROR  = xmlrpclib.NOT_WELLFORMED_ERROR
UNSUPPORTED_ENCODING  = xmlrpclib.UNSUPPORTED_ENCODING
INVALID_ENCODING_CHAR = xmlrpclib.INVALID_ENCODING_CHAR
INVALID_JSONRPC       = xmlrpclib.INVALID_XMLRPC
METHOD_NOT_FOUND      = xmlrpclib.METHOD_NOT_FOUND
INVALID_METHOD_PARAMS = xmlrpclib.INVALID_METHOD_PARAMS
INTERNAL_ERROR        = xmlrpclib.INTERNAL_ERROR
Fault                 = xmlrpclib.Fault
# Custom errors
METHOD_NOT_CALLABLE   = -32604

class NoSuchFunction(Fault):
    """There is no function by the given name."""
    pass

def dumps(obj, **kws):
    if isinstance(obj, Exception):
        obj = {'fault': obj.__class__.__name__,
            'faultCode': obj.faultCode,
            'faultString': obj.faultString}
    #print "In dumps(), obj = %s" % obj
    return simplejson.dumps(obj, **kws)

def loads(string, **kws):
    unmarshalled = simplejson.loads(string, **kws)
    if (isinstance(unmarshalled, dict) and
        unmarshalled.has_key('fault')):
        raise Fault(unmarshalled['faultCode'],
            unmarshalled['faultString'])
    return unmarshalled

class BogusParser(object):

    def feed(self, data):
        self.data = loads(data)

    def close(self):
        pass

class BogusUnmarshaller(object):

    def getmethodname(self):
        return self.parser.data.get("method")

    def close(self):
        return self.parser.data.get("params")

def getparser():
    parser = BogusParser()
    marshaller = BogusUnmarshaller()
    marshaller.parser = parser
    return parser, marshaller

