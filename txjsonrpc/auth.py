from zope.interface import implements

from twisted import web
from twisted.cred.portal import IRealm, Portal
from twisted.web import guard


class HTTPAuthRealm(object):

    implements(IRealm)

    def __init__(self, resource):
        self.resource = resource

    def logout(self):
        pass

    def requestAvatar(self, avatarId, mind, *interfaces):
        if web.resource.IResource in interfaces:
            return web.resource.IResource, self.resource, self.logout
        raise NotImplementedError()


def wrapResource(resource, checkers, credFactories=[],
                            realmName=""):

    defaultCredFactory = guard.BasicCredentialFactory(realmName)
    credFactories.insert(0, defaultCredFactory)
    realm = HTTPAuthRealm(resource)
    portal = Portal(realm, checkers)
    return guard.HTTPAuthSessionWrapper(portal, credFactories)
