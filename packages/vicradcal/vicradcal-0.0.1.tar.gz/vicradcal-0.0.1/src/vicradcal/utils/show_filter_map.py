
# External Imports
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

# Local Imports
from vicradcal.constants import (
    VIC_IMAGE_SIZE, VIC_FILTER_BOUNDARIES, VIC_FILTER_WVL_DICT,
    VIC_FLAT_FIELD_REGIONS, EDU_FILTER_BOUNDARIES, EDU_FILTER_WVL_DICT,
    EDU_FLAT_FIELD_REGIONS
)


def show_filter_map(cam: str = "VIC", show_flatfield_regions: bool = False):
    if cam not in ["VIC", "EDU"]:
        raise ValueError(f"{cam} is an invalid camera type.")

    imsize = VIC_IMAGE_SIZE
    if cam == "VIC":
        filtbounds = VIC_FILTER_BOUNDARIES
        wvldict = VIC_FILTER_WVL_DICT
        ff_regions = VIC_FLAT_FIELD_REGIONS
    else:
        filtbounds = EDU_FILTER_BOUNDARIES
        wvldict = EDU_FILTER_WVL_DICT
        ff_regions = EDU_FLAT_FIELD_REGIONS
    n = 0
    image_arr = np.zeros(imsize)

    f, ax = plt.subplots()
    for val, (val1, val2), val3 in zip(
        filtbounds.values(),
        wvldict.items(),
        ff_regions.values()
    ):
        n += 1
        image_arr[val[2]:val[3], val[0]:val[1]] = 1
        ax.text(
            (val[0]+val[1])/2, (val[3]+val[2])/2,
            f'Filter {val1[-1]}: {val2} nm',
            color='black', rotation='vertical', zorder=2
        )
        if show_flatfield_regions:
            r = Rectangle(
                (val3[0], val3[2]),
                val3[1]-val3[0], val3[3]-val3[2],
                edgecolor='r', facecolor='none', linewidth=1, zorder=1
            )
            ax.add_patch(r)

    ax.imshow(image_arr, cmap='gray')
    plt.show()
