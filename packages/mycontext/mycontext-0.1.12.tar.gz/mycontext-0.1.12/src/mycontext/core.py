##### ./src/mycontext/core.py #####
import os
import fnmatch
import importlib.resources
import json
import subprocess
import sys
import io

def _get_module_config_dir():
    """Gets the directory where the module's configuration files will be stored."""
    try:
        package_path = importlib.resources.files('mycontext')
        config_dir = str(package_path)
        
        test_file = os.path.join(config_dir, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return config_dir
        except (PermissionError, OSError):
            home_config = os.path.join(os.path.expanduser('~'), '.mycontext')
            os.makedirs(home_config, exist_ok=True)
            return home_config
            
    except Exception:
        config_dir = os.path.dirname(os.path.abspath(__file__))
        
        test_file = os.path.join(config_dir, '.write_test')
        try:
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            return config_dir
        except (PermissionError, OSError):
            home_config = os.path.join(os.path.expanduser('~'), '.mycontext')
            os.makedirs(home_config, exist_ok=True)
            return home_config

MODULE_CONFIG_DIR = _get_module_config_dir()
CUSTOM_IGNORE_FILE = os.path.join(MODULE_CONFIG_DIR, "custom_ignore.json")
RULES_FILE = os.path.join(MODULE_CONFIG_DIR, "context_rules.md")
LOCAL_IGNORE_FILE = ".mycontext-ignore" 

def _get_config_location_info():
    """Returns information about where the configuration files are being saved."""
    if MODULE_CONFIG_DIR == os.path.dirname(os.path.abspath(__file__)):
        return "configuration files saved in the module directory (development mode)"
    elif MODULE_CONFIG_DIR.endswith('.mycontext'):
        return "configuration files saved in ~/.mycontext (user directory)"
    else:
        return f"configuration files saved in: {MODULE_CONFIG_DIR}"



def _load_default_ignore_config():
    """Loads the ignore configuration from the package's JSON file."""
    try:
        with importlib.resources.files('mycontext').joinpath('default_ignore.json').open('r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"names": [], "patterns": [], "extensions": []}


def _load_ignore_config():    
    """
    Loads the ignore configuration based on priority:
    1. .mycontext-ignore in the current directory.
    2. custom_ignore.json in the user's config directory.
    3. default_ignore.json packaged with the module.
    """

    local_ignore_path = os.path.join(os.getcwd(), LOCAL_IGNORE_FILE)

    if os.path.exists(local_ignore_path):
        try:
            with open(local_ignore_path, 'r') as f:
                config_data = json.load(f)
                return (
                    config_data.get("names", []),
                    config_data.get("patterns", []),
                    config_data.get("extensions", [])
                )
        except (FileNotFoundError, json.JSONDecodeError):
             print(f"Warning: Could not read or parse local ignore file '{local_ignore_path}'. Falling back to global/default config.", file=sys.stderr)
    
    config_data = _load_default_ignore_config()
    if os.path.exists(CUSTOM_IGNORE_FILE):
        try:
            with open(CUSTOM_IGNORE_FILE, 'r') as f:
                custom_config = json.load(f)
            config_data = custom_config
        except (FileNotFoundError, json.JSONDecodeError):
            pass
    return (
        config_data.get("names", []),
        config_data.get("patterns", []),
        config_data.get("extensions", [])
    )


def add_to_custom_ignore(kind, value):
    """Adds a new rule to the custom_ignore.json file."""
    local_ignore_path = os.path.join(os.getcwd(), LOCAL_IGNORE_FILE)
    if os.path.exists(local_ignore_path):
        print(f"Warning: A local '{LOCAL_IGNORE_FILE}' file exists which overrides global rules in this directory.")
        print("The 'add-ignore' command only modifies the global file. Your changes may not take effect here.")

    config_data = _load_default_ignore_config()
    if os.path.exists(CUSTOM_IGNORE_FILE):
        try:
            with open(CUSTOM_IGNORE_FILE, 'r') as f:
                config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Warning: Could not read '{CUSTOM_IGNORE_FILE}', a new one will be created.")

    kind_map = {"name": "names", "pattern": "patterns", "ext": "extensions"}
    key = kind_map.get(kind)
    if key and value not in config_data.get(key, []):
        config_data.setdefault(key, []).append(value)
    
    try:
        with open(CUSTOM_IGNORE_FILE, 'w') as f:
            json.dump(config_data, f, indent=4)
        location_info = _get_config_location_info()
        print(f"Rule '{value}' added to 'custom_ignore.json' in section '{key}'.")
        print(f"Location: {location_info}")
    except IOError as e:
        print(f"Error writing to '{CUSTOM_IGNORE_FILE}': {e}", file=sys.stderr)


def remove_from_custom_ignore(kind, value):
    """Removes an existing rule from the custom_ignore.json file."""
    local_ignore_path = os.path.join(os.getcwd(), LOCAL_IGNORE_FILE)
    if os.path.exists(local_ignore_path):
        print(f"Warning: A local '{LOCAL_IGNORE_FILE}' file exists which overrides global rules in this directory.")
        print("The 'remove-ignore' command only modifies the global file. Your changes may not take effect here.")

    config_data = {}
    if not os.path.exists(CUSTOM_IGNORE_FILE):
        print(f"The file '{CUSTOM_IGNORE_FILE}' does not exist. It will be created from the default.")
        config_data = _load_default_ignore_config()
    else:
        try:
            with open(CUSTOM_IGNORE_FILE, 'r') as f:
                config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error: Cannot read or decode '{CUSTOM_IGNORE_FILE}'. Operation cannot be performed.", file=sys.stderr)
            return

    kind_map = {"name": "names", "pattern": "patterns", "ext": "extensions"}
    key = kind_map.get(kind)
    
    if key and key in config_data and value in config_data[key]:
        config_data[key].remove(value)
        try:
            with open(CUSTOM_IGNORE_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
            print(f"Rule '{value}' removed from '{CUSTOM_IGNORE_FILE}' in section '{key}'.")
        except IOError as e:
            print(f"Error writing to '{CUSTOM_IGNORE_FILE}': {e}", file=sys.stderr)
    else:
        if not os.path.exists(CUSTOM_IGNORE_FILE):
             with open(CUSTOM_IGNORE_FILE, 'w') as f:
                json.dump(config_data, f, indent=4)
        print(f"Warning: Rule '{value}' not found in section '{key}' of the active configuration.")


def list_current_ignores():
    """Displays the current ignore rules, prioritizing the custom file."""
    source_file = ""
    config_data = {}
    local_ignore_path = os.path.join(os.getcwd(), LOCAL_IGNORE_FILE)

    if os.path.exists(local_ignore_path):
        source_file = f"{local_ignore_path} (local project-specific)"
        try:
            with open(local_ignore_path, 'r') as f:
                config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error: The local file '{local_ignore_path}' is corrupt. Cannot display rules.", file=sys.stderr)
            return
        
    elif os.path.exists(CUSTOM_IGNORE_FILE):
        source_file = CUSTOM_IGNORE_FILE
        try:
            with open(CUSTOM_IGNORE_FILE, 'r') as f:
                config_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            print(f"Error: The file '{CUSTOM_IGNORE_FILE}' is corrupt. Using fallback.", file=sys.stderr)
            source_file = "default_ignore.json (fallback)"
            config_data = _load_default_ignore_config()
    else:
        source_file = "default_ignore.json (default)"
        config_data = _load_default_ignore_config()

    print(f"--- Showing rules from: '{source_file}' ---")
    names = config_data.get("names", [])
    patterns = config_data.get("patterns", [])
    extensions = config_data.get("extensions", [])

    print("\n[Names to ignore]")
    print("\n".join(f"- {name}" for name in names) if names else " (None)")
    print("\n[Patterns to ignore]")
    print("\n".join(f"- {pattern}" for pattern in patterns) if patterns else " (None)")
    print("\n[Extensions to ignore]")
    print("\n".join(f"- {ext}" for ext in extensions) if extensions else " (None)")
    print("\n-------------------------------------------------")


def _load_default_rules_content():
    """Loads the default rules content from the package."""
    try:
        with importlib.resources.files('mycontext').joinpath('default_rules.md').open('r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return ""


def get_rules_content(rules_filename=None):
    """
    Reads the rules content.
    - If rules_filename is specified, reads that file.
    - If not, looks for context_rules.md.
    - If not found, uses the package's default rules.
    """
    if rules_filename:
        if not os.path.exists(rules_filename):
            print(f"Error: The specified rules file '{rules_filename}' was not found.", file=sys.stderr)
            sys.exit(1)
        try:
            with open(rules_filename, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError as e:
            print(f"Error: Could not read the rules file '{rules_filename}': {e}", file=sys.stderr)
            sys.exit(1)
            
    if os.path.exists(RULES_FILE):
        try:
            with open(RULES_FILE, 'r', encoding='utf-8') as f:
                return f.read()
        except IOError:
            return _load_default_rules_content()
    return _load_default_rules_content()


def _ensure_custom_rules_exist():
    """Ensures that context_rules.md exists, creating it from the default if necessary."""
    if not os.path.exists(RULES_FILE):
        location_info = _get_config_location_info()
        print(f"Creating 'context_rules.md' from the default rules.")
        print(f"Location: {location_info}")
        default_content = _load_default_rules_content()
        try:
            with open(RULES_FILE, 'w', encoding='utf-8') as f:
                f.write(default_content)
        except IOError as e:
            print(f"Error creating '{RULES_FILE}': {e}", file=sys.stderr)
            return False
    return True


def add_rule(content):
    """Appends content to the end of the rules file, creating it if it doesn't exist."""
    if not _ensure_custom_rules_exist():
        return
    try:
        with open(RULES_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{content}\n")
        location_info = _get_config_location_info()
        print(f"Content added to 'context_rules.md'.")
        print(f"Location: {location_info}")
    except IOError as e:
        print(f"Error writing to '{RULES_FILE}': {e}", file=sys.stderr)


def list_rules():
    """Displays the content of the active rules file (custom or default)."""
    source_file = f"{RULES_FILE} (custom)" if os.path.exists(RULES_FILE) else "default_rules.md (default)"
    print(f"--- Rules content from: '{source_file}' ---")
    content = get_rules_content()
    print(content if content.strip() else "(No rules defined)")
    print("--------------------------------------------------")


def remove_rules_file():
    """Deletes the custom rules file."""
    if os.path.exists(RULES_FILE):
        try:
            os.remove(RULES_FILE)
            print(f"File '{RULES_FILE}' deleted successfully.")
        except OSError as e:
            print(f"Error deleting file '{RULES_FILE}': {e}", file=sys.stderr)
    else:
        print(f"The file '{RULES_FILE}' does not exist, nothing to do.")


def update_rules_with_editor():
    """Opens the rules file in the editor, creating it from the default if it doesn't exist."""
    if not _ensure_custom_rules_exist():
        return
        
    editor = os.getenv('EDITOR') or ('notepad' if os.name == 'nt' else 'vim')
    print(f"Opening '{RULES_FILE}' with '{editor}'...")
    try:
        subprocess.run([editor, RULES_FILE], check=True)
    except (FileNotFoundError, subprocess.CalledProcessError) as e:
        print(f"Error opening editor '{editor}': {e}", file=sys.stderr)
        print("Make sure your $EDITOR environment variable is set or the editor is in your PATH.", file=sys.stderr)



IGNORE_NAMES, IGNORE_PATTERNS, IGNORE_EXT = _load_ignore_config()


def has_content(path):
    """Checks if a file is not empty."""
    try:
        if os.path.getsize(path) == 0:
            return False
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return bool(f.read().strip())
    except (IOError, OSError):
        return False


def is_ignored(name):
    """Checks if a file or directory should be ignored."""
    if name in IGNORE_NAMES:
        return True
    if any(fnmatch.fnmatch(name, pattern) for pattern in IGNORE_PATTERNS):
        return True
    if name.endswith(tuple(IGNORE_EXT)):
        return True
    return False


def collect_files(paths):
    """Walks the paths and collects valid files."""
    files = []
    for path in paths:
        if os.path.isfile(path):
            name = os.path.basename(path)
            if name == RULES_FILE or is_ignored(name) or not has_content(path):
                continue
            files.append(path)
        elif os.path.isdir(path):
            for root, dirs, file_names in os.walk(path):
                dirs[:] = [d for d in dirs if not is_ignored(d)]
                for file in file_names:
                    if file == RULES_FILE or is_ignored(file):
                        continue
                    file_path = os.path.join(root, file)
                    if has_content(file_path):
                        files.append(file_path)
        else:
            print(f"Notice: '{path}' is not a valid file or directory, skipping.")
    return files


def _build_content(files, rules_content=""):
    """
    Internal function that builds the full context string.
    Used both for writing to file and copying to clipboard.
    """
    output = io.StringIO()
    
    output.write("Below, I will provide you with a set of rules and the source code of a project for you to analyze.\n\n")

    if rules_content.strip():
        output.write("### RULES AND GUIDELINES ###\n")
        output.write("First, these are the rules and context you must strictly follow for your analysis:\n\n")
        output.write("```markdown\n")
        output.write(rules_content.strip())
        output.write("\n```\n\n")
        output.write("### SOURCE CODE ###\n")
        output.write("Now, here is the source code of the project to which you must apply the above rules:\n\n")
    else:
        output.write("### SOURCE CODE ###\n")
        output.write("Analyze and validate the content of the following files:\n\n")

    for file in files:
        output.write(f"##### {file} #####\n")
        _, extension = os.path.splitext(file)
        lang = extension.lstrip('.')
        output.write(f"```{lang}\n") 
        try:
            with open(file, 'r', encoding='utf-8', errors='replace') as in_file:
                output.write(in_file.read())
        except Exception as e:
            output.write(f"[Error reading file: {e}]")
        output.write("\n```\n\n")
        
    return output.getvalue()


def join_files(files, output_file, rules_content=""):
    """Writes the built content to an output file."""
    full_content = _build_content(files, rules_content)
    try:
        with open(output_file, 'w', encoding='utf-8') as out_file:
            out_file.write(full_content)
        
        num_rules = 1 if rules_content.strip() else 0
        print(f"File '{output_file}' generated successfully with {num_rules} set of rules and {len(files)} files included.")
    except IOError as e:
        print(f"Error writing to file '{output_file}': {e}", file=sys.stderr)


def join_content_to_string(files, rules_content=""):
    """Returns the built content as a string."""
    return _build_content(files, rules_content)
