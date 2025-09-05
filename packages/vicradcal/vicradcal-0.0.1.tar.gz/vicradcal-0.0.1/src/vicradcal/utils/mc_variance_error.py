# Dependencies
import numpy as np


def mc_variance_error(
    x: np.ndarray, sigma_x: np.ndarray, n_samples=10000
) -> tuple[np.ndarray, np.ndarray]:
    """
    Estimates the sample variance and its uncertainty using a Monte Carlo
    method.

    Parameters
    ----------
    x: array-like
        Array of measured values.
    sigma_x: array-like
        Array of 1-sigma uncertainties on each value of `x`.
    n_samples: int
        Number of Monte Carlo samples.

    Returns
    -------
    var_est: float
        Estimated sample variance.
    var_std: float
        Estimated standard error (uncertainty) on the variance.
    """
    rng = np.random.default_rng()
    x = np.asarray(x)
    sigma_x = np.asarray(sigma_x)

    # Generate Monte Carlo runs of the data
    mc_runs = np.empty(n_samples)
    for i in range(n_samples):
        sample = rng.normal(loc=x, scale=sigma_x)
        # Compute sample variance for each Monte Carlo run
        mc_runs[i] = np.nanvar(sample, ddof=1)

    true_var_est = np.nanmean(mc_runs) - np.nanmean(sigma_x**2)

    mc_err = np.nanstd(mc_runs, ddof=1)
    data_err = np.nanstd(np.nanmean(sigma_x**2))

    true_var_std = np.sqrt(mc_err**2 + data_err**2)

    return np.array(true_var_est), true_var_std
