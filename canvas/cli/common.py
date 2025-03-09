import sys
import json

# keys: [(items key, title, pretty title), ...]
def cli_list(items, keys, table = False, skip_headers = False,
        collective_name = 'items', sort_key = 'id',
        **kwargs):
    if (len(items) == 0):
        print("No %s found." % (collective_name), file = sys.stderr)
        return 0

    items = list(sorted(items, key = lambda item: item.get(sort_key, '')))
    
    if kwargs.get('json', False):
        _output_json(items, keys, skip_headers)
    else:
        _output_tsv(items, keys, table, skip_headers)

    return 0

def _output_json(items, keys, skip_headers = False):
    json_data = []
    for item in items:
        values = {}
        for items_key, _, pretty_title in keys:
            value = item.get(items_key, '')
            if value is None:
                value = ''
            values[pretty_title if not skip_headers else items_key] = str(value).strip()
        json_data.append(values)
    print(json.dumps(json_data, indent=2))

def _output_tsv(items, keys, table = False, skip_headers = False):
    if (table and (not skip_headers)):
            print("\t".join([key_set[1] for key_set in keys]))

    for i in range(len(items)):
        item = items[i]

        values = {}
        for items_key, _, _ in keys:
            value = item[items_key]
            if (value is None):
                value = ''

            values[items_key] = str(value).strip()

        if (table):
            print("\t".join(map(_clean_cell, [values[key_set[0]] for key_set in keys])))
        else:
            if (i != 0):
                print()

            for key_set in keys:
                print("%s: %s" % (key_set[2], values[key_set[0]]))


def _clean_cell(text):
    """
    Clean the text that will be in a TSV cell.
    """

    return str(text).replace("\t", " ").replace("\n", " ")
