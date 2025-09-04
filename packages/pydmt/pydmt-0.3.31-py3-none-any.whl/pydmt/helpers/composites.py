"""
composites.py
"""

import pydmt.helpers.apt
import pydmt.helpers.git

def get_deb_version():
    return f"{pydmt.helpers.git.get_git_version()}~{pydmt.helpers.apt.codename}"
