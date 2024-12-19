import canvas.api.common

# Default keys that will be returned with a user.
DEFAULT_KEYS = [
    'id',
    'email',
    'name',
    'enrollment',
    'sis_user_id',
]

COMPUTED_SCORE_KEYS = [
    'current_score',
    'final_score',
    'unposted_current_score',
    'unposted_final_score',
]

def list_users(url, headers, keys, missing_value = ''):
    output = []

    while (url is not None):
        _, url, new_users = canvas.api.common.make_get_request(url, headers)

        for new_user in new_users:
            _extract_enrollment(new_user)
            _extract_computed_grades(new_user)

            if (keys is not None):
                new_user = {key: new_user.get(key, missing_value) for key in keys}

            output.append(new_user)

    return output

def _extract_enrollment(user):
    raw_enrollments = user.get('enrollments', [])

    enrollment_types = [raw_enrollment.get('role') for raw_enrollment in raw_enrollments]
    user['enrollment'] = canvas.api.common.get_max_enrollment_type(enrollment_types)

    return user

def _extract_computed_grades(user):
    raw_enrollments = user.get('enrollments', [])

    for key in COMPUTED_SCORE_KEYS:
        user[key] = None

    if (len(raw_enrollments) == 0):
        return user

    section_ids = ', '.join([str(raw_enrollment.get('course_section_id', None)) for raw_enrollment in raw_enrollments])

    for raw_enrollment in raw_enrollments:
        for key in COMPUTED_SCORE_KEYS:
            old_value = user[key]
            new_value = raw_enrollment.get('grades', {}).get(key, None)

            if (new_value is None):
                continue

            if (old_value is None):
                user[key] = new_value
            elif (old_value != new_value):
                logging.warning("Found a mismatch in grades for user '%s' over sections '%s'. %f vs %f." % (user['id'], section_ids, old_value, new_value))
                continue

    return user
