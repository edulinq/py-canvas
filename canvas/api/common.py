import json
import logging

import requests

DEFAULT_PAGE_SIZE = 95
HEADER_LINK = 'Link'

# Standard enrollment types order by priority.
ENROLLMENT_TYPES = [
    'ObserverEnrollment',
    'Student Auditor',
    'StudentEnrollment',
    'Tutor',
    'TaEnrollment',
    'DesignerEnrollment',
    'TA - Site Manager',
    'TeacherEnrollment',
]

ENROLLMENT_TYPE_UNKNOWN = '<unknown>'

# Return: (response, next_url, body)
def make_get_request(url, headers, raise_for_status = True,
        fetch_next_url = True, json_body = True):
    logging.info("Making request: '%s'." % (url))
    response = requests.get(url, headers = headers)
    response.raise_for_status()

    next_url = None
    if (fetch_next_url):
        next_url = fetch_next_canvas_link(response.headers)

    body = None
    log_body = None
    if (json_body):
        body = response.json()
        if (logging.getLogger().level <= logging.DEBUG):
            log_body = json.dumps(body, indent = 4)
    else:
        body = response.text
        log_body = body

    logging.debug("Response:\n%s" % log_body)

    return response, next_url, body

# Repeatedly call make_get_request() (using a JSON body and next link) until there are no more results.
# Collect the results and filter using the provided keys.
def make_get_request_list(url, headers,
        keys = None, missing_value = None):
    output = []

    while (url is not None):
        _, url, new_results = make_get_request(url, headers)

        for new_result in new_results:
            if (keys is not None):
                new_result = {key: new_result.get(key, missing_value) for key in keys}

            output.append(new_result)

    return output

# Return: (response, body)
def make_post(url, headers, data,
        raise_for_status = True, json_body = True):
    logging.info("Making request: '%s'." % (url))
    logging.debug("Data:\n%s" % json.dumps(data, indent = 4))

    response = requests.post(url, headers = headers, data = data)
    response.raise_for_status()

    body = None
    log_body = None
    if (json_body):
        body = response.json()
        if (logging.getLogger().level <= logging.DEBUG):
            log_body = json.dumps(body, indent = 4)
    else:
        body = response.text
        log_body = body

    logging.debug("Response:\n%s" % log_body)

    return response, body

def validate_param(value, name, param_type = str, optional = False, strip = True):
    if (value is None):
        if (optional):
            return None

        raise ValueError("Parameter '%s' is missing or null/None." % (name))

    if (param_type == str):
        value = str(value)
        if (strip):
            value = value.strip()

        return value

    if (not isinstance(value, param_type)):
        raise ValueError("Parameter '%s' has the incorrect type '%s', expected '%s'." % (name, type(value), param_type))

    return value

def standard_headers(token):
    return {
        "Authorization": "Bearer %s" % (token),
        "Accept": "application/json+canvas-string-ids",
    }

def fetch_next_canvas_link(headers):
    if (HEADER_LINK not in headers):
        return None

    links = headers[HEADER_LINK].split(',')
    for link in links:
        parts = link.split(';')
        if (len(parts) != 2):
            continue

        if (parts[1].strip() != 'rel="next"'):
            continue

        return parts[0].strip().strip('<>')

    return None

# Given multiple enrollment types, return the one with the most authority.
def get_max_enrollment_type(enrollment_types):
    max_type = ENROLLMENT_TYPE_UNKNOWN
    max_index = -2

    for enrollment_type in enrollment_types:
        if (enrollment_type not in ENROLLMENT_TYPES):
            logging.warning("Unknown enrollment type: '%s'." % (enrollment_type))
            index = -1
        else:
            index = ENROLLMENT_TYPES.index(enrollment_type)

        if (index > max_index):
            max_index = index
            max_type = enrollment_type

    return max_type
