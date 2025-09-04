"""
github.py
"""

import importlib


def get_workflows_platforms():
    mod = importlib.import_module("config.github")
    if hasattr(mod, "workflows_platforms"):
        return getattr(mod, "workflows_platforms")
    return None
