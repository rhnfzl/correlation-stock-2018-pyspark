import numpy as np


def numpy_correlation(a, b):

    nan = np.isnan(a) | np.isnan(b)
    a = a[~nan]
    b = b[~nan]

    size = len(a)

    numerator = np.sum(a*b) - np.sum(a)*np.sum(b)/size
    denominator = np.sqrt( (np.sum(a**2) - np.sum(a)**2/size) * (np.sum(b**2) - np.sum(b)**2/size) )

    if denominator == 0:
        return 0

    return numerator / denominator
