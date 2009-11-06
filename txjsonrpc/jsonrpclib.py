"""
Requires simplejson; can be downloaded from 
http://cheeseshop.python.org/pypi/simplejson
"""
import xmlrpclib
from datetime import datetime

import simplejson


# From xmlrpclib
SERVER_ERROR          = xmlrpclib.SERVER_ERROR
NOT_WELLFORMED_ERROR  = xmlrpclib.NOT_WELLFORMED_ERROR
UNSUPPORTED_ENCODING  = xmlrpclib.UNSUPPORTED_ENCODING
INVALID_ENCODING_CHAR = xmlrpclib.INVALID_ENCODING_CHAR
INVALID_JSONRPC       = xmlrpclib.INVALID_XMLRPC
METHOD_NOT_FOUND      = xmlrpclib.METHOD_NOT_FOUND
INVALID_METHOD_PARAMS = xmlrpclib.INVALID_METHOD_PARAMS
INTERNAL_ERROR        = xmlrpclib.INTERNAL_ERROR
# Custom errors
METHOD_NOT_CALLABLE   = -32604


class Fault(xmlrpclib.Fault):
    pass


class NoSuchFunction(Fault):
    """
    There is no function by the given name.
    """

class JSONRPCEncoder(simplejson.JSONEncoder):
    """
    Provide custom serializers for JSON-RPC.
    """
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y%m%dT%H:%M:%S")
        raise TypeError("%r is not JSON serializable" % (obj,))


def dumps(obj, **kws):
    if isinstance(obj, Exception):
        obj = {'fault': obj.__class__.__name__,
            'faultCode': obj.faultCode,
            'faultString': obj.faultString}
    return simplejson.dumps(obj, cls=JSONRPCEncoder, **kws)


def loads(string, **kws):
    unmarshalled = simplejson.loads(string, **kws)
    if (isinstance(unmarshalled, dict) and
        unmarshalled.has_key('fault')):
        raise Fault(unmarshalled['faultCode'],
            unmarshalled['faultString'])
    return unmarshalled


class SimpleParser(object):

    buffer = ''

    def feed(self, data):
        self.buffer += data

    def close(self):
        self.data = loads(self.buffer)


class SimpleUnmarshaller(object):

    def getmethodname(self):
        return self.parser.data.get("method")

    def close(self):
        if isinstance(self.parser.data, dict):
            return self.parser.data.get("params")
        return self.parser.data


def getparser():
    parser = SimpleParser()
    marshaller = SimpleUnmarshaller()
    marshaller.parser = parser
    return parser, marshaller


class Transport(xmlrpclib.Transport):
    """
    Handles an HTTP transaction to an XML-RPC server.
    """
    user_agent = "jsonrpclib.py (by txJSON-RPC)"

    def getparser(self):
        """
        Get Parser and unmarshaller.
        """
        return getparser()


class ServerProxy(xmlrpclib.ServerProxy):
    """

    """
    def __init__(self, uri, transport=Transport(), *args, **kwds):
        xmlrpclib.ServerProxy.__init__(self, uri, transport, *args, **kwds)

    def __request(self, method, args):
        """
        Call a method on the remote server.
        """
        request = dumps({'method':method, 'params':args})
        response = self.__transport.request(
            self.__host,
            self.__handler,
            request,
            verbose=self.__verbose
            )
        if len(response) == 1:
            response = response[0]
        return response

