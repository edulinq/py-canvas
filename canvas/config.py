import argparse
import logging
import os
import sys
import urllib.parse

import json5
import platformdirs

import canvas.log

DEFAULT_CONFIG_FILENAME = 'edq-canvas.json'
DEFAULT_USER_CONFIG_PATH = platformdirs.user_config_dir(DEFAULT_CONFIG_FILENAME)

CONFIG_PATHS_KEY = 'config_paths'

REQUIRED_KEYS = ['server', 'token']

def get_config(exit_on_error = False, modify_parser = None, **parser_options):
    """
    Collect config values from files and the command line.
    """

    try:
        return _get_config(modify_parser = modify_parser, **parser_options)
    except Exception as ex:
        if (exit_on_error):
            print("ERROR: " + ex.args[0], file = sys.stderr)
            sys.exit(1)

        raise ValueError("Failed to get config") from ex

def _get_config(modify_parser = None, **parser_options):
    parser = get_argument_parser(**parser_options)

    if (modify_parser is not None):
        modify_parser(parser)

    arguments = parser.parse_args()
    config = get_tiered_config(arguments)

    # Work with and clean standard options,
    canvas.log.init(level = config.get('log_level', canvas.log.DEFAULT_LOGGING_LEVEL))

    for key in REQUIRED_KEYS:
        if (key not in config):
            raise ValueError("Missing required config value: '%s'." % (key))

    try:
        parts = urllib.parse.urlparse(config['server'], scheme = 'https')
        if (parts.netloc != ''):
            config['server'] = parts.geturl()
        else:
            config['server'] = "%s://%s" % (parts.scheme, parts.path)
    except Exception as ex:
        raise ValueError("Failed to parse Canvas server: '%s'." % config['server']) from ex

    return config

def get_tiered_config(cli_arguments, skip_keys = [CONFIG_PATHS_KEY]):
    """
    Get all the tiered configuration options (from files and CLI).
    """

    config = {}

    if (isinstance(cli_arguments, argparse.Namespace)):
        cli_arguments = vars(cli_arguments)

    # Check the current directory config.
    if (os.path.isfile(DEFAULT_CONFIG_FILENAME)):
        with open(DEFAULT_CONFIG_FILENAME, 'r') as file:
            for key, value in json5.load(file).items():
                config[key] = value

    # Check the user config file.
    if (os.path.isfile(DEFAULT_USER_CONFIG_PATH)):
        with open(DEFAULT_USER_CONFIG_PATH, 'r') as file:
            for key, value in json5.load(file).items():
                config[key] = value

    # Check the config files specified on the command-line.
    config_paths = cli_arguments.get(CONFIG_PATHS_KEY, [])
    if (config_paths is not None):
        for path in config_paths:
            with open(path, 'r') as file:
                for key, value in json5.load(file).items():
                    config[key] = value

    # Finally, any command-line options.
    for (key, value) in cli_arguments.items():
        if (key in skip_keys):
            continue

        if ((value is None) or (value == '')):
            continue

        config[key] = value

    return config

def get_argument_parser(description = '', course = True, **kwargs):
    """
    Create an argparse parser that has all the standard options for API requests.
    """

    parser = argparse.ArgumentParser(description = description)

    parser.add_argument('--config', dest = CONFIG_PATHS_KEY,
        action = 'append', type = str,
        help = 'A JSON config file with your submission/authentication details.'
            + " Can be specified multiple times with later values overriding earlier ones."
            + " Config values can be specified in multiple places"
            + " (with later values overriding earlier values):"
            + " First './%s'," % (DEFAULT_CONFIG_FILENAME)
            + " then '%s'," % (DEFAULT_USER_CONFIG_PATH)
            + " now any files specified using --config in the order they were specified,"
            + " and finally any variables specified directly on the command line (like --user).")

    parser.add_argument('--log-level', dest = 'log_level',
        action = 'store', type = str, default = canvas.log.DEFAULT_LOGGING_LEVEL,
        choices = canvas.log.LEVELS,
        help = 'The logging level (default: %(default)s).')

    parser.add_argument('--server', dest = 'server',
        action = 'store', type = str, default = None,
        help = 'The Canvas instance to work with.')

    parser.add_argument('--token', dest = 'token',
        action = 'store', type = str, default = None,
        help = 'A Canvas authentication token.')

    if (course):
        parser.add_argument('--course', dest = 'course',
            action = 'store', type = int, default = None,
            help = 'The Canvas course ID.')

    return parser
