from twisted.trial.unittest import TestCase


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
        try:
            from twisted import web
        except ImportError:
            web = None
        self.original_twisted_web = web
        return web

    def getTwistedWeb2(self):
        try:
            from twisted import web2
        except ImportError:
            web2 = None
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
        self.assertEquals(auth.web, None)

    def test_twisted_web(self):
        self.setTwistedWeb()
        from txjsonrpc import auth
        self.assertTrue(auth.web is not None)

    def test_no_twisted_web2(self):
        self.removeTwistedWeb2()
        from txjsonrpc import auth
        self.assertEquals(auth.web2, None)

    def test_twisted_web2(self):
        self.setTwistedWeb2()
        from txjsonrpc import auth
        self.assertTrue(auth.web2 is not None)


class HTTPAuthRealmTestCase(TestCase):
    pass


class WrapResourceTestCase(TestCase):
    pass
