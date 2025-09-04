"""
This module builds python virtual envrionments
"""


import os
import shutil

from pydmt.utils.filesystem import mkdir_touch
from pydmt.utils.subprocess import check_call, check_call_ve
from pydmt.utils.python import collect_reqs, collect_bootstrap_reqs, get_install_args

from pydmt.api.one_source_one_target import OneSourceOneTarget
from pydmt.configs import ConfigVenv

SOURCE_FILE = "config/python.py"
TARGET_FOLDER = ".venv/default"
REQUIREMENTS = "requirements.txt"


class BuilderVenv(OneSourceOneTarget):
    """
    This is a review of how to build a python virtual environment:
    # create the virtualenv
    virtualenv [folder]
    # activate it
    source [folder]/bin/activate
    # install package
    pip install -r requirements.txt
    """
    def build(self) -> None:
        if ConfigVenv.incremental and os.path.isdir(TARGET_FOLDER):
            if os.path.isfile(REQUIREMENTS):
                args = get_install_args()
                args.extend(["-r", REQUIREMENTS])
                check_call_ve(args)
                mkdir_touch(self.target)
                return
            # now install regular packages (we only run the install if there are packages to install)
            packs = collect_reqs(add_dev=ConfigVenv.add_dev)
            if packs:
                args = get_install_args()
                args.extend(packs)
                check_call_ve(args)
            mkdir_touch(self.target)
            return
        # remove previous virtual env
        if os.path.isdir(TARGET_FOLDER):
            shutil.rmtree(TARGET_FOLDER)
        # create new virtual env
        args = [
            "virtualenv",
        ]
        if ConfigVenv.system_site_packages:
            args.append("--system-site-packages")
        args.append(TARGET_FOLDER)
        check_call(args)
        # upgrade pip if the condig says so
        if ConfigVenv.upgrade_pip:
            args = [
                "pip",
                "install",
                "--upgrade",
                "pip",
            ]
            check_call_ve(args)
        if os.path.isfile(REQUIREMENTS):
            args = get_install_args()
            args.extend(["-r", REQUIREMENTS])
            check_call_ve(args)
            mkdir_touch(self.target)
            return
        # install bootstrap packages so that we could read config/* files
        packs = collect_bootstrap_reqs()
        if packs:
            args = get_install_args()
            args.extend(packs)
            check_call_ve(args)
        # now install regular packages (we only run the install if there are packages to install)
        packs = collect_reqs(add_dev=ConfigVenv.add_dev)
        if packs:
            args = get_install_args()
            args.extend(packs)
            check_call_ve(args)
        mkdir_touch(self.target)
