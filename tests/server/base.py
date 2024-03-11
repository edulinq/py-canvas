import json
import unittest
import sys

import tests.server.server

SERVER_URL = "http://127.0.0.1:%s" % (tests.server.server.PORT)
FORMAT_STR = "\n--- Expected ---\n%s\n--- Actual ---\n%s\n---\n"

BASE_ARGUMENTS = {
    'server': SERVER_URL,
    'token': 'abc123',
    'course': 12345,
}

@unittest.skipUnless(sys.platform.startswith('linux'), 'linux only (multiprocessing)')
class ServerBaseTest(unittest.TestCase):
    """
    A base tests that need to call the mock server.
    """

    _server_process = None

    @classmethod
    def setUpClass(cls):
        cls._server_process = tests.server.server.start()

    @classmethod
    def tearDownClass(cls):
        tests.server.server.stop(cls._server_process)
        cls._server_process = None

    def get_base_arguments(self):
        return BASE_ARGUMENTS.copy()

    def assertJSONEqual(self, a, b):
        a_json = json.dumps(a, indent = 4)
        b_json = json.dumps(b, indent = 4)

        super().assertEqual(a, b, FORMAT_STR % (a_json, b_json))
