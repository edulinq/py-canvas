import logging

import canvas.api.common
import canvas.api.group.common
import canvas.api.group.resolve

ALL_ENDPOINT = "/api/v1/courses/{course}/groups?per_page={page_size}"
GROUPING_ENDPOINT = "/api/v1/group_categories/{grouping}/groups?per_page={page_size}"

def request(server = None, token = None, course = None,
        grouping = None,
        keys = canvas.api.group.common.DEFAULT_KEYS, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    if (grouping is not None):
        grouping = str(grouping).strip()
        if (grouping == ''):
            grouping = None

    if (grouping is None):
        return list_all_groups(server, token, course, keys = keys)

    return list_grouping_groups(server, token, course, grouping, keys = keys)

def list_all_groups(server, token, course, keys = canvas.api.group.common.DEFAULT_KEYS):
    logging.info("Fetching all course ('%s') groups from '%s'." % (str(course), server))

    url = server + ALL_ENDPOINT.format(course = course, page_size = canvas.api.common.DEFAULT_PAGE_SIZE)
    headers = canvas.api.common.standard_headers(token)

    return canvas.api.common.make_get_request_list(url, headers, keys = keys)

def list_grouping_groups(server, token, course, grouping, keys = canvas.api.group.common.DEFAULT_KEYS):
    logging.info("Fetching course ('%s') groups for grouping '%s' from '%s'." % (str(course), str(grouping), server))

    if (canvas.api.group.resolve.requires_resolution([grouping])):
        grouping = canvas.api.group.resolve.fetch_and_resolve_grouping_id(server, token, course, grouping)

    if (grouping is None):
        return []

    url = server + GROUPING_ENDPOINT.format(grouping = grouping, page_size = canvas.api.common.DEFAULT_PAGE_SIZE)
    headers = canvas.api.common.standard_headers(token)

    return canvas.api.common.make_get_request_list(url, headers, keys = keys)
