import os

from zope.interface import Interface

from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.trial.unittest import SkipTest, TestCase

from txjsonrpc.auth import HTTPAuthRealm, wrapResource


def removeCompiled(filename):
    if filename.endswith(".pyc") or filename.endswith(".pyo"):
        if os.path.exists(filename):
            os.unlink(filename)


def getTwistedWeb():
    try:
        from twisted import web
        if hasattr(web, "__file__"):
            removeCompiled(web.__file__)
    except ImportError:
        web = None
    return web


def getTwistedWeb2():
    try:
        from twisted import web2
        if hasattr(web2, "__file__"):
            removeCompiled(web2.__file__)
    except ImportError:
        web2 = None
    return web2


class ImportTestCase(TestCase):

    def setUp(self):
        super(ImportTestCase, self).setUp()
        self.original_twisted_web = self.getTwistedWeb()
        self.original_twisted_web2 = self.getTwistedWeb2()

    def tearDown(self):
        import twisted
        if self.original_twisted_web is None:
            del twisted.web
        else:
            twisted.web = self.original_twisted_web
        if self.original_twisted_web2 is None:
            del twisted.web2
        else:
            twisted.web2 = self.original_twisted_web2

    def getTwistedWeb(self):
        web = getTwistedWeb()
        self.original_twisted_web = web
        return web

    def getTwistedWeb2(self):
        web2 = getTwistedWeb2()
        self.original_twisted_web2 = web2
        return web2

    def setTwistedWeb(self):
        # We need to do this for folks that are running the test suite but
        # don't actually have twisted.web installed.
        web = self.getTwistedWeb() or "no twisted.web"
        import twisted
        twisted.web = web

    def setTwistedWeb2(self):
        # We need to do this for folks that are running the test suite but
        # don't actually have twisted.web installed.
        web2 = self.getTwistedWeb2() or "no twisted.web2"
        import twisted
        twisted.web2 = web2

    def removeTwistedWeb(self):
        self.setTwistedWeb()
        import twisted
        del twisted.web

    def removeTwistedWeb2(self):
        self.setTwistedWeb2()
        import twisted
        del twisted.web2

    def test_no_twisted_web(self):
        self.removeTwistedWeb()
        from txjsonrpc import auth
        reload(auth)
        self.assertEquals(auth.web, None)

    def test_no_twisted_web2(self):
        self.removeTwistedWeb2()
        from txjsonrpc import auth
        reload(auth)
        self.assertEquals(auth.web2, None)

    def test_twisted_web(self):
        self.setTwistedWeb()
        from txjsonrpc import auth
        reload(auth)
        self.assertTrue(auth.web is not None)

    def test_twisted_web2(self):
        self.setTwistedWeb2()
        from txjsonrpc import auth
        reload(auth)
        self.assertTrue(auth.web2 is not None)


class HTTPAuthRealmTestCase(TestCase):

    def setUp(self):
        self.realm = HTTPAuthRealm("a resource")

    def test_creation(self):
        self.assertEquals(self.realm.resource, "a resource")

    def test_requestAvatarWeb(self):
        from twisted.web.resource import IResource
        interface, resource, logoutMethod = self.realm.requestAvatar(
            "an id", None, IResource)
        self.assertEquals(interface, IResource)
        self.assertEquals(resource, self.realm.resource)
        self.assertEquals(logoutMethod, self.realm.logout)

    def test_requestAvatarWeb2(self):
        from twisted.web2.iweb import IResource
        interface, resource = self.realm.requestAvatar(
            "an id", None, IResource)
        self.assertEquals(interface, IResource)
        self.assertEquals(resource, self.realm.resource)

    def test_requestAvatarNonWeb(self):
        self.assertRaises(NotImplementedError, self.realm.requestAvatar,
                          "an id", None, [Interface])


class WrapResourceTestCase(TestCase):

    def setUp(self):
        self.checker = InMemoryUsernamePasswordDatabaseDontUse()
        self.checker.addUser("joe", "blow")

    def test_wrapResourceWeb(self):
        if not getTwistedWeb():
            raise SkipTest("This test requires both twisted.web.")
        from twisted.web.resource import IResource, Resource
        root = Resource()
        wrapped = wrapResource(root, [self.checker])
        self.assertTrue(IResource.providedBy(wrapped))

    def test_wrapResourceWeb2(self):
        if not getTwistedWeb2():
            raise SkipTest("This test requires both twisted.web2.")
        from twisted.web2.iweb import IResource
        from twisted.web2.resource import Resource
        root = Resource()
        wrapped = wrapResource(root, [self.checker])
        self.assertTrue(IResource.providedBy(wrapped))
