from main import app as tested_app
import unittest
import json


_404 = (
    "The requested URL was not found on the server. "
    "If you entered the URL manually please check your "
    "spelling and try again."
)


class TestApp(unittest.TestCase):

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


if __name__ == "__main__":
    unittest.main()
