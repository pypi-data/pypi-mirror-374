from numba import njit
import numpy as np
from utils.numeric import sigmoid


@njit(cache=True)
def compute_cosine_distance(feature_row, reference_features):
    """Compute cosine distance between normalized feature vectors.

    Assumes both feature_row and reference_features are already normalized (unit vectors).
    For normalized vectors, cosine distance = 1 - dot_product.
    """
    costs = np.empty(reference_features.shape[1], dtype=np.float32)

    for j in range(reference_features.shape[1]):
        ref_col = reference_features[:, j]
        dot_product = np.sum(feature_row * ref_col)
        costs[j] = 1.0 - dot_product

    return costs


@njit(cache=True)
def update_alignment_row_numba(i, prev_j, costs, D, B, dn, dm, dw, ref_length):
    """
    Update alignment row using numba for optimized performance.

    Args:
        i (int): Current row index in the alignment matrix.
        costs (np.ndarray): Cost vector for the current feature row.
        D (np.ndarray): Alignment cost matrix.
        B (np.ndarray): Backtrace matrix.
        dn (np.ndarray): Row step sizes.
        dm (np.ndarray): Column step sizes.
        dw (np.ndarray): Weights for each step.
        ref_length (int): Length of the reference features.
    """
    best_j = 0
    best_cost = np.inf

    for j in range(min(costs.shape[0], ref_length)):
        best_step_cost = np.inf
        best_step = -1

        for k, (di, dj, w) in enumerate(zip(dn, dm, dw)):
            prev_i, prev_j = i - di, j - dj

            if prev_i < 0 or prev_j < 0 or prev_j >= ref_length:
                continue

            cur_cost = D[prev_i, prev_j] + costs[j] * w

            if cur_cost < best_step_cost:
                best_step_cost = cur_cost
                best_step = k

        if best_step != -1:
            D[i, j] = best_step_cost
            B[i, j] = best_step

            if best_step_cost < best_cost:
                best_cost = best_step_cost
                best_j = j

    return best_j


def _get_alpha_numba(
    path,
    i,
    history=100,
    default_alpha=1.0,
    max_timewarp_factor=2.0,
    x=np.array([], dtype=np.float64),
    sum_x=-1.0,  # -1.0 means not computed yet
    sum_x2=-1.0,  # -1.0 means not computed yet
):
    """
    Calculate the alpha (playback speed factor) value based on the path and desired history window.
    Optionally uses precomputed x, sum_x, and sum_x2 for efficiency.

    Args:
        path (array): The current alignment path as a numpy array.
        i (int): The current index in the path for which to calculate the alpha value.
        history (int): The number of previous locations to consider for calculating the alpha value.
        default_alpha (float): The default alpha value to return if not enough history is available.
        max_timewarp_factor (float): Maximum time warp factor for TSM.
        x (array, optional): Precomputed x values for the current history window.
        sum_x (float, optional): Precomputed sum of x values.
        sum_x2 (float, optional): Precomputed sum of squares of x values.

    Returns:
        float: The calculated alpha value.
    """
    if i + 1 < history:
        return default_alpha

    # Get the last `history` locations
    if x.size == 0:
        x = np.arange(i - history + 1, i + 1, dtype=np.float64)  # query
    y = np.array(path[i - history + 1 : i + 1], dtype=np.float64)  # ref

    # Calculate sums for least squares formula
    sum_x, sum_y, sum_xy, sum_x2 = _calc_sums(x, y, sum_x, sum_x2)

    # Calculate alpha
    alpha = _calc_alpha(
        sum_x, sum_x2, sum_y, sum_xy, history, max_timewarp_factor, default_alpha
    )
    return alpha


@njit
def _calc_sums(x, y, sum_x, sum_x2):
    """helper function to calculate sums"""
    if sum_x == -1.0:
        sum_x = np.sum(x)
    if sum_x2 == -1.0:
        sum_x2 = np.sum(x * x)
    sum_y = np.sum(y)
    sum_xy = np.sum(x * y)
    return sum_x, sum_y, sum_xy, sum_x2


@njit
def _calc_alpha(
    sum_x, sum_x2, sum_y, sum_xy, history, max_timewarp_factor, default_alpha
):
    """helper function to calculate alpha"""
    denominator = history * sum_x2 - sum_x * sum_x

    # Handle edge case where denominator is zero (all x values are the same)
    if abs(denominator) < 1e-10:
        return default_alpha

    # Calculate slope using manual least squares formula
    # For line y = mx + c, slope m = (n*Σxy - Σx*Σy) / (n*Σx² - (Σx)²)
    m = (history * sum_xy - sum_x * sum_y) / denominator
    alpha = 1.0 / m if m != 0 else default_alpha  # alpha is inverse of slope

    # Clip m to be within a reasonable range
    alpha = max(1.0 / max_timewarp_factor, min(max_timewarp_factor, alpha))

    return alpha


@njit(cache=True)
def calc_scale_from_deviation(deviation, sensitivity, max_scale):
    """Calculate the alpha adjustment scale from the deviation between current TSM position and predicted alignment position.

    Args:
        deviation (float): The deviation between current TSM position and predicted alignment position.
        sensitivity (float): The sensitivity of the scale. Higher sensitivity means more aggressive scaling and potentially more unstable.
        max_scale (float): The maximum scale factor for alpha adjustment.

    Returns:
        float: The scale factor for alpha adjustment.
    """

    # Map deviation to a scaling factor
    normalized_deviation = sensitivity * deviation

    # use sigmoid to map deviation to a scale factor in (0, 1)
    dev_scale = sigmoid(normalized_deviation)

    # Rescale to [-1, 1]
    scale = -1 + 2 * dev_scale

    # Rescale to [-max_scale, max_scale]
    scale = max_scale**scale

    return scale
