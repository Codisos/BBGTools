""" Init BBG Tools """

import sys
import importlib
import os

bl_info = {
    "name": "BBG",
    "description": "BBG Tools",
    "author": "BBG",
    "version": (1, 0, 7),
    "blender": (4, 2, 0),
    "location": "VIEW_3D",
}

# Ensure Blender can find the module
script_path = os.path.dirname(os.path.abspath(__file__))
if script_path not in sys.path:
    sys.path.append(script_path)

module_names = [
    ('.main.BBG', 'BBG')  # Ensure correct module path
]

def register():
    """ Register classes """
    for name, package in module_names:
        mod = importlib.import_module(name, package)
        importlib.reload(mod)  # Ensure latest version loads

        # Only call register() if the module has it
        if hasattr(mod, 'register') and callable(mod.register):
            mod.register()


def unregister():
    """ Unregister classes """
    for name, package in reversed(module_names):
        mod_name = package + '.' + name
        mod = sys.modules.get(mod_name)
        if mod and hasattr(mod, 'unregister') and callable(mod.unregister):
            mod.unregister()

