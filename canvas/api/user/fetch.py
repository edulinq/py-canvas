import logging

import canvas.api.common
import canvas.api.user.common

BASE_ENDPOINT = "/api/v1/courses/{course}/users?include[]=enrollments&per_page={page_size}"

DEFAULT_KEYS = [
    'id',
    'email',
    'name',
    'enrollment',
    'sis_user_id',
]

def request(server = None, token = None, course = None,
        users = [],
        page_size = canvas.api.common.DEFAULT_PAGE_SIZE,
        keys = canvas.api.user.common.DEFAULT_KEYS, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    logging.info("Fetching course ('%s') users (%s) from '%s'." % (
            str(course), ", ".join(map(str, users)), server))

    if (len(users) == 0):
        return []

    url = server + BASE_ENDPOINT.format(course = course, page_size = page_size)
    headers = canvas.api.common.standard_headers(token)

    for user in users:
        url += "&user_ids[]=%s" % (str(user))

    return canvas.api.user.common._list_users(url, headers, keys)
