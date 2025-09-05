# Standard Libraries
import os
from pathlib import Path

# Dependencies
import numpy as np

# Top-Level Imports
from vicradcal.io.read_fits import read_ITsweep
from vicradcal.masking.filtermask import FilterMask
from vicradcal.constants import VIC_FILTER_BOUNDARIES, EDU_FILTER_BOUNDARIES
from vicradcal.utils.linear_fitting import fit_linear_cube_with_error, save_fit


PathLike = str | os.PathLike | Path


def build_curve_pixelbypixel(
    mean_image_collection: PathLike,
    camera: str,
    analyzed_filter: str | int,
):
    """
    Builds a photon transfer curve for every pixel in a collection of mean
    images. The means are taken from a stack of repeated images.

    Parameters
    ----------
    camera: str
        Either "VIC" or "EDU"
    analyzed_filter: str | int
        Either "all" for a long IT collection, or the filter number (1-7 for
        VIC, 2-7 for EDU).
    """
    data, data_var, itlbls = read_ITsweep(mean_image_collection)
    save_dir = Path(Path(mean_image_collection).parent, "pixel_gains")
    if not save_dir.is_dir():
        save_dir.mkdir()

    if camera == "VIC":
        filt_bounds = VIC_FILTER_BOUNDARIES
    elif camera == "EDU":
        filt_bounds = EDU_FILTER_BOUNDARIES
    else:
        raise ValueError(f"{camera} is an invalid camera type")

    filt_mask = FilterMask(data, filt_bounds, data_var)
    filt_mask._trim_image_3D()

    def fit_curve_single_filter(filter_name: str):
        filt_data = getattr(filt_mask, filter_name)
        filt_var = getattr(filt_mask, f"{filter_name}_var")
        filt_var_se = np.sqrt(2 * filt_var**2 / (filt_data.shape[0] - 1))

        sat_test = np.mean(filt_data, axis=(1, 2))
        nonsat_idx = sat_test < (0.94 * sat_test.max())

        fitresult = fit_linear_cube_with_error(
            filt_var[nonsat_idx, ...],
            filt_data[nonsat_idx, ...],
            filt_var_se[nonsat_idx, ...],
            bandsfirst=True,
        )

        save_file = Path(save_dir, filter_name).with_suffix(".fits")
        save_fit(fitresult, save_file)
        print(f"Pixel Gains saved to: {save_file}")

    if analyzed_filter == "all":
        for i in filt_bounds.keys():
            fit_curve_single_filter(i)
    else:
        fit_curve_single_filter(f"filter{analyzed_filter}")
