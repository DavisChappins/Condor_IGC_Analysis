import numpy as np


time_values_sec = [122, 47, 105, 111, 69, 96, 99, 46, 61, 75, 126, 55, 106, 74, 108, 152, 88, 62, 96, 74, 101, 87, 64, 169, 128, 339]

percent90 = int(np.percentile(time_values_sec, 10))
minvalue = min(time_values_sec)