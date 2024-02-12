import logging
import requests

import canvas.api.common

BASE_ENDPOINT = "/api/v1/courses/%%s/students/submissions?per_page=%d&include[]=user&include[]=assignment" % (canvas.api.common.DEFAULT_PAGE_SIZE)

# Get the current grades for all users/assignments.
# A count of all submissions will be returned for each assignment.
# Users will have a None for unsubmitted assignments.
# Return: (
#   {assignment_id: {id: <id>, name: <name>, group_id: <id>, count: <int>, group_position: <int>}, ...},
#   {user_id: {assignment_id: score, ...}, ...},
# )
def request(server = None, token = None, course = None, users = [], **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    logging.debug("Fetching gradebook for course '%s' from '%s'." % (str(course), server))

    url = server + BASE_ENDPOINT % (course)
    headers = canvas.api.common.standard_headers(token)

    if (len(users) == 0):
        url += "&student_ids[]=all"
    else:
        for user in users:
            url += "&student_ids[]=%s" % (user)

    assignments = {}
    grades = {}

    while (url is not None):
        logging.debug("Making request: '%s'." % (url))
        response = requests.get(url, headers = headers)
        response.raise_for_status()

        url = canvas.api.common.fetch_next_canvas_link(response.headers)
        items = response.json()

        for item in items:
            if (('user' not in item) or ('assignment' not in item)):
                continue

            if ((item['user'].get('name', '') == 'Test Student') and (item['user'].get('sis_user_id', None) is None)):
                continue

            user_id = item['user'].get('login_id', None)
            if (user_id is None):
                continue

            assignment_id = item['assignment'].get('id', None)
            assignment_name = item['assignment'].get('name', None)
            assignment_group_id = item['assignment'].get('assignment_group_id', None)
            assignment_group_pos = item['assignment'].get('position', -1)

            if ((assignment_id is None) or (assignment_name is None)):
                continue

            score = item.get('score', None)
            if (score is not None):
                score = float(score)

            if (assignment_id not in assignments):
                assignments[assignment_id] = {
                    'id': assignment_id,
                    'name': assignment_name,
                    'group_id': assignment_group_id,
                    'group_position': assignment_group_pos,
                    'count': 0,
                }

            if (user_id not in grades):
                grades[user_id] = {}

            if (score is not None):
                assignments[assignment_id]['count'] += 1

            grades[user_id][assignment_id] = score

    return assignments, grades
