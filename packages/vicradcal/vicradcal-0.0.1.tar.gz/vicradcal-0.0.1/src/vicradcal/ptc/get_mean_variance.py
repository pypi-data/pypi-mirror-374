# Dependencies
import numpy as np
from tqdm import tqdm  # type: ignore

# Top-Level Imports
from vicradcal.utils import mc_variance_error


def get_mean_variance(
    data: np.ndarray,
    data_var: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Given an array of data representing an image cube and an array representing
    a cube of variance, returns the mean, the estimated true variance and the
    error on this true variance of the whole image dataset, which are all the
    components needed to plot a photon transfer curve.

    Parameters
    ----------
    data: np.ndarray
        An image cube where the third dimension is the Integration Time domain.
        Each image slice in the cube will be the mean of stacked images.
    data_var: str
        The corresponding variance for each mean slice.

    Return
    ------
    mean: array
        Array is of length N-exclude where N is the number of integration
        times.
    variance: array
        An estimate of the true variance calculated using Monte Carlo methods.
        Same size as `mean`.
    variance_err: array
        The estimated uncertainty on the true variance calculated using Monte
        Carlo methods. Same size as `mean`.
    """
    # Pre-compute mean
    mean = np.nanmean(data, axis=(1, 2))

    # Initialize output arrays
    variance = np.empty_like(mean)
    variance_err = np.empty_like(mean)

    pbar = tqdm(
        range(len(variance)),
        total=len(variance),
        desc="Running Monte Carlo Estimation of Variance: ",
    )

    for i in pbar:
        data_slice = data[i, :, :].flatten()
        var_slice = np.sqrt(data_var[i, :, :]).flatten()

        est_var, var_err = mc_variance_error(
            data_slice, var_slice, n_samples=100
        )

        variance[i] = est_var
        variance_err[i] = var_err

    return mean, variance, variance_err
