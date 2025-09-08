##### ./src/mycontext/commands/generate.py #####
import sys
import datetime
import pyperclip
from ..core import collect_files, join_files, get_rules_content, join_content_to_string

def execute(args):
    """Function executed for this command."""
    if not args.paths:
        print("Error: You must specify at least one file or folder.", file=sys.stderr)
        sys.exit(1)
    
    rules = ""
    if args.use_rules:
        rules = get_rules_content(args.rules)

    files = collect_files(args.paths)
    if not files and not rules.strip():
        print("Warning: No valid files or rules found to include.")
        sys.exit(0)
        
    if args.to_clipboard:
        if args.output:
            print("Warning: --to-clipboard takes precedence over --output. No file will be created.")

        full_content = join_content_to_string(files, rules)
        try:
            pyperclip.copy(full_content)
            print(f"Success! The context with {len(files)} files has been copied to the clipboard.")
        except pyperclip.PyperclipException as e:
            print("Error: Could not copy to clipboard.", file=sys.stderr)
            print(f"Details: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        if args.output:
            output = args.output
        else:
            date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output = f"context_window_{date}.txt"

        join_files(files, output, rules)

    sys.exit(0)

def register_subparser(subparsers):
    """Registers this command in the main parser."""
    parser_generate = subparsers.add_parser("generate", help="Generates the context file (default action).")
    parser_generate.add_argument(
        "paths",
        nargs="*",
        help="Files or folders to include."
    )
    parser_generate.add_argument(
        "-o", "--output",
        help="Name of the output file."
    )
    parser_generate.add_argument(
        "-r", "--rules",
        help="Specifies a custom rules file (.md) to use for this run."
    )
    parser_generate.add_argument(
        "-c", "--to-clipboard",
        action="store_true",
        help="Copies the generated context directly to the clipboard instead of saving it to a file."
    )
    
    parser_generate.add_argument(
        "--no-rules",
        dest="use_rules",       
        action="store_false",   
        help="Generates the context without including the rules file."
    )
    
    parser_generate.set_defaults(func=execute, use_rules=True)
