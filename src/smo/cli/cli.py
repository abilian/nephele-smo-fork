from __future__ import annotations

import argparse

from smo.cli.commands import register_commands


def main(argv: list[str] | None = None):
    parser = make_parser()

    # Parse arguments
    if argv is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(argv)

    # Default behavior (print help if no arguments are provided)
    if func := getattr(args, "func", None):
        func(args)
    elif args.command == "plugins":
        list_plugins(verbose=args.verbose)
    else:
        parser.print_help()


def make_parser():
    parser = argparse.ArgumentParser(
        description="SMO CLI - Simplified Modular Operations"
    )
    subparsers = parser.add_subparsers(
        title="commands", dest="command", help="Available commands"
    )

    register_commands(subparsers)
    register_plugins_command(subparsers)

    return parser


def register_plugins_command(subparsers):
    # 'plugins' command
    plugins_parser = subparsers.add_parser(
        "plugins", help="List currently installed plugins"
    )
    plugins_parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display plugins in a verbose format",
    )


def list_plugins(verbose=False):
    # Example plugins; replace with dynamic retrieval logic
    plugins = [
        {"name": "plugin1", "description": "Description for plugin1"},
        {"name": "plugin2", "description": "Description for plugin2"},
        {"name": "plugin3", "description": "Description for plugin3"},
    ]

    if verbose:
        for plugin in plugins:
            print(f"{plugin['name']}: {plugin['description']}")
    else:
        for plugin in plugins:
            print(plugin["name"])


if __name__ == "__main__":
    main()
