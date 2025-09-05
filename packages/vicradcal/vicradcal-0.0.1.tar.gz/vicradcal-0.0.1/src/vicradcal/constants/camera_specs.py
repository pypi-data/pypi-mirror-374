VIC_IMAGE_SIZE = (int(2004), int(2752))  # Pixel dimensions of a VIC Image

# WVL Dictionary values are tuples like (band center, band width)
VIC_FILTER_WVL_DICT = {
    'filter1': (415, 30),
    'filter2': (850, 40),
    'filter3': (750, 40),
    'filter4': (565, 40),
    'filter5': (675, 40),
    'filter6': (900, 40),
    'filter7': (950, 40)
}

EDU_FILTER_WVL_DICT = {
    'filter2': (850, 40),
    'filter3': (750, 40),
    'filter4': (566, 40),
    'filter5': (675, 40),
    'filter6': (900, 40),
    'filter7': (950, 40)
}

# Conversion from shutter width (IT) to exposure time (s)
IT_CONVERSION = 1.214E-4
