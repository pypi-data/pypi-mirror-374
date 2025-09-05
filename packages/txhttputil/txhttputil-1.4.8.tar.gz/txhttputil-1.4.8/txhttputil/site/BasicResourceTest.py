import logging

from twisted.trial import unittest
from twisted.web.resource import NoResource
from twisted.web.test.requesthelper import DummyRequest
from txhttputil.site.BasicResource import BasicResource

logger = logging.getLogger(__name__)


class MockAddress:
    def __init__(self, host):
        self.host = host


class TestBasicResource(BasicResource):
    def render_GET(self, request):
        return b"GET response"

    def render_POST(self, request):
        return b"POST response"


class BasicResourceTest(unittest.TestCase):

    def setUp(self):
        self.resource = TestBasicResource()

    def testBasicGetChild(self):
        child = self.resource.getChild(b"nonexistent", None)
        self.assertIsInstance(child, NoResource)

    def testPutAndGetChild(self):
        childResource = TestBasicResource()
        self.resource.putChild(b"child", childResource)

        retrievedChild = self.resource.getChild(b"child", None)
        self.assertEqual(retrievedChild, childResource)

    def testDeleteChild(self):
        childResource = TestBasicResource()
        self.resource.putChild(b"child", childResource)

        self.resource.deleteChild(b"child")

        retrievedChild = self.resource.getChild(b"child", None)
        self.assertIsInstance(retrievedChild, NoResource)

    def testRenderGetMethod(self):
        request = DummyRequest([])
        request.method = b"GET"

        response = self.resource.render(request)
        self.assertEqual(response, b"GET response")

    def testRenderPostMethod(self):
        request = DummyRequest([])
        request.method = b"POST"

        response = self.resource.render(request)
        self.assertEqual(response, b"POST response")

    def testIpFilteringAllowed(self):
        allowedIps = ["127.0.0.1", "192.168.1.100"]
        resource = TestBasicResource(allowedIpsList=allowedIps)

        request = DummyRequest([])
        request.method = b"GET"
        request.getClientAddress = lambda: MockAddress("127.0.0.1")

        response = resource.render(request)
        self.assertEqual(response, b"GET response")

    def testIpFilteringBlocked(self):
        allowedIps = ["127.0.0.1", "192.168.1.100"]
        resource = TestBasicResource(allowedIpsList=allowedIps)

        request = DummyRequest([])
        request.method = b"GET"
        request.getClientAddress = lambda: MockAddress("10.0.0.1")

        response = resource.render(request)
        self.assertEqual(response, b"Forbidden: IP address not allowed")
        self.assertEqual(request.responseCode, 403)

    def testIpFilteringDisabled(self):
        resource = TestBasicResource(allowedIpsList=None)

        request = DummyRequest([])
        request.method = b"GET"
        request.getClientAddress = lambda: MockAddress("10.0.0.1")

        response = resource.render(request)
        self.assertEqual(response, b"GET response")


if __name__ == "__main__":
    from twisted.trial import runner, reporter
    import sys

    trialRunner = runner.TrialRunner(reporter.VerboseTextReporter)
    suite = runner.TestLoader().loadClass(BasicResourceTest)
    result = trialRunner.run(suite)
    sys.exit(not result.wasSuccessful())
