import logging
import re

def fetch_and_resolve(server, token, course, queries,
        list_function, list_function_kwargs = {},
        keys = None, resolve_kwargs = {}):
    course_items = list_function(server = server, token = token, course = course, keys = None, **list_function_kwargs)

    items = resolve(queries, course_items, **resolve_kwargs)

    if (keys is None):
        return items

    result = []
    for item in items:
        if (item is None):
            result.append(None)
        else:
            result.append({key: item.get(key, None) for key in keys})

    return result

def resolve(queries, course_items, fill_missing = False,
        label_uses_email = True,
        match_email = True, match_name = True):
    """
    Try to match each query to an actual course item.

    If |fill_missing| is True, then missing (unresolved) items will be replaced with a None.
    This means that the returned results will always be the same size as the input queries.

    If the label does not use email (label_uses_email == False),
    then it must use name.
    """

    items = []

    for query in queries:
        id = None
        email = None
        name = None

        # Clean whitespace.
        query = re.sub(r'\s+', ' ', str(query)).strip()
        if (query == ''):
            continue

        match = re.search(r'^(\S.*)\((\d+)\)$', query)
        if (match is not None):
            label_text = match.group(1).strip()
            id = match.group(2)

            if (label_uses_email):
                email = label_text
            else:
                name = label_text
        elif (re.search(r'^\d+$', query) is not None):
            # Query must be an ID.
            id = query
        elif ('@' in query):
            # Query should be an email.
            email = query
        else:
            # Otherwise, query must be a name.
            name = query

        found_items = {}
        for item in course_items:
            if ('id' not in item):
                raise ValueError("Could not find id field in item ('%s')." % (str(item.keys())))
            item_id = item['id']

            if ((id is not None) and (item_id == id)):
                found_items[item_id] = item

            if (match_email and (email is not None)):
                emails = [
                    item.get('email', ''),
                    item.get('login_id', ''),
                ]

                if (email in emails):
                    found_items[item_id] = item

            if (match_name and (name is not None)):
                names = [
                    item.get('name', ''),
                    item.get('sortable_name', ''),
                    item.get('short_name', ''),
                ]

                if (name in names):
                    found_items[item_id] = item

        if (len(found_items) == 0):
            logging.warning("No item found that matches item query: '%s'." % (query))

            if (fill_missing):
                items.append(None)
        elif (len(found_items) > 1):
            labels = ["%s (%s)" % (str(item.get('email', '')), str(item.get('id', ''))) for item in found_items.values()]
            logging.warning("Query ('%s') matches multiple items: '%s'." % (query, labels))

            if (fill_missing):
                items.append(None)
        else:
            items.append(list(found_items.values())[0])

    return items

def requires_resolution(items):
    """
    Does this list of queries require resolution?
    I.E., does the list only contain Canvas IDs?
    """

    for item in items:
        if (re.search(r'^\s*\d+\s*$', str(item)) is None):
            return True

    return False
