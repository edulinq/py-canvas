import sys

import canvas.api.group.listgroupings
import canvas.cli.common
import canvas.config

DEFAULT_TABLE = False
DEFAULT_SKIP_HEADERS = False

OUTPUT_KEYS = [
    ('name', 'name', 'Name'),
    ('id', 'canvas_id', 'Canvas ID'),
]

def run_cli(table = DEFAULT_TABLE, skip_headers = DEFAULT_SKIP_HEADERS, **kwargs):
    groupings = canvas.api.group.listgroupings.request(**kwargs)

    return canvas.cli.common.cli_list(groupings, OUTPUT_KEYS,
            table = table, skip_headers = skip_headers,
            collective_name = 'groupings', sort_key = 'name',
            **kwargs)

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = ('List groupings in a course.'
        + ' Canvas also calls groupings ("Group Sets" or "Group Categories").'
        + ' This does not list group(ing) membership.')

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers when outputting as a table (default: %(default)s).')

    group = parser.add_mutually_exclusive_group()

    group.add_argument('-t', '--table', dest = 'table',
        action = 'store_true', default = DEFAULT_TABLE,
        help = 'Output the results as a TSV table with a header (default: %(default)s).')

    group.add_argument('--json',action = 'store_true',
        help = 'Output in JSON format instead of TSV')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
