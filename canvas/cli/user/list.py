import sys

import canvas.api.user.list
import canvas.cli.common
import canvas.cli.user.common
import canvas.config

DEFAULT_INCLUDE_ROLE = False
DEFAULT_TABLE = False
DEFAULT_SKIP_HEADERS = False

def run_cli(include_role = DEFAULT_INCLUDE_ROLE,
        table = DEFAULT_TABLE, skip_headers = DEFAULT_SKIP_HEADERS,
        **kwargs):
    users = canvas.api.user.list.request(include_role = include_role,
            **kwargs)

    keys = canvas.cli.user.common.OUTPUT_KEYS.copy()
    if (include_role):
        keys.append(canvas.cli.user.common.ENROLLMENT_KEY)

    return canvas.cli.common.cli_list(users, keys,
            table = table, skip_headers = skip_headers,
            collective_name = 'users', sort_key = 'email')

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List users in a course.'

    parser.add_argument('--include-role', dest = 'include_role',
        action = 'store_true', default = DEFAULT_INCLUDE_ROLE,
        help = 'Include user\'s role in the course (default: %(default)s).')

    parser.add_argument('-t', '--table', dest = 'table',
        action = 'store_true', default = DEFAULT_TABLE,
        help = 'Output the results as a TSV table with a header (default: %(default)s).')

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers when outputting as a table (default: %(default)s).')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
