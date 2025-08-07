#!/usr/bin/env python3

import os
import sys
import argparse

from container_craft.arguments import parse_build, parse_exec, parse_start, parse_stop, parse_checkout, parse_info,parse_logs, parse_shell, parse_console, parse_menu

from container_craft.plugins import build, logs, info, shell, console, menu, runner, checkout

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def main():
    parser = argparse.ArgumentParser(description="Container Craft CLI")
    parser.add_argument("build", help="Build a Minecraft network or a single instance", action="store_true")
    parser.add_argument("start", help="Start a Minecraft Network", action="store_true")
    parser.add_argument("stop", help="Stop a Minecraft Network", action="store_true")
    parser.add_argument("exec", help="Run a command to a minecraft console", action="store_true")
    parser.add_argument("checkout", help="Clone other git repositories that have yaml", action="store_true")
    parser.add_argument("info", help="Information Minecraft network and images", action="store_true")
    parser.add_argument("logs", help="View logs for mincraft", action="store_true")
    parser.add_argument("shell", help="Open a shell in a Docker container", action="store_true")
    parser.add_argument("console", help="Open a running Minecraft console", action="store_true")
    parser.add_argument("menu", help="Run the TUI based on the Kconfig file", action="store_true")
    args = parser.parse_args()

    if args.command == "build":
      parse_build(parser)
      args = parser.parse_args()
      build.build_all(args)
    elif args.command == "exec":
        parse_run(parser)
        args = parser.parse_args()
        ## run.exec(args)
    elif parser._subparsers == "stop":
        parse_stop(parser)
        args = parser.parse_args()
        runner.stop(args)
    elif parser._subparsers == "start":
        parse_start(parser)
        args = parser.parse_args()
        runner.start(args)
    elif args.command == "checkout":     
        parse_checkout(parser)
        args = parser.parse_args()
        checkout.checkout(args)
    elif args.command == "info":
        parse_info(parser)
        args = parser.parse_args()
        info.show_info(args)
    elif args.command == "logs":     
        parse_info(parser)
        args = parser.parse_args()
        logs.tail_logs(args)
    elif args.command == "shell":
        parse_shell(parser)
        args = parser.parse_args()
        shell.attach_shell(args)
    elif args.command == "console":
        parse_console(parser)
        args = parser.parse_args()
        console.attach(args)
    elif args.command == "menu":     
        parse_menu(parser)
        args = parser.parse_args()
        menu.show(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
