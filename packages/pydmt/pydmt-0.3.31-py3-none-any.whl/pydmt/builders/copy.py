"""
copy.py
"""

from collections.abc import Generator

from pydmt.api.builder import Builder, Node, SourceFile, TargetFile
from pydmt.utils.filesystem import copy_mkdir
from pydmt.utils.digest import sha1_file


class BuilderCopy(Builder):
    def __init__(self,
                 source: str,
                 target: str,
                 ):
        # super().__init__()
        self.source = source
        self.sources: list[Node] = [SourceFile(self.source)]
        self.target = target
        self.targets: list[Node] = [TargetFile(self.target)]

    def get_sources(self) -> list[Node]:
        return self.sources

    def get_targets(self) -> list[Node]:
        return self.targets

    def build(self):
        copy_mkdir(self.source, self.target)

    def yield_results(self) -> Generator[tuple[str, str], None, None]:
        yield sha1_file(self.target), self.target
