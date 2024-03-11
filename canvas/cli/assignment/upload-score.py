import sys

import canvas.api.assignment.uploadscores
import canvas.config

def run_cli(assignment = None, user = None, score = None, comment = None, **kwargs):
    score_count = canvas.api.assignment.uploadscores.request(
            assignment = assignment, users = [user],
            scores = [score], comments = [comment],
            **kwargs)

    print("Uploaded %d Scores" % (score_count))
    return 0

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'Upload a single score (and optional comment) for an assignment.'

    parser.add_argument('assignment', metavar = 'ASSIGNMENT',
        action = 'store', type = str,
        help = 'The query for the assignment to upload scores for.')

    parser.add_argument('user', metavar = 'USER',
        action = 'store', type = str,
        help = 'The query for the user to upload scores for.')

    parser.add_argument('score', metavar = 'SCORE',
        action = 'store', type = float,
        help = 'Score to upload.')

    parser.add_argument('comment', metavar = 'COMMENT',
        action = 'store', type = str, nargs = '?', default = None,
        help = 'Optional comment.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
