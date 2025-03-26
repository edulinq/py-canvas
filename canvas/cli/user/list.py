import sys

import canvas.api.user.list
import canvas.cli.common
import canvas.cli.user.common
import canvas.config

DEFAULT_INCLUDE_ROLE = False

def run_cli(include_role = DEFAULT_INCLUDE_ROLE, **kwargs):
    users = canvas.api.user.list.request(include_role = include_role,
            **kwargs)

    keys = canvas.cli.user.common.OUTPUT_KEYS.copy()
    if (include_role):
        keys.append(canvas.cli.user.common.ENROLLMENT_KEY)

    return canvas.cli.common.cli_list(users, keys, collective_name = 'users',
            sort_key = 'email', **kwargs)

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List users in a course.'

    canvas.cli.common.add_output_args(parser)

    parser.add_argument('--include-role', dest = 'include_role',
        action = 'store_true', default = DEFAULT_INCLUDE_ROLE,
        help = 'Include user\'s role in the course (default: %(default)s).')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
