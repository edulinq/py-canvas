import logging
import requests

import canvas.api.common

BASE_ENDPOINT = "/api/v1/courses/%%s/users?include[]=enrollments&per_page=%d" % (canvas.api.common.DEFAULT_PAGE_SIZE)

def request(server = None, token = None, course = None, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    logging.debug("Fetching course ('%s') users from '%s'." % (str(course), server))

    url = server + BASE_ENDPOINT % (course)
    headers = canvas.api.common.standard_headers(token)

    users = []

    while (url is not None):
        logging.debug("Making request: '%s'." % (url))
        response = requests.get(url, headers = headers)
        response.raise_for_status()

        url = canvas.api.common.fetch_next_canvas_link(response.headers)
        new_users = response.json()

        for new_user in new_users:
            raw_enrollments = new_user.get('enrollments', [])
            enrollment_types = [raw_enrollment.get('role') for raw_enrollment in raw_enrollments]
            new_user['enrollment'] = canvas.api.common.get_max_enrollment_type(enrollment_types)

            users.append(new_user)

    return users
