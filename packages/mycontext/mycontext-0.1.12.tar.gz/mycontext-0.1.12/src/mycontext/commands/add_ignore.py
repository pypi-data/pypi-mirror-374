##### ./src/mycontext/commands/add-ignore.py #####
from ..core import add_to_custom_ignore

def execute(args):
    add_to_custom_ignore(args.type, args.value)

def register_subparser(subparsers):
    parser_add = subparsers.add_parser("add-ignore", help="Adds a new rule to the custom ignore file.")
    parser_add.add_argument("type", choices=["name", "pattern", "ext"], help="Type of rule to ignore.")
    parser_add.add_argument("value", help="Value to ignore.")
    parser_add.set_defaults(func=execute)