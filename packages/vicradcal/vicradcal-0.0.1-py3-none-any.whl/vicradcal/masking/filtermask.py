# Standard Imports
from typing import Optional

# Dependencies
import numpy as np

# Top-Level Imports
from vicradcal.constants import VIC_IMAGE_SIZE

# Relative Imports


class FilterMask:
    """
    Object for splitting a whole image into 7 pre-defined filter components.

    Parameters
    ----------
    data: np.ndarray
        Image Data to be split into filters.
    filter_mask_dict: dictionary
        Dictionary defining filter boundaries. Keys should be filter names
        (i.e. "filter1") and values should be a tuple of filter boundaries
        in the following format (LEFT, RIGHT, TOP, BOTTOM).
    data_var: np.ndarray, optional
        Data variance. If None, the variance will be assumed to be 0. Default
        is None.

    Attributes
    ----------
    filterN: np.ma.MaskedArray
        Filter values for filterN where N is the number of filter starting
        from the left.

    Methods
    -------
    _crop_top_bottom()
        Crops the tops and bottoms of all filters.
    _trim_image()
        Trims each filter down to just the filter size instead of the
        whole image size.
    combine_filters()
        Returns an array that combines all filter bands.
    """
    def __init__(
        self,
        data: np.ndarray,
        filter_mask_dict: dict,
        data_var: Optional[np.ndarray] = None
    ):

        self.filter_mask_dict = filter_mask_dict

        if data_var is None:
            data_var = np.zeros_like(data)

        if np.ndim(data) == 2:
            for key, val in self.filter_mask_dict.items():
                filter_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)
                filter_mask[:, val[0]:val[1]] = False
                setattr(self, key, np.ma.masked_array(data, filter_mask))
                setattr(
                    self,
                    f'{key}_var',
                    np.ma.masked_array(data_var, filter_mask)
                )

            self._crop_top_bottom()
            # self._trim_image()

        elif np.ndim(data) == 3:
            self._handle_cube(data, data_var)

    def _crop_top_bottom(self):
        row_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)

        for key, val in self.filter_mask_dict.items():
            row_mask[val[2]:val[3], :] = False
            uncropped_mask = getattr(self, key)
            setattr(self, key, np.ma.masked_where(row_mask, uncropped_mask))
            setattr(
                self,
                f'{key}_var',
                np.ma.masked_where(row_mask, getattr(self, f'{key}_var'))
            )

    def _crop_top_bottom3D(self, ax1_size: int):
        row_mask = np.ones([ax1_size, *VIC_IMAGE_SIZE]).astype(bool)

        for key, val in self.filter_mask_dict.items():
            row_mask[:, val[2]:val[3], :] = False
            uncropped_mask = getattr(self, key)
            setattr(self, key, np.ma.masked_array(uncropped_mask, row_mask))
            setattr(
                self,
                f'{key}_var',
                np.ma.masked_array(getattr(self, f'{key}_var'), row_mask)
            )

    def _trim_image(self):
        for key, val in self.filter_mask_dict.items():
            untrimmed_mask = getattr(self, key)
            untrimmed_var = getattr(self, f'{key}_var')
            setattr(self, key, untrimmed_mask[val[2]:val[3], val[0]:val[1]])
            setattr(
                self,
                f'{key}_var',
                untrimmed_var[val[2]:val[3], val[0]:val[1]]
            )

    def _trim_image_3D(self):
        for key, val in self.filter_mask_dict.items():
            untrimmed_mask = getattr(self, key)
            untrimmed_var = getattr(self, f'{key}_var')
            setattr(
                self,
                key,
                untrimmed_mask[:, val[2]:val[3], val[0]:val[1]].filled(np.nan)
            )
            setattr(
                self,
                f'{key}_var',
                untrimmed_var[:, val[2]:val[3], val[0]:val[1]].filled(np.nan)
            )

    def combine_filters(self):
        whole_image = np.zeros(VIC_IMAGE_SIZE)
        for key in self.filter_mask_dict.keys():
            whole_image += getattr(self, key).filled(0)
        return whole_image

    def _handle_cube(self, data, data_var):
        print("3D dataset detected...")
        for key, val in self.filter_mask_dict.items():
            filter_mask = np.ones(
                [data.shape[0], *VIC_IMAGE_SIZE]
            ).astype(bool)
            filter_mask[:, :, val[0]:val[1]] = False
            setattr(self, key, np.ma.masked_array(data, filter_mask))
            setattr(
                self,
                f'{key}_var',
                np.ma.masked_array(data_var, filter_mask)
            )

        self._crop_top_bottom3D(data.shape[0])
