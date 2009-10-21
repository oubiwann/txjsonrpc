"""
Requires simplejson; can be downloaded from 
http://cheeseshop.python.org/pypi/simplejson
"""
import xmlrpclib
from datetime import datetime

import simplejson


# From xmlrpclib.
SERVER_ERROR          = xmlrpclib.SERVER_ERROR
NOT_WELLFORMED_ERROR  = xmlrpclib.NOT_WELLFORMED_ERROR
UNSUPPORTED_ENCODING  = xmlrpclib.UNSUPPORTED_ENCODING
INVALID_ENCODING_CHAR = xmlrpclib.INVALID_ENCODING_CHAR
INVALID_JSONRPC       = xmlrpclib.INVALID_XMLRPC
METHOD_NOT_FOUND      = xmlrpclib.METHOD_NOT_FOUND
INVALID_METHOD_PARAMS = xmlrpclib.INVALID_METHOD_PARAMS
INTERNAL_ERROR        = xmlrpclib.INTERNAL_ERROR
# Custom errors.
METHOD_NOT_CALLABLE   = -32604

# Version constants.
VERSION_PRE1 = 0
VERSION_1 = 1
VERSION_2 = 2


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


def _preV1Request(method="", params=[], *args):
    return dumps({"method": method, "params": params})


def _v1Request(method="", params=[], id="", *args):
    return dumps({"method": method, "params": params, "id": id})


def _v1Notification(method="", params=[], *args):
    return _v1Request(method=method, params=param, id=None)


def _v2Request(method="", params=[], id="", *args):
    return dumps({
        "jsonrpc": "2.0", "method": method, "params": params, "id": id})


def _v2Notification(method="", params=[], *args):
    return _v2Request(method=method, params=param, id=None)


class ServerProxy(xmlrpclib.ServerProxy):
    """
    XXX add missing docstring
    """
    def __init__(self, uri, transport=Transport(), version=VERSION_PRE1, *args,
                 **kwds):
        xmlrpclib.ServerProxy.__init__(self, uri, transport, *args, **kwds)
        self.version = version

    def __request(self, *args):
        """
        Call a method on the remote server.

        XXX what calls __request?
        XXX Is there any way to indicate that we'd want a notification request
        instead of a regular request?
        """
        request = self._getVersionedRequest(*args)
        # XXX do a check here for id; if null, skip the response
        # XXX in order to do this effectively, we might have to change the
        # request functions to objects, so that we can get at an id attribute
        response = self.__transport.request(
            self.__host,
            self.__handler,
            request,
            verbose=self.__verbose
            )
        if len(response) == 1:
            response = response[0]
        return response

    def _getVersionedRequest(self, *args):
        if self.version == VERSION_PRE1:
            return _preV1Request(*args)
        elif self.version == VERSION_1:
            return _v1Request(*args)
        elif self.version == VERSION_2:
            return _v2Request(*args)
