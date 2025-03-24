import sys

import canvas.api.group.listgroupmembers
import canvas.cli.common
import canvas.config

DEFAULT_SKIP_HEADERS = False

OUTPUT_KEYS = [
    ('login_id', 'email', 'Email'),
    ('name', 'name', 'Name'),
    ('id', 'canvas_id', 'Canvas ID'),
    ('sis_user_id', 'student_id', 'Student ID'),
]

def run_cli(table = canvas.cli.common.DEFAULT_TABLE, skip_headers = DEFAULT_SKIP_HEADERS,
        output_json = canvas.cli.common.DEFAULT_JSON, **kwargs):
    users = canvas.api.group.listgroupmembers.request(**kwargs)

    return canvas.cli.common.cli_list(users, OUTPUT_KEYS,
            table = table, skip_headers = skip_headers,
            collective_name = 'users', sort_key = 'name',
            output_json = output_json)

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List the members of a single group.'

    canvas.cli.common.add_output_args(parser)

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers when outputting as a table (default: %(default)s).')

    parser.add_argument('group',
        action = 'store', type = str,
        help = 'The query for the group to list.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
