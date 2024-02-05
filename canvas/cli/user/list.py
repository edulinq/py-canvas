import sys

import canvas.api.user.list
import canvas.config

DEFAULT_TABLE = False
DEFAULT_SKIP_HEADERS = False

# [(title, canvas key, pretty title), ...]
HEADERS = [
    ('email', 'email', 'Email'),
    ('name', 'name', 'Name'),
    ('role', 'enrollment', 'Course Role'),
    ('canvas_id', 'id', 'Canvas ID'),
    ('student_id', 'sis_user_id', 'Student ID'),
]

def run_cli(table = DEFAULT_TABLE, skip_headers = DEFAULT_SKIP_HEADERS, **kwargs):
    users = canvas.api.user.list.request(**kwargs)

    if (len(users) == 0):
        print("No users found.", file = sys.stderr)
        return 0

    if (table and (not skip_headers)):
        print("\t".join([header[0] for header in HEADERS]))

    users = list(sorted(users, key = lambda user: user.get('email')))
    for i in range(len(users)):
        user = users[i]

        values = {}
        for _, key, _ in HEADERS:
            value = user[key]

            if (value is None):
                value = ''

            values[key] = str(value).strip()

        if (table):
            print("\t".join(map(str, [values[header[1]] for header in HEADERS])))
        else:
            if (i != 0):
                print()

            for header in HEADERS:
                print("%s: %s" % (header[2], values[header[1]]))

    return 0

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List users in a course.'

    parser.add_argument('-t', '--table', dest = 'table',
        action = 'store_true', default = DEFAULT_TABLE,
        help = 'Output the results as a TSV table with a header (default: %(default)s).')

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers when outputting as a table (default: %(default)s).')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
