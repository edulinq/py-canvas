import glob
import os
import unittest

import canvas.util.code

THIS_DIR = os.path.abspath(os.path.dirname(os.path.realpath(__file__)))
ROOT_DIR = os.path.join(THIS_DIR, "..")
CLI_DIR = os.path.join(ROOT_DIR, "canvas", "cli")

SKIP_BASENNAMES = ['__init__', '__main__']

class CLITest(unittest.TestCase):
    """
    Trivially test all the CLI executables by importing them.
    """

    pass

def _discover_cli_tests():
    for path in sorted(glob.glob(os.path.join(CLI_DIR, "**", "*.py"), recursive = True)):
        try:
            _add_cli_test(path)
        except Exception as ex:
            raise ValueError("Failed to parse test case '%s'." % (path)) from ex

def _add_cli_test(path):
    basename = os.path.splitext(os.path.basename(path))[0]
    if (basename in SKIP_BASENNAMES):
        return

    relpath = os.path.relpath(path, CLI_DIR)
    test_basename = '.'.join(os.path.splitext(relpath)[0].split('/'))

    test_name = 'test_cli_import_%s' % (test_basename)

    cli_module = canvas.util.code.import_path(path)
    if ('run_cli' not in dir(cli_module)):
        return

    setattr(CLITest, test_name, _get_cli_test_method(path))

def _get_cli_test_method(path):
    def __method(self):
        canvas.util.code.import_path(path)

    return __method

_discover_cli_tests()
