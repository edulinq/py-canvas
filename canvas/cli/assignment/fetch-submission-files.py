import shutil
import sys

import canvas.api.assignment.fetchsubmissionfiles
import canvas.config

DEFAULT_OUT_DIR = 'out'

def run_cli(out_dir = DEFAULT_OUT_DIR, **kwargs):
    temp_dir, count = canvas.api.assignment.fetchsubmissionfiles.request(**kwargs)
    shutil.copytree(temp_dir, out_dir, dirs_exist_ok = True)
    print("Downloaded %d files to '%s'." % (count, out_dir))

    return 0

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'Fetch the submitted files (or text-entry) for an assignment.'

    parser.add_argument('assignment',
        action = 'store', type = str,
        help = 'The query for the assignment to fetch submission files for.')

    parser.add_argument('--out-dir', dest = 'out_dir',
        action = 'store', type = str, default = DEFAULT_OUT_DIR,
        help = 'The directory to put the resulting files in (default: %(default)s).')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
