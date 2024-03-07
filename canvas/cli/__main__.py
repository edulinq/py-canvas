"""
The `canvas.cli` package contains several packages for interacting with Canvas in differnt ways.
Each package can be invoked to list the tools (or subpackages) it contains.
Each tool includes a help prompt that can be accessed with the `-h`/`--help` flag.
"""

import sys

import canvas.util.cli

def main():
    canvas.util.cli.auto_list()
    return 0

if (__name__ == '__main__'):
    sys.exit(main())
