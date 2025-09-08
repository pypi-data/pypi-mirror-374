##### ./src/mycontext/commands/list_rules.py #####
from ..core import list_rules

def execute(args):
    list_rules()

def register_subparser(subparsers):
    parser_list = subparsers.add_parser("list-rules", help="Shows the current context rules.")
    parser_list.set_defaults(func=execute)