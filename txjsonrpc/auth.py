from zope.interface import Interface, implements

from twisted.cred.portal import IRealm, Portal
from twisted.web.guard import BasicCredentialFactory, HTTPAuthSessionWrapper
from twisted.web.resource import IResource


class TwistedWebHTTPAuthRealm(object):

    implements(IRealm)

    def __init__(self, resource):
        self.resource = resource

    def logout(self):
        pass

    def requestAvatar(self, avatarId, mind, *interfaces):
        if IResource in interfaces:
            return IResource, self.resource, self.logout
        raise NotImplementedError()


class TwistedWeb2HTTPAuthRealm(object):
    pass


def wrapResource(resource, checkers, credFactories=[], realmName=""):
    defaultCredFactory = BasicCredentialFactory(realmName)
    credFactories.insert(0, defaultCredFactory)
    realm = TwistedWebHTTPAuthRealm(resource)
    portal = Portal(realm, checkers)
    return HTTPAuthSessionWrapper(portal, credFactories)
