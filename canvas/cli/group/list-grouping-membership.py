import sys

import canvas.api.group.listgroupingmembership
import canvas.cli.common
import canvas.config

OUTPUT_KEYS = [
    ('group_name', 'group_name', 'Group Name'),
    ('canvas_group_id', 'group_id', 'Canvas Group ID'),
    ('email', 'email', 'Email'),
]

def run_cli(**kwargs):
    groups = canvas.api.group.listgroupingmembership.request(**kwargs)

    return canvas.cli.common.cli_list(groups, OUTPUT_KEYS,
            collective_name = 'groups', sort_key = 'name',
            **kwargs)

def main():
    config = canvas.config.get_config(exit_on_error = True, modify_parser = _modify_parser, course = True)
    return run_cli(**config)

def _modify_parser(parser):
    parser.description = 'List the membership of all groups within a grouping.'

    canvas.cli.common.add_output_args(parser)

    parser.add_argument('grouping',
        action = 'store', type = str,
        help = 'The query for the grouping (aka "group set" or "group category") to list.')

    return parser

if (__name__ == '__main__'):
    sys.exit(main())
