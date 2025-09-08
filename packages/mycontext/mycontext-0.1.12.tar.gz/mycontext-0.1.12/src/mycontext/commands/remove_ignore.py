##### ./src/mycontext/commands/remove-ignore.py #####
from ..core import remove_from_custom_ignore

def execute(args):
    remove_from_custom_ignore(args.type, args.value)

def register_subparser(subparsers):
    parser_rem = subparsers.add_parser(
        "remove-ignore",
        help="Removes an existing rule from the custom ignore file."
    )
    parser_rem.add_argument(
        "type",
        choices=["name", "pattern", "ext"],
        help="Type of rule to remove."
    )
    parser_rem.add_argument(
        "value",
        help="Value to remove."
    )
    parser_rem.set_defaults(func=execute)