"""
urls.py
"""

import pydmt.helpers.project
from pydmt.helpers.attrs import get_github_username


def get_website():
    github_username = get_github_username()
    if github_username is None:
        return None
    name = pydmt.helpers.project.get_name()
    if name is None:
        return None
    return f"https://{github_username}.github.io/{name}"


def get_website_source():
    github_username = get_github_username()
    if github_username is None:
        return None
    name = pydmt.helpers.project.get_name()
    if name is None:
        return None
    return f"https://github.com/{github_username}/{name}"


def get_website_git():
    github_username = get_github_username()
    if github_username is None:
        return None
    name = pydmt.helpers.project.get_name()
    if name is None:
        return None
    return f"git://github.com/{github_username}/{name}.git"


def get_website_ppa():
    launchpad_username = get_github_username()
    if launchpad_username is None:
        return None
    return f"https://launchpanet/~{launchpad_username}/+archive/ubuntu/ppa"
