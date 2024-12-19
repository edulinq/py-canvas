import sys

import canvas.api.gradebook.fetch
import canvas.config

DEFAULT_SKIP_HEADERS = False
DEFAULT_INCLUDE_EMPTY_ASSIGNMENTS = False
DEFAULT_INCLUDE_EMPTY_USERS = False
DEFAULT_INCLUDE_COMPUTED_SCORES = False

def run_cli(include_empty_assignments = DEFAULT_INCLUDE_EMPTY_ASSIGNMENTS, include_empty_users = DEFAULT_INCLUDE_EMPTY_USERS,
        include_computed_scores = DEFAULT_INCLUDE_COMPUTED_SCORES,
        skip_headers = DEFAULT_SKIP_HEADERS, students = [], **kwargs):
    assignments, user_grades = canvas.api.gradebook.fetch.request(user_queries = students, include_computed_scores = include_computed_scores, **kwargs)

    if (len(assignments) == 0):
        print("No assignments found.", file = sys.stderr)
        return 0

    if (len(user_grades) == 0):
        print("No submissions found.", file = sys.stderr)
        return 0

    sorted_assignments = list(sorted(assignments.values(), key = lambda assignment: (assignment['assignment_group_id'], assignment['position'], assignment['id'])))

    if (not include_empty_assignments):
        new_assignments = []

        for assignment in sorted_assignments:
            if (assignment['count'] > 0):
                new_assignments.append(assignment)

        sorted_assignments = new_assignments

    if (not skip_headers):
        headers = ["%s (%s)" % (assignment['name'], str(assignment['id'])) for assignment in sorted_assignments]
        print("\t".join(['email'] + headers))

    for (email, grades) in user_grades.items():
        row = []
        has_score = False

        for assignment in sorted_assignments:
            score = grades.get(assignment['id'], None)
            if (score is None):
                score = ''
            else:
                has_score = True

            row.append(str(score))

        if ((not include_empty_users) and (not has_score)):
            continue

        print("\t".join([email] + row))

    return 0

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'Fetch the gradebook for a course. This may take several minutes.'

    parser.add_argument('--include-empty-assignments', dest = 'include_empty_assignments',
        action = 'store_true', default = DEFAULT_INCLUDE_EMPTY_ASSIGNMENTS,
        help = 'Include assignments with no submissions (default: %(default)s).')

    parser.add_argument('--include-empty-users', dest = 'include_empty_users',
        action = 'store_true', default = DEFAULT_INCLUDE_EMPTY_USERS,
        help = 'Include users with no submissions (default: %(default)s).')

    parser.add_argument('--include-computed-scores', dest = 'include_computed_scores',
        action = 'store_true', default = DEFAULT_INCLUDE_COMPUTED_SCORES,
        help = 'Include scores computed Canvas (default: %(default)s).')

    parser.add_argument('--skip-headers', dest = 'skip_headers',
        action = 'store_true', default = DEFAULT_SKIP_HEADERS,
        help = 'Skip headers (default: %(default)s).')

    parser.add_argument('students',
        nargs = '*',
        help = 'If specified, only fetch the gradebook for the specified students.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
