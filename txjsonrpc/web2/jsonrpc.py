# Copyright (c) 2001-2004 Twisted Matrix Laboratories.
# See LICENSE for details.
"""
A generic resource for publishing objects via JSON-RPC.

API Stability: semi-stable

Maintainer: U{Duncan McGreggor <mailto:oubiwann@adytum.us>}
"""
from twisted.internet import defer
from twisted.python import log, reflect
from twisted.web2 import http, http_headers, resource, responsecode, stream

from txjsonrpc import jsonrpclib
from txjsonrpc.jsonrpc import (
    BaseSubhandler, Introspection as BaseIntrospection)


__all__ = ["JSONRPC", "addIntrospection"]


class JSONRPC(resource.Resource, BaseSubhandler):
    """
    A resource that implements JSON-RPC.

    You probably want to connect this to '/RPC2'.

    Methods published can return JSON-RPC serializable results, Faults,
    Binary, Boolean, DateTime, Deferreds, or Handler instances.

    By default methods beginning with 'jsonrpc_' are published.

    Sub-handlers for prefixed methods (e.g., system.listMethods)
    can be added with putSubHandler. By default, prefixes are
    separated with a '.'. Override self.separator to change this.
    """

    # Error codes for Twisted, if they conflict with yours then
    # modify them at runtime.
    NOT_FOUND = 8001
    FAILURE = 8002

    separator = '.'

    def __init__(self):
        resource.Resource.__init__(self)
        BaseSubhandler.__init__(self)

    def render(self, request):
        # For GET/HEAD: Return an error message
        s=("<html><head><title>JSON-RPC responder</title></head>"
           "<body><h1>JSON-RPC responder</h1>POST your JSON-RPC "
           "here.</body></html>")

        return http.Response(responsecode.OK,
            {'content-type': http_headers.MimeType('text', 'html')},
            s)

    def http_POST(self, request):
        parser, unmarshaller = jsonrpclib.getparser()
        deferred = stream.readStream(request.stream, parser.feed)
        deferred.addCallback(lambda x: self._cbDispatch(
            request, parser, unmarshaller))
        deferred.addErrback(self._ebRender)
        deferred.addCallback(self._cbRender, request)
        return deferred

    def _cbDispatch(self, request, parser, unmarshaller):
        parser.close()
        args, functionPath = unmarshaller.close(), unmarshaller.getmethodname()

        function = self._getFunction(functionPath)
        return defer.maybeDeferred(function, request, *args)

    def _cbRender(self, result, request):
        if not isinstance(result, jsonrpclib.Fault):
            result = (result,)
        try:
            s = jsonrpclib.dumps(result)
        except:
            f = jsonrpclib.Fault(self.FAILURE, "can't serialize output")
            s = jsonrpclib.dumps(f)
        return http.Response(responsecode.OK,
            {'content-type': http_headers.MimeType('text', 'json')},
            s)

    def _ebRender(self, failure):
        if isinstance(failure.value, jsonrpclib.Fault):
            return failure.value
        log.err(failure)
        return jsonrpclib.Fault(self.FAILURE, "error")


class Introspection(BaseIntrospection):
    """
    twisted.web2 resources get passed the request in every method, so we need
    to adjust for that with the introepction class.
    """

    def jsonrpc_listMethods(self, request):
        return BaseIntrospection.jsonrpc_listMethods(self)

    def jsonrpc_methodHelp(self, request, method):
        return BaseIntrospection.jsonrpc_methodHelp(self, method)

    def jsonrpc_methodSignature(self, request, method):
        return BaseIntrospection.jsonrpc_methodSignature(self, method)


def addIntrospection(jsonrpc):
    """
    Add Introspection support to an JSONRPC server.

    @param jsonrpc: The jsonrpc server to add Introspection support to.
    """
    jsonrpc.putSubHandler('system', Introspection(jsonrpc))
