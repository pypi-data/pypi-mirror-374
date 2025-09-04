"""
npm.py
"""

import os.path

from pydmt.api.feature import Feature
from pydmt.builders.npm import Installer
from pydmt.core.pydmt import PyDMT


class FeatureNpm(Feature):
    def setup(self, pydmt: PyDMT) -> None:
        if not os.path.isfile("package.json"):
            return
        pydmt.add_builder(Installer(
            source="package.json",
            target="out/npm.stamp",
        ))
