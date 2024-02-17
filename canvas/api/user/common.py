import logging
import re

import canvas.api.common

# Default keys that will be returned with a user.
DEFAULT_KEYS = [
    'id',
    'email',
    'name',
    'enrollment',
    'sis_user_id',
]

def resolve_users(user_queries, course_users,
        id_field = 'id'):
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

        if (re.search(r'^\d+$', query) is not None):
            # Query must be an ID.
            id = int(query)
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

def _list_users(url, headers, keys):
    output = []

    while (url is not None):
        _, url, new_users = canvas.api.common.make_get_request(url, headers)

        for new_user in new_users:
            raw_enrollments = new_user.get('enrollments', [])
            enrollment_types = [raw_enrollment.get('role') for raw_enrollment in raw_enrollments]
            new_user['enrollment'] = canvas.api.common.get_max_enrollment_type(enrollment_types)

            if (keys is not None):
                new_user = {key: new_user[key] for key in keys}

            output.append(new_user)

    return output
