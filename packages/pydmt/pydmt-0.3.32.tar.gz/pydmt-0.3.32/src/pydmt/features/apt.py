"""
apt.py
"""

import os

from pydmt.api.feature import Feature
from pydmt.builders.apt import BuilderApt
from pydmt.core.pydmt import PyDMT
from pydmt.helpers.attrs import get_packages, get_packages_remove


class FeatureApt(Feature):
    def __init__(
        self,
    ):
        self.packages = get_packages()
        self.packages_remove = get_packages_remove()

    def setup(self, pydmt: PyDMT) -> None:
        if self.packages is None:
            return
        if not os.path.isfile("config/deps.py"):
            return
        pydmt.add_builder(BuilderApt(
            source="config/deps.py",
            target="out/deps.stamp",
            packages=self.packages,
            packages_remove=self.packages_remove,
        ))
