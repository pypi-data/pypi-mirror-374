"""
project.py
"""

import importlib


def get_name():
    """ this gives you the name of the project, this must exist """
    mod = importlib.import_module("config.project")
    return getattr(mod, "name")
