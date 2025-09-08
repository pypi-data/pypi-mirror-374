from ..core import MODULE_CONFIG_DIR, CUSTOM_IGNORE_FILE, RULES_FILE, _get_config_location_info
import os

def execute(args):
    """Shows information about the module configuration."""
    print("=== MyContext Configuration Information ===")
    print(f"Configuration directory: {MODULE_CONFIG_DIR}")
    print(f"Description: {_get_config_location_info()}")
    print()
    
    print("Configuration files:")
    
    if os.path.exists(CUSTOM_IGNORE_FILE):
        print(f"✓ custom_ignore.json: {CUSTOM_IGNORE_FILE}")
    else:
        print(f"○ custom_ignore.json: {CUSTOM_IGNORE_FILE} (does not exist, default will be used)")
    
    if os.path.exists(RULES_FILE):
        print(f"✓ context_rules.md: {RULES_FILE}")
    else:
        print(f"○ context_rules.md: {RULES_FILE} (does not exist, default will be used)")
    
    print()
    print("Legend: ✓ = file exists, ○ = file does not exist")

def register_subparser(subparsers):
    """Registers the subparser for the config-info command."""
    parser = subparsers.add_parser(
        "config-info", 
        help="Shows information about configuration and file locations."
    )
    parser.set_defaults(func=execute)
