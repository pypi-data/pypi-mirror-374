import os
from typing import *

import deprecation


def path_split_all(path: str) -> Tuple:
    """
    Split a given path into a list of its individual parts.

    This builds on os.path.split by doing it for all parts::

        >>> import os
        >>> os.path.split('/c/hey/there/hey.tif')
        ('/c/hey/there', 'hey.tif')
        >>> path_split_all('/c/hey/there/hey.tif')
        ('/', 'c', 'hey', 'there', 'hey.tif')
    """
    parts = []  # type: List[str]
    while True:
        split = os.path.split(path)
        if split[0] == path:
            parts.insert(0, split[0])
            break
        elif split[1] == path:
            parts.insert(0, split[1])
            break
        else:
            path = split[0]
            parts.insert(0, split[1])
    return tuple(parts)


@deprecation.deprecated("Use intelinair_utils.os_utils.list_all_files_in_dir instead")
def get_files(path: str, recursive=True, search_str=None) -> List[str]:
    """Get a list of all files within the directory"""

    def get_files_r(path, recursive):
        """Recursively processes a path returning an array of strings of file paths"""
        files = []  # type: List[str]
        path_str = os.path.join(*path)
        dir_files = os.listdir(path_str)
        dir_files.sort()
        for f in dir_files:
            local_path = os.path.join(path_str, f)
            if os.path.isfile(local_path):
                if search_str is not None:
                    if local_path.find(search_str) != -1:
                        files.append(local_path)
                else:
                    files.append(local_path)
            elif recursive and os.path.isdir(local_path):
                new_path = path + [f]
                files += get_files_r(new_path, recursive)
        return files

    path_parts = list(path_split_all(path))
    return get_files_r(path_parts, recursive)
