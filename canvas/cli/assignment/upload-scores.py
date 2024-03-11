import ast
import sys

import canvas.api.assignment.uploadscores
import canvas.config

DEFAULT_SKIP_ROWS = 0

def run_cli(assignment = None, path = None, skip_rows = DEFAULT_SKIP_ROWS, **kwargs):
    users, scores, comments = _load_scores(path, skip_rows)
    score_count = canvas.api.assignment.uploadscores.request(assignment = assignment,
            users = users, scores = scores, comments = comments,
            **kwargs)

    print("Uploaded %d Scores" % (score_count))
    return 0

def _load_scores(path, skip_rows):
    users = []
    scores = []
    comments = []

    with open(path, 'r') as file:
        lineno = 0
        for line in file:
            lineno += 1

            if (lineno <= skip_rows):
                continue

            line = line.strip()
            if (line == ""):
                continue

            parts = [part.strip() for part in line.split("\t")]
            if (len(parts) not in [2, 3]):
                raise ValueError(
                    "File '%s' line %d has the incorrect number of values." % (path, lineno)
                    + " Expecting 2-3, found %d." % (len(parts)))

            score = None
            if (parts[1] != ''):
                try:
                    score = ast.literal_eval(parts[1])
                except Exception as ex:
                    raise ValueError(
                        "File '%s' line %d has a score that cannot be" % (path, lineno)
                        + " converted to a number: '%s'." % (parts[1])) from ex

            users.append(parts[0])
            scores.append(score)

            if (len(parts) >= 3):
                comments.append(parts[2].strip())
            else:
                comments.append(None)

    return users, scores, comments

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'Upload scores (and optional comments) for an assignment.'

    parser.add_argument('--skip-rows', dest = 'skip_rows',
        action = 'store', type = int, default = DEFAULT_SKIP_ROWS,
        help = 'The number of header rows to skip (default: %(default)s).')

    parser.add_argument('assignment', metavar = 'ASSIGNMENT',
        action = 'store', type = str,
        help = 'The query for the assignment to upload scores to.')

    parser.add_argument('path', metavar = 'PATH',
        action = 'store', type = str,
        help = 'Path to a TSV file where each row has 2-3 columns: email, score, and comment (optional).')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
