"""
misc.py
"""

import importlib


def get_version_str():
    mod = importlib.import_module("config.version")
    tup = getattr(mod, "tup")
    return ".".join(str(x) for x in tup)
