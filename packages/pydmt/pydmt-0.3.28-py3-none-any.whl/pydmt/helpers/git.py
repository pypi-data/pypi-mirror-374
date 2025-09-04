"""
git.py
"""

import subprocess


def get_git_last_tag() -> str:
    """ return the output of git describe --tag """
    return subprocess.check_output(
        ["git", "describe", "--abbrev=0", "--tags"],
        stderr=subprocess.DEVNULL,
    ).decode().rstrip()


def get_git_describe() -> str:
    """ return the output of git describe """
    return subprocess.check_output(
        ["git", "describe"],
        stderr=subprocess.DEVNULL,
    ).decode().rstrip()


def get_git_version() -> str:
    """ get version by git """
    return ".".join(get_git_describe().split("-"))


def count_files(pattern: str) -> int:
    """ Count the number of sources files of a certain pattern """
    return int(subprocess.check_output(f"git ls-files -- \"{pattern}\" | wc -l", shell=True).decode().rstrip())
