import logging
import requests

import canvas.api.assignment.resolve
import canvas.api.assignment.uploadscores
import canvas.api.common
import canvas.api.user.resolve

# Scores are a full 2d list indexed by user then assignment, None entries indicate a missing score.
def request(server = None, token = None, course = None,
        assignments = [], users = [], scores = [],
        **kwargs):
    server = canvas.api.common.validate_param(server, 'server')
    token = canvas.api.common.validate_param(token, 'token')
    course = canvas.api.common.validate_param(course, 'course', param_type = int)

    _validate_shape(assignments, users, scores)

    original_users = users
    original_assignments = assignments

    logging.info("Uploading gradebook for course '%s' from '%s'." % (str(course), server))

    if (canvas.api.assignment.resolve.requires_resolution(assignments)):
        resolved_assignments = canvas.api.assignment.resolve.fetch_and_resolve_assignments(server, token, course, assignments)
        if (len(resolved_assignments) != len(assignments)):
            raise ValueError("Unable to resolve all assignment queries.")

        assignments = [assignment['id'] for assignment in resolved_assignments]

    if (canvas.api.user.resolve.requires_resolution(users)):
        resolved_users = canvas.api.user.resolve.fetch_and_resolve_users(server, token, course, users)
        if (len(resolved_users) != len(users)):
            raise ValueError("Unable to resolve all user queries.")

        users = [resolved_user['id'] for resolved_user in resolved_users]

    _validate_dups(users, original_users, 'users')
    _validate_dups(assignments, original_assignments, 'assignments')

    score_count = 0

    for assignment_index in range(len(assignments)):
        assignment = assignments[assignment_index]
        assignment_scores = [scores[user_index][assignment_index] for user_index in range(len(users))]

        score_count += canvas.api.assignment.uploadscores.direct_request(server, token, course,
                assignment, users, assignment_scores)

    return score_count

def _validate_shape(assignments, users, scores):
    if (len(scores) != len(users)):
        raise ValueError("Scores does not match the number of users (%d), found %d rows." % (len(users), len(scores)))

    for i in range(len(scores)):
        user = users[i]
        assignment_scores = scores[i]

        if (len(assignment_scores) != len(assignments)):
            raise ValueError("Scores for user '%s' does not match the number of assignment (%d), found %d scores." % (
                    str(user), len(assignments), len(assignment_scores)))

def _validate_dups(resolved, original, label):
    dup_indexes = {}

    for i in range(len(resolved)):
        if (resolved[i] not in dup_indexes):
            dup_indexes[resolved[i]] = []
        dup_indexes[resolved[i]].append(i)

    dups = []
    for indexes in dup_indexes.values():
        if (len(indexes) > 1):
            dups.append("(%s)" % (', '.join([str(original[index]) for index in indexes])))

    if (len(dups) == 0):
        return

    raise ValueError("Found duplicates in %s: [%s]." % (label, ', '.join(dups)))
