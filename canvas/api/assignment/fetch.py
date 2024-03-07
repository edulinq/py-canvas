import logging

import canvas.api.assignment.common
import canvas.api.assignment.resolve
import canvas.api.common

BASE_ENDPOINT = "/api/v1/courses/{course}/assignments?per_page={page_size}"

def request(server = None, token = None, course = None,
        assignments = [],
        keys = canvas.api.assignment.common.DEFAULT_KEYS, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    logging.info("Fetching course ('%s') assignments ('%s') from '%s'." % (
            str(course), ', '.join(map(str, assignments)), server))

    if (len(assignments) == 0):
        return []

    if (canvas.api.assignment.resolve.requires_resolution(assignments)):
        return canvas.api.assignment.resolve.fetch_and_resolve_assignments(
                server, token, course, assignments,
                keys = keys)

    url = server + BASE_ENDPOINT.format(course = course, page_size = canvas.api.common.DEFAULT_PAGE_SIZE)
    headers = canvas.api.common.standard_headers(token)

    for assignment in assignments:
        url += "&assignment_ids[]=%s" % (str(assignment))

    return canvas.api.assignment.common.list_assignments(url, headers, keys)
