"""
This module runs make
"""


import os
from pydmt.utils.filesystem import mkdir_touch
from pydmt.utils.subprocess import check_call_ve

from pydmt.api.one_source_one_target import OneSourceOneTarget


class BuilderMake(OneSourceOneTarget):
    def build(self) -> None:
        args = [
            "make",
        ]
        if "GITHUB_WORKFLOW" in os.environ:
            # TODO: Im assuming here that there is no previous MAKEFLAGS variable. Not good.
            # -j will cause endless parallel jobs to be run and that is why we add the number
            # of cores
            os.environ["MAKEFLAGS"] = f"-j{os.cpu_count()}"
        check_call_ve(args)
        mkdir_touch(self.target)
