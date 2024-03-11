import glob
import json
import importlib
import os

import tests.server.base

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
TEST_CASES_DIR = os.path.join(THIS_DIR, "test_cases")

class APITest(tests.server.base.ServerBaseTest):
    """
    Test API calls by mocking a server.
    """

    def _get_test_info(self, path):
        with open(path, 'r') as file:
            data = json.load(file)

        parts = data['endpoint'].split('/')
        prefix = parts[0]
        suffix = ''.join(parts[1:])

        module_name = '.'.join(['canvas', 'api', prefix, suffix])

        expected = data['expected']
        is_error = data.get('error', False)

        arguments = self.get_base_arguments()
        for key, value in data.get('arguments', {}).items():
            arguments[key] = value

        output_modifier = clean_output_noop
        if ('output-modifier' in data):
            modifier_name = data['output-modifier']
            if (modifier_name not in globals()):
                raise ValueError("Could not find API '%s' function: '%s'." % ('output-modifier', modifier_name))

            output_modifier = globals()[modifier_name]

        return module_name, arguments, expected, is_error, output_modifier

def _discover_test_cases():
    for path in sorted(glob.glob(os.path.join(TEST_CASES_DIR, "**", "*.json"), recursive = True)):
        try:
            _add_test_case(path)
        except Exception as ex:
            raise ValueError("Failed to parse test case '%s'." % (path)) from ex

def _add_test_case(path):
    test_name = 'test_' + os.path.splitext(os.path.basename(path))[0]
    setattr(APITest, test_name, _get_test_method(path))

def _get_test_method(path):
    def __method(self):
        module_name, arguments, expected, is_error, output_modifier = self._get_test_info(path)

        module = importlib.import_module(module_name)

        try:
            actual = module.request(**arguments)
            if (isinstance(actual, tuple)):
                actual = list(actual)

            if (is_error):
                self.fail("No error was not raised when one was expected ('%s')." % (str(expected)))
        except Exception as ex:
            if (not is_error):
                raise ex

            self.assertEqual(expected, str(ex))
            return

        actual = output_modifier(actual)

        self.assertJSONEqual(expected, actual)

    return __method

def clean_output_noop(output):
    return output

_discover_test_cases()
