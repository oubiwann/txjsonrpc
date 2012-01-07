import os

from zope.interface import Interface

from twisted import web
from twisted.cred.checkers import InMemoryUsernamePasswordDatabaseDontUse
from twisted.trial.unittest import SkipTest, TestCase

from txjsonrpc.auth import HTTPAuthRealm, wrapResource


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

    def test_requestAvatarNonWeb(self):
        self.assertRaises(NotImplementedError, self.realm.requestAvatar,
                          "an id", None, [Interface])


class WrapResourceTestCase(TestCase):

    def setUp(self):
        self.checker = InMemoryUsernamePasswordDatabaseDontUse()
        self.checker.addUser("joe", "blow")

    def test_wrapResourceWeb(self):
        from twisted.web.resource import IResource, Resource
        root = Resource()
        wrapped = wrapResource(root, [self.checker])
        self.assertTrue(IResource.providedBy(wrapped))
