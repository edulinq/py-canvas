import logging
import requests

import canvas.api.common

BASE_ENDPOINT = "/api/v1/courses/%%s/assignments/%%s/submissions?include[]=user&include[]=assignment&per_page=%d" % (canvas.api.common.DEFAULT_PAGE_SIZE)

def request(server = None, token = None, course = None, assignment = None, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)
    assignment = canvas.api.common.validate_param(assignment, 'assignment', param_type = int)

    logging.debug("Fetching scores for assignement ('%s' (course '%s')) from '%s'." % (str(assignment), str(course), server))

    url = server + BASE_ENDPOINT % (course, assignment)
    headers = canvas.api.common.standard_headers(token)

    submissions = []

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

            if ((assignment_id is None) or (assignment_name is None)):
                continue

            item['user_id'] = user_id
            item['assignment_header'] = "%s (%s)" % (assignment_name, str(assignment_id))

            submissions.append(item)

    return submissions
