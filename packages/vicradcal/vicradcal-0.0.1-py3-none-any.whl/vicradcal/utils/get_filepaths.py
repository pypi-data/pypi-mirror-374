# Standard Libraries
from pathlib import Path
import os


def get_filepaths(
    dirpath: str,
    return_path_objects: bool = True
) -> tuple[str | os.PathLike, list]:
    """
    Returns the directory and the files within.

    Parameters
    ----------
    dirpath: string
        Filepath to directory
    return_path: boolean, optional (default = True)
        Determines whether or not the paths are returned as Path objects

    Returns
    -------
    tuple of strings
        First entry is the directory path, the second is the list of files.
    """
    filepaths = [Path(dirpath, i) for i in Path(dirpath).iterdir()]
    if return_path_objects:
        return Path(dirpath), filepaths
    else:
        return dirpath.__str__(), [i.__str__() for i in filepaths]
