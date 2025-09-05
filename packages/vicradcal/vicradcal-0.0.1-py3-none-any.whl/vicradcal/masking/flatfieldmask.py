
# Standard Libraries
from typing import Optional

# External Imports
import numpy as np

# Top-Level Imports
from vicradcal.constants import VIC_IMAGE_SIZE

# Relative Imports
from .filtermask import FilterMask


class FlatFieldMask():
    """
    Flat field class. The attributes are the flat fields for every filter.

    Parameters
    ----------
    ref_img: np.ndarray
        Reference image for the flat field. Nominally, this will be a mean of
        1000 images taken at roughly 80% saturation.
    flat_field_regions: dict
        Dictionary of sub-filter pixel regions that will be corrected to
        when making the flat-field correction.
    ref_img_var: np.ndarray, optional.
        Reference image variance. If None (default), no error will be
        calculated on the flatfield.
    """
    def __init__(
        self,
        ref_img: np.ndarray,
        flat_field_regions: dict,
        ref_img_var: Optional[np.ndarray] = None
    ):
        self.ref_img = ref_img
        self.flat_field_regions = flat_field_regions

        if ref_img_var is None:
            self.ref_img_var = np.zeros_like(ref_img)
        else:
            self.ref_img_var = ref_img_var

        for key, val in flat_field_regions.items():
            mask = np.ones(VIC_IMAGE_SIZE, bool)
            mask[val[2]:val[3], val[0]:val[1]] = False

            setattr(self, key, np.ma.masked_array(ref_img, mask))

            setattr(
                self,
                f'{key}_mean',
                np.mean(getattr(self, key).compressed())
            )

            setattr(
                self,
                f'{key}_var',
                np.var(getattr(self, key).compressed())
            )

    def create_flatfields(self, filtermask: FilterMask, trim: bool = False):
        """
        Creates flat field images for each filter.

        Parameters
        ----------
        filtermask: FilterMask
            FilterMask object for the un-corrected data
        trim: bool, optional, default=False
            Toggles whether or not to trim the filters to filter size. If
            False, flatfield images will be masked arrays of the original
            image size.
        """
        filtermask._crop_top_bottom()

        if trim:
            filtermask._trim_image()

        for key in self.flat_field_regions.keys():
            filt_data = getattr(filtermask, key)
            filt_var = getattr(filtermask, f'{key}_var')
            ffregion_mean = getattr(self, f'{key}_mean')
            ffregion_var = getattr(self, f'{key}_var')
            setattr(
                self, f'{key}_flatfield', filt_data / ffregion_mean
            )

            setattr(
                self,
                f'{key}_flatfield_var',
                filt_data / getattr(self, f'{key}_mean') *
                (filt_var / filt_data**2) + (ffregion_var / ffregion_mean**2)
            )

    def trim_image(self):
        for key in self.flat_field_regions.keys():
            ff = getattr(self, f'{key}_flatfield')
            print(type(ff))
            coords = np.argwhere(~ff)
            top_left = coords.min(axis=0)
            bottom_right = coords.max(axis=0)
            setattr(self,
                    f'{key}_flatfield',
                    ff[top_left[0]:bottom_right[0]+1,
                       top_left[1]:bottom_right[1]+1])

    def combine_flatfields(self):
        combined_ff = np.zeros(self.ref_img.shape, 'float')
        for key in self.flat_field_regions.keys():
            ff_correction = getattr(self, f'{key}_flatfield').astype('float')
            combined_ff += ff_correction.filled(0)
        return combined_ff
