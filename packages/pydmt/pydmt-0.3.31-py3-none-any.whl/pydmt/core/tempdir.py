"""
tempdir.py
"""

import contextlib
import os
import shutil
import tempfile
from collections.abc import Callable


@contextlib.contextmanager
def cd(new_dir: str, cleanup: Callable):
    prev_dir = os.getcwd()
    os.chdir(os.path.expanduser(new_dir))
    try:
        yield
    finally:
        os.chdir(prev_dir)
        cleanup()


@contextlib.contextmanager
def tempdir():
    dir_path = tempfile.mkdtemp()

    def cleanup():
        shutil.rmtree(dir_path)
    with cd(dir_path, cleanup):
        yield dir_path
