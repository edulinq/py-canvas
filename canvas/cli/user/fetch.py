import sys

import canvas.api.user.fetch
import canvas.cli.common
import canvas.cli.user.common
import canvas.config

DEFAULT_TABLE = False
DEFAULT_SKIP_HEADERS = False

def run_cli(user = None, table = DEFAULT_TABLE, skip_headers = DEFAULT_SKIP_HEADERS, **kwargs):
    user = canvas.api.user.fetch.request(users = [user], **kwargs)

    return canvas.cli.common.cli_list(user, canvas.cli.user.common.OUTPUT_KEYS,
            table = table, skip_headers = skip_headers,
            collective_name = 'user', sort_key = 'email')

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'Fetch information for a user.'

    parser.add_argument('-t', '--table', dest = 'table',
        action = 'store_true', default = DEFAULT_TABLE,
        help = 'Output the results as a TSV table with a header (default: %(default)s).')

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers when outputting as a table (default: %(default)s).')

    parser.add_argument('user',
        action = 'store', type = str,
        help = 'The query for the user to fetch information about.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
