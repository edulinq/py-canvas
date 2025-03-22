import sys

import canvas.api.group.listgroupingmembership
import canvas.cli.common
import canvas.config

DEFAULT_JSON = False
DEFAULT_TABLE = False
DEFAULT_SKIP_HEADERS = False

OUTPUT_KEYS = [
    ('group_name', 'group_name', 'Group Name'),
    ('canvas_group_id', 'group_id', 'Canvas Group ID'),
    ('email', 'email', 'Email'),
]

def run_cli(table = DEFAULT_TABLE, skip_headers = DEFAULT_SKIP_HEADERS,
        output_json = DEFAULT_JSON, **kwargs):
    groups = canvas.api.group.listgroupingmembership.request(**kwargs)

    return canvas.cli.common.cli_list(groups, OUTPUT_KEYS,
            table = table, skip_headers = skip_headers,
            collective_name = 'groups', sort_key = 'name',
            output_json = output_json)

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List the membership of all groups within a grouping.'

    canvas.cli.common.add_output_args(parser)

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers when outputting as a table (default: %(default)s).')

    parser.add_argument('grouping',
        action = 'store', type = str,
        help = 'The query for the grouping (aka "group set" or "group category") to list.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
