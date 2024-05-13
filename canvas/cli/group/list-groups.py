import sys

import canvas.api.group.listgroups
import canvas.cli.common
import canvas.config

DEFAULT_TABLE = False
DEFAULT_SKIP_HEADERS = False

OUTPUT_KEYS = [
    ('name', 'name', 'Name'),
    ('id', 'canvas_id', 'Canvas ID'),
]

def run_cli(table = DEFAULT_TABLE, skip_headers = DEFAULT_SKIP_HEADERS, **kwargs):
    groups = canvas.api.group.listgroups.request(**kwargs)

    return canvas.cli.common.cli_list(groups, OUTPUT_KEYS,
            table = table, skip_headers = skip_headers,
            collective_name = 'groups', sort_key = 'name')

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List groups withing a grouping in a course.'

    parser.add_argument('-t', '--table', dest = 'table',
        action = 'store_true', default = DEFAULT_TABLE,
        help = 'Output the results as a TSV table with a header (default: %(default)s).')

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers when outputting as a table (default: %(default)s).')

    parser.add_argument('grouping',
        action = 'store', type = str, nargs = '?', default = None,
        help = ('The optional query for the grouping (aka "group set" or "group category") to list.'
                + ' If not provided, all groups in the course will be listed.'))

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
