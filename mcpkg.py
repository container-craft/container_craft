#!/usr/bin/env python3
import os
import sys

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


from mcpkg.cli import parse_commands
if __name__ == "__main__":
    parse_commands()
