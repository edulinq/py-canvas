import canvas.api.common

# Default keys that will be returned with an assignment.
DEFAULT_KEYS = [
    'id',
    'name',
    'points_possible',
    'published',
    'due_at',
    'assignment_group_id',
    'position',
    'description',
]

def list_assignments(url, headers, keys):
    output = []

    while (url is not None):
        _, url, new_assignments = canvas.api.common.make_get_request(url, headers)

        for new_assignment in new_assignments:
            if (keys is not None):
                new_assignment = {key: new_assignment.get(key, None) for key in keys}

            output.append(new_assignment)

    return output
