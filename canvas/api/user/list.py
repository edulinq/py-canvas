import logging

import canvas.api.common

BASE_ENDPOINT = "/api/v1/courses/{course}/users?include[]=enrollments&per_page={page_size}"

DEFAULT_KEYS = [
    'id',
    'email',
    'name',
    'enrollment',
    'sis_user_id',
]

def request(server = None, token = None, course = None,
        page_size = canvas.api.common.DEFAULT_PAGE_SIZE,
        keys = DEFAULT_KEYS, **kwargs):
    """
    Perform a request for users from Canvas.

    keys defines the keys from the user object that will be returned.
    Set to None for all keys.
    """

    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    logging.info("Fetching course ('%s') users from '%s'." % (str(course), server))

    url = server + BASE_ENDPOINT.format(course = course, page_size = page_size)
    headers = canvas.api.common.standard_headers(token)

    users = []

    while (url is not None):
        _, url, new_users = canvas.api.common.make_get_request(url, headers)

        for new_user in new_users:
            raw_enrollments = new_user.get('enrollments', [])
            enrollment_types = [raw_enrollment.get('role') for raw_enrollment in raw_enrollments]
            new_user['enrollment'] = canvas.api.common.get_max_enrollment_type(enrollment_types)

            if (keys is not None):
                new_user = {key: new_user[key] for key in keys}

            users.append(new_user)

    return users
