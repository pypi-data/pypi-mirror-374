# 🚀 mycontext

[![PyPI Version](https://img.shields.io/pypi/v/mycontext.svg)](https://pypi.org/project/mycontext/)
[![Build Status](https://img.shields.io/github/actions/workflow/status/MartinCastellano/mycontext/python-package.yml?branch=main)](https://github.com/MartinCastellano/mycontext/actions)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Versions](https://img.shields.io/pypi/pyversions/mycontext.svg)](https://pypi.org/project/mycontext/)

**Supercharge your interactions with LLMs by effortlessly creating clean, complete, and personalized context files directly from your source code.**

`mycontext` is a command-line tool (CLI) designed to eliminate the tedious task of copying and pasting code into large language models. It intelligently collects, filters, and formats your project's files into a single optimized prompt, ready for analysis.

![Demo Gif Placeholder](https://user-images.githubusercontent.com/1028795/203233214-32134f72-974a-4318-b219-b695279f684c.gif)

---

## 🤔 Why `mycontext`?

Copying and pasting code into LLMs is a slow and error-prone process:
- You forget important files.
- You include unnecessary files (`node_modules`, `.pyc`).
- You lose formatting or structure.
- You have to rewrite the same instructions over and over.

`mycontext` automates this workflow, allowing you to:
- **Save Time:** Generate a complete context in seconds.
- **Improve Quality:** Well-structured prompts produce better LLM responses.
- **Be Consistent:** Use reusable rule profiles to ensure the LLM always receives the same guidelines.
- **Work Faster:** Send the context directly to your clipboard and paste it into your LLM.

## ✨ Key Features

-   **Smart Collection:** Recursively scans directories and collects files.
-   **Exclusion Rules:** Comes with a sensible default list of files and folders to ignore (like `.git`, `__pycache__`), fully customizable.
-   **Rule Profiles (Powerful!):** Define how the LLM should behave with `.md` files. Use the default profile or specify one on the fly for different tasks (e.g., `security_audit.md`, `refactor_code.md`).
-   **Clipboard Integration:** Why save a file? Send the context directly to your clipboard with the `-c` option.
-   **Simple Management:** Intuitive commands to add/remove/list your exclusion and context rules.
-   **Modular and Extensible:** The command architecture makes it easy to add new features.

## 📦 Installation

### Prerequisites (for Linux users)

On Debian-based systems (like Ubuntu), you may need to install the `python3-venv` package, which is required to create virtual environments:
```bash
sudo apt update && sudo apt install python3-venv
```

You can install `mycontext` using `pip` (for Python environments) or `npm` (for Node.js environments).

### With pip
```bash
pip install mycontext
```

### With npm
```bash
npm install -g mycontext-node
```

## ⌨️ Usage and Commands

### Quick Guide

```bash
# 1. Generate a context from the current directory into a text file
mycontext .

# 2. Generate context and copy it directly to the clipboard (most used)
mycontext . -c

# 3. Use a specific rule profile for generation
mycontext ./src --rules ./docs/refactoring_rules.md

# 4. Generate context without applying any rules
mycontext . --no-rules

# 5. Combine everything: generate from 'src' with a profile and copy to clipboard
mycontext ./src --rules security_audit.md -c
```

### Command Reference

### Project-Specific Ignores with `.mycontext-ignore`

For more granular control, you can define ignore rules on a per-project basis by creating a **`.mycontext-ignore`** file in the root directory of your project.

If this file is present, it will take **highest priority**, overriding any global or default settings. The `add-ignore` and `remove-ignore` commands will not affect this file; it must be managed manually.

The `.mycontext-ignore` file must be a JSON file with the same structure as the default ignore configuration.

**Example `.mycontext-ignore`:**
```json
{
  "names": [
    "dist",
    "build",
    "docs"
  ],
  "patterns": [
    "*.test.js",
    "temp_*"
  ],
  "extensions": [
    ".env"
  ]
}
```

#### **Generate Context**
The default command. Runs if no other is specified.
- `mycontext [paths...]`: Generates context from the specified paths.
- `-o, --output [FILENAME]`: Saves the output to a specific file.
- `-r, --rules [RULES_FILE.md]`: Uses a custom rule profile for this run.
- `-c, --to-clipboard`: Copies the output to the clipboard instead of a file.
- `--no-rules`: Generates the context without including any rules file.

#### **Manage Exclusion Rules (Ignores)**
- `mycontext list-ignore`: Displays the current exclusion rules.
- `mycontext add-ignore [name|pattern|ext] [value]`: Adds a new rule to `custom_ignore.json`.
  - `mycontext add-ignore name "dist"`
- `mycontext remove-ignore [name|pattern|ext] [value]`: Removes a rule from `custom_ignore.json`.
  - `mycontext remove-ignore ext ".log"`

#### **Manage Context Rules**
- `mycontext list-rules`: Displays the active context rules (either custom or default).
- `mycontext add-rule "[CONTENT]"`: Adds a new line of text to the `context_rules.md` file.
- `mycontext update-rules`: Opens `context_rules.md` in your default text editor (`$EDITOR`).
- `mycontext remove-rules`: Deletes your custom `context_rules.md` file (reverts to the default).

## 🤝 Contributions

Contributions are welcome! If you have ideas for new features, improvements, or have found a bug, please open an issue on GitHub or submit a pull request.

## 📜 License

This project is licensed under the GNU General Public License v3 License. See the [LICENSE](LICENSE) file for details.
