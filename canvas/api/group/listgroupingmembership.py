import csv
import logging

import canvas.api.common
import canvas.api.group.common
import canvas.api.group.resolve

BASE_ENDPOINT = "/api/v1/group_categories/{grouping}/export"

# [(old name, new name), ...]
KEYS = [
    ('canvas_group_id', 'canvas_group_id'),
    ('group_name', 'group_name'),
    ('login_id', 'email'),
]

def request(server = None, token = None, course = None,
        grouping = None, **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)
    grouping = canvas.api.common.validate_param(grouping, 'grouping')

    logging.info("Fetching course ('%s') groups for grouping '%s' from '%s'." % (str(course), str(grouping), server))

    if (canvas.api.group.resolve.requires_resolution([grouping])):
        grouping = canvas.api.group.resolve.fetch_and_resolve_grouping_id(server, token, course, grouping)

    if (grouping is None):
        return []

    url = server + BASE_ENDPOINT.format(grouping = grouping)
    headers = canvas.api.common.standard_headers(token)

    _, _, content = canvas.api.common.make_get_request(url, headers, fetch_next_url = False, json_body = False)

    items = []
    for row in csv.DictReader(content.strip().splitlines()):
        items.append({new_key: row.get(old_key, None) for (old_key, new_key) in KEYS})

    return items
