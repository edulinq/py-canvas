import logging

import canvas.api.common

BASE_ENDPOINT = "/api/v1/courses/{course}/assignments?per_page={page_size}"

def request(server = None, token = None, course = None,
        page_size = canvas.api.common.DEFAULT_PAGE_SIZE, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    logging.info("Fetching course ('%s') assignments from '%s'." % (str(course), server))

    url = server + BASE_ENDPOINT.format(course = course, page_size = page_size)
    headers = canvas.api.common.standard_headers(token)

    assignments = []

    while (url is not None):
        _, url, new_assignments = canvas.api.common.make_get_request(url, headers)

        for new_assignment in new_assignments:
            assignments.append(new_assignment)

    return assignments
