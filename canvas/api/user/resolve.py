import logging
import re

import canvas.api.user.common
import canvas.api.user.list

def fetch_and_resolve_users(server, token, course, user_queries,
        keys = canvas.api.user.common.DEFAULT_KEYS, include_role = False):
    course_users = canvas.api.user.list.request(server = server, token = token,
            course = course, include_role = include_role, keys = None)

    users = resolve_users(user_queries, course_users)

    if (keys is None):
        return users

    return [{key: user[key] for key in keys} for user in users]

def resolve_users(user_queries, course_users, id_field = 'id'):
    """
    Try to match each user query to an acutal user.
    """

    users = []

    for query in user_queries:
        id = None
        email = None
        name = None

        # Clean whitespace.
        query = re.sub(r'\s+', ' ', str(query)).strip()
        if (query == ''):
            continue

        match = re.search(r'^(\S.*)\((\d+)\)$', query)
        if (match is not None):
            email = match.group(1).strip()
            id = match.group(2)
        elif (re.search(r'^\d+$', query) is not None):
            # Query must be an ID.
            id = query
        elif ('@' in query):
            # Query should be an email.
            email = query
        else:
            # Otherwise, query must be a name.
            name = query

        found_users = {}
        for user in course_users:
            if (id_field not in user):
                raise ValueError("Could not find id field '%s' in user ('%s')." % (id_field, str(user.keys())))
            user_id = user[id_field]

            if ((id is not None) and (user.get('id', '') == id)):
                found_users[user_id] = user

            if (email is not None):
                emails = [
                    user.get('email', ''),
                    user.get('login_id', ''),
                ]

                if (email in emails):
                    found_users[user_id] = user

            if (name is not None):
                names = [
                    user.get('name', ''),
                    user.get('sortable_name', ''),
                    user.get('short_name', ''),
                ]

                if (name in names):
                    found_users[user_id] = user

        if (len(found_users) == 0):
            logging.warning("No user found that matches user query: '%s'." % (query))
        elif (len(found_users) > 1):
            labels = ["%s (%s)" % (str(user.get('email', '')), str(user.get('id', ''))) for user in found_users.values()]
            logging.warning("User query ('%s') matches multiple users: '%s'." % (query, labels))
        else:
            users.append(list(found_users.values())[0])

    return users

def requires_resolution(users):
    """
    Does this list of users require resolution?
    I.E., does the list only contain user IDs?
    """

    for user in users:
        if (re.search(r'^\s*\d+\s*$', str(user)) is None):
            return True

    return False
