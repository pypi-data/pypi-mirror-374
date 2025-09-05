# split_repeated_images.py

# Standard Libraries
from pathlib import Path

# Dependencies
import numpy as np
from tqdm import tqdm  # type: ignore
from astropy.io import fits  # type: ignore

# Top-Level Imports
from vicradcal.io import read_dat
from vicradcal.utils import get_filepaths, get_options_errors
from vicradcal.metadata import metadata_from_template


def save_sweep(
    data_arr: np.ndarray,
    bias_frame_mean: np.ndarray,
    bias_frame_var: np.ndarray,
    metadata: dict,
    save_type: str,
    save_name: str,
):
    """
    Saves 3D numpy array to various types of fits file.

    Parameters
    ----------
    data_arr: ndarray
        Data to be saved. Must be 3D. Third dimension is IT Sweep domain.
    metadata: dict
        metadata dictionary.
    save_type: str
        Specifies how exactly to save the data. Options are:

        - `'mean'`: Saves the mean of the 3D array along axis 2.
        - `'mean_nobias'`: Same as the 'mean' but the bias is removed.
        - `'single'`: Saves a single NxM image, selected along axis 2.
        - `'single_nobias'`: Same as the 'single' but the bias is removed.

    save_name: str
        File name to save the fits file to.

    bf: BiasFrame or None, optional
        Bias frame object must be passed if a 'nobias' `save_type` is used
        (default: None).
    """
    rng = np.random.default_rng()

    valid_save_types = ["mean", "mean_nobias", "single", "single_nobias"]
    if save_type not in valid_save_types:
        raise ValueError(
            get_options_errors(
                save_type, valid_save_types, option_name="save type"
            )
        )

    # Select the primary array based on save type
    if save_type in {"mean", "mean_nobias"}:
        primary_arr = np.mean(data_arr, axis=2)  # taking mean
    elif save_type in {"single", "single_nobias"}:
        idx = rng.integers(0, data_arr.shape[2])  # randomizing selection
        primary_arr = data_arr[:, :, idx].astype(float)
    else:
        raise ValueError("Invalid Save Type.")

    # Remove bias if needed
    if "nobias" in save_type:
        primary_arr -= bias_frame_mean  # Subtracting bias!

    # Create the primary HDU and update metadata
    primary_hdu = fits.PrimaryHDU(primary_arr)
    for key, val in metadata.items():
        primary_hdu.header[key] = val

    # Save the FITS file
    if "mean" in save_type:
        secondary_arr = np.var(data_arr, axis=2)
        secondary_arr += bias_frame_var  # Accounting for bias variance!
        secondary_hdu = fits.ImageHDU(secondary_arr, name="VARIANCE")
        hdul = fits.HDUList([primary_hdu, secondary_hdu])
        hdul.writeto(save_name, overwrite=True)
    else:
        primary_hdu.writeto(save_name, overwrite=True)


def split_repeated_images(
    itsweep_directory: str,
    bias_frame_mean: np.ndarray,
    bias_frame_var: np.ndarray,
    save_directory: str,
    metadata_template: dict,
    num_images: int = 100,
    extra_metadata: dict | None = None,
):
    """
    Converts a directory of raw .dat files of repeated images and saves them as
    a series of FITS files into a seperate directory. The output directory will
    follow the file tree outlined below:

    save_directory/\n
    ├── means\n
    │   ├── IT1.FITS\n
    │   ├── IT2.FITS\n
    │   :\n
    │   └── ITN.FITS\n
    ├── means_nobias\n
    │   :\n
    │   └── ITN.FITS\n
    ├── singles\n
    │   :\n
    │   └── ITN.FITS\n
    ├── singles_nobias\n
    │   :\n
    │   └── ITN.FITS\n

    Parameters
    ----------
    itsweep_directory: string
        File path to directory containing raw IT sweep .dat files.
    save_directory: string
        File path to directory where new files will be saved.
    metadata_template: dict
        Metadata template defined in `metadata_templates.py`
    bf: BiasFrame
        Bias frame object.
    num_images: int, optional (default: 100)
        Number of images in the IT sweep.
    extra_metadata: dict
        Extra metadata to pass alongside that obtained from metadata template.

    Returns
    -------
    None

    Raises
    ------
    None
    """
    incomplete_save = False

    # Setting subdirectory names
    means_dir = Path(save_directory, "means")
    means_nobias_dir = Path(save_directory, "means_nobias")

    singles_dir = Path(save_directory, "singles")
    singles_nobias_dir = Path(save_directory, "singles_nobias")

    dir_list = [means_dir, means_nobias_dir, singles_dir, singles_nobias_dir]

    # Returns directory name and list of filepaths
    itdir, itfp = get_filepaths(itsweep_directory)

    if not Path(save_directory).exists():
        Path(save_directory).mkdir(parents=True)
        incomplete_save = True

    else:
        file_counts = [sum([1 for _ in i.iterdir()]) for i in dir_list]
        if not all([i == len(itfp) for i in file_counts]):
            print(f"Partial save detected, overwriting {save_directory}.")
            incomplete_save = True

    if incomplete_save:
        print(f"Processing {itsweep_directory}...")
        md_list = [
            metadata_from_template(i, metadata_template, extra_metadata)
            for i in itfp
        ]

        # Making subdirectories but checking if they exist and have files.
        for i in dir_list:
            if i.is_dir():
                num_files = sum(1 for _ in i.iterdir())
                if num_files == 0:
                    i.rmdir()
                    i.mkdir()
            else:
                i.mkdir()

        # Saving means, and singles with and without bias subtraction
        pbar = tqdm(
            itfp, desc=f"Reading 0 of {len(itfp)} Files:", total=len(itfp)
        )
        for n, p in enumerate(pbar):
            pbar.desc = f"Reading {n+1} of {len(itfp)} Files"

            filename = f"IT{md_list[n]["IT"]}"
            save_paths = [
                Path(means_dir, filename).with_suffix(".fits"),
                Path(means_nobias_dir, filename).with_suffix(".fits"),
                Path(singles_dir, filename).with_suffix(".fits"),
                Path(singles_nobias_dir, filename).with_suffix(".fits"),
            ]

            all_exist = all(path.exists() for path in save_paths)

            save_types = ["mean", "mean_nobias", "single", "single_nobias"]

            if not all_exist:
                data_arr = read_dat(p, num_images=num_images)

                for m, i in enumerate(save_paths):
                    save_sweep(
                        data_arr,
                        bias_frame_mean,
                        bias_frame_var,
                        md_list[n],
                        save_types[m],
                        str(i),
                    )
            else:
                print(f"All fits files exist for: {p}")
    else:
        print(f"All fits files saved in {save_directory}")
