import logging

import canvas.api.common

BASE_ENDPOINT = "/api/v1/courses/{course}/assignments?per_page={page_size}"

DEFAULT_KEYS = [
    'id',
    'name',
    'points_possible',
    'published',
    'due_at',
    'assignment_group_id',
    'position',
    'description',
]

def request(server = None, token = None, course = None,
        page_size = canvas.api.common.DEFAULT_PAGE_SIZE,
        keys = DEFAULT_KEYS, **kwargs):
    """
    Perform a request for assignments from Canvas.

    keys defines the keys from the assignment object that will be returned.
    Set to None for all keys.
    """

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
            if (keys is not None):
                new_assignment = {key: new_assignment[key] for key in keys}

            assignments.append(new_assignment)

    return assignments
