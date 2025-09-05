# Standard Libraries
from pathlib import Path
import os
from typing import Tuple

# Dependencies
import numpy as np
from tqdm import tqdm  # type: ignore

# Top-Level Imports
from vicradcal.constants import VIC_IMAGE_SIZE

# Relative Imports


PathLike = str | os.PathLike | Path


def read_dat(filepath: PathLike,
             image_size: tuple[int, int] = VIC_IMAGE_SIZE,
             num_images: int = 100) -> np.ndarray:
    """
    Loads a binary .dat image file into a numpy array

    Parameters
    ----------
    filepath: str
        Path to .dat file
    image_size: optional, tuple of ints
        Size of whole image frame, default: VIC_IMAGE_SIZE
    num_images: optional, int
        Number of repeated images in .dat file, default: 100
    """

    if Path(filepath).suffix != '.dat':
        raise ValueError('Input filepath is not a compatible format!')

    with open(filepath, 'rb') as file:
        binary_data = file.read()
        int_data = np.frombuffer(binary_data, 'uint16')
        array_data = int_data.reshape(*image_size[::-1],
                                      num_images,
                                      order='F').transpose(1, 0, 2)

    return np.array(array_data)


def read_dat_large(
    filepath: str,
    num_images: int,
    image_size: tuple[int, int] = VIC_IMAGE_SIZE,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Reads in .dat files with over image stacks > 100

    Parameters
    ----------
    filepath: str
        File path to .dat file
    image_size: tuple of int
        Pixel dimensions of image
    num_images: int
        Number of images in the stack. Should be > 100.

    Returns
    -------
    tuple of ndarray
        Mean array, Variance array
    """

    if Path(filepath).suffix != '.dat':
        raise ValueError('Input filepath is not a compatible format!')

    slices_per_iter = 1

    num_steps = int(num_images/slices_per_iter)

    mean_array = np.zeros(image_size)
    var_array = np.zeros(image_size)

    with open(filepath, 'rb') as file:
        chunk_start = 0
        chunk_size = image_size[0] * image_size[1] * 2 * slices_per_iter
        pbar = tqdm(range(num_steps),
                    total=num_steps,
                    desc=f"Chunk 0 of {num_steps}")

        for n in pbar:
            pbar.desc = f"Chunk {n+1} of {num_steps}"
            file.seek(chunk_start)
            binary_data = file.read(chunk_size)
            int_data = np.frombuffer(binary_data, 'uint16')
            array_data = int_data.reshape(*image_size[::-1],
                                          order='F').transpose(1, 0)

            # Welford's algorithm
            delta = array_data - mean_array
            mean_array += delta / (n+1)  # update mean
            delta2 = array_data - mean_array
            var_array += delta * delta2  # update variance

            chunk_start += chunk_size

    return mean_array, var_array / num_images
