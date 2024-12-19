import ast
import re
import sys

import canvas.api.gradebook.upload
import canvas.config

def run_cli(path = None, **kwargs):
    assignments, users, scores = _load_gradebook(path)

    # Filter out assignments that look like computed scores.
    remove_indexes = []
    for i in range(len(assignments)):
        if (re.search(r'\(_computed_\d+_\)$', assignments[i]) is not None):
            remove_indexes.append(i)

    for index in reversed(remove_indexes):
        assignments.pop(index)

        for user_scores in scores:
            user_scores.pop(index)

    score_count = canvas.api.gradebook.upload.request(
            assignments = assignments, users = users, scores = scores,
            **kwargs)

    print("Uploaded %d Scores" % (score_count))
    return 0

# Return: ([assignment, ...], [user, ...], [[score, ...], ...])
# The scores are indexed by user then assignment: [user_index][assignment_index].
# Scores will always have all cells represented, a None indicates no score to upload.
def _load_gradebook(path):
    assignments = []
    users = []
    scores = []

    with open(path, 'r') as file:
        lineno = 0
        for line in file:
            lineno += 1

            if (line.strip() == ""):
                continue

            parts = [part.strip() for part in line.split("\t")]

            # First row has an empty cell then assignments.
            if (len(assignments) == 0):
                if (len(parts) <= 1):
                    raise ValueError("Gradebook '%s' has no assignments." % (path))

                for assignment in parts[1:]:
                    if (assignment == ''):
                        raise ValueError("Gradebook '%s' has an empty assignment name." % (path))

                    if (assignment in assignments):
                        raise ValueError("Gradebook '%s' has a duplicate assignment: '%s'." % (path, assignment))

                    assignments.append(assignment)

                continue

            if (len(parts) != (len(assignments) + 1)):
                raise ValueError(
                    "Gradebook '%s' line %d has the incorrect number of values." % (path, lineno)
                    + " Expecting %d, found %d." % ((len(assignments) + 1), len(parts)))

            user = parts.pop(0)
            if (user == ''):
                raise ValueError("Gradebook '%s' line %d has an empty user." % (path, lineno))

            if (user in users):
                raise ValueError("Gradebook '%s' line %d has a duplicate user '%s'." % (path, lineno, user))

            users.append(user)

            user_scores = []
            for i in range(len(parts)):
                score = None
                if (parts[i] != ''):
                    try:
                        score = ast.literal_eval(parts[i])
                    except Exception as ex:
                        raise ValueError(
                            "Gradebook '%s' line %d column %d has a score that cannot be" % (path, lineno, i + 2)
                            + " converted to a number: '%s'." % (parts[i])) from ex

                user_scores.append(score)

            scores.append(user_scores)

    return assignments, users, scores

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'Upload a gradebook.'

    parser.epilog = ('A gradebook file is a tab-separated file where'
            + ' the first column is user queries (the first cell is ignored),'
            + ' the first row is assignment queries (the first cell is ignored),'
            + ' and the remaining cells are the associated scores.'
            + ' Any number of users and assignments can be specified as long as they exist in the course.'
            + ' Empty cells will not be uploaded.')

    parser.add_argument('path', metavar = 'PATH',
        action = 'store', type = str,
        help = 'Path to a TSV gradebook file.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
