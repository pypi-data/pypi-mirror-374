# Standard Libraries
import os
from pathlib import Path

# Dependencies
import numpy as np
from astropy.io import fits  # type: ignore

# Top-Level Imports
from vicradcal.constants import (
    VIC_FILTER_BOUNDARIES,
    EDU_FILTER_BOUNDARIES,
    VIC_FILTER_WVL_DICT,
    EDU_FILTER_WVL_DICT,
)
from vicradcal.masking import FilterMask
from vicradcal.utils.linear_fitting import fit_single_line_with_error

# Relative Imports
from .get_mean_variance import get_mean_variance


def estimate_fullwell_number(
    cube: np.ndarray, minimum_fullwell: int = 2
) -> int:
    """
    Given an image cube dataset with axis=3 being the integration time domain,
    estiamtes the number of slices are saturated or at the "full-well" level.
    """
    all_mean_vals = np.nanmean(cube, axis=(1, 2))
    saturated_idx = np.argwhere(
        (all_mean_vals / all_mean_vals.max()) > 0.98
    ).flatten()
    if len(saturated_idx) == 0:
        full_well_slices = 0
    else:
        full_well_slices = len(all_mean_vals) - saturated_idx.min()

    full_well_slices += minimum_fullwell  # Default full-well slices = 2.

    return full_well_slices


def build_curve_full_filter(
    ffcorr_collection: str | os.PathLike,
    camera: str,
    analyzed_filter: str | float,
) -> None:
    """
    Builds a photon transfer curve from flat-field corrected data.

    Parameters
    ----------
    ffcorr_collection: path-like
        File path to the .fits image cube of flat-field corrected data.
    camera: str
        Camera type for the dataset. Options are:

        - `"VIC"`
        - `"EDU"`

    analyzed_filter: str or float
        Either the band number of the filter analyzed in the ffcorr collection
        or `all` if all filters are analyzed.
    """
    # Handling Path Argument
    ffcorr_collection = Path(ffcorr_collection)

    # Validating camera argument
    if camera not in ["VIC", "EDU"]:
        raise ValueError(f"Invalid camera type: {camera}")

    # Opening the dataset
    print(f"Opening {ffcorr_collection}")
    ds = fits.open(ffcorr_collection)
    dat = ds[0].data  # type: ignore
    dat_var = ds["VARIANCE"].data  # type: ignore
    int_times = ds["ITLABELS"].data["ITLabels"]  # type: ignore
    ds.close()

    if camera == "VIC":
        filt_bounds = VIC_FILTER_BOUNDARIES
        filt_wvl_dict = VIC_FILTER_WVL_DICT
        filt_list = [f"filter{n}" for n in range(1, 8)]
    else:
        filt_bounds = EDU_FILTER_BOUNDARIES
        filt_wvl_dict = EDU_FILTER_WVL_DICT
        filt_list = [f"filter{n}" for n in range(2, 8)]

    fm = FilterMask(dat, filt_bounds, dat_var)
    fm._trim_image_3D()
    ptc_data = {}

    if analyzed_filter == "all":
        for filt in filt_list:
            print(f"\n============Filter {filt[-1]}============")
            data = getattr(fm, filt)
            data_var = getattr(fm, f"{filt}_var")
            exclude_slices = estimate_fullwell_number(data)

            mean, variance, variance_err = get_mean_variance(
                data[:-exclude_slices, :, :], data_var[:-exclude_slices, :, :]
            )

            ptc_data[filt] = np.concat(
                [
                    int_times[:-exclude_slices, np.newaxis],
                    mean[:, np.newaxis],
                    variance[:, np.newaxis],
                    variance_err[:, np.newaxis],
                ],
                axis=1,
            )

            print(
                f"Filter {filt[-1]} of {filt_list[-1][-1]} complete. "
                f"{exclude_slices} integration times were excluded. \n"
            )
    else:
        filt = f"filter{analyzed_filter}"
        print(f"\n============Filter {filt[-1]} (single)============")
        data = getattr(fm, filt)
        data_var = getattr(fm, filt)
        exclude_slices = estimate_fullwell_number(data)

        mean, variance, variance_err = get_mean_variance(
            data[:-exclude_slices, :, :], data_var[:-exclude_slices, :, :]
        )

        ptc_data[filt] = np.concat(
            [
                int_times[:-exclude_slices, np.newaxis],
                mean[:, np.newaxis],
                variance[:, np.newaxis],
                variance_err[:, np.newaxis],
            ],
            axis=1,
        )

        print(
            f"Filter {filt[-1]} of {filt_list[-1][-1]} complete. "
            f"{exclude_slices} integration times were excluded. \n"
        )

    # Saving PTC Data...
    save_dir = ffcorr_collection.parent
    filters_dir = Path(save_dir, "ptc_data")

    if not filters_dir.is_dir():
        filters_dir.mkdir()
        print(f"Created save directory: {filters_dir}")

    for filt, data in ptc_data.items():
        filtsave = Path(filters_dir, f"{filt}.txt")
        np.savetxt(
            filtsave,
            np.array(data),
            header="Integration_Time, Mean, Variance, Variance_Error",
        )
        print(f"{filt} saved to {filtsave}")

    # Saving slope info...
    slope_array = np.empty([len(ptc_data), 6])
    for n, (filter_num, filter_ptc) in enumerate(ptc_data.items()):
        mean_vals = filter_ptc[:, 1]
        variance_vals = filter_ptc[:, 2]
        variance_err_vals = filter_ptc[:, 3]

        _, _, m, merr, b, berr = fit_single_line_with_error(
            mean_vals, variance_vals, variance_err_vals
        )

        slope_array[n, :] = [
            filter_num[-1],
            filt_wvl_dict[filter_num][0],
            m,
            merr,
            b,
            berr,
        ]

    slopesave = Path(save_dir, "slope_data.txt")
    np.savetxt(
        slopesave,
        slope_array,
        header="Filter, Filter_Wavelength(nm), Gain, Gain_Error, Intercept,"
        "Intercept_Error",
    )
    print(f"Gain information saved to {slopesave}")

    return None
