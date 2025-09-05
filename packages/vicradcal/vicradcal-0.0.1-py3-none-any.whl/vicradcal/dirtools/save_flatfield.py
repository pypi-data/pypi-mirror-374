# Standard Libraries
from pathlib import Path
import os

# Dependencies
from astropy.io import fits  # type: ignore
import numpy as np
from tqdm import tqdm  # type: ignore

# Top-Level Imports
from vicradcal.io import read_dat_large, read_fits
from vicradcal.constants import VIC_IMAGE_SIZE
from vicradcal.masking import FlatFieldMask, FilterMask


def save_flatfield_reference(
    ffref_path: str | os.PathLike,
    bias_frame_mean: np.ndarray,
    bias_frame_var: np.ndarray,
    save_directory: str | os.PathLike,
    save_name: str | os.PathLike,
    num_images: int = 1000,
    extra_metadata: dict | None = None,
):
    """
    Converts a single flatfield reference file to a flatfield .fits file.

    Parameters
    ----------
    ffref_path: string
        File path to flatfield reference image.
    bf: BiasFrame
        Bias frame to be subtracted from flat field reference.
    save_directory: string
        File path for the save directory for flatfield reference images.
        If directory does not exist, it will be created.
    save_name: string
        Name to save the .fits file to within the `save_directory`.
    num_images: int
        Number of images in the flatfield reference image.
    extra_metadata: dict
        Extra metadata to be added on top of the metadata obtained from the
        filename.
    """

    if not Path(save_directory).exists():
        print(f"Making {save_directory}")
        Path(save_directory).mkdir(parents=True)

    # Getting flatfield reference
    mean_ff, var_ff = read_dat_large(
        str(ffref_path), image_size=VIC_IMAGE_SIZE, num_images=num_images
    )
    mean_ff -= bias_frame_mean  # Subtracting bias!
    var_ff += bias_frame_var  # Incorporating bias variance!

    primaryHDU = fits.PrimaryHDU(mean_ff)
    varHDU = fits.ImageHDU(var_ff, name="VARIANCE")
    if extra_metadata is not None:
        for key, val in extra_metadata.items():
            primaryHDU.header[key] = val
    hdul = fits.HDUList([primaryHDU, varHDU])
    hdul.writeto(Path(save_directory, save_name), overwrite=True)
    print(f"Saved to: {Path(save_directory, save_name)}")


def save_flatfield_frame(
    flatfield_ref_pointer: str | os.PathLike,
    flatfield_labels: list,
    flatfield_regions: dict,
    filter_boundaries: dict,
    save_dir: str,
    image_size: tuple = VIC_IMAGE_SIZE,
):
    """
    Using a directory of flatfield references images (FITS files only!), each
    representing one filter band, save a singular flatfield image called
    "flatfield.fits"

    Parameters
    ----------
    flatfield_ref_pointer: string
        File path to flatfield reference directory. Should be as many files
        as there are filter bands (7 for VIC, 6 for EDU).
    flatfield_labels: list
        List of filters in the flatfield frame
    flatfield_regions: dict
        Flat field regions dictionary. See `constants.py`.
    filter_boundaries: dict
        Filter boundary dictionary. See `constants.py`.
    save_dir: str
        Flat field images will be saved within this directory as
        "flatfield.fits".
    image_size: tuple of int, optional
        Size of an entire image panel. Default is cnst.VIC_IMAGE_SIZE.
    """
    if Path(flatfield_ref_pointer).is_dir():
        ffref_dir = Path(flatfield_ref_pointer)

        nfiles = sum([1 for _ in ffref_dir.iterdir()])
        whole_flatfield = np.zeros(image_size)
        whole_flatfield_var = np.zeros(image_size)

        pbar = tqdm(
            ffref_dir.iterdir(), desc=f"0 of {nfiles} read: ", total=nfiles
        )

        for n, ffref_path in enumerate(pbar):
            pbar.desc = f"{n+1} of {nfiles} read: "
            ffref_img, ffref_err = read_fits(ffref_path, dims=2)
            ff = FlatFieldMask(ffref_img, flatfield_regions, ffref_err)
            fm = FilterMask(ffref_img, filter_boundaries, ffref_err)
            ff.create_flatfields(fm, trim=False)

            # print(f"Path: {ffref_path}, Label: {flatfield_labels[n]}")

            whole_flatfield += getattr(
                ff, f"{flatfield_labels[n]}_flatfield"
            ).filled(0)

            whole_flatfield_var += getattr(
                ff, f"{flatfield_labels[n]}_flatfield_var"
            ).filled(0)

    elif Path(flatfield_ref_pointer).is_file():
        ffref_file = flatfield_ref_pointer

        ffref_img, ffref_err = read_fits(ffref_file, dims=2)

        ff = FlatFieldMask(ffref_img, flatfield_regions, ffref_err)
        fm = FilterMask(ffref_img, filter_boundaries, ffref_err)
        ff.create_flatfields(fm, trim=False)

        whole_flatfield = getattr(
            ff, f"{flatfield_labels[0]}_flatfield"
        ).filled(0)
        whole_flatfield_var = getattr(
            ff, f"{flatfield_labels[0]}_flatfield_var"
        ).filled(0)

    else:
        raise ValueError("Flatfield Reference is incompatible.")

    primaryHDU = fits.PrimaryHDU(whole_flatfield)
    varHDU = fits.ImageHDU(whole_flatfield_var, name="VARIANCE")
    hdul = fits.HDUList([primaryHDU, varHDU])
    hdul.writeto(Path(save_dir, "flatfield.fits"), overwrite=True)
    print(f"Flatfield saved to: {save_dir}/flatfield.fits")


def save_ffcorr_directory(
    uncorrected_dir: str | os.PathLike,
    flatfield_image: str | os.PathLike,
    save_dir: str | os.PathLike,
) -> None:
    """
    Creates a flat-field corrected directory of images.

    Parameters
    ----------
    uncorrected_dir: string
        File path to list of un-corrected images. Bias should be removed
        and images should be named for their IT (i.e. ITN.fits where N is the
        IT).
    flatfield_image: string
        File path to single flat field image for all filters.
    save_dir: string
        File path to the location to save the corrected images.

    Returns
    -------
    None
    """

    save_dir = Path(save_dir)
    if not save_dir.exists():
        save_dir.mkdir()

    print(f"Saving flatfield corrected images to: {save_dir}")

    flatfield, flatfield_var = read_fits(flatfield_image, dims=2)

    # Ensuring no divide by zero errors occur between filter boundaries
    flatfield[flatfield == 0] = np.nan
    flatfield_var[flatfield_var == 0] = np.nan

    # Returns ndarray and metadata dictionary
    nfiles = sum([1 for _ in Path(uncorrected_dir).iterdir()])
    pbar = tqdm(
        Path(uncorrected_dir).iterdir(), desc="No files read: ", total=nfiles
    )
    for i in pbar:
        pbar.desc = f"Image saved as {Path(i.stem).with_suffix('.fits')}"
        arr, _ = read_fits(i, dims=2)
        arr[arr == 0] = np.nan
        corrected_image = arr / flatfield
        corrected_var = corrected_image**2 * (flatfield_var / flatfield**2)

        hdu1 = fits.PrimaryHDU(corrected_image)
        hdu2 = fits.ImageHDU(corrected_var, name="VARIANCE")

        hdul = fits.HDUList([hdu1, hdu2])
        hdul.writeto(
            f"{Path(save_dir, i.with_suffix('.fits').name)}", overwrite=True
        )

    print("Complete!")

    return None
