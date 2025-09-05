# Standard Libraries
from pathlib import Path
import os
from typing import Optional

# Dependencies
from astropy.io import fits  # type: ignore
import numpy as np

# Top-Level Imports
from vicradcal.constants import VIC_IMAGE_SIZE

# Relative Imports
from .read_dat import read_dat

PathLike = str | os.PathLike | Path


def dat2fits(file_input: PathLike,
             save_path: PathLike,
             options: Optional[dict] = None,
             **kwargs) -> None:
    """
    Reads in .dat binary images and turns them into FITS files with
    human-readable metadata.

    Parameters
    ----------
    file_input: str
        File path to either a single .dat file or to a directory containing
        several .dat files.
    save_path: str
        File path of a single FITS file or a directory to save several FITS
        files. If file_input is a directory, save_name be one also. Similarly
        if file_input is a single file, save_name must be one also.
    options: dict, optional
        A dictionary containg option key-value pairs. If None, default options
        will be passed.

        -`"image_size"` (tuple of ints, default: `VIC_IMAGE_SIZE`): Pixel
           dimensions of VIC Image.

        -`"num_images"` (int, default: 100): Number of repeated images.

        -`"save_mode"`: (str, default: singleimage): Specifies what to save
           from .dat file. Options are:

            - `"wholefile"`: Saves all `num_images` repeated images.
            - `"meanimage"`: Saves the mean of the `num_images`.
            - `"singleimage"`: Saves a single image from the `num_images`.

        -`"image_picking"`: If `save_mode` is `"singleimage"`, this must be
           specified. Options are:

            - `"random"`: Randomly selects image from stack.
            - `"set"`: Prompt user to select an index used for every file.

        -`"bias_frame"` (ndarray or None, default: None): If not None, then
           subtracts the bias frame from the save mode.

        -`"metadata"` (list[dict], default: list[{'Index': 1}, {'Index': 2}]
           List of dict of metadata key-value pairs. A list can only be
           specified if `file_input` is a directory and the length must match
           the number of files in this directory. Keys must be <8 characters
           by FITS file standards.

        -`"namekey"` (str, default:'Index'): metadata dict key to use a file
           name.
    **kwargs
        Will be passed as key-value pairs to options dictionary.

    Returns
    -------
    None

    Raises
    ------
    ValueError
        If an invalid option is specified.
    ValueError
        If file_input and save_path are not both directories or single files.
    ValueError
        If file_input is not a valid file or directory.
    ValueError
        If an invalid save mode is passed.
    """
    # Setting options
    if options is None:
        options = {}

    options = {**options, **kwargs}

    valid_options = ["image_size", "num_images", "save_mode", "image_picking",
                     "bias_frame", "metadata", "namekey"]

    if any([i not in valid_options for i in options.keys()]):
        raise ValueError("Invalid option was specified!")

    # Converting str to Path objects
    save_path = Path(save_path)
    file_input = Path(file_input)

    # Checking whether file_input is a single file or a directory and
    # ensuring compatibility between the two.
    if file_input.is_dir():
        print("Input directory identified!")
        file_paths = [Path(file_input, i) for i in file_input.iterdir()]
        dir_input = True
        if save_path.suffix != '':
            raise ValueError('file_input and save_path are incompatible.')

    elif file_input.is_file():

        file_paths = [file_input]
        dir_input = False
        if save_path.suffix == '':
            raise ValueError('file_input and save_path are incompatible.')

    else:
        raise ValueError("file_path does not exist!")

    # Ensuring the existence of save location
    if dir_input:
        if not save_path.is_dir():
            save_path.mkdir(parents=True, exist_ok=False)
    elif not dir_input:
        if not save_path.is_file():
            save_path.touch()

    # Creating default metadata and namekey
    default_metadata = [{'Index': n} for n, i in enumerate(file_paths)]
    namekey = options.get('namekey', 'Index')
    metadata = options.get('metadata', default_metadata)

    # Saving files
    savemode = options.get('save_mode', 'singleimage')
    bf = options.get('bias_frame', None)
    # Ensuring valid save mode
    if not any([savemode == i for i in ['meanimage',
                                        'singleimage',
                                        'wholeimage']]):

        raise ValueError("Invalid save mode selected!")

    num_images = options.get('num_images', 100)
    for n, i in enumerate(file_paths):
        img_array = read_dat(i,
                             options.get('image_size', VIC_IMAGE_SIZE),
                             num_images)

        # Handling save_mode options
        if savemode == 'meanimage':
            mean_image = np.mean(img_array, 2)
            var_image = np.var(img_array, 2)

            if bf is not None:
                mean_image -= bf

            mean_hdu = fits.PrimaryHDU(mean_image)
            var_hdu = fits.ImageHDU(var_image, name='VARIANCE')

            hdr = mean_hdu.header
            for key, value in metadata[n].items():
                hdr[key] = value

            if dir_input:
                savefilename = Path(
                    f'{save_path}/{metadata[n].get(namekey)}.fits'
                )
            else:
                savefilename = save_path

            hdul = fits.HDUList([mean_hdu, var_hdu])
            hdul.writeto(savefilename,
                         overwrite=True)

        elif savemode == 'singleimage':
            if options.get('image_picking', 'random') == 'random':
                single_image_index = np.random.randint(
                    0, num_images
                    )
            elif options.get('image_picking', 'random') == 'set':
                single_image_index = int(input(f"Select image index between 0"
                                         f"and {num_images}: "))
            else:
                raise ValueError("Image picking method not suported")

            single_image = img_array[:, :, single_image_index].astype('float')

            if bf is not None:
                single_image -= bf

            hdu = fits.PrimaryHDU(single_image)
            hdr = hdu.header

            hdr['img_idx'] = single_image_index
            for key, value in metadata[n].items():
                hdr[key] = value

            if dir_input:
                savefilename = Path(
                    f'{save_path}/{metadata[n].get(namekey)}.fits'
                )
            else:
                savefilename = save_path

            hdu.writeto(savefilename,
                        overwrite=True)

        else:
            raise ValueError("Invalid save mode!")

        print(f'Saved to {savefilename}')
    print(f'All {len(file_paths)} files saved')
