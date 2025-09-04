import numpy as np
from numba import njit

@njit(cache=True)
def sigmoid(x):
    """
    Compute the sigmoid function for a given input x. sigmoid(x) = 1 / (1 + exp(-x))
    """
    return 1.0 / (1.0 + np.exp(-x))

def round_alpha(alpha, hop):
    """
    Round the alpha to the nearest integer hop size.

    Args:
        alpha (float): The alpha to round.
        hop (int): The hop size.

    Returns:
        float: The rounded alpha.
    """
    return hop / int(hop / alpha)