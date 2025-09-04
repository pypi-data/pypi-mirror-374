"""
digest.py
"""

import hashlib

from pydmt.utils.filesystem import files_under_folders


BLOCK_SIZE = 65536


def hex_digest_files(filenames: list[str], algorithm_name: str) -> str:
    hash_object = hashlib.new(algorithm_name)
    for filename in filenames:
        with open(filename, "rb") as file_handle:
            buf = file_handle.read(BLOCK_SIZE)
            while len(buf) > 0:
                hash_object.update(buf)
                buf = file_handle.read(BLOCK_SIZE)
    return hash_object.hexdigest()


def hex_digest_file(filename: str, algorithm_name: str) -> str:
    return hex_digest_files(filenames=[filename], algorithm_name=algorithm_name)


def sha1_file(filename: str) -> str:
    return hex_digest_file(filename=filename, algorithm_name="sha1")


def sha1_files(filenames: list[str]) -> str:
    return hex_digest_files(filenames=filenames, algorithm_name="sha1")


def sha1_folders(folders: list[str]) -> str:
    return sha1_files(filenames=files_under_folders(folders=folders))


def sha1_files_folders(files: list[str], folders: list[str]) -> str:
    f = files
    f.extend(files_under_folders(folders=folders))
    return sha1_files(f)
