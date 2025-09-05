# Dependencies
import numpy as np

# Top-Level Imports
from vicradcal.constants import VIC_IMAGE_SIZE


class ColorIdx:
    y1 = np.arange(0, 2003, 2)
    y2 = np.arange(1, 2004, 2)
    x1 = np.arange(0, 2751, 2)
    x2 = np.arange(1, 2752, 2)

    r = np.meshgrid(y1, x2)
    g1 = np.meshgrid(y1, x1)
    g2 = np.meshgrid(y2, x2)
    b = np.meshgrid(y2, x1)


class OctantIdx:
    y1 = np.arange(2, VIC_IMAGE_SIZE[0]-1, 2)
    y2 = np.arange(3, VIC_IMAGE_SIZE[0], 2)

    x1 = np.arange(0, VIC_IMAGE_SIZE[1]-3, 4)
    x2 = np.arange(1, VIC_IMAGE_SIZE[1]-2, 4)
    x3 = np.arange(2, VIC_IMAGE_SIZE[1]-1, 4)
    x4 = np.arange(3, VIC_IMAGE_SIZE[1], 4)

    r1 = np.meshgrid(y1, x2)
    r2 = np.meshgrid(y1, x4)

    g11 = np.meshgrid(y1, x1)
    g12 = np.meshgrid(y1, x3)

    g21 = np.meshgrid(y2, x2)
    g22 = np.meshgrid(y2, x4)

    b1 = np.meshgrid(y2, x1)
    b2 = np.meshgrid(y2, x3)
