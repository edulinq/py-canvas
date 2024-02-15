import glob
import json
import importlib
import os
import unittest
import sys

import tests.api.server

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
DATA_DIR = os.path.join(THIS_DIR, "data")
TESTS_DIR = os.path.join(DATA_DIR, "tests")
RESPONSES_DIR = os.path.join(DATA_DIR, "responses")

SERVER_URL = "http://127.0.0.1:%s" % (tests.api.server.PORT)
FORMAT_STR = "\n--- Expected ---\n%s\n--- Actual ---\n%s\n---\n"

BASE_ARGUMENTS = {
    'server': SERVER_URL,
    'token': 'abc123',
    'course': 12345,
    'assignment': 67890,
    'page_size': 95,
}

@unittest.skipUnless(sys.platform.startswith('linux'), 'linux only (multiprocessing)')
class APITest(unittest.TestCase):
    """
    Test API calls by mocking a server.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._server_process = None

    def setUp(self):
        self._server_process = tests.api.server.start(RESPONSES_DIR)

    def tearDown(self):
        tests.api.server.stop(self._server_process)
        self._server_process = None

    def assertJSONEqual(self, a, b):
        a_json = json.dumps(a, indent = 4)
        b_json = json.dumps(b, indent = 4)

        super().assertEqual(a, b, FORMAT_STR % (a_json, b_json))

def _discover_api_tests():
    for path in sorted(glob.glob(os.path.join(TESTS_DIR, "**", "*.json"), recursive = True)):
        try:
            _add_api_test(path)
        except Exception as ex:
            raise ValueError("Failed to parse test case '%s'." % (path)) from ex

def _add_api_test(path):
    test_name = 'test_' + os.path.splitext(os.path.basename(path))[0]
    setattr(APITest, test_name, _get_api_test_method(path))

def get_api_test_info(path):
    with open(path, 'r') as file:
        data = json.load(file)

    parts = data['endpoint'].split('/')
    prefix = parts[0]
    suffix = ''.join(parts[1:])

    import_module_name = '.'.join(['canvas', 'api', prefix, suffix])

    expected = data['expected']

    arguments = BASE_ARGUMENTS.copy()
    for key, value in data.get('arguments', {}).items():
        arguments[key] = value

    output_modifier = clean_output_noop
    if ('output-modifier' in data):
        modifier_name = data['output-modifier']
        if (modifier_name not in globals()):
            raise ValueError("Could not find API '%s' function: '%s'." % ('output-modifier', modifier_name))

        output_modifier = globals()[modifier_name]

    return import_module_name, arguments, expected, output_modifier

def _get_api_test_method(path):
    import_module_name, arguments, expected, output_modifier = get_api_test_info(path)

    def __method(self):
        api_module = importlib.import_module(import_module_name)

        actual = api_module.request(**arguments)
        if (isinstance(actual, tuple)):
            actual = list(actual)

        actual = output_modifier(actual)

        self.assertJSONEqual(expected, actual)

    return __method

def clean_output_noop(output):
    return output

_discover_api_tests()
