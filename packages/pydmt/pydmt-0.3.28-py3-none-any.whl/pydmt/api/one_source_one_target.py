"""
one_source_one_target.py
"""

from collections.abc import Generator, Sequence
from pydmt.api.builder import Builder, SourceFile, TargetFile, Node
from pydmt.utils.digest import sha1_file


class OneSourceOneTarget(Builder):
    """
    This is a builder which has one source file and one target file
    """

    def __init__(self, source: str, target: str):
        # super().__init__()
        self.source = source
        self.target = target
        self.sources: Sequence[Node] = [SourceFile(filename=source)]
        self.targets: Sequence[Node] = [TargetFile(filename=target)]

    def get_sources(self) -> Sequence[Node]:
        return self.sources

    def get_targets(self) -> Sequence[Node]:
        return self.targets

    def yield_results(self) -> Generator[tuple[str, str], None, None]:
        yield sha1_file(self.target), self.target
