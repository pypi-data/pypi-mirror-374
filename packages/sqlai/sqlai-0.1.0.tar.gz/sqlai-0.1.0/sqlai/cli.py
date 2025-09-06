import argparse

from .config import read_config, set_config
from .helpers import read_sql_file, show_actions


def main():
    # Create the main argument parser for the CLI and set its description
    parser = argparse.ArgumentParser(description="SQL AI CLI")

    # Add subparsers to the main parser, allowing the CLI to support subcommands (e.g., 'run', 'set_config')
    subparsers = parser.add_subparsers(dest="command")

    # Subcommand: set_config (no args)
    subparsers.add_parser(
        "set_config", help="Set global AI provider, API key, and model"
    )

    subparsers.add_parser("show_config", help="Show current configuration")

    # Subcommand: run (requires sql_file positional argument)
    parser_run = subparsers.add_parser("run", help="Read SQL file and show actions")
    parser_run.add_argument("sql_file", help="SQL file to explain")

    # Parse the command-line arguments and store them in the 'args' variable
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        exit(1)

    elif args.command == "set_config":
        set_config()
    elif args.command == "show_config":
        print(read_config())
    elif args.command == "run":
        sql = read_sql_file(args.sql_file)

        if sql:
            show_actions(sql)


if __name__ == "__main__":
    main()
