import json
import sys

DEFAULT_JSON = False
DEFAULT_TABLE = False

# keys: [(items key, title, pretty title), ...]
def cli_list(items, keys, table = DEFAULT_TABLE, skip_headers = False,
        collective_name = 'items', sort_key = 'id', output_json = DEFAULT_JSON):
    if (len(items) == 0):
        print("No %s found." % (collective_name), file = sys.stderr)
        return 0

    items = list(sorted(items, key=lambda item: item.get(sort_key, '')))

    processed_items = []
    for item in items:
        values = {}

        for items_key, _, _ in keys:
            value = item[items_key]
            if (value is None):
                value = ''

            if (output_json):
                values[items_key] = value
            else:
                values[items_key] = str(value).strip()

        processed_items.append(values)

    if (output_json):
        print(json.dumps(processed_items, indent = 4, sort_keys = True))
    else:
        if (table and (not skip_headers)):
            print("\t".join([key_set[1] for key_set in keys]))

        for i, values in enumerate(processed_items):
            if (table):
                print("\t".join(map(_clean_cell, [values[key_set[0]] for key_set in keys])))
            else:
                if (i != 0):
                    print()

                for key_set in keys:
                    print("%s: %s" % (key_set[2], values[key_set[0]]))

    return 0

def _clean_cell(text):
    """
    Clean the text that will be in a TSV cell.
    """

    return str(text).replace("\t", " ").replace("\n", " ")

def add_output_args(parser):
    group = parser.add_mutually_exclusive_group()

    group.add_argument('-t', '--table', dest = 'table',
        action = 'store_true', default = DEFAULT_TABLE,
        help = 'Output the results as a TSV table with a header (default: %(default)s).')

    group.add_argument('--json', dest = 'output_json',
        action = 'store_true', default = DEFAULT_JSON,
        help = 'Output in JSON format instead of TSV')
