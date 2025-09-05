# Standard Libraries
from pathlib import Path
import os

# Dependencies
from astropy.io import fits
from astropy.table import Table
from tqdm import tqdm
import numpy as np

# Top-Level Imports
from vicradcal.constants import VIC_IMAGE_SIZE


class ITsweepFitsFiles:
    """
    Stores file path information for a processed set of ITSweep FITS files.

    Parameters
    ----------
    root_dir: str
        Path to root directory with the following file structure:
        ```
        root_dir
        ├───means
        │   ├───IT1.fits
        │   ├───IT2.fits
        │   ├───etc...
        ├───means_nobias
        │   ├───etc...
        ├───singles
        │   ├───etc...
        ├───singles_nobias
        │   ├───etc...
        ├───ffcorr
        │   ├───etc...
        ├───flatfield_references
        │   ├───...band1.fits
        │   ├───...band2.fits
        │   ├───all bands that are applicable.
        └───flatfield.fits
        ```
    """
    def __init__(self, root_dir: str | os.PathLike) -> None:
        self.root = Path(root_dir)
        self.means = Path(root_dir, "means")
        self.means_nb = Path(root_dir, "means_nobias")
        self.sings = Path(root_dir, "singles")
        self.sings_nb = Path(root_dir, "singles_nobias")
        self.ffcorr = Path(root_dir, "ffcorr")
        self.flatfield = Path(root_dir, "flatfield.fits")

    def validate_paths(self):
        data_dirs = [
            self.means,
            self.means_nb,
            self.sings,
            self.sings_nb,
            self.ffcorr
        ]

        missing_dirs = [
            path for path in data_dirs if not path.exists()
        ]

        if len(missing_dirs) > 0:
            raise FileNotFoundError(f"Missing directories: {missing_dirs}")

        num_files = [
            sum(1 for _ in p.iterdir()) for p in data_dirs
        ]

        if len(set(num_files)) > 1:
            raise ValueError(f"Invalid file counts: {num_files}")

        for i in data_dirs:
            file_exts = [p.suffix for p in i.iterdir()]
            if not all([True for e in file_exts if e == ".fits"]):
                raise ValueError("Invalid file extension encountered in"
                                 f"{i} directory.")

        return True


def condense_fits(root_dir: str, options: dict = None, **kwargs):
    """
    Condenses ITSweep directory FITS files for 2D image into a single 3D image
    FITS file with appropriate labels in the header.

    Parameters
    ----------
    root_dir: str
        Path to root directory with the following file structure:
        ```
        root_dir
        ├───means
        │   ├───IT1.fits
        │   ├───IT2.fits
        │   ├───etc...
        ├───means_nobias
        │   ├───etc...
        ├───singles
        │   ├───etc...
        ├───singles_nobias
        │   ├───etc...
        ├───ffcorr
        │   ├───etc...
        ├───flatfield_references
        │   ├───...band1.fits
        │   ├───...band2.fits
        │   ├───all bands that are applicable.
        └───flatfield.fits
        ```
    options: dict, optional
        Options for which files to condense. If None, defaults will be passed.
        Default is None. Options are:

        - `"means"`: Bool (default: True)
        - `"means_nb"`: Bool (default: True)
        - `"sings"`: Bool (default: True)
        - `"sings_nb"`: Bool (default: True)
        - `"ffcorr"`: Bool (default: True)
    **kwargs
        Will be passed to options dictionary as key-value pairs.
    """
    default_options = {
        "means": True,
        "means_nb": True,
        "sings": True,
        "sings_nb": True,
        "ffcorr": True
    }

    invalid_kwargs = [i for i in kwargs.keys() if i not in default_options]
    if len(invalid_kwargs) > 0:
        if len(invalid_kwargs) == 1:
            raise ValueError(f"{invalid_kwargs[0]} is an invalid option.")
        else:
            raise ValueError("The following invalid options were "
                             f"passed: {invalid_kwargs}")

    if options is None:
        options = {**default_options, **kwargs}
    else:
        options = {**default_options, **options, **kwargs}

    activated_keys = [key for key, val in options.items() if val]

    isf = ITsweepFitsFiles(root_dir)

    for n, name in enumerate(activated_keys):
        fp = getattr(isf, name)
        nfiles = sum([1 for i in fp.iterdir()])

        pbar = tqdm(
            fp.iterdir(), desc=f"Reading 0 of {nfiles} ", total=nfiles
        )

        savepath = Path(fp.parent, f"{name}.fits")

        if name not in ["means", "means_nb", "ffcorr"]:
            cube = np.empty([*VIC_IMAGE_SIZE, nfiles])
            itarray = np.empty(nfiles, dtype=int)
            for file_num, i in enumerate(pbar):
                pbar.desc = f"Reading {file_num+1} of {nfiles}"
                with fits.open(i) as hdul:
                    cube[:, :, file_num] = hdul[0].data
                    itarray[file_num] = int(hdul[0].header["IT"])

            cube = cube[:, :, np.argsort(itarray)]
            cube = np.moveaxis(cube, 2, 0)

            hdu = fits.PrimaryHDU(cube)
            table = Table([itarray], names=['ITLabels'])
            meta_hdu = fits.BinTableHDU(table, name='ITLabels')
            hdul = fits.HDUList([hdu, meta_hdu])
            hdul.writeto(savepath, overwrite=True)
            print(f"Condensed {name} saved as: {savepath}")

        else:
            mean_cube = np.empty([*VIC_IMAGE_SIZE, nfiles])
            var_cube = np.empty([*VIC_IMAGE_SIZE, nfiles])
            itarray = np.empty(nfiles, dtype=int)
            for file_num, i in enumerate(pbar):
                pbar.desc = f"Reading {file_num+1} of {nfiles} "
                with fits.open(i) as hdul:
                    mean_cube[:, :, file_num] = hdul[0].data
                    var_cube[:, :, file_num] = hdul[1].data
                    itarray[file_num] = int(hdul[0].header["IT"])

            mean_cube = mean_cube[:, :, np.argsort(itarray)]
            var_cube = var_cube[:, :, np.argsort(itarray)]

            mean_cube = np.moveaxis(mean_cube, 2, 0)
            var_cube = np.moveaxis(var_cube, 2, 0)

            primary_hdu = fits.PrimaryHDU(mean_cube)

            secondary_hdu_name = "VARIANCE"

            secondary_hdu = fits.ImageHDU(var_cube, name=secondary_hdu_name)
            table = Table([np.sort(itarray)], names=['ITLabels'])
            meta_hdu = fits.BinTableHDU(table, name='ITLabels')
            hdul = fits.HDUList([primary_hdu, secondary_hdu, meta_hdu])
            hdul.writeto(savepath, overwrite=True)
            print(f"Condensed {name} saved as: {savepath}")
