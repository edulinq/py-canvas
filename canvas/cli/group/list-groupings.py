import sys

import canvas.api.group.listgroupings
import canvas.cli.common
import canvas.config

OUTPUT_KEYS = [
    ('name', 'name', 'Name'),
    ('id', 'canvas_id', 'Canvas ID'),
]

def run_cli(**kwargs):
    groupings = canvas.api.group.listgroupings.request(**kwargs)

    return canvas.cli.common.cli_list(groupings, OUTPUT_KEYS,
            collective_name = 'groupings', sort_key = 'name',
            **kwargs)

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = ('List groupings in a course.'
        + ' Canvas also calls groupings ("Group Sets" or "Group Categories").'
        + ' This does not list group(ing) membership.')

    canvas.cli.common.add_output_args(parser)

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
