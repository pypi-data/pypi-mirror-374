##### ./src/mycontext/commands/update_rules.py #####
from ..core import update_rules_with_editor

def execute(args):
    update_rules_with_editor()

def register_subparser(subparsers):
    parser_update = subparsers.add_parser(
        "update-rules",
        help="Opens the rules file in your default text editor."
    )
    parser_update.set_defaults(func=execute)