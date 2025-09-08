##### ./src/mycontext/commands/remove_rules.py #####
from ..core import remove_rules_file

def execute(args):
    if not args.yes:
        confirm = input("Are you sure you want to delete 'context_rules.md'? [y/N]: ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
    remove_rules_file()

def register_subparser(subparsers):
    parser_rem = subparsers.add_parser("remove-rules", help="Deletes the 'context_rules.md' rules file.")
    parser_rem.add_argument("-y", "--yes", action="store_true", help="Confirm deletion without asking.")
    parser_rem.set_defaults(func=execute)