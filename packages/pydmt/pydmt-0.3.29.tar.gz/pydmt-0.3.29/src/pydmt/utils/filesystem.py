"""
filesystem.py
"""

import os
import shutil


def makedirs_for_file(filename: str):
    folder = os.path.dirname(filename)
    if folder != "":
        os.makedirs(folder, exist_ok=True)


def copy_mkdir(source: str, destination: str):
    makedirs_for_file(destination)
    shutil.copy(source, destination)


def unlink_files(files: list[str], only_if_exist: bool = True) -> None:
    for file in files:
        if only_if_exist:
            if os.path.isfile(file):
                os.unlink(file)
        else:
            os.unlink(file)


def files_under_folder(folder: str, suffix: str | None = None) -> list[str]:
    file_list = []
    for dir_path, _, filenames in os.walk(folder):
        for filename in filenames:
            if suffix is None or filename.endswith(suffix):
                file_list.append(os.path.join(dir_path, filename))
    return sorted(file_list)


def files_under_folders(folders: list[str]) -> list[str]:
    file_list = []
    for folder in folders:
        file_list.extend(files_under_folder(folder))
    return sorted(file_list)


def touch(filename: str) -> None:
    with open(filename, "w"):
        pass


def mkdir_touch(filename: str) -> None:
    makedirs_for_file(filename)
    touch(filename)


def remove_files_by_suffix(folder:str, suffix:str, exceptions: list[str]):
    for filename in os.listdir(folder):
        file= os.path.join(folder, filename)
        if (
            os.path.isfile(file)
            and filename.endswith(suffix)
            and filename not in exceptions
        ):
            os.remove(file)
