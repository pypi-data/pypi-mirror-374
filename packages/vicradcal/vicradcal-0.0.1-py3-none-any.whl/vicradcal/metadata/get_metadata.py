# Standard Libraries
from pathlib import Path
from datetime import datetime
from typing import Optional


def findall(my_string: str, char_to_find: str):
    return [i for i, char in enumerate(my_string) if char == char_to_find]


def metadata_from_template(
    filepath, metadata_template: dict, extra_metadata: dict | None = None
) -> dict[str, int | str]:
    """
    Returns a dictionary of metadata from a filepath string.

    Parameters
    ----------
    filepath: str
        Path to the image for which metadata will be obtained.
    metadata_template: dict
        Metadata template dictionary described in `metadata_templates.py`
    extra_metadata: dict, optional
        Any extra metadata not contained within the file name.

    Returns
    -------
    dict
        Dictionary of metadata labels and values.
    """
    filepath_split = Path(filepath).stem.__str__().split("_")
    if extra_metadata is None:
        extra_metadata = {}

    metadata = {}
    for md_entry in metadata_template:
        name_piece = filepath_split[md_entry.fileposition]

        if md_entry.include is False:
            str_val = name_piece[
                0
                + md_entry.startoffset : len(name_piece)  # noqa
                - md_entry.endoffset
            ]
        else:
            str_val = name_piece[0 : md_entry.startoffset]  # noqa
            str_val += name_piece[
                len(name_piece) - md_entry.endoffset :  # noqa
            ]

        if md_entry.numeric_only:
            str_val = "".join([i for i in str_val if i.isnumeric()])

        if md_entry.expected_length is not None:
            if len(str_val) != md_entry.expected_length:
                raise ValueError(f"{str_val} is not the expected length")

        metadata[md_entry.label] = md_entry.datatype(str_val)

    metadata["RAWFILE"] = Path(filepath).name

    metadata = {**metadata, **extra_metadata}

    return metadata


def metadata_from_dir(
    directory: str, options: Optional[dict] = None, **kwargs
) -> tuple[list[str], list[dict]]:
    """
    Reads the metadata provided in the filenames of a directory.

    Parameters
    ----------
    directory: str
        File path to the data directory.
    options: dict, options
        Specifications on how to extract metadata from files.

    - "'universal_metadata'" (dict or None, default: None): A dictionary
        of metadata to be applied to every file in the directory

    **kwargs
        Will be passed into options as key-value pairs.

    Returns
    -------
    list of str, list of dicts
        List of filepath strings and a list of metadata dictionaries
        corresponding to those filepaths.
    """
    if options is None:
        options = {}
    options = {**options, **kwargs}

    filenames = [Path(directory, i).name for i in Path(directory).iterdir()]

    md_dict_list = []

    for i in filenames:
        md_dict: dict[str, str | int] = {}

        # Indices for all underscores separating data
        data_sep = findall(str(i), "_")

        # Pulling date time info
        dt_str = str(i)[data_sep[0] + 1 : data_sep[7]]  # noqa
        fmt = "%Y_%m_%d_%H_%M_%S_%f"
        dt = datetime.strptime(dt_str, fmt)
        md_dict["Year"] = dt.year
        md_dict["Month"] = dt.month
        md_dict["Day"] = dt.day
        md_dict["Time"] = dt.strftime("%H:%M:%S")

        # Pulling Testing config info
        md_dict["IT"] = int(str(i)[data_sep[8] + 3 : data_sep[9]])  # noqa
        md_dict["DSSlvl"] = int(
            str(i)[data_sep[9] + 7 : data_sep[10] - 1]  # noqa
        )
        md_dict["TargWvl"] = int(
            str(i)[data_sep[10] + 1 : data_sep[11] - 2]  # noqa
        )

        # Pulling other file information
        md_dict["datfile"] = str(i)

        # Adding universal metadata
        uni_md = options.get("universal_metadata", None)
        if uni_md is not None:
            md_dict = {**md_dict, **uni_md}

        md_dict_list.append(md_dict)

    return filenames, md_dict_list


def metadata_from_filepath(filepath: str):
    md_dict: dict[str, str | int] = {}
    filename = Path(filepath).name
    # Indices for all underscores separating data
    data_sep = findall(filename, "_")

    # Pulling date time info
    dt_str = filename[data_sep[0] + 1 : data_sep[7]]  # noqa
    fmt = "%Y_%m_%d_%H_%M_%S_%f"
    dt = datetime.strptime(dt_str, fmt)
    md_dict["Year"] = dt.year
    md_dict["Month"] = dt.month
    md_dict["Day"] = dt.day
    md_dict["Time"] = dt.strftime("%H:%M:%S")

    # Pulling Testing config info
    md_dict["IT"] = int(filename[data_sep[8] + 3 : data_sep[9]])  # noqa
    md_dict["DSSlvl"] = int(
        filename[data_sep[9] + 7 : data_sep[10] - 1]  # noqa
    )
    md_dict["TargWvl"] = int(
        filename[data_sep[10] + 1 : data_sep[11] - 2]  # noqa
    )

    # Pulling other file information
    md_dict["datfile"] = filename

    return md_dict
