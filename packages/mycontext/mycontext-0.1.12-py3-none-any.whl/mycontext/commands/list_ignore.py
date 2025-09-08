##### ./src/mycontext/commands/list-ignore.py #####
from ..core import list_current_ignores

def execute(args):
    list_current_ignores()

def register_subparser(subparsers):
    parser_list = subparsers.add_parser("list-ignore", help="List the current ignore rules.")
    parser_list.set_defaults(func=execute)