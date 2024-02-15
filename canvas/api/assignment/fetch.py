import logging

import canvas.api.assignment.common
import canvas.api.common

BASE_ENDPOINT = "/api/v1/courses/{course}/assignments/{assignment}"

def request(server = None, token = None, course = None, assignment = None,
        keys = canvas.api.assignment.common.DEFAULT_KEYS, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)
    assignment = canvas.api.common.validate_param(assignment, 'assignment', param_type = int)

    logging.info("Fetching course ('%s') assignment ('%s') from '%s'." % (
            str(course), str(assignment), server))

    url = server + BASE_ENDPOINT.format(course = course, assignment = assignment)
    headers = canvas.api.common.standard_headers(token)

    _, _, new_assignment = canvas.api.common.make_get_request(url, headers)

    if (keys is not None):
        new_assignment = {key: new_assignment[key] for key in keys}

    return new_assignment
