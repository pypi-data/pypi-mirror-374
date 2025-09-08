##### ./src/mycontext/cli.py #####
import sys
import argparse
from . import commands  

VERSION = "0.1.12"

def main():
    parser = argparse.ArgumentParser(
        description="Generate a consolidated file or manage rules to ignore files."
    )
    parser.add_argument(
        "-v", "--version",
        action="store_true",
        help="Show the program version"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    commands.register_commands(subparsers)

    known_commands = list(subparsers.choices.keys())
    known_options = ['-h', '--help', '-v', '--version']
    
    if len(sys.argv) > 1 and sys.argv[1] not in known_commands and sys.argv[1] not in known_options:
        sys.argv.insert(1, 'generate')
        
    args = parser.parse_args()

    if args.version:
        print(f"mycontext {VERSION}")
        sys.exit(0)

    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(0)