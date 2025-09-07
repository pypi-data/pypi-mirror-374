##### ./src/mycontext/commands/__init__.py #####
import pkgutil
import importlib

def register_commands(subparsers):
    for _, name, _ in pkgutil.iter_modules(__path__, __name__ + '.'):
        module = importlib.import_module(name)
        if hasattr(module, 'register_subparser'):
            module.register_subparser(subparsers)