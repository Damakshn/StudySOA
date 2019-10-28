import unittest
from unittest import mock
import requests
from requests.exceptions import ConnectionError
import requests_mock
from Bugzilla import MyBugzilla


class TestBugzilla(unittest.TestCase):

    def test_bug_id(self):
        zilla = MyBugzilla("someone@mozilla.com", server="http://example.com")
        link = zilla.bug_link(23)
        self.assertEqual(link, "http://example.com/show_bug.cgi?id=23")

    @requests_mock.mock()
    def test_get_new_bugs(self, mocker):
        bugs = [{"id": 12345}, {"id": 54321}]
        mocker.get(requests_mock.ANY, json={"bugs": bugs})
        zilla = MyBugzilla("someone@mozilla.com", server="http://example.com")
        bugs = list(zilla.get_new_bugs())
        self.assertEqual(
            bugs[0]["link"],
            "http://example.com/show_bug.cgi?id=12345"
        )

    @mock.patch.object(requests.Session, "get",
                       side_effect=ConnectionError("No network"))
    def test_network_error(self, mocked):
        zilla = MyBugzilla("someone@mozilla.com", server="http://example.com")
        bugs = list(zilla.get_new_bugs())
        self.assertEqual(len(bugs), 0)


if __name__ == "__main__":
    unittest.main()
