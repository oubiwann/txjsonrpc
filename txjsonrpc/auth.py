from zope.interface import Interface, implements

try:
    from twisted import web
except ImportError:
    web = None
try:
    from twisted import web2
except ImportError:
    web2 = None

from twisted.cred.portal import IRealm, Portal


class HTTPAuthRealm(object):

    implements(IRealm)

    def __init__(self, resource):
        self.resource = resource

    def logout(self):
        pass

    def requestAvatar(self, avatarId, mind, *interfaces):
        if web.resource.IResource in interfaces:
            return web.resource.IResource, self.resource, self.logout
        elif web2.iweb.IResource in interfaces:
            return web2.iweb.IResource, self.resource
        raise NotImplementedError()


def _wrapTwistedWebResource(resource, checkers, credFactories=[],
                            realmName=""):
    from twisted.web import guard

    defaultCredFactory = guard.BasicCredentialFactory(realmName)
    credFactories.insert(0, defaultCredFactory)
    realm = HTTPAuthRealm(resource)
    portal = Portal(realm, checkers)
    return guard.HTTPAuthSessionWrapper(portal, credFactories)


def _wrapTwistedWeb2Resource(resource, checkers, credFactories=[],
                            realmName=""):
    from twisted.web2.auth import basic
    from twisted.web2.auth import wrapper

    defaultCredFactory = basic.BasicCredentialFactory(realmName)
    credFactories.insert(0, defaultCredFactory)
    realm = HTTPAuthRealm(resource)
    portal = Portal(realm, checkers)
    interfaces = (web2.iweb.IResource,)
    return wrapper.HTTPAuthResource(
        resource, credFactories, portal, interfaces)


def wrapResource(resource, *args, **kwargs):
    from twisted import web, web2

    if web.resource.IResource.providedBy(resource):
        return _wrapTwistedWebResource(resource, *args, **kwargs)
    elif web2.iweb.IResource.providedBy(resource):
        return _wrapTwistedWeb2Resource(resource, *args, **kwargs)
