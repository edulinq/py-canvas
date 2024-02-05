import logging

DEFAULT_PAGE_SIZE = 75
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

def validate_param(value, name, param_type = str, optional = False):
    if (value is None):
        if (optional):
            return None

        raise ValueError("Parameter '%s' is missing or null/None." % (name))

    if (param_type == str):
        return str(value)

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
