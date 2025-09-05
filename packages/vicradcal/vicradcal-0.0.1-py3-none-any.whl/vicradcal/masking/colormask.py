# Dependencies
import numpy as np
from numpy.ma import MaskedArray

# Top-Level Imports
from vicradcal.constants import VIC_IMAGE_SIZE, ColorIdx, OctantIdx


class ColorMask():
    def __init__(self, data: np.ndarray):
        r_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)
        g1_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)
        g2_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)
        b_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)

        r_mask[*ColorIdx.r] = False
        g1_mask[*ColorIdx.g1] = False
        g2_mask[*ColorIdx.g2] = False
        b_mask[*ColorIdx.b] = False

        self.red_pixels: MaskedArray = np.ma.masked_array(data, r_mask)
        self.green1_pixels: MaskedArray = np.ma.masked_array(data, g1_mask)
        self.green2_pixels: MaskedArray = np.ma.masked_array(data, g2_mask)
        self.blue_pixels: MaskedArray = np.ma.masked_array(data, b_mask)

    def trim_image(self):
        coords = np.argwhere(~self.green1_pixels.mask)
        top_left = coords.min(axis=0)
        bottom_right = coords.max(axis=0)

        self.red_pixels = self.red_pixels[top_left[0]:bottom_right[0]+1,
                                          top_left[1]:bottom_right[1]+1]

        self.green1_pixels = self.green1_pixels[top_left[0]:bottom_right[0]+1,
                                                top_left[1]:bottom_right[1]+1]

        self.green2_pixels = self.green2_pixels[top_left[0]:bottom_right[0]+1,
                                                top_left[1]:bottom_right[1]+1]

        self.blue_pixels = self.blue_pixels[top_left[0]:bottom_right[0]+1,
                                            top_left[1]:bottom_right[1]+1]


class OctantMask():
    def __init__(self, data: np.ndarray):
        r1_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)
        r2_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)

        g11_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)
        g12_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)

        g21_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)
        g22_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)

        b1_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)
        b2_mask = np.ones(VIC_IMAGE_SIZE).astype(bool)

        r1_mask[OctantIdx.r1] = False
        r2_mask[OctantIdx.r2] = False

        g11_mask[OctantIdx.g11] = False
        g12_mask[OctantIdx.g12] = False

        g21_mask[OctantIdx.g21] = False
        g22_mask[OctantIdx.g22] = False

        b1_mask[OctantIdx.b1] = False
        b2_mask[OctantIdx.b2] = False

        self.r1_pixels: MaskedArray = np.ma.masked_array(data, r1_mask)
        self.r2_pixels: MaskedArray = np.ma.masked_array(data, r2_mask)

        self.g11_pixels: MaskedArray = np.ma.masked_array(data, g11_mask)
        self.g12_pixels: MaskedArray = np.ma.masked_array(data, g12_mask)

        self.g21_pixels: MaskedArray = np.ma.masked_array(data, g21_mask)
        self.g22_pixels: MaskedArray = np.ma.masked_array(data, g22_mask)

        self.b1_pixels: MaskedArray = np.ma.masked_array(data, b1_mask)
        self.b2_pixels: MaskedArray = np.ma.masked_array(data, b2_mask)

    def trim_image(self):
        coords = np.argwhere(~self.g11_pixels.mask)
        top_left = coords.min(axis=0)
        bottom_right = coords.max(axis=0)

        self.r1_pixels = self.r1_pixels[top_left[0]:bottom_right[0]+1,
                                        top_left[1]:bottom_right[1]+1]
        self.r2_pixels = self.r2_pixels[top_left[0]:bottom_right[0]+1,
                                        top_left[1]:bottom_right[1]+1]

        self.g11_pixels = self.g11_pixels[top_left[0]:bottom_right[0]+1,
                                          top_left[1]:bottom_right[1]+1]
        self.g12_pixels = self.g12_pixels[top_left[0]:bottom_right[0]+1,
                                          top_left[1]:bottom_right[1]+1]

        self.g21_pixels = self.g21_pixels[top_left[0]:bottom_right[0]+1,
                                          top_left[1]:bottom_right[1]+1]
        self.g22_pixels = self.g22_pixels[top_left[0]:bottom_right[0]+1,
                                          top_left[1]:bottom_right[1]+1]

        self.b1_pixels = self.b1_pixels[top_left[0]:bottom_right[0]+1,
                                        top_left[1]:bottom_right[1]+1]
        self.b2_pixels = self.b2_pixels[top_left[0]:bottom_right[0]+1,
                                        top_left[1]:bottom_right[1]+1]
