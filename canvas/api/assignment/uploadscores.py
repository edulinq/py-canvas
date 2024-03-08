import logging
import requests

import canvas.api.assignment.resolve
import canvas.api.common
import canvas.api.user.resolve

BASE_ENDPOINT = "/api/v1/courses/{course}/assignments/{assignment}/submissions/update_grades"

def request(server = None, token = None, course = None, assignment = None,
        users = [], scores = [], comments = [],
        **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)
    assignment = canvas.api.common.validate_param(assignment, 'assignment')

    logging.info("Uploading %d scores for assignement ('%s' (course '%s')) from '%s'." % (len(users), assignment, str(course), server))

    if (canvas.api.assignment.resolve.requires_resolution([assignment])):
        resolved_assignments = canvas.api.assignment.resolve.fetch_and_resolve_assignments(server, token, course, [assignment])
        if (len(resolved_assignments) == 0):
            raise ValueError("Unable to resolve assignment query '%s'." % (assignment))

        assignment = resolved_assignments[0]['id']

    if (canvas.api.user.resolve.requires_resolution(users)):
        resolved_users = canvas.api.user.resolve.fetch_and_resolve_users(server, token, course, users)
        users = [resolved_user['id'] for resolved_user in resolved_users]

    if ((len(users) != len(scores)) or (len(users) != len(comments))):
        raise ValueError("Mismatched count of users (%d), scores (%d), and comments (%d)." % (len(users), len(scores), len(comments)))

    if (len(users) == 0):
        return False

    data = {}
    for i in range(len(users)):
        data["grade_data[%s][posted_grade]" % (users[i])] = scores[i]

        if (comments[i] is None):
            continue

        comment = comments[i].strip()
        if (comment == ''):
            continue

        data["grade_data[%s][text_comment]" % (users[i])] = comment

    url = server + BASE_ENDPOINT.format(course = course, assignment = assignment)
    headers = canvas.api.common.standard_headers(token)

    response = requests.post(url, headers = headers, data = data)
    response.raise_for_status()

    return True
