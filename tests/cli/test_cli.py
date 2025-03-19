import contextlib
import glob
import json
import importlib
import io
import os
import re
import sys

import tests.server.base
import canvas.util.file

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
TEST_CASES_DIR = os.path.join(THIS_DIR, "test_cases")
DATA_DIR = os.path.join(THIS_DIR, "data")

TEST_CASE_SEP = '---'
DATA_DIR_ID = '__DATA_DIR__'
TEMP_DIR_ID = '__TEMP_DIR__'

DEFAULT_OUTPUT_CHECK = 'content_equals'

class CLITest(tests.server.base.ServerBaseTest):
    """
    Test CLI tools.
    """

    _base_temp_dir = canvas.util.file.get_temp_path('canvas_CLITest_')

    def _get_test_info(self, test_name, path):
        options, expected_output = _read_test_file(path)

        temp_dir = os.path.join(CLITest._base_temp_dir, test_name)

        module_name = options['cli']
        exit_status = options.get('exit_status', 0)
        is_error = options.get('error', False)

        output_check_name = options.get('output-check', DEFAULT_OUTPUT_CHECK)
        if (output_check_name not in globals()):
            raise ValueError("Could not find output check function: '%s'." % (output_check_name))
        output_check = globals()[output_check_name]

        if (is_error):
            expected_output = expected_output.strip()

        arguments = self.get_base_arguments()
        for key, value in options.get('overrides', {}).items():
            arguments[key] = value

        cli_arguments = []

        for key, value in arguments.items():
            cli_arguments += ["--%s" % (str(key)), str(value)]

        cli_arguments += options.get('arguments', [])

        # Make any substitutions.
        expected_output = _prepare_string(expected_output, temp_dir)
        for i in range(len(cli_arguments)):
            cli_arguments[i] = _prepare_string(cli_arguments[i], temp_dir)

        return module_name, cli_arguments, expected_output, output_check, exit_status, is_error

def _prepare_string(text, temp_dir):
    replacements = [
        (DATA_DIR_ID, DATA_DIR),
        (TEMP_DIR_ID, temp_dir),
    ]

    for (key, base_dir) in replacements:
        text = _replace_path(text, key, base_dir)

    return text

def _replace_path(text, key, base_dir):
    match = re.search(r'%s\(([^)]*)\)' % (key), text)
    if (match is not None):
        filename = match.group(1)

        # Normalize any path seperators.
        filename = os.path.join(*filename.split('/'))

        if (filename == ''):
            path = base_dir
        else:
            path = os.path.join(base_dir, filename)

        text = text.replace(match.group(0), path)

    return text

def _read_test_file(path):
    json_lines = []
    output_lines = []

    with open(path, 'r') as file:
        accumulator = json_lines
        for line in file:
            if (line.strip() == TEST_CASE_SEP):
                accumulator = output_lines
                continue

            accumulator.append(line)

    options = json.loads(''.join(json_lines))
    output = ''.join(output_lines)

    return options, output

def _discover_test_cases():
    for path in sorted(glob.glob(os.path.join(TEST_CASES_DIR, "**", "*.txt"), recursive = True)):
        try:
            _add_test_case(path)
        except Exception as ex:
            raise ValueError("Failed to parse test case '%s'." % (path)) from ex

def _add_test_case(path):
    test_name = 'test_cli__' + os.path.splitext(os.path.basename(path))[0]
    setattr(CLITest, test_name, _get_test_method(test_name, path))

def _get_test_method(test_name, path):
    def __method(self):
        module_name, cli_arguments, expected_output, output_check, expected_exit_status, is_error = self._get_test_info(test_name, path)
        module = importlib.import_module(module_name)

        old_args = sys.argv
        sys.argv = [module.__file__] + cli_arguments

        is_json = "--json" in cli_arguments or []

        _test_output(self, module, expected_output, output_check, expected_exit_status, is_error, is_json)

        sys.argv = old_args

    return __method

def _test_output(test_case, module, expected_output, output_check, expected_exit_status, is_error, is_json = False):
    try:
        with contextlib.redirect_stdout(io.StringIO()) as output:
            actual_exit_status = module.main()
        actual_output = output.getvalue()

        if (is_error):
            test_case.fail("No error was raised when one was expected ('%s')" % (expected_output))
    except BaseException as ex:
        if (not is_error):
            raise ex

        if (isinstance(ex, SystemExit)):
            if (ex.__context__ is None):
                test_case.fail("Unexpected exit without context.")

            ex = ex.__context__

        content_equals(test_case, expected_output, str(ex))
        return

    content_equals(test_case, expected_exit_status, actual_exit_status)

    if (is_json is True):
        try:
            expected_json = _sort_and_normalize_json(json.loads(expected_output))
            actual_json = _sort_and_normalize_json(json.loads(actual_output))

            content_equals(test_case, expected_json, actual_json)

        except json.JSONDecodeError as ex:
            test_case.fail("Failed to parse JSON output: '%s'" % (str(ex)))
    else:
        output_check(test_case, expected_output, actual_output)

def _sort_and_normalize_json(json_data):
    if (isinstance(json_data, list)):
        return sorted(
            [_sort_and_normalize_json(item) for item in json_data],
            key = lambda x: x.get('id', '')
        )
    elif (isinstance(json_data, dict)):
        return {k: str(v).strip() for k, v in sorted(json_data.items())}

    return str(json_data).strip()

def content_equals(test_case, expected, actual, **kwargs):
    test_case.assertEqual(expected, actual)

def has_content_100(test_case, expected, actual, **kwargs):
    return has_content(test_case, expected, actual, min_length = 100)

# Ensure that the output has content.
def has_content(test_case, expected, actual, min_length = 100):
    message = "Output does not meet minimum length of %d, it is only %d." % (min_length, len(actual))
    test_case.assertTrue((len(actual) >= min_length), msg = message)

_discover_test_cases()
