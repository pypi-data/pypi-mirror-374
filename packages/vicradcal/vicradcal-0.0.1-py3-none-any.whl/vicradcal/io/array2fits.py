# Standard Libraries
from pathlib import Path
import os
from typing import Optional

# Dependencies
import numpy as np
from astropy.io import fits  # type: ignore

# Top-level Imports

# Relative Imports


def array2fits(arr: np.ndarray,
               save_name: str | os.PathLike,
               metadata: Optional[dict] = None,
               silent: bool = False) -> None:
    """
    Saves a numpy arr to a fits file.

    Parameters
    ----------
    arr: np.ndarray
        Array of values to save to FITS file.
    save_name: str
        File path to save FITS file.
    metadata: dict or None
        Dictionary of metadata, default is None.
    silent: bool
        Toggles whether or not to print save confirmation.

    Returns
    -------
    None

    Raises
    ------
    None
    """

    hdu = fits.PrimaryHDU(arr)

    if metadata is not None:
        hdr = hdu.header
        for key, value in metadata.items():
            hdr[key] = value

    save_name = Path(save_name)
    if not save_name.parent.exists():
        save_name.parent.mkdir(parents=True, exist_ok=False)

    hdu.writeto(save_name,
                overwrite=True)

    if not silent:
        print(f"Array saved to {save_name}")

    return None
