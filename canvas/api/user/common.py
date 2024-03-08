import canvas.api.common

# Default keys that will be returned with a user.
DEFAULT_KEYS = [
    'id',
    'email',
    'name',
    'enrollment',
    'sis_user_id',
]

def list_users(url, headers, keys, missing_value = ''):
    output = []

    while (url is not None):
        _, url, new_users = canvas.api.common.make_get_request(url, headers)

        for new_user in new_users:
            raw_enrollments = new_user.get('enrollments', [])
            enrollment_types = [raw_enrollment.get('role') for raw_enrollment in raw_enrollments]
            new_user['enrollment'] = canvas.api.common.get_max_enrollment_type(enrollment_types)

            if (keys is not None):
                new_user = {key: new_user.get(key, missing_value) for key in keys}

            output.append(new_user)

    return output
