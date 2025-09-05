# Standard Libraries
from typing import NamedTuple

"""
Here are listed the metadata templates that are used to parse metadata
from image file names.
"""


class MetadataEntry(NamedTuple):
    """
    Represents one metadata entry that can pulled from a file name string.

    Parameters
    ----------
    label: str
        Name of the metadata field.
    fileposition: int
        Number of underscores before the entry in the full file name. For
        example, if the file name is VIC_2025, the "VIC" entry would have
        an `"underscoreindex"` of 0 and "2025" would be 1.
    startoffset: int
        Number of indices to exclude after the underscore at the start. For
        example, is the whole entry is "Sphere6.5", the `"startoffset"` would
        be 6 to exclude "Sphere" and include "6.5"
    endoffset: int
        Same as `"startoffset"`, but it counts from the ending underscore.
    datatype: type
        The expected data type of the metadata entry.
    include: bool
        If true, the offests are now included in the name and indices outside
        the offest positions are excluded.
    """
    label: str
    fileposition: int
    startoffset: int
    endoffset: int
    datatype: type
    include: bool = False
    numeric_only: bool = False
    expected_length: int | None = None


VIC_PRIMARY = [
    MetadataEntry("CAMERA", 0, 0, 0, str),
    MetadataEntry("YEAR", 1, 0, 0, int),
    MetadataEntry("MONTH", 2, 0, 0, int),
    MetadataEntry("DAY", 3, 0, 0, int),
    MetadataEntry("HOUR", 4, 0, 0, int),
    MetadataEntry("MINUTE", 5, 0, 0, int),
    MetadataEntry("SECOND", 6, 0, 0, int),
    MetadataEntry("DECIMAL", 7, 0, 0, int),
    MetadataEntry("CALTYPE", 8, 0, 0, str),
    MetadataEntry("IT", 9, 2, 0, int),
    MetadataEntry("DSSSTATE", 10, 6, 0, str),
    MetadataEntry("TARGWVL", 11, 0, 2, int),
    MetadataEntry("WVLUNIT", 11, 3, 0, str),
    MetadataEntry("TESTIDX", 12, 3, 0, int, include=True, numeric_only=True),
    MetadataEntry("TOTTESTS", 12, 0, 3, int, include=True, numeric_only=True)
]


VIC_NOISETEST = [
    MetadataEntry("CAMERA", 0, 0, 0, str),
    MetadataEntry("YEAR", 1, 0, 0, int),
    MetadataEntry("MONTH", 2, 0, 0, int),
    MetadataEntry("DAY", 3, 0, 0, int),
    MetadataEntry("HOUR", 4, 0, 0, int),
    MetadataEntry("MINUTE", 5, 0, 0, int),
    MetadataEntry("SECOND", 6, 0, 0, int),
    MetadataEntry("DECIMAL", 7, 0, 0, int),
    MetadataEntry("CALTYPE", 8, 0, 0, str),
    MetadataEntry("IT", 9, 2, 0, int),
    MetadataEntry("DSSSTATE", 10, 6, 0, str),
    MetadataEntry("NOISE", 11, 0, 0, str),
    MetadataEntry("TARGWVL", 12, 0, 2, int),
    MetadataEntry("TESTIDX", 13, 3, 0, int, include=True, numeric_only=True),
    MetadataEntry("TOTTESTS", 13, 0, 3, int, include=True, numeric_only=True)
]

VIC_OFFSET_ADJUST = [
    MetadataEntry("CAMERA", 0, 0, 0, str),
    MetadataEntry("YEAR", 1, 0, 0, int),
    MetadataEntry("MONTH", 2, 0, 0, int),
    MetadataEntry("DAY", 3, 0, 0, int),
    MetadataEntry("HOUR", 4, 0, 0, int),
    MetadataEntry("MINUTE", 5, 0, 0, int),
    MetadataEntry("SECOND", 6, 0, 0, int),
    MetadataEntry("DECIMAL", 7, 0, 0, int),
    MetadataEntry("CALTYPE", 8, 0, 0, str),
    MetadataEntry("IT", 9, 2, 0, int),
    MetadataEntry("DSSSTATE", 10, 6, 0, str),
    MetadataEntry("OFFSET", 11, 0, 2, int, include=True, numeric_only=True),
    MetadataEntry("TARGWVL", 12, 0, 2, int),
]

VIC_HAR = [
    MetadataEntry("CAMERA", 0, 0, 0, str),
    MetadataEntry("YEAR", 1, 0, 0, int),
    MetadataEntry("MONTH", 2, 0, 0, int),
    MetadataEntry("DAY", 3, 0, 0, int),
    MetadataEntry("HOUR", 4, 0, 0, int),
    MetadataEntry("MINUTE", 5, 0, 0, int),
    MetadataEntry("SECOND", 6, 0, 0, int),
    MetadataEntry("DECIMAL", 7, 0, 0, int),
    MetadataEntry("CALTYPE", 8, 0, 0, str),
    MetadataEntry("IT", 9, 2, 0, int),
    MetadataEntry("ALBEDO", 10, 6, 1, float),
    MetadataEntry("HARNUM", 11, 3, 0, int),
    MetadataEntry("DISPO", 12, 4, 0, int, numeric_only=True),
    MetadataEntry("TARGWVL", 13, 0, 2, int),
    MetadataEntry("TESTIDX", 14, 3, 0, int, include=True, numeric_only=True),
    MetadataEntry("TOTTESTS", 14, 0, 3, int, include=True, numeric_only=True)
]

VIC_TEMP_TESTS_IT_SWEEPS = [
    MetadataEntry("CAMERA", 0, 0, 0, str),
    MetadataEntry("YEAR", 1, 0, 0, int),
    MetadataEntry("MONTH", 2, 0, 0, int),
    MetadataEntry("DAY", 3, 0, 0, int),
    MetadataEntry("HOUR", 4, 0, 0, int),
    MetadataEntry("MINUTE", 5, 0, 0, int),
    MetadataEntry("SECOND", 6, 0, 0, int),
    MetadataEntry("DECIMAL", 7, 0, 0, int),
    MetadataEntry("CALTYPE", 8, 0, 0, str),
    MetadataEntry("IT", 9, 2, 0, int),
    MetadataEntry("DSSSTATE", 10, 6, 0, str),
    MetadataEntry("TEMP", 11, 4, 1, float),
    MetadataEntry("TESTIDX", 13, 3, 0, int, include=True, numeric_only=True),
    MetadataEntry("TOTTESTS", 13, 0, 3, int, include=True, numeric_only=True)
]


EDU_TEMP_TESTS = [
    MetadataEntry("CAMERA", 0, 0, 0, str),
    MetadataEntry("YEAR", 1, 0, 0, int),
    MetadataEntry("MONTH", 2, 0, 0, int),
    MetadataEntry("DAY", 3, 0, 0, int),
    MetadataEntry("HOUR", 4, 0, 0, int),
    MetadataEntry("MINUTE", 5, 0, 0, int),
    MetadataEntry("SECOND", 6, 0, 0, int),
    MetadataEntry("DECIMAL", 7, 0, 0, int),
    MetadataEntry("CALTYPE", 8, 0, 0, str),
    MetadataEntry("IT", 9, 2, 0, int),
    MetadataEntry("DSSCONF", 10, 0, 1, int, include=True),
    MetadataEntry("TEMP", 11, 4, 1, float),
    MetadataEntry("TARGWVL", 12, 0, 2, int),
    MetadataEntry("TESTIDX", 12, 3, 0, int, include=True, numeric_only=True),
    MetadataEntry("TOTTESTS", 12, 0, 3, int, include=True, numeric_only=True)
]


EDU_IT_SWEEPS = [
    MetadataEntry("CAMERA", 0, 0, 0, str),
    MetadataEntry("YEAR", 1, 0, 0, int),
    MetadataEntry("MONTH", 2, 0, 0, int),
    MetadataEntry("DAY", 3, 0, 0, int),
    MetadataEntry("HOUR", 4, 0, 0, int),
    MetadataEntry("MINUTE", 5, 0, 0, int),
    MetadataEntry("SECOND", 6, 0, 0, int),
    MetadataEntry("DECIMAL", 7, 0, 0, int),
    MetadataEntry("CALTYPE", 8, 0, 0, str),
    MetadataEntry("IT", 9, 2, 0, int)
]

# TEMPLATE_LIST = [VIC_IT_SWEEPS, EDU_IT_SWEEPS]
TEMPLATE_LIST = [
    VIC_NOISETEST,
    VIC_OFFSET_ADJUST,
    VIC_HAR,
    VIC_TEMP_TESTS_IT_SWEEPS,
    EDU_TEMP_TESTS,
    EDU_IT_SWEEPS
]
