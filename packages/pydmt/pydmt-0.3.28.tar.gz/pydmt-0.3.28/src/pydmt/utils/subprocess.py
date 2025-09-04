"""
subprocess.py
"""

import os
import os.path
import subprocess

from pydmt.configs import ConfigSubprocess


def check_call(args: list[str]) -> None:
    if ConfigSubprocess.print_command:
        print(f"running {args}")
    if ConfigSubprocess.quiet:
        subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.check_call(args)


def check_call_ve_env(args: list[str]) -> None:
    virtual_env = os.getenv("VIRTUAL_ENV")
    assert virtual_env is not None, "not in virtual env"
    args[0] = os.path.join(virtual_env, "bin", args[0])
    if ConfigSubprocess.print_command:
        print(f"running {args}")
    if ConfigSubprocess.quiet:
        subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.check_call(args)


def check_call_ve(orig_args: list[str]) -> None:
    # we call "venv-run" with absolute path since it may change folder
    args = [
        "venv-run",
        "--venv",
        os.path.abspath(".venv/default"),
        "--",
    ]
    args.extend(orig_args)
    if ConfigSubprocess.print_command:
        print(f"running {args}")
    if ConfigSubprocess.quiet:
        subprocess.check_call(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.check_call(args)
