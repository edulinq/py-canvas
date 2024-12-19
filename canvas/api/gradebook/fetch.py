import logging

import canvas.api.assignment.list
import canvas.api.common
import canvas.api.user.common
import canvas.api.user.list
import canvas.api.user.resolve

BASE_ENDPOINT = "/api/v1/courses/{course}/students/submissions?per_page={page_size}"

# Get the current grades for all users/assignments.
# A count of all submissions will be returned for each assignment.
# Users will have a None for unsubmitted assignments.
# Return: (
#   {assignment_id: {id: <id>, name: <name>, assignment_group_id: <id>, count: <int>, position: <int>}, ...},
#   {user_email: {assignment_id: score, ...}, ...},
# )
def request(server = None, token = None, course = None,
        user_queries = [],
        include_computed_scores = False,
        **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    users = _fetch_users(server, token, course, user_queries, include_computed_scores)
    assignments = _fetch_assignments(server, token, course)

    logging.info("Fetching gradebook for course '%s' from '%s'." % (str(course), server))

    url = server + BASE_ENDPOINT.format(course = course, page_size = canvas.api.common.DEFAULT_PAGE_SIZE)
    headers = canvas.api.common.standard_headers(token)

    if (len(user_queries) == 0):
        url += "&student_ids[]=all"
    else:
        for user in users.values():
            url += "&student_ids[]=%s" % (user['id'])

    # {user_email: {assignment_id: score, ...}, ...}
    grades = {}

    while (url is not None):
        _, url, items = canvas.api.common.make_get_request(url, headers)

        for item in items:
            user_id = item.get('user_id', None)
            if (user_id is None):
                continue

            if (user_id not in users):
                continue

            user_email = users[user_id]['email']

            assignment_id = item.get('assignment_id', None)
            if (assignment_id is None):
                continue

            if (assignment_id not in assignments):
                continue

            assignment_name = assignments[assignment_id]['name']

            score = item.get('score', None)
            if (score is not None):
                score = float(score)

            if (user_email not in grades):
                grades[user_email] = {}

            if (score is not None):
                assignments[assignment_id]['count'] += 1

            grades[user_email][assignment_id] = score

    # Add computed scores.
    if (include_computed_scores):
        assignments, grades = _add_computed_scores(users, assignments, grades)

    return assignments, grades

def _fetch_users(server, token, course, user_queries, include_computed_scores):
    extra_args = {}
    if (include_computed_scores):
        extra_args = {
            'keys': None,
            'include_role': True,
        }

    if (len(user_queries) == 0):
        users = canvas.api.user.list.request(server = server, token = token, course = course,
            keys = None, include_role = True)
    else:
        users = canvas.api.user.resolve.fetch_and_resolve_users(server, token, course, user_queries,
            keys = None, include_role = True)

    if (len(users) == 0):
        raise ValueError("Could not find any users for the gradebook.")

    return {user['id']: user for user in users}

def _fetch_assignments(server, token, course):
    assignments = canvas.api.assignment.list.request(server = server, token = token, course = course)
    for assignment in assignments:
        assignment['count'] = 0

    return {assignment['id']: assignment for assignment in assignments}

def _add_computed_scores(users, assignments, grades):
    for i in range(len(canvas.api.user.common.COMPUTED_SCORE_KEYS)):
        key = canvas.api.user.common.COMPUTED_SCORE_KEYS[i]
        assignment_id = f"_computed_{i + 1}_"

        assignments[assignment_id] = {
            'id': f"{assignment_id}",
            'name': key,
            'assignment_group_id': '999999999',
            'count': 0,
            'position': 999999990 + i,
        }

    for user in users.values():
        if (user['email'] not in grades):
            continue

        for i in range(len(canvas.api.user.common.COMPUTED_SCORE_KEYS)):
            key = canvas.api.user.common.COMPUTED_SCORE_KEYS[i]
            score = user.get(key, None)

            assignment_id = f"_computed_{i + 1}_"
            grades[user['email']][assignment_id] = score

            if (score is not None):
                assignments[assignment_id]['count'] += 1

    return assignments, grades
