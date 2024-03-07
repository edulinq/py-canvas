import sys

import canvas.api.assignment.fetch
import canvas.cli.assignment.common
import canvas.cli.common
import canvas.config

DEFAULT_TABLE = False
DEFAULT_SKIP_HEADERS = False
DEFAULT_SKIP_DESCRIPTION = False

def run_cli(assignment = None, table = DEFAULT_TABLE, skip_headers = DEFAULT_SKIP_HEADERS,
        skip_description = DEFAULT_SKIP_DESCRIPTION, **kwargs):
    raw_assignments = []
    if (assignment is not None):
        raw_assignments.append(assignment)

    assignments = canvas.api.assignment.fetch.request(assignments = raw_assignments, **kwargs)

    keys = canvas.cli.assignment.common.OUTPUT_KEYS.copy()
    if (skip_description):
        keys = keys[:-1]

    return canvas.cli.common.cli_list(assignments, keys,
            table = table, skip_headers = skip_headers,
            collective_name = 'assignment', sort_key = 'name')

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'Fetch information for an assignment.'

    parser.add_argument('-t', '--table', dest = 'table',
        action = 'store_true', default = DEFAULT_TABLE,
        help = 'Output the results as a TSV table with a header (default: %(default)s).')

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers when outputting as a table (default: %(default)s).')

    parser.add_argument('--skip-description', dest = 'skip_description',
        action = 'store_true', default = DEFAULT_SKIP_DESCRIPTION,
        help = 'Skip outputting the assignment description (default: %(default)s).')

    parser.add_argument('assignment',
        action = 'store', type = str,
        help = 'The query for the assignment to fetch information about.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
