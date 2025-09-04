"""
attrs.py
"""

import importlib
from pydmt.utils.importlib import module_exists


def get_github_username():
    if not module_exists("config"):
        return None
    if not module_exists("config.personal"):
        return None
    mod = importlib.import_module("config.personal")
    if not hasattr(mod, "github_username"):
        return None
    return getattr(mod, "github_username")


def get_launchpad_username():
    if not module_exists("config"):
        return None
    if not module_exists("config.personal"):
        return None
    mod = importlib.import_module("config.personal")
    if not hasattr(mod, "launchpad_username"):
        return None
    return getattr(mod, "launchpad_username")


def get_packages():
    if not module_exists("config"):
        return None
    if not module_exists("config.deps"):
        return None
    mod = importlib.import_module("config.deps")
    if not hasattr(mod, "packages"):
        return None
    return getattr(mod, "packages")


def get_packages_remove():
    if not module_exists("config"):
        return None
    if not module_exists("config.deps"):
        return None
    mod = importlib.import_module("config.deps")
    if not hasattr(mod, "packages_remove"):
        return None
    return getattr(mod, "packages_remove")
