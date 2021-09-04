import numpy as np
# Reference: https://datascience.stackexchange.com/a/68392


def entropy(array):
    unique, count = np.unique(array, return_counts=True, axis=0)
    probabilities = count / len(array)
    entropy_value = np.sum((-1) * probabilities * np.log2(probabilities))
    return entropy_value


def joint_entropy(array1, array2):
    combined = np.c_[array1, array2]
    return entropy(combined)


def conditional_entropy(array1, array2):
    """
    Conditional entropy (Y|X) = Joint Entropy (Y, X) - Entropy of condition (X)
    """
    return joint_entropy(array1, array2) - entropy(array2)


def mutual_information(X, Y):
    nan = np.isnan(X) | np.isnan(Y)
    X = X[~nan]
    Y = Y[~nan]
    return entropy(X) - conditional_entropy(X, Y)
