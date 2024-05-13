import logging

import canvas.api.common
import canvas.api.group.resolve

BASE_ENDPOINT = "/api/v1/groups/{group}/users"

DEFAULT_KEYS = [
    'id',
    'login_id',
    'sis_user_id',
    'name',
]

def request(server = None, token = None, course = None,
        group = None,
        keys = DEFAULT_KEYS,
        **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)
    group = canvas.api.common.validate_param(group, 'group')

    logging.info("Fetching group ('%s') membership for course '%s' from '%s'." % (str(group), str(course), server))

    if (canvas.api.group.resolve.requires_resolution([group])):
        group = canvas.api.group.resolve.fetch_and_resolve_group_id(server, token, course, group)

    if (group is None):
        return []

    url = server + BASE_ENDPOINT.format(group = group)
    headers = canvas.api.common.standard_headers(token)


    return canvas.api.common.make_get_request_list(url, headers, keys = keys)
