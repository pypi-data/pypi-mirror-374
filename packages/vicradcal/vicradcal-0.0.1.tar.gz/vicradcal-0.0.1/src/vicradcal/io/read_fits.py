# Standard Libraries
import os

# Dependencies
import numpy as np
from astropy.io import fits  # type: ignore

# Top-Level Imports

# Relative Imports


def read_fits(
    filepath: str | os.PathLike, hdu_num: int = 0, dims: int = 3
) -> tuple[np.ndarray, np.ndarray]:
    """
    Reads a FITS file and returns an array.

    Parameters
    ----------
    filepath: str
        File path to FITS file.
    hdu_num: int
        HDU to read the data from.
    dims: int, default = 3
        Number of dimensions for the dataset.
    return_metadata: bool, default = True
        Toggles the return of the metadata dict from the HDU

    Returns
    -------
    data
        FITS data in a numpy array representing main dataset.
    data_var
        Represents the variance in `data`.
    """
    if dims == 3:
        with fits.open(filepath) as hdul:
            data = hdul[hdu_num].data  # type: ignore
            data_var = hdul["VARIANCE"].data  # type: ignore
        return data, data_var
    else:
        raise ValueError("Number of dims not supported!")


def read_ITsweep(
    filepath: str | os.PathLike, hdu_num: int = 0, dims: int = 3
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if dims == 3:
        with fits.open(filepath) as hdul:
            data = hdul[hdu_num].data  # type: ignore
            data_var = hdul["VARIANCE"].data  # type: ignore
            it_labels = hdul["ITLABELS"].data["ITLabels"]  # type: ignore
        return data, data_var, it_labels
    else:
        raise ValueError("Number of dims not supported!")
