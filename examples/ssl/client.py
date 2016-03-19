from __future__ import print_function

import logging
from twisted.internet import reactor, ssl
from txjsonrpc.web.jsonrpc import Proxy

from OpenSSL import SSL
from twisted.python import log

def printValue(value):
    print("Result: %s" % str(value))

def printError(error):
    print('error', error)

def shutDown(data):
    print("Shutting down reactor...")
    reactor.stop()

def verifyCallback(connection, x509, errnum, errdepth, ok):
    log.msg(connection.__str__())
    if not ok:
        log.msg('invalid server cert: %s' % x509.get_subject(), logLevel=logging.ERROR)
        return False
    else:
        log.msg('good server cert: %s' % x509.get_subject(), logLevel=logging.INFO)
        return True

class AltCtxFactory(ssl.ClientContextFactory):
    def getContext(self):
        #self.method = SSL.SSLv23_METHOD
        ctx = ssl.ClientContextFactory.getContext(self)
        ctx.set_verify(SSL.VERIFY_PEER, verifyCallback)
        ctx.load_verify_locations("cacert.pem")
        #ctx.use_certificate_file('keys/client.crt')
        #ctx.use_privatekey_file('keys/client.key')
        return ctx


import sys
log.startLogging(sys.stdout)

#proxy = Proxy('https://127.0.0.1:7443/', ssl_ctx_factory=AltCtxFactory)
proxy = Proxy('https://127.0.0.2:7443/', ssl_ctx_factory=AltCtxFactory)

d = proxy.callRemote('add', 3, 5)
d.addCallback(printValue).addErrback(printError).addBoth(shutDown)
reactor.run()

