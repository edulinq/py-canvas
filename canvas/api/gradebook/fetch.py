import logging

import canvas.api.assignment.list
import canvas.api.common
import canvas.api.user.list

BASE_ENDPOINT = "/api/v1/courses/{course}/students/submissions?per_page={page_size}"

# Get the current grades for all users/assignments.
# A count of all submissions will be returned for each assignment.
# Users will have a None for unsubmitted assignments.
# Return: (
#   {assignment_id: {id: <id>, name: <name>, assignment_group_id: <id>, count: <int>, position: <int>}, ...},
#   {user_email: {assignment_id: score, ...}, ...},
# )
def request(server = None, token = None, course = None, users = [],
        page_size = canvas.api.common.DEFAULT_PAGE_SIZE, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    all_users = _fetch_users(server, token, course, page_size)
    assignments = _fetch_assignments(server, token, course, page_size)

    logging.info("Fetching gradebook for course '%s' from '%s'." % (str(course), server))

    url = server + BASE_ENDPOINT.format(course = course, page_size = page_size)
    headers = canvas.api.common.standard_headers(token)

    if (len(users) == 0):
        url += "&student_ids[]=all"
    else:
        for user in users:
            url += "&student_ids[]=%s" % (user)

    grades = {}

    while (url is not None):
        _, url, items = canvas.api.common.make_get_request(url, headers)

        for item in items:
            user_id = item.get('user_id', None)
            if (user_id is None):
                continue

            if (user_id not in all_users):
                continue

            user_email = all_users[user_id]['email']

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

    return assignments, grades

def _fetch_users(server, token, course, page_size):
    users = canvas.api.user.list.request(server = server, token = token, course = course,
        page_size = page_size)

    return {user['id']: user for user in users}

def _fetch_assignments(server, token, course, page_size):
    assignments = canvas.api.assignment.list.request(server = server, token = token, course = course,
        page_size = page_size)

    for assignment in assignments:
        assignment['count'] = 0

    return {assignment['id']: assignment for assignment in assignments}
