##### ./src/mycontext/commands/add_rule.py #####
from ..core import add_rule

def execute(args):
    add_rule(args.content)

def register_subparser(subparsers):
    parser_add = subparsers.add_parser("add-rule", help="Adds a new rule to the rules file.")
    parser_add.add_argument("content", help="The text of the rule to add (in quotes).")
    parser_add.set_defaults(func=execute)