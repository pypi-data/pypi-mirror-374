# Standard Libraries
from pathlib import Path
import os
from typing import Optional

# Dependencies
import yaml  # type: ignore

# Top-Level Imports
from vicradcal.io import read_dat_large
from vicradcal.constants import (
    VIC_FILTER_WVL_DICT,
    VIC_FLAT_FIELD_REGIONS,
    VIC_FILTER_BOUNDARIES,
    EDU_FLAT_FIELD_REGIONS,
    EDU_FILTER_BOUNDARIES,
)

# Relative Imports
from .save_it_sweep import split_repeated_images
from .save_flatfield import (
    save_flatfield_reference,
    save_flatfield_frame,
    save_ffcorr_directory,
)


class SweepConfig:
    """
    Class for storing configuration data for IT Sweep processing

    Parameters
    ----------
    config_init: Dict
        Configuration dictionary.

        - `'band'`: Number of band.
        - `'itsweep_directory'`: Directory to ITSweep files.
        - `'bf_file'`: Bias frame .dat file.
        - `'ffref_pointer'`: Either a directory or a single file, depending on
                             the processing type (single band or all)
        - `'camera'`: Camera type, either 'VIC' or 'EDU'.
        - `'temp'`: Temperature of IT sweeps.
        - `'num_bf_images'`: Number of images that make up the bias frame.
        - `'num_it_images'`: Number of images in each IT sweep image.
        - `'num_ff_images'`: Number of images in a flatfield reference.

    root_dir: str
        Path to root directory of data drive

    Attributes
    ----------
    bf_file: str
        Root directory of data
    ffref: str or list str
        Folder to dark frames within root_dir
    itsweep_directory: str
        Directory of ITsweeps
    """

    def __init__(self, config_init: dict, root_dir: str | os.PathLike) -> None:
        # Checking to make sure dictionary is valid.
        valid_keys = {
            "band",
            "itsweep_directory",
            "bf_file",
            "ffref_pointer",
            "camera",
            "temp",
            "num_bf_images",
            "num_it_images",
            "num_ff_images",
        }

        invalid_keys = set(config_init.keys()) - valid_keys
        if invalid_keys:
            raise ValueError(
                f"Invalid config entries: {', '.join(invalid_keys)}"
                f"\nExpected Keys: {', '.join(valid_keys)}"
            )

        paths = ["itsweep_directory", "bf_file", "ffref_pointer"]
        for key, val in config_init.items():
            if key in paths:
                newpath = Path(root_dir, val)
                if not newpath.exists():
                    raise FileNotFoundError(f"{newpath} does not exist.")

        self.config_init = config_init

        if self.config_init["camera"] == "VIC":
            self.filter_boundaries = VIC_FILTER_BOUNDARIES
            self.flatfield_regions = VIC_FLAT_FIELD_REGIONS
        elif self.config_init["camera"] == "EDU":
            self.filter_boundaries = EDU_FILTER_BOUNDARIES
            self.flatfield_regions = EDU_FLAT_FIELD_REGIONS
        else:
            raise ValueError("Invalid Camera Type.")

        if self.config_init["ffref_pointer"].is_file():
            self.ff_lbls = [f"filter{self.config_init["band"]}"]
            filter_num = f"filter{self.config_init["band"]}"
            filter_wvl = VIC_FILTER_WVL_DICT[filter_num]
            self.ffref_name = Path(
                f"{filter_num}_{filter_wvl[0]}_{self.config_init["temp"]}C_"
                "flatfield_reference.fits"
            )
        elif self.config_init["ffref_pointer"].is_dir():
            self.ff_lbls_dict = {}
            for i in self.config_init["ffref_pointer"].iterdir():
                file_name = Path(i).name.__str__()
                idx = file_name.find("Band")
                self.ff_lbls_dict[i.stem] = f"filter{file_name[idx+4]}"
        else:
            raise ValueError("Invalid flatfield reference point")

    def __str__(self):
        return_string = "\nIT Sweep Configuration\n"
        for k, v in self.__dict__.items():
            return_string += f"{k}: {v}\n"
        return return_string

    def convert_to_fits(
        self,
        md_template: dict,
        extra_md: Optional[dict] = None,
        convert_it: bool = True,
        convert_ff: bool = True,
        save_dir: str | os.PathLike | None = None,
    ):
        """
        Utility method for running the FITS conversion.

        Parameters
        ----------
        md_template: dict
            Metadata template dict. See `metadata_templates.py`
        extra_md: dict
            Any extra metadata to add to each IT sweep image.
        convert_it: bool, optional
            Toggles whether or not to convert it sweep images (default: True).
        convert_ff: bool, optional
            Toggles whether or not to convert flatfield (default: True).
        save_dir: path-like
            Directory to save the FITS ITsweep files to.

        Returns
        -------
        None

        Raises
        ------
        ValueError
            If an invalid configuration option is passed to `config`.
        """
        biasframe_mean, biasframe_var = read_dat_large(
            self.config_init["bf_file"],
            num_images=self.config_init["num_bf_images"],
        )

        if save_dir is None:
            self.fits_save = Path(
                self.config_init["itsweep_directory"].parent,
                f"{self.config_init["itsweep_directory"].name}_fits",
            )
        else:
            self.fits_save = Path(save_dir)

        if convert_it:
            split_repeated_images(
                self.config_init["itsweep_directory"],
                biasframe_mean,
                biasframe_var,
                self.config_init["fits_save"],
                md_template,
                num_images=self.config_init["num_it_images"],
                extra_metadata=extra_md,
            )

        if convert_ff:
            if self.config_init["ffref_pointer"].is_file():
                print("Single Band flatfield detected...")
                save_flatfield_reference(
                    self.config_init["ffref_pointer"],
                    biasframe_mean,
                    biasframe_var,
                    Path(self.fits_save),
                    self.ffref_name,
                    num_images=self.config_init["num_ff_images"],
                    extra_metadata={
                        "label": f"filter{self.config_init["band"]}"
                    },
                )
            elif self.config_init["ffref_pointer"].is_dir():
                print("Multi-Band Flatfield detected...")
                ffref_files = [
                    i for i in self.config_init["ffref_pointer"].iterdir()
                ]
                ffref_labels = [
                    f'filter{i.name.split("_")[11][-1]}'
                    for i in self.config_init["ffref_pointer"].iterdir()
                ]

                for i, j in zip(ffref_files, ffref_labels):
                    save_flatfield_reference(
                        i,
                        biasframe_mean,
                        biasframe_var,
                        Path(self.fits_save, "flatfield_references"),
                        Path(Path(i).name).with_suffix(".fits"),
                        num_images=self.config_init["num_ff_images"],
                        extra_metadata={"label": j},
                    )

    def flatfielding(self, fits_dir: str | os.PathLike):
        if self.config_init["ffref_pointer"].is_file():
            save_flatfield_frame(
                Path(fits_dir, self.ffref_name),
                self.ff_lbls,
                self.flatfield_regions,
                self.filter_boundaries,
                save_dir=str(fits_dir),
            )
        elif self.config_init["ffref_pointer"].is_dir():
            ffref_dir = Path(fits_dir, "flatfield_references")
            save_flatfield_frame(
                ffref_dir,
                [self.ff_lbls_dict[i.stem] for i in ffref_dir.iterdir()],
                self.flatfield_regions,
                self.filter_boundaries,
                save_dir=str(fits_dir),
            )

        save_ffcorr_directory(
            Path(fits_dir, "singles_nobias"),
            Path(fits_dir, "flatfield.fits"),
            Path(fits_dir, "ffcorr"),
        )


def read_sweep_config(config_path: str | os.PathLike) -> list[SweepConfig]:
    """
    Reads a .yaml file into a list of SweepConfig objects.
    """
    yaml_list = []
    config_path = Path(config_path)
    with open(config_path, "r") as f:
        for i in yaml.load_all(f, Loader=yaml.SafeLoader):
            yaml_list.append(i)

    config_list = []
    for i in yaml_list[1:]:
        sc = SweepConfig(i, yaml_list[0]["root_dir"])
        config_list.append(sc)

    return config_list
