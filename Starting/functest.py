from main import app as tested_app
import unittest
import json
from webtest import TestApp
import os


_404 = (
    "The requested URL was not found on the server. "
    "If you entered the URL manually please check your "
    "spelling and try again."
)


class TestMyApp(unittest.TestCase):

    def setUp(self):
        self.app = tested_app.test_client()

    def test_help(self):
        hello = self.app.get("/api")
        body = json.loads(str(hello.data, "utf8"))
        self.assertEqual(body["Hello"], "Anonymous")

    def test_raise(self):
        pass

    def test_404(self):
        hello = self.app.get("/boo")
        self.assertEqual(hello.status_code, 404)

    def test_help_webtest(self):
        # by WebTest
        app = TestApp(tested_app)
        hello = app.get("/api")
        self.assertEqual(hello.json["Hello"], "Anonymous")


class TestWithWSGIProxy2(unittest.TestCase):

    def setUp(self):
        http_server = os.environ.get("HTTP_SERVER")
        if http_server is not None:
            from webtest import TestApp
            self.app = TestApp(http_server)
        else:
            from main import app
            from webtest import TestApp
            self.app = TestApp(app)

    def test_help(self):
        hello = self.app.get("/api")
        self.assertEqual(hello.json["Hello"], "Anonymous")


if __name__ == "__main__":
    unittest.main()
