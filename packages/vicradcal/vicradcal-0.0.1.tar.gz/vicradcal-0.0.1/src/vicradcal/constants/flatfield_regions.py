"""
Flatfield region format is:
'filternum': (left_col, right_col, top_row, bottom_row)
"""

VIC_FLAT_FIELD_REGIONS = {
    'filter1': (int(75), int(175), int(680), int(980)),
    'filter2': (int(470), int(570), int(920), int(1220)),
    'filter3': (int(890), int(990), int(390), int(690)),
    'filter4': (int(1270), int(1370), int(820), int(1120)),
    'filter5': (int(1670), int(1770), int(890), int(1190)),
    'filter6': (int(2065), int(2165), int(620), int(920)),
    'filter7': (int(2460), int(2560), int(860), int(1160))
}

EDU_FLAT_FIELD_REGIONS = {
    'filter2': (246, 326, 1050, 1182),
    'filter3': (665, 745, 437, 564),
    'filter4': (1068, 1148, 1610, 1749),
    'filter5': (1446, 1526, 531, 693),
    'filter6': (1827, 1907, 942, 1089),
    'filter7': (2250, 2320, 1035, 1221),
}
