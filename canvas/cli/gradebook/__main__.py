"""
The `canvas.cli.gradebook` package contains tools for interacting with Canvas gradebooks.
"""

import sys

import canvas.config
import canvas.util.cli

def main():
    canvas.util.cli.auto_list(default_parser = canvas.config.get_argument_parser())
    return 0

if (__name__ == '__main__'):
    sys.exit(main())
